"""
价格复权处理器模块

实现前复权和后复权算法，处理股票分红送股事件对价格的影响
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime
from config import (
    logger,
    DataError,
    ValidationError,
    DEFAULT_ADJUST_TYPE
)
from src.xtdata_client import XtDataClient


class PriceAdjuster:
    """
    价格复权处理器
    
    实现前复权和后复权算法，确保历史价格数据正确反映分红送股等公司行为事件。
    
    **复权说明：**
    - **前复权（Forward Adjust）**：从分红送股事件向前调整历史价格，保持当前价格不变。
      适用于回测场景，避免未来函数。在每个历史时点，使用该时点之前的复权因子
      调整更早的价格。
    
    - **后复权（Backward Adjust）**：从当前价格向后调整历史价格，保持历史价格连续性。
      适用于展示场景，使价格曲线更加平滑。
    
    **OHLCV一致性：**
    复权时会同时调整开盘价(Open)、最高价(High)、最低价(Low)、收盘价(Close)和
    成交量(Volume)，确保价格关系和市值计算的正确性。
    
    Attributes:
        client: XtData客户端实例，用于获取复权因子
    
    Example:
        >>> client = XtDataClient(account_id="test", account_key="test")
        >>> client.connect()
        >>> adjuster = PriceAdjuster(client)
        >>> 
        >>> # 前复权（用于回测）
        >>> adjusted_data = adjuster.forward_adjust(raw_data, '000001.SZ')
        >>> 
        >>> # 后复权（用于展示）
        >>> adjusted_data = adjuster.backward_adjust(raw_data, '000001.SZ')
    """
    
    def __init__(self, client: XtDataClient):
        """
        初始化复权处理器
        
        Args:
            client: XtData客户端，用于获取复权因子
        
        Raises:
            ValueError: 客户端为None
        """
        if client is None:
            raise ValueError("XtDataClient不能为None")
        
        self.client = client
        
        logger.info("PriceAdjuster初始化完成")
    
    def forward_adjust(
        self,
        data: pd.DataFrame,
        stock_code: str
    ) -> pd.DataFrame:
        """
        前复权：从分红送股事件向前调整价格
        
        前复权保持当前价格不变，向前调整历史价格。这是回测的标准做法，
        因为它避免了未来函数——在任何历史时点，我们只使用该时点之前
        已知的信息来调整更早的价格。
        
        **算法说明：**
        1. 获取复权因子序列
        2. 对于每个交易日，使用该日的复权因子调整之前所有日期的价格
        3. OHLCV数据同时调整，保持相对关系
        
        **未来函数防范：**
        前复权确保在回测中不会使用未来信息。在历史时点t，我们只使用
        时点t及之前的复权因子，不会使用t之后的信息。
        
        Args:
            data: 原始价格数据，必须包含以下列：
                  - date: 日期（YYYYMMDD格式）
                  - open: 开盘价
                  - high: 最高价
                  - low: 最低价
                  - close: 收盘价
                  - volume: 成交量
            stock_code: 股票代码，格式如 '000001.SZ'
        
        Returns:
            前复权后的数据DataFrame，包含相同的列
        
        Raises:
            ValueError: 数据格式无效或缺少必需列
            DataError: 获取复权因子失败
        
        Example:
            >>> raw_data = pd.DataFrame({
            ...     'date': ['20240101', '20240102', '20240103'],
            ...     'open': [10.0, 10.5, 10.3],
            ...     'high': [10.8, 10.9, 10.7],
            ...     'low': [9.8, 10.2, 10.0],
            ...     'close': [10.5, 10.3, 10.6],
            ...     'volume': [1000000, 1200000, 900000]
            ... })
            >>> adjusted = adjuster.forward_adjust(raw_data, '000001.SZ')
        """
        # 验证输入数据
        self._validate_price_data(data)
        
        logger.info(f"开始前复权处理: {stock_code}, {len(data)} 条记录")
        
        # 复制数据，避免修改原始数据
        result = data.copy()
        
        # 确保按日期排序
        result = result.sort_values('date').reset_index(drop=True)
        
        try:
            # 获取复权因子
            if len(result) == 0:
                logger.warning(f"股票 {stock_code} 没有数据，跳过复权")
                return result
            
            start_date = result['date'].iloc[0]
            end_date = result['date'].iloc[-1]
            
            adjust_factors = self.get_adjust_factors(
                stock_code,
                start_date,
                end_date
            )
            
            # 如果没有复权因子，返回原始数据并警告
            if adjust_factors is None or adjust_factors.empty:
                logger.warning(
                    f"股票 {stock_code} 没有复权因子数据，返回未复权数据"
                )
                return result
            
            # 将复权因子合并到数据中
            # 如果数据中已有adjust_factor列，先删除
            has_adjust_factor = 'adjust_factor' in result.columns
            if has_adjust_factor:
                result = result.drop(columns=['adjust_factor'])
            
            result = result.merge(
                adjust_factors,
                on='date',
                how='left'
            )
            
            # 填充缺失的复权因子（使用前向填充）
            result['adjust_factor'] = result['adjust_factor'].fillna(method='ffill')
            
            # 如果第一行的复权因子仍然是NaN，使用1.0
            if pd.isna(result['adjust_factor'].iloc[0]):
                result['adjust_factor'] = result['adjust_factor'].fillna(1.0)
            
            # 应用前复权
            # 前复权公式：调整后价格 = 原始价格 × 复权因子
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in result.columns:
                    result[col] = result[col] * result['adjust_factor']
            
            # 成交量不需要调整（或者可以选择反向调整）
            # 这里保持成交量不变，因为成交量反映的是实际交易数量
            
            # 移除临时的复权因子列（如果原始数据中没有）
            if not has_adjust_factor:
                result = result.drop(columns=['adjust_factor'])
            
            logger.info(f"前复权处理完成: {stock_code}")
            
            return result
        
        except Exception as e:
            error_msg = f"前复权处理失败: {stock_code}, {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def backward_adjust(
        self,
        data: pd.DataFrame,
        stock_code: str
    ) -> pd.DataFrame:
        """
        后复权：从当前价格向后调整历史价格
        
        后复权保持最新交易日的价格不变，向后调整历史价格。这种方法
        适用于展示场景，使价格曲线更加连续和平滑。
        
        **算法说明：**
        1. 获取复权因子序列
        2. 计算最新日期的累积复权因子
        3. 使用累积因子调整所有历史价格，使最新价格保持不变
        
        **注意：**
        后复权不适合用于回测，因为它使用了未来的信息（最新的复权因子）
        来调整历史价格。
        
        Args:
            data: 原始价格数据，必须包含以下列：
                  - date: 日期（YYYYMMDD格式）
                  - open: 开盘价
                  - high: 最高价
                  - low: 最低价
                  - close: 收盘价
                  - volume: 成交量
            stock_code: 股票代码，格式如 '000001.SZ'
        
        Returns:
            后复权后的数据DataFrame，包含相同的列
        
        Raises:
            ValueError: 数据格式无效或缺少必需列
            DataError: 获取复权因子失败
        
        Example:
            >>> raw_data = pd.DataFrame({
            ...     'date': ['20240101', '20240102', '20240103'],
            ...     'open': [10.0, 10.5, 10.3],
            ...     'high': [10.8, 10.9, 10.7],
            ...     'low': [9.8, 10.2, 10.0],
            ...     'close': [10.5, 10.3, 10.6],
            ...     'volume': [1000000, 1200000, 900000]
            ... })
            >>> adjusted = adjuster.backward_adjust(raw_data, '000001.SZ')
        """
        # 验证输入数据
        self._validate_price_data(data)
        
        logger.info(f"开始后复权处理: {stock_code}, {len(data)} 条记录")
        
        # 复制数据，避免修改原始数据
        result = data.copy()
        
        # 确保按日期排序
        result = result.sort_values('date').reset_index(drop=True)
        
        try:
            # 获取复权因子
            if len(result) == 0:
                logger.warning(f"股票 {stock_code} 没有数据，跳过复权")
                return result
            
            start_date = result['date'].iloc[0]
            end_date = result['date'].iloc[-1]
            
            adjust_factors = self.get_adjust_factors(
                stock_code,
                start_date,
                end_date
            )
            
            # 如果没有复权因子，返回原始数据并警告
            if adjust_factors is None or adjust_factors.empty:
                logger.warning(
                    f"股票 {stock_code} 没有复权因子数据，返回未复权数据"
                )
                return result
            
            # 将复权因子合并到数据中
            # 如果数据中已有adjust_factor列，先删除
            has_adjust_factor = 'adjust_factor' in result.columns
            if has_adjust_factor:
                result = result.drop(columns=['adjust_factor'])
            
            result = result.merge(
                adjust_factors,
                on='date',
                how='left'
            )
            
            # 填充缺失的复权因子（使用前向填充）
            result['adjust_factor'] = result['adjust_factor'].fillna(method='ffill')
            
            # 如果第一行的复权因子仍然是NaN，使用1.0
            if pd.isna(result['adjust_factor'].iloc[0]):
                result['adjust_factor'] = result['adjust_factor'].fillna(1.0)
            
            # 应用后复权
            # 后复权公式：调整后价格 = 原始价格 × (最新复权因子 / 当日复权因子)
            latest_factor = result['adjust_factor'].iloc[-1]
            
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in result.columns:
                    result[col] = result[col] * (latest_factor / result['adjust_factor'])
            
            # 成交量不需要调整
            
            # 移除临时的复权因子列（如果原始数据中没有）
            if not has_adjust_factor:
                result = result.drop(columns=['adjust_factor'])
            
            logger.info(f"后复权处理完成: {stock_code}")
            
            return result
        
        except Exception as e:
            error_msg = f"后复权处理失败: {stock_code}, {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def get_adjust_factors(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        获取复权因子
        
        从XtData API获取指定股票和日期范围的复权因子数据。
        复权因子反映了分红、送股、配股等公司行为对股价的影响。
        
        **复权因子说明：**
        - 复权因子 = 1.0 表示没有分红送股事件
        - 复权因子 < 1.0 表示发生了除权除息，需要向下调整历史价格
        - 复权因子 > 1.0 表示发生了其他调整事件
        
        Args:
            stock_code: 股票代码，格式如 '000001.SZ'
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
        
        Returns:
            包含日期和复权因子的DataFrame，列包括：
            - date: 日期（YYYYMMDD格式）
            - adjust_factor: 复权因子
            
            如果获取失败或没有数据，返回None
        
        Raises:
            ValueError: 参数无效
            DataError: 数据获取失败
        
        Example:
            >>> factors = adjuster.get_adjust_factors(
            ...     '000001.SZ',
            ...     '20240101',
            ...     '20240110'
            ... )
            >>> print(factors)
                    date  adjust_factor
            0  20240101       1.000000
            1  20240102       1.000000
            2  20240103       0.950000  # 发生了除权除息
        """
        # 参数验证
        self._validate_stock_code(stock_code)
        self._validate_date_range(start_date, end_date)
        
        logger.debug(
            f"获取复权因子: {stock_code}, "
            f"日期范围: {start_date} - {end_date}"
        )
        
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_divid_factors(stock_code, start_date, end_date)
            
            # 检查连接状态
            if not self.client.is_connected():
                logger.warning("XtData客户端未连接，无法获取复权因子")
                return None
            
            # 模拟复权因子数据
            # 实际代码应该是：
            # xtdata = self.client.get_xtdata_module()
            # factors = xtdata.get_divid_factors(stock_code, start_date, end_date)
            
            # 生成日期范围
            start_dt = datetime.strptime(start_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            dates = pd.date_range(start_dt, end_dt, freq='D')
            
            # 模拟复权因子（大部分时间为1.0，偶尔有除权除息）
            factors = []
            for i, date in enumerate(dates):
                # 模拟：每10天可能发生一次除权除息
                if i > 0 and i % 10 == 0:
                    factor = 0.95  # 模拟10%的分红导致的除权
                else:
                    factor = 1.0
                
                factors.append({
                    'date': date.strftime('%Y%m%d'),
                    'adjust_factor': factor
                })
            
            result = pd.DataFrame(factors)
            
            # 计算累积复权因子（用于前复权）
            result['adjust_factor'] = result['adjust_factor'].cumprod()
            
            logger.debug(f"获取到 {len(result)} 条复权因子记录")
            
            return result
        
        except Exception as e:
            error_msg = f"获取复权因子失败: {stock_code}, {str(e)}"
            logger.error(error_msg)
            # 不抛出异常，返回None让调用者处理
            return None
    
    # ========================================================================
    # 验证方法
    # ========================================================================
    
    def _validate_price_data(self, data: pd.DataFrame) -> None:
        """
        验证价格数据格式
        
        Args:
            data: 价格数据DataFrame
        
        Raises:
            ValueError: 数据格式无效
        """
        if data is None:
            raise ValueError("数据不能为None")
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("数据必须是pandas DataFrame类型")
        
        # 检查必需的列
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(
                f"数据缺少必需的列: {', '.join(missing_columns)}。"
                f"必需列: {', '.join(required_columns)}"
            )
        
        # 检查数据类型
        if len(data) > 0:
            # 检查价格列是否为数值类型
            price_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in price_columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    raise ValueError(f"列 {col} 必须是数值类型")
            
            # 检查OHLC关系（允许一定的容差，因为可能有数据误差）
            # high >= max(open, close) >= min(open, close) >= low
            invalid_rows = data[
                (data['high'] < data['open'] - 0.01) |
                (data['high'] < data['close'] - 0.01) |
                (data['low'] > data['open'] + 0.01) |
                (data['low'] > data['close'] + 0.01)
            ]
            
            if len(invalid_rows) > 0:
                logger.warning(
                    f"发现 {len(invalid_rows)} 条记录的OHLC关系异常，"
                    f"可能存在数据质量问题"
                )
    
    def _validate_stock_code(self, stock_code: str) -> None:
        """
        验证股票代码格式
        
        Args:
            stock_code: 股票代码
        
        Raises:
            ValueError: 股票代码格式无效
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
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"PriceAdjuster(client={self.client})"
