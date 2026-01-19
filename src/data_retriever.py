"""
数据获取器模块

提供高级数据获取接口，支持历史数据和实时数据获取
"""

import time
import pandas as pd
from typing import List, Optional, Union
from datetime import datetime
from config import (
    logger,
    DataError,
    ValidationError,
    ConnectionError,
    API_RATE_LIMIT_DELAY,
    API_BATCH_SIZE,
    DEFAULT_PERIOD,
    DEFAULT_ADJUST_TYPE
)
from src.xtdata_client import XtDataClient


class DataRetriever:
    """
    市场数据获取器
    
    提供高级数据获取接口，封装XtData API调用，支持历史数据下载、
    实时快照获取和股票列表查询。包含参数验证和错误处理机制。
    
    Attributes:
        client: XtData客户端实例
        rate_limit_delay: 批量请求间延迟（秒）
        batch_size: 批量请求大小
    
    Example:
        >>> client = XtDataClient(account_id="test", account_key="test")
        >>> client.connect()
        >>> retriever = DataRetriever(client)
        >>> data = retriever.download_history_data(
        ...     stock_codes=['000001.SZ'],
        ...     start_date='20240101',
        ...     end_date='20240110'
        ... )
    """
    
    def __init__(
        self,
        client: XtDataClient,
        rate_limit_delay: float = API_RATE_LIMIT_DELAY,
        batch_size: int = API_BATCH_SIZE
    ):
        """
        初始化数据获取器
        
        Args:
            client: XtData客户端实例
            rate_limit_delay: 批量请求间延迟（秒）
            batch_size: 批量请求大小
        
        Raises:
            ValueError: 客户端为None
        """
        if client is None:
            raise ValueError("XtDataClient不能为None")
        
        self.client = client
        self.rate_limit_delay = rate_limit_delay
        self.batch_size = batch_size
        
        logger.info("DataRetriever初始化完成")
    
    def download_history_data(
        self,
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        period: str = DEFAULT_PERIOD,
        adjust_type: str = 'none'
    ) -> pd.DataFrame:
        """
        下载历史市场数据
        
        从XtData API获取指定股票代码和日期范围的历史数据。
        支持tick和日线数据，支持不同的复权类型。
        
        Args:
            stock_codes: 股票代码列表，如 ['000001.SZ', '600000.SH']
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            period: 数据周期，'tick' 或 '1d'
            adjust_type: 复权类型，'none', 'front', 'back'
        
        Returns:
            包含OHLCV数据的DataFrame
            
        Raises:
            ConnectionError: API连接失败
            ValueError: 参数无效
            DataError: 数据获取失败
        
        Example:
            >>> data = retriever.download_history_data(
            ...     stock_codes=['000001.SZ', '600000.SH'],
            ...     start_date='20240101',
            ...     end_date='20240110',
            ...     period='1d'
            ... )
        """
        # 参数验证
        self._validate_stock_codes(stock_codes)
        self._validate_date_range(start_date, end_date)
        self._validate_period(period)
        self._validate_adjust_type(adjust_type)
        
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info(
            f"开始下载历史数据: {len(stock_codes)}只股票, "
            f"日期范围: {start_date} - {end_date}, 周期: {period}"
        )
        
        all_data = []
        
        try:
            # 批量处理股票代码
            for i in range(0, len(stock_codes), self.batch_size):
                batch_codes = stock_codes[i:i + self.batch_size]
                
                logger.debug(
                    f"处理批次 {i // self.batch_size + 1}: "
                    f"{len(batch_codes)}只股票"
                )
                
                # 获取每只股票的数据
                for stock_code in batch_codes:
                    try:
                        data = self._fetch_history_data(
                            stock_code,
                            start_date,
                            end_date,
                            period,
                            adjust_type
                        )
                        
                        if data is not None and not data.empty:
                            all_data.append(data)
                        else:
                            logger.warning(f"股票 {stock_code} 没有返回数据")
                    
                    except Exception as e:
                        logger.error(f"获取股票 {stock_code} 数据失败: {str(e)}")
                        # 继续处理其他股票，不中断整个流程
                        continue
                
                # 速率限制
                if i + self.batch_size < len(stock_codes):
                    time.sleep(self.rate_limit_delay)
            
            # 合并所有数据
            if not all_data:
                logger.warning("没有获取到任何数据")
                return pd.DataFrame()
            
            result = pd.concat(all_data, ignore_index=True)
            
            logger.info(
                f"历史数据下载完成: 共 {len(result)} 条记录, "
                f"{len(result['stock_code'].unique())} 只股票"
            )
            
            return result
        
        except Exception as e:
            error_msg = f"下载历史数据失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def _fetch_history_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjust_type: str
    ) -> Optional[pd.DataFrame]:
        """
        获取单只股票的历史数据
        
        内部方法，调用XtData API获取数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 数据周期
            adjust_type: 复权类型
        
        Returns:
            包含数据的DataFrame，失败返回None
        """
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_market_data_ex(...)
            
            # 模拟数据生成（用于测试）
            # 实际代码应该是：
            # xtdata = self.client.get_xtdata_module()
            # data = xtdata.get_market_data_ex(...)
            
            logger.debug(f"获取股票 {stock_code} 的历史数据")
            
            # 生成日期范围
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            
            if period == '1d':
                # 日线数据
                dates = pd.date_range(start_dt, end_dt, freq='D')
                
                data = pd.DataFrame({
                    'stock_code': [stock_code] * len(dates),
                    'date': [d.strftime('%Y%m%d') for d in dates],
                    'open': [10.0] * len(dates),
                    'high': [11.0] * len(dates),
                    'low': [9.0] * len(dates),
                    'close': [10.5] * len(dates),
                    'volume': [1000000] * len(dates),
                    'amount': [10500000] * len(dates)
                })
            
            elif period == 'tick':
                # Tick数据
                # 生成一些tick记录
                num_ticks = 10
                base_time = int(start_dt.timestamp() * 1000)
                
                data = pd.DataFrame({
                    'stock_code': [stock_code] * num_ticks,
                    'timestamp': [base_time + i * 1000 for i in range(num_ticks)],
                    'price': [10.0 + i * 0.1 for i in range(num_ticks)],
                    'volume': [100 * (i + 1) for i in range(num_ticks)],
                    'bid_price': [10.0 + i * 0.1 - 0.01 for i in range(num_ticks)],
                    'ask_price': [10.0 + i * 0.1 + 0.01 for i in range(num_ticks)],
                    'bid_volume': [1000 * (i + 1) for i in range(num_ticks)],
                    'ask_volume': [1000 * (i + 1) for i in range(num_ticks)]
                })
            
            else:
                raise ValueError(f"不支持的周期: {period}")
            
            return data
        
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 数据时发生错误: {str(e)}")
            return None
    
    def get_market_data(
        self,
        stock_codes: List[str]
    ) -> pd.DataFrame:
        """
        获取当前市场快照数据
        
        获取指定股票的实时市场数据快照，包括最新价格、成交量等信息。
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            包含当前市场数据的DataFrame
        
        Raises:
            ConnectionError: API连接失败
            ValueError: 参数无效
            DataError: 数据获取失败
        
        Example:
            >>> snapshot = retriever.get_market_data(['000001.SZ', '600000.SH'])
        """
        # 参数验证
        self._validate_stock_codes(stock_codes)
        
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info(f"获取市场快照数据: {len(stock_codes)}只股票")
        
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_full_tick(stock_codes)
            
            all_data = []
            
            for stock_code in stock_codes:
                # 模拟快照数据
                snapshot = {
                    'stock_code': stock_code,
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'last_price': 10.5,
                    'open': 10.0,
                    'high': 11.0,
                    'low': 9.8,
                    'volume': 1000000,
                    'amount': 10500000,
                    'bid_price': 10.49,
                    'ask_price': 10.51,
                    'bid_volume': 10000,
                    'ask_volume': 10000
                }
                all_data.append(snapshot)
            
            result = pd.DataFrame(all_data)
            
            logger.info(f"市场快照数据获取完成: {len(result)} 只股票")
            
            return result
        
        except Exception as e:
            error_msg = f"获取市场快照数据失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def get_all_stock_codes(self) -> List[str]:
        """
        获取所有可用的股票代码
        
        从XtData API获取所有可交易的股票代码列表。
        
        Returns:
            股票代码列表
        
        Raises:
            ConnectionError: API连接失败
            DataError: 数据获取失败
        
        Example:
            >>> all_codes = retriever.get_all_stock_codes()
            >>> print(f"共有 {len(all_codes)} 只股票")
        """
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info("获取所有股票代码列表")
        
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_stock_list_in_sector('沪深A股')
            
            # 模拟股票代码列表
            stock_codes = [
                '000001.SZ', '000002.SZ', '000003.SZ',
                '600000.SH', '600001.SH', '600002.SH'
            ]
            
            logger.info(f"获取到 {len(stock_codes)} 只股票代码")
            
            return stock_codes
        
        except Exception as e:
            error_msg = f"获取股票代码列表失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    # ========================================================================
    # 参数验证方法
    # ========================================================================
    
    def _validate_stock_codes(self, stock_codes: List[str]) -> None:
        """
        验证股票代码列表
        
        Args:
            stock_codes: 股票代码列表
        
        Raises:
            ValueError: 股票代码无效
        """
        if not stock_codes:
            raise ValueError("股票代码列表不能为空")
        
        if not isinstance(stock_codes, list):
            raise ValueError("stock_codes必须是列表类型")
        
        for code in stock_codes:
            if not isinstance(code, str):
                raise ValueError(f"无效的股票代码类型: {type(code)}")
            
            if not code:
                raise ValueError("股票代码不能为空字符串")
            
            # 验证股票代码格式（6位数字 + . + 市场代码）
            if '.' not in code:
                raise ValueError(
                    f"无效的股票代码格式: {code}。"
                    f"正确格式: '000001.SZ' 或 '600000.SH'"
                )
            
            parts = code.split('.')
            if len(parts) != 2:
                raise ValueError(f"无效的股票代码格式: {code}")
            
            stock_num, market = parts
            
            if len(stock_num) != 6 or not stock_num.isdigit():
                raise ValueError(
                    f"无效的股票代码: {code}。股票代码应为6位数字"
                )
            
            if market not in ['SZ', 'SH']:
                raise ValueError(
                    f"无效的市场代码: {market}。应为 'SZ' 或 'SH'"
                )
    
    def _validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Raises:
            ValueError: 日期格式或范围无效
        """
        # 验证日期格式
        try:
            start_dt = datetime.strptime(start_date, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"无效的开始日期格式: {start_date}。应为 'YYYYMMDD'"
            )
        
        try:
            end_dt = datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"无效的结束日期格式: {end_date}。应为 'YYYYMMDD'"
            )
        
        # 验证日期范围
        if start_dt > end_dt:
            raise ValueError(
                f"开始日期 {start_date} 不能晚于结束日期 {end_date}"
            )
        
        # 验证日期不在未来
        if end_dt > datetime.now():
            raise ValueError(
                f"结束日期 {end_date} 不能是未来日期"
            )
    
    def _validate_period(self, period: str) -> None:
        """
        验证数据周期
        
        Args:
            period: 数据周期
        
        Raises:
            ValueError: 周期无效
        """
        valid_periods = ['tick', '1d']
        
        if period not in valid_periods:
            raise ValueError(
                f"无效的数据周期: {period}。"
                f"支持的周期: {', '.join(valid_periods)}"
            )
    
    def _validate_adjust_type(self, adjust_type: str) -> None:
        """
        验证复权类型
        
        Args:
            adjust_type: 复权类型
        
        Raises:
            ValueError: 复权类型无效
        """
        valid_types = ['none', 'front', 'back']
        
        if adjust_type not in valid_types:
            raise ValueError(
                f"无效的复权类型: {adjust_type}。"
                f"支持的类型: {', '.join(valid_types)}"
            )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"DataRetriever("
            f"client={self.client}, "
            f"batch_size={self.batch_size})"
        )
