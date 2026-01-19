"""
基本面数据处理器模块

处理财务指标数据，确保时间点正确性，防止未来函数
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime
from config import (
    logger,
    DataError,
    ValidationError
)
from src.xtdata_client import XtDataClient


class FundamentalHandler:
    """
    基本面数据处理器
    
    处理财务指标数据（PE、PB、ROE等），严格确保时间点正确性。
    所有数据查询都基于公告日期（announce_date）而非报告期（report_date），
    以防止未来函数问题。
    
    **时间点正确性说明：**
    在量化回测中，最常见的错误之一是"未来函数"——使用了在历史时点
    尚未公开的信息。对于财务数据，关键是使用公告日期而非报告期：
    
    - **报告期（report_date）**：财务报表所属的会计期间结束日期
      例如：2024年第一季度报告的report_date是2024-03-31
    
    - **公告日期（announce_date）**：财务报表实际公开披露的日期
      例如：2024年第一季度报告可能在2024-04-30才公告
    
    在回测中，我们只能使用公告日期之后的数据，否则就是使用了
    "未来信息"，导致回测结果过于乐观。
    
    **缺失数据处理：**
    财务数据经常存在缺失情况（公司未披露、数据源问题等）。本处理器
    采用优雅降级策略，返回None而非抛出异常，让调用者决定如何处理。
    
    Attributes:
        client: XtData客户端实例，用于获取财务数据
    
    Example:
        >>> client = XtDataClient(account_id="test", account_key="test")
        >>> client.connect()
        >>> handler = FundamentalHandler(client)
        >>> 
        >>> # 获取时间点正确的财务数据
        >>> data = handler.get_financial_data(
        ...     stock_codes=['000001.SZ'],
        ...     indicators=['pe', 'pb', 'roe'],
        ...     as_of_date='20240430'  # 只返回4月30日之前公告的数据
        ... )
        >>> 
        >>> # 计算PE比率
        >>> pe = handler.calculate_pe_ratio(
        ...     stock_code='000001.SZ',
        ...     date='20240430',
        ...     price_data=price_df
        ... )
    """
    
    def __init__(self, client: XtDataClient):
        """
        初始化基本面处理器
        
        Args:
            client: XtData客户端实例
        
        Raises:
            ValueError: 客户端为None
        """
        if client is None:
            raise ValueError("XtDataClient不能为None")
        
        self.client = client
        
        logger.info("FundamentalHandler初始化完成")
    
    def get_financial_data(
        self,
        stock_codes: List[str],
        indicators: List[str],
        as_of_date: str
    ) -> pd.DataFrame:
        """
        获取指定时点的财务数据（时间点正确）
        
        **关键特性：时间点正确性**
        此方法确保只返回在as_of_date之前已经公告的财务数据。
        使用announce_date（公告日期）而非report_date（报告期）进行过滤，
        这是防止未来函数的关键。
        
        **工作原理：**
        1. 从XtData API获取财务数据
        2. 过滤：只保留 announce_date <= as_of_date 的记录
        3. 对于每只股票，如果有多条符合条件的记录，返回最新的一条
        
        **支持的指标：**
        - 'pe': 市盈率（Price-to-Earnings Ratio）
        - 'pb': 市净率（Price-to-Book Ratio）
        - 'roe': 净资产收益率（Return on Equity）
        - 'revenue': 营业收入
        - 'net_profit': 净利润
        - 'total_assets': 总资产
        - 'total_equity': 净资产
        
        Args:
            stock_codes: 股票代码列表，如 ['000001.SZ', '600000.SH']
            indicators: 指标列表，如 ['pe', 'pb', 'roe']
            as_of_date: 查询时点，格式 'YYYYMMDD'
                       只返回此日期或之前公告的数据
        
        Returns:
            包含财务指标的DataFrame，列包括：
            - stock_code: 股票代码
            - report_date: 报告期
            - announce_date: 公告日期
            - [indicators]: 请求的各项指标
            
            如果某只股票没有数据，该股票不会出现在结果中
        
        Raises:
            ValueError: 参数无效
            DataError: 数据获取失败
        
        Example:
            >>> # 获取2024年4月30日时点的财务数据
            >>> data = handler.get_financial_data(
            ...     stock_codes=['000001.SZ', '000002.SZ'],
            ...     indicators=['pe', 'pb', 'roe'],
            ...     as_of_date='20240430'
            ... )
            >>> print(data)
              stock_code report_date announce_date     pe     pb    roe
            0  000001.SZ    20231231      20240330  12.5   1.8  15.2
            1  000002.SZ    20231231      20240328  18.3   2.1  12.8
        """
        # 参数验证
        self._validate_stock_codes(stock_codes)
        self._validate_indicators(indicators)
        self._validate_date(as_of_date)
        
        # 检查连接状态
        if not self.client.is_connected():
            raise DataError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info(
            f"获取财务数据: {len(stock_codes)}只股票, "
            f"指标: {indicators}, 时点: {as_of_date}"
        )
        
        try:
            all_data = []
            
            for stock_code in stock_codes:
                try:
                    # 获取单只股票的财务数据
                    stock_data = self._fetch_financial_data(
                        stock_code,
                        indicators,
                        as_of_date
                    )
                    
                    if stock_data is not None and not stock_data.empty:
                        all_data.append(stock_data)
                    else:
                        logger.debug(f"股票 {stock_code} 没有财务数据")
                
                except Exception as e:
                    logger.warning(
                        f"获取股票 {stock_code} 财务数据失败: {str(e)}"
                    )
                    # 继续处理其他股票
                    continue
            
            # 合并所有数据
            if not all_data:
                logger.warning("没有获取到任何财务数据")
                return pd.DataFrame()
            
            result = pd.concat(all_data, ignore_index=True)
            
            logger.info(
                f"财务数据获取完成: {len(result)} 条记录, "
                f"{len(result['stock_code'].unique())} 只股票"
            )
            
            return result
        
        except Exception as e:
            error_msg = f"获取财务数据失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def _fetch_financial_data(
        self,
        stock_code: str,
        indicators: List[str],
        as_of_date: str
    ) -> Optional[pd.DataFrame]:
        """
        获取单只股票的财务数据（内部方法）
        
        Args:
            stock_code: 股票代码
            indicators: 指标列表
            as_of_date: 查询时点
        
        Returns:
            财务数据DataFrame，失败返回None
        """
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_financial_data(stock_code, indicators)
            
            logger.debug(f"获取股票 {stock_code} 的财务数据")
            
            # 模拟财务数据
            # 实际代码应该是：
            # xtdata = self.client.get_xtdata_module()
            # data = xtdata.get_financial_data(stock_code, indicators)
            
            # 生成模拟数据：最近4个季度的财务报告
            as_of_dt = datetime.strptime(as_of_date, "%Y%m%d")
            
            # 模拟季度报告
            quarters = [
                ('20231231', '20240330'),  # 年报，3月30日公告
                ('20230930', '20231030'),  # 三季报，10月30日公告
                ('20230630', '20230830'),  # 半年报，8月30日公告
                ('20230331', '20230430'),  # 一季报，4月30日公告
            ]
            
            records = []
            for report_date, announce_date in quarters:
                announce_dt = datetime.strptime(announce_date, "%Y%m%d")
                
                # 只返回公告日期在as_of_date之前的数据
                if announce_dt <= as_of_dt:
                    record = {
                        'stock_code': stock_code,
                        'report_date': report_date,
                        'announce_date': announce_date
                    }
                    
                    # 添加请求的指标（模拟数据）
                    if 'pe' in indicators:
                        record['pe'] = np.random.uniform(10, 30)
                    if 'pb' in indicators:
                        record['pb'] = np.random.uniform(1, 5)
                    if 'roe' in indicators:
                        record['roe'] = np.random.uniform(5, 20)
                    if 'revenue' in indicators:
                        record['revenue'] = np.random.uniform(1e8, 1e10)
                    if 'net_profit' in indicators:
                        record['net_profit'] = np.random.uniform(1e7, 1e9)
                    if 'total_assets' in indicators:
                        record['total_assets'] = np.random.uniform(1e9, 1e11)
                    if 'total_equity' in indicators:
                        record['total_equity'] = np.random.uniform(1e8, 1e10)
                    
                    records.append(record)
            
            if not records:
                return None
            
            # 返回最新的一条记录（公告日期最晚的）
            df = pd.DataFrame(records)
            df = df.sort_values('announce_date', ascending=False)
            result = df.head(1).reset_index(drop=True)
            
            return result
        
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 财务数据时发生错误: {str(e)}")
            return None
    
    def calculate_pe_ratio(
        self,
        stock_code: str,
        date: str,
        price_data: pd.DataFrame
    ) -> Optional[float]:
        """
        计算PE比率（市盈率）
        
        PE比率 = 股价 / 每股收益（EPS）
        
        **时间对齐：**
        使用指定日期的收盘价和该日期之前最新公告的盈利数据。
        确保不使用未来信息。
        
        **计算说明：**
        1. 获取指定日期的收盘价
        2. 获取该日期之前最新公告的净利润和总股本
        3. 计算EPS = 净利润 / 总股本
        4. 计算PE = 股价 / EPS
        
        Args:
            stock_code: 股票代码，格式如 '000001.SZ'
            date: 计算日期，格式 'YYYYMMDD'
            price_data: 价格数据DataFrame，必须包含以下列：
                       - stock_code: 股票代码
                       - date: 日期
                       - close: 收盘价
        
        Returns:
            PE比率，如果数据不可用则返回None
        
        Raises:
            ValueError: 参数无效
        
        Example:
            >>> price_df = pd.DataFrame({
            ...     'stock_code': ['000001.SZ', '000001.SZ'],
            ...     'date': ['20240429', '20240430'],
            ...     'close': [10.5, 10.8]
            ... })
            >>> pe = handler.calculate_pe_ratio(
            ...     stock_code='000001.SZ',
            ...     date='20240430',
            ...     price_data=price_df
            ... )
            >>> print(f"PE比率: {pe:.2f}")
        """
        # 参数验证
        self._validate_stock_code(stock_code)
        self._validate_date(date)
        self._validate_price_data(price_data)
        
        logger.debug(f"计算PE比率: {stock_code}, 日期: {date}")
        
        try:
            # 获取指定日期的收盘价
            price_row = price_data[
                (price_data['stock_code'] == stock_code) &
                (price_data['date'] == date)
            ]
            
            if price_row.empty:
                logger.warning(
                    f"未找到股票 {stock_code} 在 {date} 的价格数据"
                )
                return None
            
            close_price = price_row['close'].iloc[0]
            
            # 获取该日期之前最新公告的财务数据
            financial_data = self.get_financial_data(
                stock_codes=[stock_code],
                indicators=['net_profit'],
                as_of_date=date
            )
            
            if financial_data.empty:
                logger.warning(
                    f"未找到股票 {stock_code} 在 {date} 之前的财务数据"
                )
                return None
            
            net_profit = financial_data['net_profit'].iloc[0]
            
            # 获取总股本（这里简化处理，实际应该从API获取）
            # 实际实现：total_shares = xtdata.get_total_shares(stock_code, date)
            total_shares = 1e9  # 模拟：10亿股
            
            # 计算EPS
            eps = net_profit / total_shares
            
            # 计算PE
            if eps <= 0:
                logger.warning(
                    f"股票 {stock_code} 的EPS为负或零，无法计算PE比率"
                )
                return None
            
            pe_ratio = close_price / eps
            
            logger.debug(
                f"PE比率计算完成: {stock_code}, "
                f"价格={close_price:.2f}, EPS={eps:.4f}, PE={pe_ratio:.2f}"
            )
            
            return pe_ratio
        
        except Exception as e:
            logger.error(f"计算PE比率失败: {stock_code}, {str(e)}")
            return None
    
    def calculate_pb_ratio(
        self,
        stock_code: str,
        date: str,
        price_data: pd.DataFrame
    ) -> Optional[float]:
        """
        计算PB比率（市净率）
        
        PB比率 = 股价 / 每股净资产（BVPS）
        
        **时间对齐：**
        使用指定日期的收盘价和该日期之前最新公告的净资产数据。
        确保不使用未来信息。
        
        **计算说明：**
        1. 获取指定日期的收盘价
        2. 获取该日期之前最新公告的净资产和总股本
        3. 计算BVPS = 净资产 / 总股本
        4. 计算PB = 股价 / BVPS
        
        Args:
            stock_code: 股票代码，格式如 '000001.SZ'
            date: 计算日期，格式 'YYYYMMDD'
            price_data: 价格数据DataFrame，必须包含以下列：
                       - stock_code: 股票代码
                       - date: 日期
                       - close: 收盘价
        
        Returns:
            PB比率，如果数据不可用则返回None
        
        Raises:
            ValueError: 参数无效
        
        Example:
            >>> price_df = pd.DataFrame({
            ...     'stock_code': ['000001.SZ', '000001.SZ'],
            ...     'date': ['20240429', '20240430'],
            ...     'close': [10.5, 10.8]
            ... })
            >>> pb = handler.calculate_pb_ratio(
            ...     stock_code='000001.SZ',
            ...     date='20240430',
            ...     price_data=price_df
            ... )
            >>> print(f"PB比率: {pb:.2f}")
        """
        # 参数验证
        self._validate_stock_code(stock_code)
        self._validate_date(date)
        self._validate_price_data(price_data)
        
        logger.debug(f"计算PB比率: {stock_code}, 日期: {date}")
        
        try:
            # 获取指定日期的收盘价
            price_row = price_data[
                (price_data['stock_code'] == stock_code) &
                (price_data['date'] == date)
            ]
            
            if price_row.empty:
                logger.warning(
                    f"未找到股票 {stock_code} 在 {date} 的价格数据"
                )
                return None
            
            close_price = price_row['close'].iloc[0]
            
            # 获取该日期之前最新公告的财务数据
            financial_data = self.get_financial_data(
                stock_codes=[stock_code],
                indicators=['total_equity'],
                as_of_date=date
            )
            
            if financial_data.empty:
                logger.warning(
                    f"未找到股票 {stock_code} 在 {date} 之前的财务数据"
                )
                return None
            
            total_equity = financial_data['total_equity'].iloc[0]
            
            # 获取总股本（这里简化处理，实际应该从API获取）
            # 实际实现：total_shares = xtdata.get_total_shares(stock_code, date)
            total_shares = 1e9  # 模拟：10亿股
            
            # 计算BVPS（每股净资产）
            bvps = total_equity / total_shares
            
            # 计算PB
            if bvps <= 0:
                logger.warning(
                    f"股票 {stock_code} 的BVPS为负或零，无法计算PB比率"
                )
                return None
            
            pb_ratio = close_price / bvps
            
            logger.debug(
                f"PB比率计算完成: {stock_code}, "
                f"价格={close_price:.2f}, BVPS={bvps:.4f}, PB={pb_ratio:.2f}"
            )
            
            return pb_ratio
        
        except Exception as e:
            logger.error(f"计算PB比率失败: {stock_code}, {str(e)}")
            return None
    
    # ========================================================================
    # 验证方法
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
            self._validate_stock_code(code)
    
    def _validate_stock_code(self, stock_code: str) -> None:
        """
        验证单个股票代码
        
        Args:
            stock_code: 股票代码
        
        Raises:
            ValueError: 股票代码无效
        """
        if not stock_code:
            raise ValueError("股票代码不能为空")
        
        if not isinstance(stock_code, str):
            raise ValueError(f"股票代码必须是字符串类型，当前类型: {type(stock_code)}")
        
        # 验证格式：6位数字 + . + 市场代码
        if '.' not in stock_code:
            raise ValueError(
                f"无效的股票代码格式: {stock_code}。"
                f"正确格式: '000001.SZ' 或 '600000.SH'"
            )
        
        parts = stock_code.split('.')
        if len(parts) != 2:
            raise ValueError(f"无效的股票代码格式: {stock_code}")
        
        stock_num, market = parts
        
        if len(stock_num) != 6 or not stock_num.isdigit():
            raise ValueError(
                f"无效的股票代码: {stock_code}。股票代码应为6位数字"
            )
        
        if market not in ['SZ', 'SH']:
            raise ValueError(
                f"无效的市场代码: {market}。应为 'SZ' 或 'SH'"
            )
    
    def _validate_indicators(self, indicators: List[str]) -> None:
        """
        验证指标列表
        
        Args:
            indicators: 指标列表
        
        Raises:
            ValueError: 指标无效
        """
        if not indicators:
            raise ValueError("指标列表不能为空")
        
        if not isinstance(indicators, list):
            raise ValueError("indicators必须是列表类型")
        
        valid_indicators = [
            'pe', 'pb', 'roe', 'revenue', 'net_profit',
            'total_assets', 'total_equity'
        ]
        
        for indicator in indicators:
            if not isinstance(indicator, str):
                raise ValueError(f"指标必须是字符串类型: {indicator}")
            
            if indicator not in valid_indicators:
                raise ValueError(
                    f"不支持的指标: {indicator}。"
                    f"支持的指标: {', '.join(valid_indicators)}"
                )
    
    def _validate_date(self, date: str) -> None:
        """
        验证日期格式
        
        Args:
            date: 日期字符串
        
        Raises:
            ValueError: 日期格式无效
        """
        if not date:
            raise ValueError("日期不能为空")
        
        if not isinstance(date, str):
            raise ValueError(f"日期必须是字符串类型，当前类型: {type(date)}")
        
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"无效的日期格式: {date}。应为 'YYYYMMDD'"
            )
    
    def _validate_price_data(self, price_data: pd.DataFrame) -> None:
        """
        验证价格数据格式
        
        Args:
            price_data: 价格数据DataFrame
        
        Raises:
            ValueError: 数据格式无效
        """
        if price_data is None:
            raise ValueError("价格数据不能为None")
        
        if not isinstance(price_data, pd.DataFrame):
            raise ValueError("价格数据必须是pandas DataFrame类型")
        
        # 检查必需的列
        required_columns = ['stock_code', 'date', 'close']
        missing_columns = [
            col for col in required_columns
            if col not in price_data.columns
        ]
        
        if missing_columns:
            raise ValueError(
                f"价格数据缺少必需的列: {', '.join(missing_columns)}。"
                f"必需列: {', '.join(required_columns)}"
            )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"FundamentalHandler(client={self.client})"
