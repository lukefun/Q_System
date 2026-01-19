"""
数据管理器模块

提供数据持久化和管理功能，支持HDF5存储、CSV导出和增量更新
"""

import os
import pandas as pd
import tables
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from config import (
    logger,
    StorageError,
    ValidationError,
    DataError,
    HDF5_PATH,
    HDF5_COMPRESSION,
    HDF5_COMPLEVEL,
    HDF5_DATE_FORMAT,
    CSV_DATE_FORMAT,
    CSV_EXPORT_DIR
)


class DataManager:
    """
    数据持久化管理器
    
    管理本地数据存储和增量更新，使用HDF5格式实现高效的数据访问。
    支持按数据类型和股票代码分组存储，提供查询和导出功能。
    
    HDF5存储结构：
        /daily/{stock_code}     - 日线数据
        /tick/{stock_code}      - Tick数据
        /fundamental/{stock_code} - 基本面数据
        /industry/mapping       - 行业映射数据
        /industry/structure     - 行业结构数据
        /metadata/update_log    - 更新日志
    
    Attributes:
        storage_path: 数据存储根目录
        hdf5_path: HDF5文件路径
    
    Example:
        >>> manager = DataManager(storage_path="./data")
        >>> # 保存数据
        >>> manager.save_market_data(data, 'daily', '000001.SZ')
        >>> # 加载数据
        >>> loaded = manager.load_market_data('daily', '000001.SZ')
        >>> # 导出CSV
        >>> manager.export_to_csv('daily', 'output.csv', '000001.SZ')
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化数据管理器
        
        Args:
            storage_path: 数据存储根目录，None则使用配置的默认路径
        
        Raises:
            ValueError: 存储路径无效
        """
        if storage_path is None:
            self.storage_path = Path(HDF5_PATH).parent
            self.hdf5_path = Path(HDF5_PATH)
        else:
            self.storage_path = Path(storage_path)
            self.hdf5_path = self.storage_path / "market_data.h5"
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 支持的数据类型
        self._valid_data_types = ['daily', 'tick', 'fundamental', 'industry']
        
        logger.info(f"DataManager初始化完成，存储路径: {self.storage_path}")
        logger.info(f"HDF5文件路径: {self.hdf5_path}")
    
    def save_market_data(
        self,
        data: pd.DataFrame,
        data_type: str,
        stock_code: Optional[str] = None
    ) -> None:
        """
        保存市场数据到HDF5
        
        将数据保存到HDF5文件中，按数据类型和股票代码分组存储。
        如果数据已存在，会进行合并并去重。
        
        Args:
            data: 要保存的数据DataFrame
            data_type: 数据类型，如 'daily', 'tick', 'fundamental', 'industry'
            stock_code: 股票代码，None表示全市场数据或行业数据
        
        Raises:
            ValidationError: 数据验证失败
            StorageError: 存储失败
        
        Example:
            >>> data = pd.DataFrame({
            ...     'stock_code': ['000001.SZ'],
            ...     'date': ['20240101'],
            ...     'close': [10.5]
            ... })
            >>> manager.save_market_data(data, 'daily', '000001.SZ')
        """
        # 参数验证
        self._validate_data_type(data_type)
        
        if not isinstance(data, pd.DataFrame):
            if data is None:
                logger.warning("数据为None，跳过保存")
                return
            raise ValidationError(f"数据必须是DataFrame类型，当前类型: {type(data)}")
        
        if data.empty:
            logger.warning("数据为空，跳过保存")
            return
        
        logger.info(
            f"保存数据: 类型={data_type}, 股票={stock_code or '全市场'}, "
            f"记录数={len(data)}"
        )
        
        try:
            # 构建HDF5键路径
            if stock_code:
                # 替换.为_以符合HDF5键名规范
                safe_code = stock_code.replace('.', '_')
                key = f"/{data_type}/{safe_code}"
            else:
                key = f"/{data_type}/all"
            
            # 使用HDFStore保存数据
            with pd.HDFStore(
                str(self.hdf5_path),
                mode='a',
                complevel=HDF5_COMPLEVEL,
                complib='blosc:zstd'
            ) as store:
                # 检查是否已存在数据
                if key in store:
                    logger.debug(f"键 {key} 已存在，将合并数据")
                    
                    # 读取现有数据
                    existing_data = store[key]
                    
                    # 合并数据
                    combined_data = pd.concat([existing_data, data], ignore_index=True)
                    
                    # 去重（根据数据类型使用不同的去重键）
                    combined_data = self._deduplicate_data(combined_data, data_type)
                    
                    # 保存合并后的数据
                    store.put(
                        key,
                        combined_data,
                        format='table',
                        data_columns=True
                    )
                    
                    logger.info(
                        f"数据合并完成: 原有{len(existing_data)}条, "
                        f"新增{len(data)}条, 合并后{len(combined_data)}条"
                    )
                else:
                    # 直接保存新数据
                    store.put(
                        key,
                        data,
                        format='table',
                        data_columns=True
                    )
                    
                    logger.info(f"数据保存完成: {len(data)}条记录")
            
            # 记录更新日志
            self._log_update(data_type, stock_code, len(data))
        
        except Exception as e:
            error_msg = f"保存数据失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def load_market_data(
        self,
        data_type: str,
        stock_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        从HDF5加载市场数据
        
        从HDF5文件中加载数据，支持按股票代码和日期范围过滤。
        
        Args:
            data_type: 数据类型，如 'daily', 'tick', 'fundamental'
            stock_code: 股票代码，None表示加载全市场数据
            start_date: 开始日期，格式 'YYYYMMDD'，None表示不限制
            end_date: 结束日期，格式 'YYYYMMDD'，None表示不限制
        
        Returns:
            市场数据DataFrame，如果没有数据则返回空DataFrame
        
        Raises:
            ValidationError: 参数验证失败
            StorageError: 加载失败
        
        Example:
            >>> data = manager.load_market_data(
            ...     'daily',
            ...     '000001.SZ',
            ...     '20240101',
            ...     '20240110'
            ... )
        """
        # 参数验证
        self._validate_data_type(data_type)
        
        if start_date and end_date:
            self._validate_date_range(start_date, end_date)
        
        logger.info(
            f"加载数据: 类型={data_type}, 股票={stock_code or '全市场'}, "
            f"日期范围={start_date or '不限'} - {end_date or '不限'}"
        )
        
        try:
            # 检查HDF5文件是否存在
            if not self.hdf5_path.exists():
                logger.warning(f"HDF5文件不存在: {self.hdf5_path}")
                return pd.DataFrame()
            
            # 构建HDF5键路径
            if stock_code:
                safe_code = stock_code.replace('.', '_')
                key = f"/{data_type}/{safe_code}"
            else:
                key = f"/{data_type}/all"
            
            # 使用HDFStore加载数据
            with pd.HDFStore(str(self.hdf5_path), mode='r') as store:
                # 检查键是否存在
                if key not in store:
                    logger.warning(f"键 {key} 不存在")
                    return pd.DataFrame()
                
                # 读取数据
                data = store[key]
                
                logger.debug(f"从 {key} 读取 {len(data)} 条记录")
            
            # 应用日期过滤
            if start_date or end_date:
                data = self._filter_by_date(data, start_date, end_date)
            
            logger.info(f"数据加载完成: {len(data)}条记录")
            
            return data
        
        except Exception as e:
            error_msg = f"加载数据失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def get_last_update_date(
        self,
        data_type: str,
        stock_code: Optional[str] = None
    ) -> Optional[str]:
        """
        获取最后更新日期
        
        查询指定数据类型和股票代码的最后更新日期，用于增量更新。
        
        Args:
            data_type: 数据类型
            stock_code: 股票代码，None表示全市场数据
        
        Returns:
            最后更新日期，格式 'YYYYMMDD'，如果没有数据则返回None
        
        Raises:
            ValidationError: 参数验证失败
            StorageError: 查询失败
        
        Example:
            >>> last_date = manager.get_last_update_date('daily', '000001.SZ')
            >>> print(f"最后更新日期: {last_date}")
        """
        # 参数验证
        self._validate_data_type(data_type)
        
        logger.debug(
            f"查询最后更新日期: 类型={data_type}, 股票={stock_code or '全市场'}"
        )
        
        try:
            # 加载数据
            data = self.load_market_data(data_type, stock_code)
            
            if data.empty:
                logger.debug("没有数据，返回None")
                return None
            
            # 根据数据类型确定日期列
            date_column = self._get_date_column(data_type)
            
            if date_column not in data.columns:
                logger.warning(f"数据中没有日期列 {date_column}")
                return None
            
            # 获取最大日期
            last_date = data[date_column].max()
            
            logger.info(f"最后更新日期: {last_date}")
            
            return str(last_date)
        
        except Exception as e:
            error_msg = f"获取最后更新日期失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def incremental_update(
        self,
        retriever,
        stock_codes: List[str],
        data_type: str = 'daily',
        progress_callback: Optional[callable] = None
    ) -> int:
        """
        增量更新市场数据
        
        识别每只股票的最后更新日期，仅获取该日期之后的新数据。
        自动处理重复数据去重，支持进度报告回调。
        
        Args:
            retriever: 数据获取器实例（DataRetriever）
            stock_codes: 要更新的股票代码列表
            data_type: 数据类型，默认为 'daily'
            progress_callback: 进度回调函数，接收参数 (current, total, stock_code)
        
        Returns:
            更新的记录数（去重后）
        
        Raises:
            ValidationError: 参数验证失败
            DataError: 数据获取失败
            StorageError: 数据保存失败
        
        Example:
            >>> def progress(current, total, stock_code):
            ...     print(f"进度: {current}/{total} - {stock_code}")
            >>> 
            >>> updated = manager.incremental_update(
            ...     retriever,
            ...     ['000001.SZ', '000002.SZ'],
            ...     'daily',
            ...     progress_callback=progress
            ... )
            >>> print(f"共更新 {updated} 条记录")
        """
        # 参数验证
        self._validate_data_type(data_type)
        
        if not stock_codes:
            raise ValidationError("股票代码列表不能为空")
        
        if not isinstance(stock_codes, list):
            raise ValidationError("stock_codes必须是列表类型")
        
        if retriever is None:
            raise ValidationError("retriever不能为None")
        
        logger.info(
            f"开始增量更新: {len(stock_codes)}只股票, 数据类型={data_type}"
        )
        
        total_updated = 0
        total_stocks = len(stock_codes)
        
        # 获取当前日期作为结束日期
        end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            for idx, stock_code in enumerate(stock_codes, 1):
                try:
                    # 报告进度
                    if progress_callback:
                        progress_callback(idx, total_stocks, stock_code)
                    
                    logger.info(
                        f"处理股票 {idx}/{total_stocks}: {stock_code}"
                    )
                    
                    # 获取最后更新日期
                    last_date = self.get_last_update_date(data_type, stock_code)
                    
                    if last_date:
                        # 计算下一个交易日作为开始日期
                        # 将日期字符串转换为datetime对象
                        last_dt = datetime.strptime(last_date, '%Y%m%d')
                        
                        # 加一天作为开始日期
                        start_dt = last_dt + timedelta(days=1)
                        start_date = start_dt.strftime('%Y%m%d')
                        
                        logger.info(
                            f"股票 {stock_code} 最后更新日期: {last_date}, "
                            f"将获取 {start_date} 之后的数据"
                        )
                        
                        # 检查是否需要更新
                        if start_date > end_date:
                            logger.info(
                                f"股票 {stock_code} 数据已是最新，无需更新"
                            )
                            continue
                    else:
                        # 没有历史数据，从较早的日期开始
                        # 默认获取最近一年的数据
                        start_dt = datetime.now() - timedelta(days=365)
                        start_date = start_dt.strftime('%Y%m%d')
                        
                        logger.info(
                            f"股票 {stock_code} 没有历史数据，"
                            f"将获取 {start_date} 之后的数据"
                        )
                    
                    # 下载新数据
                    new_data = retriever.download_history_data(
                        stock_codes=[stock_code],
                        start_date=start_date,
                        end_date=end_date,
                        period='1d' if data_type == 'daily' else 'tick',
                        adjust_type='none'
                    )
                    
                    if new_data is None or new_data.empty:
                        logger.info(f"股票 {stock_code} 没有新数据")
                        continue
                    
                    # 检测重复数据
                    original_count = len(new_data)
                    
                    # 如果有历史数据，检查重复
                    if last_date:
                        # 加载所有历史数据以检查重复
                        existing_data = self.load_market_data(
                            data_type,
                            stock_code
                        )
                        
                        if not existing_data.empty:
                            # 识别重复记录
                            date_column = self._get_date_column(data_type)
                            
                            if date_column in new_data.columns and date_column in existing_data.columns:
                                existing_dates = set(existing_data[date_column])
                                
                                # 过滤掉已存在的日期
                                new_data = new_data[
                                    ~new_data[date_column].isin(existing_dates)
                                ]
                                
                                duplicate_count = original_count - len(new_data)
                                
                                if duplicate_count > 0:
                                    logger.info(
                                        f"检测到 {duplicate_count} 条重复记录，已跳过"
                                    )
                    
                    if new_data.empty:
                        logger.info(f"股票 {stock_code} 过滤重复后没有新数据")
                        continue
                    
                    # 保存新数据
                    self.save_market_data(new_data, data_type, stock_code)
                    
                    updated_count = len(new_data)
                    total_updated += updated_count
                    
                    logger.info(
                        f"股票 {stock_code} 更新完成: {updated_count} 条新记录"
                    )
                
                except Exception as e:
                    # 单只股票失败不影响其他股票
                    logger.error(
                        f"更新股票 {stock_code} 失败: {str(e)}"
                    )
                    continue
            
            logger.info(
                f"增量更新完成: 共更新 {total_updated} 条记录, "
                f"处理 {total_stocks} 只股票"
            )
            
            return total_updated
        
        except Exception as e:
            error_msg = f"增量更新失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def export_to_csv(
        self,
        data_type: str,
        output_path: str,
        stock_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> None:
        """
        导出数据到CSV
        
        从HDF5加载数据并导出为CSV格式，便于在Excel等工具中查看。
        
        Args:
            data_type: 数据类型
            output_path: 输出文件路径
            stock_code: 股票代码，None表示全市场数据
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
        
        Raises:
            ValidationError: 参数验证失败
            StorageError: 导出失败
        
        Example:
            >>> manager.export_to_csv(
            ...     'daily',
            ...     'output/000001_daily.csv',
            ...     '000001.SZ',
            ...     '20240101',
            ...     '20240110'
            ... )
        """
        # 参数验证
        self._validate_data_type(data_type)
        
        logger.info(
            f"导出CSV: 类型={data_type}, 股票={stock_code or '全市场'}, "
            f"输出路径={output_path}"
        )
        
        try:
            # 加载数据
            data = self.load_market_data(data_type, stock_code, start_date, end_date)
            
            if data.empty:
                logger.warning("没有数据可导出")
                return
            
            # 确保输出目录存在
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 导出CSV
            data.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV导出完成: {len(data)}条记录 -> {output_path}")
        
        except Exception as e:
            error_msg = f"导出CSV失败: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    # ========================================================================
    # 内部辅助方法
    # ========================================================================
    
    def _validate_data_type(self, data_type: str) -> None:
        """
        验证数据类型
        
        Args:
            data_type: 数据类型
        
        Raises:
            ValidationError: 数据类型无效
        """
        if data_type not in self._valid_data_types:
            raise ValidationError(
                f"无效的数据类型: {data_type}。"
                f"支持的类型: {', '.join(self._valid_data_types)}"
            )
    
    def _validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Raises:
            ValidationError: 日期格式或范围无效
        """
        try:
            start_dt = datetime.strptime(start_date, HDF5_DATE_FORMAT)
            end_dt = datetime.strptime(end_date, HDF5_DATE_FORMAT)
            
            if start_dt > end_dt:
                raise ValidationError(
                    f"开始日期 {start_date} 不能晚于结束日期 {end_date}"
                )
        except ValueError as e:
            raise ValidationError(
                f"日期格式无效，应为 'YYYYMMDD': {str(e)}"
            ) from e
    
    def _deduplicate_data(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> pd.DataFrame:
        """
        数据去重
        
        根据数据类型使用不同的去重键进行去重。
        
        Args:
            data: 要去重的数据
            data_type: 数据类型
        
        Returns:
            去重后的数据
        """
        if data_type == 'daily':
            # 日线数据：按股票代码和日期去重
            if 'stock_code' in data.columns and 'date' in data.columns:
                data = data.drop_duplicates(
                    subset=['stock_code', 'date'],
                    keep='last'
                )
        
        elif data_type == 'tick':
            # Tick数据：按股票代码和时间戳去重
            if 'stock_code' in data.columns and 'timestamp' in data.columns:
                data = data.drop_duplicates(
                    subset=['stock_code', 'timestamp'],
                    keep='last'
                )
        
        elif data_type == 'fundamental':
            # 基本面数据：按股票代码和报告期去重
            if 'stock_code' in data.columns and 'report_date' in data.columns:
                data = data.drop_duplicates(
                    subset=['stock_code', 'report_date'],
                    keep='last'
                )
        
        elif data_type == 'industry':
            # 行业数据：按股票代码和生效日期去重
            if 'stock_code' in data.columns and 'effective_date' in data.columns:
                data = data.drop_duplicates(
                    subset=['stock_code', 'effective_date'],
                    keep='last'
                )
        
        return data
    
    def _filter_by_date(
        self,
        data: pd.DataFrame,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        按日期范围过滤数据
        
        Args:
            data: 要过滤的数据
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            过滤后的数据
        """
        if data.empty:
            return data
        
        # 确定日期列
        date_column = None
        for col in ['date', 'timestamp', 'report_date', 'effective_date']:
            if col in data.columns:
                date_column = col
                break
        
        if not date_column:
            logger.warning("数据中没有日期列，无法按日期过滤")
            return data
        
        # 应用过滤
        if start_date:
            data = data[data[date_column] >= start_date]
        
        if end_date:
            data = data[data[date_column] <= end_date]
        
        return data
    
    def _get_date_column(self, data_type: str) -> str:
        """
        获取数据类型对应的日期列名
        
        Args:
            data_type: 数据类型
        
        Returns:
            日期列名
        """
        date_columns = {
            'daily': 'date',
            'tick': 'timestamp',
            'fundamental': 'report_date',
            'industry': 'effective_date'
        }
        
        return date_columns.get(data_type, 'date')
    
    def _log_update(
        self,
        data_type: str,
        stock_code: Optional[str],
        record_count: int
    ) -> None:
        """
        记录更新日志
        
        将数据更新操作记录到元数据中，用于审计和追踪。
        
        Args:
            data_type: 数据类型
            stock_code: 股票代码
            record_count: 记录数
        """
        try:
            log_entry = pd.DataFrame([{
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_type': data_type,
                'stock_code': stock_code or 'all',
                'record_count': record_count,
                'operation': 'save'
            }])
            
            # 保存到元数据
            with pd.HDFStore(
                str(self.hdf5_path),
                mode='a',
                complevel=HDF5_COMPLEVEL,
                complib='blosc:zstd'
            ) as store:
                key = '/metadata/update_log'
                
                if key in store:
                    existing_log = store[key]
                    combined_log = pd.concat([existing_log, log_entry], ignore_index=True)
                    store.put(key, combined_log, format='table', data_columns=True)
                else:
                    store.put(key, log_entry, format='table', data_columns=True)
        
        except Exception as e:
            # 日志记录失败不应影响主流程
            logger.warning(f"记录更新日志失败: {str(e)}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储信息
        
        返回HDF5文件的存储统计信息，包括文件大小、数据类型、记录数等。
        
        Returns:
            存储信息字典
        
        Example:
            >>> info = manager.get_storage_info()
            >>> print(f"文件大小: {info['file_size_mb']:.2f} MB")
            >>> print(f"数据类型: {info['data_types']}")
        """
        info = {
            'hdf5_path': str(self.hdf5_path),
            'file_exists': self.hdf5_path.exists(),
            'file_size_mb': 0,
            'data_types': [],
            'total_records': 0
        }
        
        if not self.hdf5_path.exists():
            return info
        
        try:
            # 文件大小
            info['file_size_mb'] = self.hdf5_path.stat().st_size / (1024 * 1024)
            
            # 数据统计
            with pd.HDFStore(str(self.hdf5_path), mode='r') as store:
                keys = store.keys()
                
                # 提取数据类型
                data_types = set()
                total_records = 0
                
                for key in keys:
                    parts = key.split('/')
                    if len(parts) >= 2:
                        data_type = parts[1]
                        data_types.add(data_type)
                        
                        # 统计记录数
                        try:
                            data = store[key]
                            total_records += len(data)
                        except:
                            pass
                
                info['data_types'] = sorted(list(data_types))
                info['total_records'] = total_records
        
        except Exception as e:
            logger.error(f"获取存储信息失败: {str(e)}")
        
        return info
    
    def validate_data(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> Dict[str, Any]:
        """
        验证数据质量
        
        对数据进行全面的质量检查，包括：
        - 数据类型验证
        - 数值范围验证
        - 异常值检测（负价格、极端值）
        - 数据完整性检查
        
        Args:
            data: 要验证的数据DataFrame
            data_type: 数据类型，如 'daily', 'tick', 'fundamental'
        
        Returns:
            验证报告字典，包含：
            - is_valid: 总体是否有效
            - errors: 错误列表
            - warnings: 警告列表
            - anomalies: 异常值列表
            - statistics: 数据统计信息
        
        Example:
            >>> report = manager.validate_data(data, 'daily')
            >>> if not report['is_valid']:
            ...     print(f"发现 {len(report['errors'])} 个错误")
            >>> if report['warnings']:
            ...     print(f"发现 {len(report['warnings'])} 个警告")
        """
        report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'anomalies': [],
            'statistics': {}
        }
        
        if data is None or data.empty:
            report['is_valid'] = False
            report['errors'].append("数据为空或None")
            return report
        
        logger.info(f"开始验证数据: 类型={data_type}, 记录数={len(data)}")
        
        # 1. 数据类型验证
        type_errors = self._validate_data_types(data, data_type)
        report['errors'].extend(type_errors)
        
        # 2. 数值范围验证
        range_errors, range_warnings = self._validate_value_ranges(data, data_type)
        report['errors'].extend(range_errors)
        report['warnings'].extend(range_warnings)
        
        # 3. 异常值检测
        anomalies = self._detect_anomalies(data, data_type)
        report['anomalies'].extend(anomalies)
        if anomalies:
            report['warnings'].append(f"检测到 {len(anomalies)} 个异常值")
        
        # 4. 数据完整性验证
        integrity_errors = self._validate_data_integrity(data, data_type)
        report['errors'].extend(integrity_errors)
        
        # 5. 生成统计信息
        report['statistics'] = self._generate_statistics(data, data_type)
        
        # 更新总体有效性
        if report['errors']:
            report['is_valid'] = False
        
        logger.info(
            f"数据验证完成: 有效={report['is_valid']}, "
            f"错误={len(report['errors'])}, "
            f"警告={len(report['warnings'])}, "
            f"异常={len(report['anomalies'])}"
        )
        
        return report
    
    def detect_data_gaps(
        self,
        data: pd.DataFrame,
        data_type: str,
        stock_code: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        检测时间序列数据缺口
        
        识别数据中缺失的交易日或时间点，返回缺失的日期范围。
        
        Args:
            data: 要检查的数据DataFrame
            data_type: 数据类型
            stock_code: 股票代码（用于日志）
        
        Returns:
            缺口列表，每个缺口包含：
            - start_date: 缺口开始日期
            - end_date: 缺口结束日期
            - gap_days: 缺失天数
        
        Example:
            >>> gaps = manager.detect_data_gaps(data, 'daily', '000001.SZ')
            >>> for gap in gaps:
            ...     print(f"缺口: {gap['start_date']} - {gap['end_date']}, "
            ...           f"缺失 {gap['gap_days']} 天")
        """
        gaps = []
        
        if data is None or data.empty:
            logger.warning("数据为空，无法检测缺口")
            return gaps
        
        # 获取日期列
        date_column = self._get_date_column(data_type)
        
        if date_column not in data.columns:
            logger.warning(f"数据中没有日期列 {date_column}，无法检测缺口")
            return gaps
        
        logger.info(
            f"检测数据缺口: 类型={data_type}, 股票={stock_code or '全市场'}"
        )
        
        try:
            # 对于日线数据，检测交易日缺口
            if data_type == 'daily':
                # 排序日期
                dates = sorted(data[date_column].unique())
                
                if len(dates) < 2:
                    logger.info("数据点少于2个，无法检测缺口")
                    return gaps
                
                # 转换为datetime对象
                date_objects = [
                    datetime.strptime(str(d), '%Y%m%d') for d in dates
                ]
                
                # 检测缺口（超过3天的间隔视为缺口，考虑周末）
                for i in range(len(date_objects) - 1):
                    current_date = date_objects[i]
                    next_date = date_objects[i + 1]
                    
                    # 计算天数差
                    gap_days = (next_date - current_date).days
                    
                    # 如果间隔超过3天（排除正常周末），记录为缺口
                    if gap_days > 3:
                        gaps.append({
                            'start_date': current_date.strftime('%Y%m%d'),
                            'end_date': next_date.strftime('%Y%m%d'),
                            'gap_days': gap_days
                        })
                        
                        logger.warning(
                            f"检测到数据缺口: {current_date.strftime('%Y%m%d')} - "
                            f"{next_date.strftime('%Y%m%d')}, 缺失 {gap_days} 天"
                        )
            
            # 对于tick数据，检测时间戳缺口（简化处理）
            elif data_type == 'tick':
                # Tick数据缺口检测较复杂，这里只做基本检查
                timestamps = sorted(data[date_column].unique())
                
                if len(timestamps) < 2:
                    return gaps
                
                # 检测大的时间间隔（超过1小时）
                for i in range(len(timestamps) - 1):
                    current_ts = int(timestamps[i])
                    next_ts = int(timestamps[i + 1])
                    
                    # 时间差（毫秒）
                    gap_ms = next_ts - current_ts
                    gap_hours = gap_ms / (1000 * 3600)
                    
                    # 如果间隔超过1小时，记录为缺口
                    if gap_hours > 1:
                        gaps.append({
                            'start_date': str(current_ts),
                            'end_date': str(next_ts),
                            'gap_days': f"{gap_hours:.2f}小时"
                        })
            
            logger.info(f"缺口检测完成: 发现 {len(gaps)} 个缺口")
        
        except Exception as e:
            logger.error(f"检测数据缺口失败: {str(e)}")
        
        return gaps
    
    def generate_quality_report(
        self,
        data_type: str,
        stock_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成数据质量报告
        
        对存储的数据进行全面的质量分析，生成详细报告。
        
        Args:
            data_type: 数据类型
            stock_code: 股票代码，None表示全市场数据
        
        Returns:
            质量报告字典，包含：
            - data_info: 数据基本信息
            - validation_result: 验证结果
            - gaps: 数据缺口
            - summary: 质量摘要
        
        Example:
            >>> report = manager.generate_quality_report('daily', '000001.SZ')
            >>> print(f"数据质量评分: {report['summary']['quality_score']}")
            >>> print(f"数据完整性: {report['summary']['completeness']}")
        """
        logger.info(
            f"生成数据质量报告: 类型={data_type}, 股票={stock_code or '全市场'}"
        )
        
        report = {
            'data_info': {},
            'validation_result': {},
            'gaps': [],
            'summary': {}
        }
        
        try:
            # 加载数据
            data = self.load_market_data(data_type, stock_code)
            
            if data.empty:
                report['summary']['status'] = '无数据'
                return report
            
            # 数据基本信息
            report['data_info'] = {
                'data_type': data_type,
                'stock_code': stock_code or '全市场',
                'record_count': len(data),
                'date_range': self._get_date_range(data, data_type),
                'columns': list(data.columns)
            }
            
            # 数据验证
            report['validation_result'] = self.validate_data(data, data_type)
            
            # 缺口检测
            report['gaps'] = self.detect_data_gaps(data, data_type, stock_code)
            
            # 生成质量摘要
            report['summary'] = self._generate_quality_summary(
                report['validation_result'],
                report['gaps'],
                len(data)
            )
            
            logger.info(
                f"质量报告生成完成: 质量评分={report['summary']['quality_score']}"
            )
        
        except Exception as e:
            logger.error(f"生成质量报告失败: {str(e)}")
            report['summary']['status'] = f'生成失败: {str(e)}'
        
        return report
    
    # ========================================================================
    # 数据验证辅助方法
    # ========================================================================
    
    def _validate_data_types(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> List[str]:
        """
        验证数据类型
        
        检查DataFrame中的列是否具有正确的数据类型。
        
        Args:
            data: 要验证的数据
            data_type: 数据类型
        
        Returns:
            错误列表
        """
        errors = []
        
        # 定义期望的数据类型
        expected_types = {
            'daily': {
                'stock_code': 'object',
                'date': 'object',
                'open': ['float64', 'float32', 'int64', 'int32'],
                'high': ['float64', 'float32', 'int64', 'int32'],
                'low': ['float64', 'float32', 'int64', 'int32'],
                'close': ['float64', 'float32', 'int64', 'int32'],
                'volume': ['float64', 'float32', 'int64', 'int32']
            },
            'tick': {
                'stock_code': 'object',
                'timestamp': ['int64', 'int32', 'object'],
                'price': ['float64', 'float32']
            },
            'fundamental': {
                'stock_code': 'object',
                'report_date': 'object',
                'announce_date': 'object'
            }
        }
        
        if data_type not in expected_types:
            return errors
        
        expected = expected_types[data_type]
        
        for col, expected_type in expected.items():
            if col in data.columns:
                actual_type = str(data[col].dtype)
                
                # 支持多种类型
                if isinstance(expected_type, list):
                    if actual_type not in expected_type:
                        errors.append(
                            f"列 {col} 的数据类型不正确: "
                            f"期望 {expected_type}, 实际 {actual_type}"
                        )
                else:
                    if actual_type != expected_type:
                        errors.append(
                            f"列 {col} 的数据类型不正确: "
                            f"期望 {expected_type}, 实际 {actual_type}"
                        )
        
        return errors
    
    def _validate_value_ranges(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> tuple:
        """
        验证数值范围
        
        检查数值列是否在合理范围内。
        
        Args:
            data: 要验证的数据
            data_type: 数据类型
        
        Returns:
            (错误列表, 警告列表)
        """
        errors = []
        warnings = []
        
        if data_type == 'daily':
            # 价格列不应为负
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in data.columns:
                    try:
                        negative_count = (data[col] < 0).sum()
                        if negative_count > 0:
                            errors.append(
                                f"列 {col} 包含 {negative_count} 个负值"
                            )
                    except (TypeError, ValueError):
                        # 如果列不是数值类型，跳过范围检查（类型错误会在类型验证中捕获）
                        pass
            
            # 成交量不应为负
            if 'volume' in data.columns:
                try:
                    negative_volume = (data['volume'] < 0).sum()
                    if negative_volume > 0:
                        errors.append(
                            f"成交量包含 {negative_volume} 个负值"
                        )
                except (TypeError, ValueError):
                    pass
            
            # 检查OHLC关系
            if all(col in data.columns for col in ['open', 'high', 'low', 'close']):
                try:
                    # high应该是最高价
                    invalid_high = (
                        (data['high'] < data['open']) |
                        (data['high'] < data['close']) |
                        (data['high'] < data['low'])
                    ).sum()
                    
                    if invalid_high > 0:
                        warnings.append(
                            f"发现 {invalid_high} 条记录的最高价不是最高值"
                        )
                    
                    # low应该是最低价
                    invalid_low = (
                        (data['low'] > data['open']) |
                        (data['low'] > data['close']) |
                        (data['low'] > data['high'])
                    ).sum()
                    
                    if invalid_low > 0:
                        warnings.append(
                            f"发现 {invalid_low} 条记录的最低价不是最低值"
                        )
                except (TypeError, ValueError):
                    # 如果列不是数值类型，跳过OHLC关系检查
                    pass
        
        elif data_type == 'tick':
            # Tick价格不应为负
            if 'price' in data.columns:
                try:
                    negative_price = (data['price'] < 0).sum()
                    if negative_price > 0:
                        errors.append(
                            f"价格包含 {negative_price} 个负值"
                        )
                except (TypeError, ValueError):
                    pass
        
        return errors, warnings
    
    def _detect_anomalies(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> List[Dict[str, Any]]:
        """
        检测异常值
        
        使用统计方法检测极端值和异常值。
        
        Args:
            data: 要检查的数据
            data_type: 数据类型
        
        Returns:
            异常值列表
        """
        anomalies = []
        
        if data_type == 'daily':
            # 检测价格异常（使用IQR方法）
            price_columns = ['open', 'high', 'low', 'close']
            
            for col in price_columns:
                if col not in data.columns:
                    continue
                
                try:
                    # 计算四分位数
                    Q1 = data[col].quantile(0.25)
                    Q3 = data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    # 定义异常值边界（1.5倍IQR）
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # 检测异常值
                    outliers = data[
                        (data[col] < lower_bound) | (data[col] > upper_bound)
                    ]
                    
                    if len(outliers) > 0:
                        for idx, row in outliers.iterrows():
                            anomalies.append({
                                'type': '价格异常',
                                'column': col,
                                'value': row[col],
                                'date': row.get('date', 'unknown'),
                                'stock_code': row.get('stock_code', 'unknown'),
                                'reason': f'超出正常范围 [{lower_bound:.2f}, {upper_bound:.2f}]'
                            })
                except (TypeError, ValueError):
                    # 如果列不是数值类型，跳过异常检测
                    pass
            
            # 检测成交量异常
            if 'volume' in data.columns:
                try:
                    # 零成交量
                    zero_volume = data[data['volume'] == 0]
                    if len(zero_volume) > 0:
                        for idx, row in zero_volume.iterrows():
                            anomalies.append({
                                'type': '成交量异常',
                                'column': 'volume',
                                'value': 0,
                                'date': row.get('date', 'unknown'),
                                'stock_code': row.get('stock_code', 'unknown'),
                                'reason': '成交量为零'
                            })
                    
                    # 极端成交量（使用IQR方法）
                    Q1 = data['volume'].quantile(0.25)
                    Q3 = data['volume'].quantile(0.75)
                    IQR = Q3 - Q1
                    upper_bound = Q3 + 3 * IQR  # 使用3倍IQR检测极端值
                    
                    extreme_volume = data[data['volume'] > upper_bound]
                    if len(extreme_volume) > 0:
                        for idx, row in extreme_volume.iterrows():
                            anomalies.append({
                                'type': '成交量异常',
                                'column': 'volume',
                                'value': row['volume'],
                                'date': row.get('date', 'unknown'),
                                'stock_code': row.get('stock_code', 'unknown'),
                                'reason': f'极端成交量（超过 {upper_bound:.0f}）'
                            })
                except (TypeError, ValueError):
                    # 如果列不是数值类型，跳过异常检测
                    pass
        
        return anomalies
    
    def _validate_data_integrity(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> List[str]:
        """
        验证数据完整性
        
        检查必需列是否存在，是否有缺失值等。
        
        Args:
            data: 要验证的数据
            data_type: 数据类型
        
        Returns:
            错误列表
        """
        errors = []
        
        # 定义必需列
        required_columns = {
            'daily': ['stock_code', 'date', 'close'],
            'tick': ['stock_code', 'timestamp', 'price'],
            'fundamental': ['stock_code', 'report_date', 'announce_date']
        }
        
        if data_type in required_columns:
            for col in required_columns[data_type]:
                if col not in data.columns:
                    errors.append(f"缺少必需列: {col}")
                else:
                    # 检查缺失值
                    null_count = data[col].isnull().sum()
                    if null_count > 0:
                        errors.append(
                            f"列 {col} 包含 {null_count} 个缺失值"
                        )
        
        return errors
    
    def _generate_statistics(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> Dict[str, Any]:
        """
        生成数据统计信息
        
        Args:
            data: 数据
            data_type: 数据类型
        
        Returns:
            统计信息字典
        """
        stats = {
            'record_count': len(data),
            'column_count': len(data.columns),
            'memory_usage_mb': data.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        if data_type == 'daily':
            if 'close' in data.columns:
                try:
                    stats['price_stats'] = {
                        'mean': float(data['close'].mean()),
                        'std': float(data['close'].std()),
                        'min': float(data['close'].min()),
                        'max': float(data['close'].max())
                    }
                except (TypeError, ValueError):
                    # Skip statistics if column is not numeric
                    pass
            
            if 'volume' in data.columns:
                try:
                    stats['volume_stats'] = {
                        'mean': float(data['volume'].mean()),
                        'std': float(data['volume'].std()),
                        'min': float(data['volume'].min()),
                        'max': float(data['volume'].max())
                    }
                except (TypeError, ValueError):
                    # Skip statistics if column is not numeric
                    pass
        
        return stats
    
    def _get_date_range(
        self,
        data: pd.DataFrame,
        data_type: str
    ) -> Dict[str, str]:
        """
        获取数据的日期范围
        
        Args:
            data: 数据
            data_type: 数据类型
        
        Returns:
            日期范围字典
        """
        date_column = self._get_date_column(data_type)
        
        if date_column not in data.columns:
            return {'start': 'unknown', 'end': 'unknown'}
        
        return {
            'start': str(data[date_column].min()),
            'end': str(data[date_column].max())
        }
    
    def _generate_quality_summary(
        self,
        validation_result: Dict[str, Any],
        gaps: List[Dict[str, str]],
        record_count: int
    ) -> Dict[str, Any]:
        """
        生成质量摘要
        
        Args:
            validation_result: 验证结果
            gaps: 数据缺口
            record_count: 记录数
        
        Returns:
            质量摘要字典
        """
        # 计算质量评分（0-100）
        score = 100
        
        # 错误扣分
        score -= len(validation_result['errors']) * 10
        
        # 警告扣分
        score -= len(validation_result['warnings']) * 5
        
        # 异常值扣分
        score -= min(len(validation_result['anomalies']) * 2, 20)
        
        # 缺口扣分
        score -= len(gaps) * 5
        
        # 确保分数在0-100之间
        score = max(0, min(100, score))
        
        # 计算完整性（基于缺口）
        if record_count > 0:
            gap_ratio = len(gaps) / record_count
            completeness = max(0, 100 - gap_ratio * 100)
        else:
            completeness = 0
        
        # 确定状态
        if score >= 90:
            status = '优秀'
        elif score >= 70:
            status = '良好'
        elif score >= 50:
            status = '一般'
        else:
            status = '较差'
        
        return {
            'quality_score': score,
            'completeness': completeness,
            'status': status,
            'error_count': len(validation_result['errors']),
            'warning_count': len(validation_result['warnings']),
            'anomaly_count': len(validation_result['anomalies']),
            'gap_count': len(gaps)
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"DataManager("
            f"storage_path={self.storage_path}, "
            f"hdf5_path={self.hdf5_path})"
        )
