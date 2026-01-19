"""
全市场数据库构建模块

提供全市场数据下载功能，支持批量下载、断点续传、进度报告和汇总统计
"""

import time
import json
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from config import (
    logger,
    DataError,
    ValidationError,
    StorageError,
    API_RATE_LIMIT_DELAY,
    DATA_DIR
)


class FullMarketDownloader:
    """
    全市场数据下载器
    
    负责批量下载全市场股票数据，支持断点续传、进度报告和汇总统计。
    使用状态文件记录下载进度，支持从中断点恢复下载。
    
    Attributes:
        retriever: 数据获取器实例
        data_manager: 数据管理器实例
        state_file: 状态文件路径
        rate_limit_delay: API速率限制延迟（秒）
    
    Example:
        >>> downloader = FullMarketDownloader(retriever, data_manager)
        >>> stats = downloader.download_full_market(
        ...     start_date='20240101',
        ...     end_date='20240110',
        ...     progress_callback=lambda c, t, s: print(f"{c}/{t}: {s}")
        ... )
        >>> print(f"下载完成: {stats['success_count']} 只股票")
    """
    
    def __init__(
        self,
        retriever,
        data_manager,
        state_file: Optional[Path] = None,
        rate_limit_delay: float = API_RATE_LIMIT_DELAY
    ):
        """
        初始化全市场下载器
        
        Args:
            retriever: 数据获取器实例（DataRetriever）
            data_manager: 数据管理器实例（DataManager）
            state_file: 状态文件路径，None则使用默认路径
            rate_limit_delay: API速率限制延迟（秒）
        
        Raises:
            ValueError: 参数无效
        """
        if retriever is None:
            raise ValueError("retriever不能为None")
        
        if data_manager is None:
            raise ValueError("data_manager不能为None")
        
        self.retriever = retriever
        self.data_manager = data_manager
        self.rate_limit_delay = rate_limit_delay
        
        # 状态文件路径
        if state_file is None:
            self.state_file = DATA_DIR / "download_state.json"
        else:
            self.state_file = Path(state_file)
        
        logger.info(
            f"FullMarketDownloader初始化完成，状态文件: {self.state_file}"
        )
    
    def download_full_market(
        self,
        start_date: str,
        end_date: str,
        data_type: str = 'daily',
        resume: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        下载全市场数据
        
        获取所有股票代码列表，批量下载日线数据。支持断点续传，
        自动处理API速率限制，提供进度报告和汇总统计。
        
        Args:
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            data_type: 数据类型，默认为 'daily'
            resume: 是否从上次中断点恢复，默认True
            progress_callback: 进度回调函数，接收参数 (current, total, stock_code)
        
        Returns:
            汇总统计字典，包含：
            - total_stocks: 总股票数
            - success_count: 成功下载数
            - failed_count: 失败数
            - skipped_count: 跳过数（已存在）
            - total_records: 总记录数
            - start_time: 开始时间
            - end_time: 结束时间
            - duration_seconds: 耗时（秒）
            - failed_stocks: 失败的股票列表
        
        Raises:
            ValidationError: 参数验证失败
            DataError: 数据获取失败
        
        Example:
            >>> def progress(current, total, stock_code):
            ...     print(f"进度: {current}/{total} - {stock_code}")
            >>> 
            >>> stats = downloader.download_full_market(
            ...     start_date='20240101',
            ...     end_date='20240110',
            ...     progress_callback=progress
            ... )
            >>> print(f"成功: {stats['success_count']}, "
            ...       f"失败: {stats['failed_count']}")
        """
        logger.info(
            f"开始全市场数据下载: 日期范围={start_date} - {end_date}, "
            f"数据类型={data_type}, 断点续传={resume}"
        )
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 初始化统计信息
        stats = {
            'total_stocks': 0,
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'total_records': 0,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': None,
            'duration_seconds': 0,
            'failed_stocks': []
        }
        
        try:
            # 1. 获取所有股票代码列表
            logger.info("获取所有股票代码列表...")
            all_stock_codes = self.retriever.get_all_stock_codes()
            stats['total_stocks'] = len(all_stock_codes)
            
            logger.info(f"获取到 {stats['total_stocks']} 只股票")
            
            if not all_stock_codes:
                logger.warning("没有获取到股票代码，下载终止")
                return stats
            
            # 2. 加载或初始化下载状态
            download_state = self._load_state() if resume else {}
            
            # 3. 确定需要下载的股票列表
            if resume and download_state:
                # 从状态中获取已完成的股票
                completed_stocks = set(download_state.get('completed_stocks', []))
                
                # 过滤出未完成的股票
                stocks_to_download = [
                    code for code in all_stock_codes
                    if code not in completed_stocks
                ]
                
                # 统计跳过的股票
                stats['skipped_count'] = len(completed_stocks)
                
                logger.info(
                    f"断点续传: 已完成 {stats['skipped_count']} 只股票, "
                    f"剩余 {len(stocks_to_download)} 只股票"
                )
            else:
                stocks_to_download = all_stock_codes
                download_state = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'data_type': data_type,
                    'completed_stocks': [],
                    'failed_stocks': []
                }
                
                # 保存初始状态
                self._save_state(download_state)
            
            # 4. 批量下载数据
            total_to_download = len(stocks_to_download)
            
            logger.info(f"开始下载 {total_to_download} 只股票的数据...")
            
            for idx, stock_code in enumerate(stocks_to_download, 1):
                try:
                    # 报告进度
                    current_progress = stats['skipped_count'] + idx
                    
                    if progress_callback:
                        progress_callback(
                            current_progress,
                            stats['total_stocks'],
                            stock_code
                        )
                    
                    logger.info(
                        f"下载进度: {current_progress}/{stats['total_stocks']} "
                        f"({current_progress/stats['total_stocks']*100:.1f}%) - {stock_code}"
                    )
                    
                    # 下载数据
                    data = self.retriever.download_history_data(
                        stock_codes=[stock_code],
                        start_date=start_date,
                        end_date=end_date,
                        period='1d' if data_type == 'daily' else 'tick',
                        adjust_type='none'
                    )
                    
                    if data is None or data.empty:
                        logger.warning(f"股票 {stock_code} 没有返回数据")
                        stats['skipped_count'] += 1
                        
                        # 标记为已完成（避免重复尝试）
                        download_state['completed_stocks'].append(stock_code)
                        self._save_state(download_state)
                        
                        continue
                    
                    # 保存数据
                    self.data_manager.save_market_data(
                        data,
                        data_type,
                        stock_code
                    )
                    
                    # 更新统计
                    stats['success_count'] += 1
                    stats['total_records'] += len(data)
                    
                    # 更新状态
                    download_state['completed_stocks'].append(stock_code)
                    self._save_state(download_state)
                    
                    logger.info(
                        f"股票 {stock_code} 下载完成: {len(data)} 条记录"
                    )
                    
                    # API速率限制延迟
                    if idx < total_to_download:
                        time.sleep(self.rate_limit_delay)
                
                except Exception as e:
                    # 单只股票失败不影响其他股票
                    error_msg = f"下载股票 {stock_code} 失败: {str(e)}"
                    logger.error(error_msg)
                    
                    stats['failed_count'] += 1
                    stats['failed_stocks'].append({
                        'stock_code': stock_code,
                        'error': str(e)
                    })
                    
                    # 记录失败状态
                    download_state['failed_stocks'].append({
                        'stock_code': stock_code,
                        'error': str(e),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    self._save_state(download_state)
                    
                    continue
            
            # 5. 记录结束时间
            end_time = datetime.now()
            stats['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
            stats['duration_seconds'] = (end_time - start_time).total_seconds()
            
            # 6. 数据完整性验证
            logger.info("验证数据完整性...")
            validation_result = self._validate_downloaded_data(
                all_stock_codes,
                data_type
            )
            stats['validation'] = validation_result
            
            # 7. 清理状态文件（下载完成）
            if stats['failed_count'] == 0:
                self._clear_state()
                logger.info("下载完成，状态文件已清理")
            
            # 8. 生成汇总报告
            self._log_summary(stats)
            
            logger.info(
                f"全市场数据下载完成: "
                f"成功 {stats['success_count']}, "
                f"失败 {stats['failed_count']}, "
                f"跳过 {stats['skipped_count']}, "
                f"总记录 {stats['total_records']}, "
                f"耗时 {stats['duration_seconds']:.2f} 秒"
            )
            
            return stats
        
        except Exception as e:
            error_msg = f"全市场数据下载失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def _load_state(self) -> Dict[str, Any]:
        """
        加载下载状态
        
        从状态文件加载上次下载的进度信息。
        
        Returns:
            状态字典，如果文件不存在则返回空字典
        """
        if not self.state_file.exists():
            logger.debug("状态文件不存在，返回空状态")
            return {}
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            logger.info(
                f"加载下载状态: 已完成 {len(state.get('completed_stocks', []))} 只股票"
            )
            
            return state
        
        except Exception as e:
            logger.error(f"加载状态文件失败: {str(e)}")
            return {}
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """
        保存下载状态
        
        将当前下载进度保存到状态文件，用于断点续传。
        
        Args:
            state: 状态字典
        """
        try:
            # 确保目录存在
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存状态
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"状态已保存: {len(state.get('completed_stocks', []))} 只股票已完成")
        
        except Exception as e:
            logger.error(f"保存状态文件失败: {str(e)}")
    
    def _clear_state(self) -> None:
        """
        清理状态文件
        
        下载完成后删除状态文件。
        """
        try:
            if self.state_file.exists():
                self.state_file.unlink()
                logger.info("状态文件已清理")
        
        except Exception as e:
            logger.warning(f"清理状态文件失败: {str(e)}")
    
    def _validate_downloaded_data(
        self,
        stock_codes: List[str],
        data_type: str
    ) -> Dict[str, Any]:
        """
        验证下载的数据完整性
        
        检查所有股票是否都有数据，数据质量是否合格。
        
        Args:
            stock_codes: 股票代码列表
            data_type: 数据类型
        
        Returns:
            验证结果字典
        """
        validation_result = {
            'total_stocks': len(stock_codes),
            'stocks_with_data': 0,
            'stocks_without_data': 0,
            'missing_stocks': []
        }
        
        logger.info("开始验证数据完整性...")
        
        try:
            for stock_code in stock_codes:
                try:
                    # 尝试加载数据
                    data = self.data_manager.load_market_data(
                        data_type,
                        stock_code
                    )
                    
                    if data is None or data.empty:
                        validation_result['stocks_without_data'] += 1
                        validation_result['missing_stocks'].append(stock_code)
                    else:
                        validation_result['stocks_with_data'] += 1
                
                except Exception as e:
                    logger.warning(f"验证股票 {stock_code} 数据失败: {str(e)}")
                    validation_result['stocks_without_data'] += 1
                    validation_result['missing_stocks'].append(stock_code)
            
            logger.info(
                f"数据完整性验证完成: "
                f"有数据 {validation_result['stocks_with_data']}, "
                f"无数据 {validation_result['stocks_without_data']}"
            )
        
        except Exception as e:
            logger.error(f"数据完整性验证失败: {str(e)}")
        
        return validation_result
    
    def _log_summary(self, stats: Dict[str, Any]) -> None:
        """
        记录汇总统计信息
        
        将下载统计信息记录到日志，便于审计和分析。
        
        Args:
            stats: 统计信息字典
        """
        logger.info("=" * 80)
        logger.info("全市场数据下载汇总报告")
        logger.info("=" * 80)
        logger.info(f"开始时间: {stats['start_time']}")
        logger.info(f"结束时间: {stats['end_time']}")
        logger.info(f"总耗时: {stats['duration_seconds']:.2f} 秒")
        logger.info("-" * 80)
        logger.info(f"总股票数: {stats['total_stocks']}")
        logger.info(f"成功下载: {stats['success_count']}")
        logger.info(f"下载失败: {stats['failed_count']}")
        logger.info(f"跳过股票: {stats['skipped_count']}")
        logger.info(f"总记录数: {stats['total_records']}")
        logger.info("-" * 80)
        
        if stats['failed_stocks']:
            logger.info("失败股票列表:")
            for failed in stats['failed_stocks'][:10]:  # 只显示前10个
                logger.info(f"  - {failed['stock_code']}: {failed['error']}")
            
            if len(stats['failed_stocks']) > 10:
                logger.info(f"  ... 还有 {len(stats['failed_stocks']) - 10} 只股票失败")
        
        if 'validation' in stats:
            logger.info("-" * 80)
            logger.info("数据完整性验证:")
            logger.info(f"  有数据: {stats['validation']['stocks_with_data']}")
            logger.info(f"  无数据: {stats['validation']['stocks_without_data']}")
        
        logger.info("=" * 80)
    
    def get_download_progress(self) -> Dict[str, Any]:
        """
        获取当前下载进度
        
        从状态文件读取当前下载进度信息。
        
        Returns:
            进度信息字典，包含：
            - is_downloading: 是否正在下载
            - completed_count: 已完成数量
            - failed_count: 失败数量
            - start_date: 开始日期
            - end_date: 结束日期
            - data_type: 数据类型
        
        Example:
            >>> progress = downloader.get_download_progress()
            >>> if progress['is_downloading']:
            ...     print(f"已完成: {progress['completed_count']}")
        """
        state = self._load_state()
        
        if not state:
            return {
                'is_downloading': False,
                'completed_count': 0,
                'failed_count': 0
            }
        
        return {
            'is_downloading': True,
            'completed_count': len(state.get('completed_stocks', [])),
            'failed_count': len(state.get('failed_stocks', [])),
            'start_date': state.get('start_date'),
            'end_date': state.get('end_date'),
            'data_type': state.get('data_type')
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"FullMarketDownloader("
            f"state_file={self.state_file})"
        )


def download_full_market(
    retriever,
    data_manager,
    start_date: str,
    end_date: str,
    data_type: str = 'daily',
    resume: bool = True,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    state_file: Optional[Path] = None
) -> Dict[str, Any]:
    """
    下载全市场数据（便捷函数）
    
    这是一个便捷函数，封装了FullMarketDownloader的使用。
    适合在脚本中快速调用。
    
    Args:
        retriever: 数据获取器实例
        data_manager: 数据管理器实例
        start_date: 开始日期，格式 'YYYYMMDD'
        end_date: 结束日期，格式 'YYYYMMDD'
        data_type: 数据类型，默认为 'daily'
        resume: 是否从上次中断点恢复，默认True
        progress_callback: 进度回调函数
        state_file: 状态文件路径，None则使用默认路径
    
    Returns:
        汇总统计字典
    
    Example:
        >>> from src.xtdata_client import XtDataClient
        >>> from src.data_retriever import DataRetriever
        >>> from src.data_manager import DataManager
        >>> from src.full_market_downloader import download_full_market
        >>> 
        >>> client = XtDataClient("account_id", "account_key")
        >>> client.connect()
        >>> retriever = DataRetriever(client)
        >>> manager = DataManager()
        >>> 
        >>> stats = download_full_market(
        ...     retriever,
        ...     manager,
        ...     '20240101',
        ...     '20240110',
        ...     progress_callback=lambda c, t, s: print(f"{c}/{t}: {s}")
        ... )
        >>> print(f"下载完成: {stats['success_count']} 只股票")
    """
    downloader = FullMarketDownloader(
        retriever,
        data_manager,
        state_file=state_file
    )
    
    return downloader.download_full_market(
        start_date=start_date,
        end_date=end_date,
        data_type=data_type,
        resume=resume,
        progress_callback=progress_callback
    )
