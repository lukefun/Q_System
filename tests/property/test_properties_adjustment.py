"""
价格复权属性测试

使用基于属性的测试验证PriceAdjuster的通用正确性属性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st, assume
from src.price_adjuster import PriceAdjuster
from unittest.mock import Mock, patch


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 股票代码生成策略
@st.composite
def stock_code_strategy(draw):
    """生成有效的股票代码"""
    stock_num = draw(st.integers(min_value=0, max_value=999999))
    stock_num_str = f"{stock_num:06d}"
    market = draw(st.sampled_from(['SZ', 'SH']))
    return f"{stock_num_str}.{market}"


# OHLCV数据生成策略
@st.composite
def ohlcv_data_strategy(draw, num_days=None):
    """
    生成符合OHLC关系的价格数据
    
    确保：high >= max(open, close) >= min(open, close) >= low
    """
    if num_days is None:
        num_days = draw(st.integers(min_value=5, max_value=30))
    
    base_price = draw(st.floats(min_value=5.0, max_value=100.0))
    
    data = []
    current_price = base_price
    
    for i in range(num_days):
        # 生成符合OHLC关系的价格
        # 先生成low和high
        low = current_price * draw(st.floats(min_value=0.90, max_value=0.99))
        high = current_price * draw(st.floats(min_value=1.01, max_value=1.10))
        
        # open和close在low和high之间
        open_price = draw(st.floats(min_value=low, max_value=high))
        close = draw(st.floats(min_value=low, max_value=high))
        
        # 成交量
        volume = draw(st.integers(min_value=100000, max_value=10000000))
        
        # 日期
        date = (datetime(2024, 1, 1) + timedelta(days=i)).strftime('%Y%m%d')
        
        data.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
        
        # 价格随机游走
        current_price = close
    
    return pd.DataFrame(data)


# 复权因子生成策略
@st.composite
def adjust_factors_strategy(draw, dates):
    """
    生成复权因子数据
    
    复权因子应该是累积的，且大部分时间为1.0，偶尔有除权除息事件
    """
    factors = []
    cumulative_factor = 1.0
    
    for i, date in enumerate(dates):
        # 10%的概率发生除权除息事件
        if i > 0 and draw(st.booleans()) and draw(st.floats(min_value=0, max_value=1)) < 0.1:
            # 除权除息导致复权因子变化（通常是减少）
            factor_change = draw(st.floats(min_value=0.90, max_value=0.99))
            cumulative_factor *= factor_change
        
        factors.append({
            'date': date,
            'adjust_factor': cumulative_factor
        })
    
    return pd.DataFrame(factors)


def create_mock_client_with_factors(adjust_factors_df):
    """创建带有复权因子的mock客户端"""
    client = Mock()
    client.is_connected.return_value = True
    
    # Mock get_adjust_factors方法
    def mock_get_factors(stock_code, start_date, end_date):
        # 过滤日期范围内的复权因子
        filtered = adjust_factors_df[
            (adjust_factors_df['date'] >= start_date) &
            (adjust_factors_df['date'] <= end_date)
        ].copy()
        return filtered if not filtered.empty else None
    
    return client, mock_get_factors


# ============================================================================
# 属性7：前复权方向正确性
# ============================================================================

class TestProperty7ForwardAdjustDirectionCorrectness:
    """
    属性7：前复权方向正确性
    
    验证需求：2.1
    
    对于任何包含分红送股事件的股票数据，前复权应该调整事件之前的历史价格，
    而保持事件之后的价格不变或向前调整。
    """
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_7_forward_adjust_direction(self, stock_code, price_data):
        """
        Feature: week2-xtdata-engineering, Property 7: 前复权方向正确性
        
        测试前复权的方向正确性：
        1. 当发生除权除息事件时，事件之前的价格应该被调整
        2. 最新的价格应该保持相对稳定（或按累积因子调整）
        3. 调整后的价格应该保持OHLC关系
        """
        # 创建包含除权除息事件的复权因子
        dates = price_data['date'].tolist()
        
        # 构造一个在中间日期发生除权除息的复权因子序列
        factors = []
        cumulative_factor = 1.0
        event_index = len(dates) // 2  # 在中间发生除权除息
        
        for i, date in enumerate(dates):
            if i == event_index:
                # 发生10%的除权除息
                cumulative_factor *= 0.90
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster并mock get_adjust_factors方法
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行前复权
            adjusted_data = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证1：返回的数据应该有相同的行数
            assert len(adjusted_data) == len(price_data)
            
            # 验证2：OHLC关系应该保持
            # high >= max(open, close) >= min(open, close) >= low
            for idx, row in adjusted_data.iterrows():
                assert row['high'] >= row['open'] - 0.01, \
                    f"行{idx}: high({row['high']}) < open({row['open']})"
                assert row['high'] >= row['close'] - 0.01, \
                    f"行{idx}: high({row['high']}) < close({row['close']})"
                assert row['low'] <= row['open'] + 0.01, \
                    f"行{idx}: low({row['low']}) > open({row['open']})"
                assert row['low'] <= row['close'] + 0.01, \
                    f"行{idx}: low({row['low']}) > close({row['close']})"
            
            # 验证3：前复权应该调整价格
            # 除权除息事件之前的价格应该被向下调整（因为复权因子<1）
            if event_index > 0:
                # 事件前的价格应该被调整
                original_close_before = price_data.iloc[event_index - 1]['close']
                adjusted_close_before = adjusted_data.iloc[event_index - 1]['close']
                
                # 前复权：调整后价格 = 原始价格 × 复权因子
                expected_factor = adjust_factors_df.iloc[event_index - 1]['adjust_factor']
                expected_close = original_close_before * expected_factor
                
                # 允许小的浮点误差
                assert abs(adjusted_close_before - expected_close) < 0.01, \
                    f"前复权调整不正确: 期望{expected_close}, 实际{adjusted_close_before}"
            
            # 验证4：最新日期的价格应该使用最新的复权因子
            original_close_last = price_data.iloc[-1]['close']
            adjusted_close_last = adjusted_data.iloc[-1]['close']
            latest_factor = adjust_factors_df.iloc[-1]['adjust_factor']
            expected_close_last = original_close_last * latest_factor
            
            assert abs(adjusted_close_last - expected_close_last) < 0.01, \
                f"最新价格调整不正确: 期望{expected_close_last}, 实际{adjusted_close_last}"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=15)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_7_multiple_events(self, stock_code, price_data):
        """
        测试多次除权除息事件的前复权
        
        验证当有多次除权除息事件时，前复权能正确累积调整
        """
        dates = price_data['date'].tolist()
        
        # 构造多次除权除息事件
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            # 每5天发生一次除权除息
            if i > 0 and i % 5 == 0:
                cumulative_factor *= 0.95  # 5%的除权
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行前复权
            adjusted_data = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证：每个日期的调整应该使用对应的累积复权因子
            for i in range(len(adjusted_data)):
                original_close = price_data.iloc[i]['close']
                adjusted_close = adjusted_data.iloc[i]['close']
                expected_factor = adjust_factors_df.iloc[i]['adjust_factor']
                expected_close = original_close * expected_factor
                
                assert abs(adjusted_close - expected_close) < 0.01, \
                    f"日期{dates[i]}的复权不正确: 期望{expected_close}, 实际{adjusted_close}"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_7_no_adjustment_without_events(self, stock_code, price_data):
        """
        测试没有除权除息事件时，前复权不应该改变价格
        
        当所有复权因子都是1.0时，前复权后的价格应该与原始价格相同
        """
        dates = price_data['date'].tolist()
        
        # 构造没有除权除息事件的复权因子（全部为1.0）
        adjust_factors_df = pd.DataFrame({
            'date': dates,
            'adjust_factor': [1.0] * len(dates)
        })
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行前复权
            adjusted_data = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证：价格应该保持不变（允许小的浮点误差）
            for col in ['open', 'high', 'low', 'close']:
                for i in range(len(adjusted_data)):
                    original_value = price_data.iloc[i][col]
                    adjusted_value = adjusted_data.iloc[i][col]
                    
                    assert abs(adjusted_value - original_value) < 0.01, \
                        f"没有除权除息时价格不应该改变: {col}列第{i}行"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_7_volume_unchanged(self, stock_code, price_data):
        """
        测试前复权不应该改变成交量
        
        成交量反映实际交易数量，不应该因为复权而改变
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息的复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            if i == len(dates) // 2:
                cumulative_factor *= 0.90
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行前复权
            adjusted_data = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证：成交量应该保持不变
            for i in range(len(adjusted_data)):
                original_volume = price_data.iloc[i]['volume']
                adjusted_volume = adjusted_data.iloc[i]['volume']
                
                assert adjusted_volume == original_volume, \
                    f"成交量不应该改变: 原始{original_volume}, 调整后{adjusted_volume}"


# ============================================================================
# 属性8：后复权当前价格不变性
# ============================================================================

class TestProperty8BackwardAdjustCurrentPriceInvariance:
    """
    属性8：后复权当前价格不变性
    
    验证需求：2.2
    
    对于任何股票数据，后复权应该保持最新交易日的收盘价不变。
    """
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_backward_adjust_preserves_latest_price(self, stock_code, price_data):
        """
        Feature: week2-xtdata-engineering, Property 8: 后复权当前价格不变性
        
        测试后复权保持最新价格不变：
        1. 最新交易日的收盘价应该保持不变
        2. 最新交易日的OHLC价格都应该保持不变
        3. 历史价格应该被调整以保持连续性
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息事件的复权因子
        factors = []
        cumulative_factor = 1.0
        event_index = len(dates) // 2  # 在中间发生除权除息
        
        for i, date in enumerate(dates):
            if i == event_index:
                # 发生10%的除权除息
                cumulative_factor *= 0.90
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 保存原始的最新价格
            original_latest_open = price_data.iloc[-1]['open']
            original_latest_high = price_data.iloc[-1]['high']
            original_latest_low = price_data.iloc[-1]['low']
            original_latest_close = price_data.iloc[-1]['close']
            
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证1：返回的数据应该有相同的行数
            assert len(adjusted_data) == len(price_data)
            
            # 验证2：最新交易日的价格应该保持不变（允许小的浮点误差）
            adjusted_latest_open = adjusted_data.iloc[-1]['open']
            adjusted_latest_high = adjusted_data.iloc[-1]['high']
            adjusted_latest_low = adjusted_data.iloc[-1]['low']
            adjusted_latest_close = adjusted_data.iloc[-1]['close']
            
            assert abs(adjusted_latest_open - original_latest_open) < 0.01, \
                f"后复权后最新开盘价应该不变: 原始{original_latest_open}, 调整后{adjusted_latest_open}"
            
            assert abs(adjusted_latest_high - original_latest_high) < 0.01, \
                f"后复权后最新最高价应该不变: 原始{original_latest_high}, 调整后{adjusted_latest_high}"
            
            assert abs(adjusted_latest_low - original_latest_low) < 0.01, \
                f"后复权后最新最低价应该不变: 原始{original_latest_low}, 调整后{adjusted_latest_low}"
            
            assert abs(adjusted_latest_close - original_latest_close) < 0.01, \
                f"后复权后最新收盘价应该不变: 原始{original_latest_close}, 调整后{adjusted_latest_close}"
            
            # 验证3：OHLC关系应该保持
            for idx, row in adjusted_data.iterrows():
                assert row['high'] >= row['open'] - 0.01, \
                    f"行{idx}: high({row['high']}) < open({row['open']})"
                assert row['high'] >= row['close'] - 0.01, \
                    f"行{idx}: high({row['high']}) < close({row['close']})"
                assert row['low'] <= row['open'] + 0.01, \
                    f"行{idx}: low({row['low']}) > open({row['open']})"
                assert row['low'] <= row['close'] + 0.01, \
                    f"行{idx}: low({row['low']}) > close({row['close']})"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=15)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_multiple_events_preserve_latest(self, stock_code, price_data):
        """
        测试多次除权除息事件的后复权仍保持最新价格不变
        
        验证即使有多次除权除息事件，后复权也应该保持最新价格不变
        """
        dates = price_data['date'].tolist()
        
        # 构造多次除权除息事件
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            # 每5天发生一次除权除息
            if i > 0 and i % 5 == 0:
                cumulative_factor *= 0.95  # 5%的除权
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 保存原始的最新价格
            original_latest_prices = {
                'open': price_data.iloc[-1]['open'],
                'high': price_data.iloc[-1]['high'],
                'low': price_data.iloc[-1]['low'],
                'close': price_data.iloc[-1]['close']
            }
            
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证：最新价格应该保持不变
            for price_type in ['open', 'high', 'low', 'close']:
                original_price = original_latest_prices[price_type]
                adjusted_price = adjusted_data.iloc[-1][price_type]
                
                assert abs(adjusted_price - original_price) < 0.01, \
                    f"多次除权后，最新{price_type}价格应该不变: 原始{original_price}, 调整后{adjusted_price}"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_historical_prices_adjusted(self, stock_code, price_data):
        """
        测试后复权调整历史价格
        
        验证后复权应该调整历史价格，使价格曲线连续
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息事件的复权因子
        factors = []
        cumulative_factor = 1.0
        event_index = len(dates) // 2  # 在中间发生除权除息
        
        for i, date in enumerate(dates):
            if i == event_index:
                # 发生明显的除权除息（20%）
                cumulative_factor *= 0.80
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证：除权除息事件之前的价格应该被调整
            if event_index > 0:
                # 事件前的价格应该被调整
                original_close_before = price_data.iloc[event_index - 1]['close']
                adjusted_close_before = adjusted_data.iloc[event_index - 1]['close']
                
                # 后复权公式：调整后价格 = 原始价格 × (最新复权因子 / 当日复权因子)
                latest_factor = adjust_factors_df.iloc[-1]['adjust_factor']
                before_factor = adjust_factors_df.iloc[event_index - 1]['adjust_factor']
                expected_close = original_close_before * (latest_factor / before_factor)
                
                # 允许小的浮点误差
                assert abs(adjusted_close_before - expected_close) < 0.01, \
                    f"后复权历史价格调整不正确: 期望{expected_close}, 实际{adjusted_close_before}"
                
                # 验证调整确实发生了（调整后价格与原始价格不同）
                # 由于latest_factor = 0.80, before_factor = 1.0，所以比值 = 0.80
                # 因此调整后价格应该是原始价格的80%
                assert abs(adjusted_close_before / original_close_before - (latest_factor / before_factor)) < 0.01, \
                    f"后复权调整比例不正确: 原始{original_close_before}, 调整后{adjusted_close_before}, " \
                    f"期望比例{latest_factor / before_factor}"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_no_adjustment_without_events(self, stock_code, price_data):
        """
        测试没有除权除息事件时，后复权不应该改变任何价格
        
        当所有复权因子都是1.0时，后复权后的所有价格应该与原始价格相同
        """
        dates = price_data['date'].tolist()
        
        # 构造没有除权除息事件的复权因子（全部为1.0）
        adjust_factors_df = pd.DataFrame({
            'date': dates,
            'adjust_factor': [1.0] * len(dates)
        })
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证：所有价格应该保持不变（允许小的浮点误差）
            for col in ['open', 'high', 'low', 'close']:
                for i in range(len(adjusted_data)):
                    original_value = price_data.iloc[i][col]
                    adjusted_value = adjusted_data.iloc[i][col]
                    
                    assert abs(adjusted_value - original_value) < 0.01, \
                        f"没有除权除息时价格不应该改变: {col}列第{i}行"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_volume_unchanged(self, stock_code, price_data):
        """
        测试后复权不应该改变成交量
        
        成交量反映实际交易数量，不应该因为复权而改变
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息的复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            if i == len(dates) // 2:
                cumulative_factor *= 0.90
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证：成交量应该保持不变
            for i in range(len(adjusted_data)):
                original_volume = price_data.iloc[i]['volume']
                adjusted_volume = adjusted_data.iloc[i]['volume']
                
                assert adjusted_volume == original_volume, \
                    f"成交量不应该改变: 原始{original_volume}, 调整后{adjusted_volume}"



# ============================================================================
# 属性9：OHLC相对关系不变性
# ============================================================================

class TestProperty9OHLCRelativeRelationshipInvariance:
    """
    属性9：OHLC相对关系不变性
    
    验证需求：2.4, 2.5
    
    对于任何价格数据，复权后每个交易日应该保持：
    high >= max(open, close) >= min(open, close) >= low
    
    这个属性确保复权不会破坏价格的基本逻辑关系。
    """
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_9_forward_adjust_preserves_ohlc_relationships(
        self,
        stock_code,
        price_data
    ):
        """
        Feature: week2-xtdata-engineering, Property 9: OHLC相对关系不变性
        
        测试前复权保持OHLC相对关系：
        1. high >= open
        2. high >= close
        3. low <= open
        4. low <= close
        5. high >= low
        
        这些关系在复权前后都应该保持不变。
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息事件的复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            # 在多个位置发生除权除息
            if i > 0 and i % 3 == 0:
                cumulative_factor *= 0.92  # 8%的除权
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 验证原始数据的OHLC关系（作为前提条件）
            for idx, row in price_data.iterrows():
                assert row['high'] >= row['open'] - 0.01, \
                    f"原始数据行{idx}: high < open"
                assert row['high'] >= row['close'] - 0.01, \
                    f"原始数据行{idx}: high < close"
                assert row['low'] <= row['open'] + 0.01, \
                    f"原始数据行{idx}: low > open"
                assert row['low'] <= row['close'] + 0.01, \
                    f"原始数据行{idx}: low > close"
                assert row['high'] >= row['low'] - 0.01, \
                    f"原始数据行{idx}: high < low"
            
            # 执行前复权
            adjusted_data = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证：复权后OHLC关系应该保持
            for idx, row in adjusted_data.iterrows():
                # high >= open
                assert row['high'] >= row['open'] - 0.01, \
                    f"前复权后行{idx}: high({row['high']:.2f}) < open({row['open']:.2f})"
                
                # high >= close
                assert row['high'] >= row['close'] - 0.01, \
                    f"前复权后行{idx}: high({row['high']:.2f}) < close({row['close']:.2f})"
                
                # low <= open
                assert row['low'] <= row['open'] + 0.01, \
                    f"前复权后行{idx}: low({row['low']:.2f}) > open({row['open']:.2f})"
                
                # low <= close
                assert row['low'] <= row['close'] + 0.01, \
                    f"前复权后行{idx}: low({row['low']:.2f}) > close({row['close']:.2f})"
                
                # high >= low
                assert row['high'] >= row['low'] - 0.01, \
                    f"前复权后行{idx}: high({row['high']:.2f}) < low({row['low']:.2f})"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_9_backward_adjust_preserves_ohlc_relationships(
        self,
        stock_code,
        price_data
    ):
        """
        测试后复权保持OHLC相对关系
        
        验证后复权也应该保持OHLC的相对关系不变。
        """
        dates = price_data['date'].tolist()
        
        # 构造包含除权除息事件的复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            # 在多个位置发生除权除息
            if i > 0 and i % 3 == 0:
                cumulative_factor *= 0.92  # 8%的除权
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 执行后复权
            adjusted_data = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证：复权后OHLC关系应该保持
            for idx, row in adjusted_data.iterrows():
                # high >= open
                assert row['high'] >= row['open'] - 0.01, \
                    f"后复权后行{idx}: high({row['high']:.2f}) < open({row['open']:.2f})"
                
                # high >= close
                assert row['high'] >= row['close'] - 0.01, \
                    f"后复权后行{idx}: high({row['high']:.2f}) < close({row['close']:.2f})"
                
                # low <= open
                assert row['low'] <= row['open'] + 0.01, \
                    f"后复权后行{idx}: low({row['low']:.2f}) > open({row['open']:.2f})"
                
                # low <= close
                assert row['low'] <= row['close'] + 0.01, \
                    f"后复权后行{idx}: low({row['low']:.2f}) > close({row['close']:.2f})"
                
                # high >= low
                assert row['high'] >= row['low'] - 0.01, \
                    f"后复权后行{idx}: high({row['high']:.2f}) < low({row['low']:.2f})"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=15)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_9_ohlc_relationships_with_extreme_adjustments(
        self,
        stock_code,
        price_data
    ):
        """
        测试极端复权因子下的OHLC关系保持
        
        验证即使在极端的除权除息情况下（如大比例分红），
        OHLC关系仍然保持不变。
        """
        dates = price_data['date'].tolist()
        
        # 构造包含极端除权除息事件的复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            # 在中间位置发生极端除权（50%的分红）
            if i == len(dates) // 2:
                cumulative_factor *= 0.50  # 50%的除权
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 测试前复权
            forward_adjusted = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证前复权后的OHLC关系
            for idx, row in forward_adjusted.iterrows():
                assert row['high'] >= row['open'] - 0.01, \
                    f"极端前复权后行{idx}: high < open"
                assert row['high'] >= row['close'] - 0.01, \
                    f"极端前复权后行{idx}: high < close"
                assert row['low'] <= row['open'] + 0.01, \
                    f"极端前复权后行{idx}: low > open"
                assert row['low'] <= row['close'] + 0.01, \
                    f"极端前复权后行{idx}: low > close"
                assert row['high'] >= row['low'] - 0.01, \
                    f"极端前复权后行{idx}: high < low"
            
            # 测试后复权
            backward_adjusted = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证后复权后的OHLC关系
            for idx, row in backward_adjusted.iterrows():
                assert row['high'] >= row['open'] - 0.01, \
                    f"极端后复权后行{idx}: high < open"
                assert row['high'] >= row['close'] - 0.01, \
                    f"极端后复权后行{idx}: high < close"
                assert row['low'] <= row['open'] + 0.01, \
                    f"极端后复权后行{idx}: low > open"
                assert row['low'] <= row['close'] + 0.01, \
                    f"极端后复权后行{idx}: low > close"
                assert row['high'] >= row['low'] - 0.01, \
                    f"极端后复权后行{idx}: high < low"
    
    @given(
        stock_code=stock_code_strategy(),
        price_data=ohlcv_data_strategy(num_days=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_9_ohlc_spread_preservation(
        self,
        stock_code,
        price_data
    ):
        """
        测试OHLC价差比例保持
        
        验证复权不会改变价格的相对价差比例。
        例如，如果原始数据中 (high - low) / close = 5%，
        复权后这个比例应该保持不变。
        """
        dates = price_data['date'].tolist()
        
        # 构造复权因子
        factors = []
        cumulative_factor = 1.0
        
        for i, date in enumerate(dates):
            if i > 0 and i % 5 == 0:
                cumulative_factor *= 0.95
            
            factors.append({
                'date': date,
                'adjust_factor': cumulative_factor
            })
        
        adjust_factors_df = pd.DataFrame(factors)
        
        # 创建mock客户端
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        
        # 创建PriceAdjuster
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors方法
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors_df):
            # 计算原始数据的价差比例
            original_spreads = []
            for idx, row in price_data.iterrows():
                if row['close'] > 0:
                    spread_ratio = (row['high'] - row['low']) / row['close']
                    original_spreads.append(spread_ratio)
                else:
                    original_spreads.append(None)
            
            # 执行前复权
            forward_adjusted = adjuster.forward_adjust(price_data.copy(), stock_code)
            
            # 验证前复权后的价差比例
            for idx, row in forward_adjusted.iterrows():
                if original_spreads[idx] is not None and row['close'] > 0:
                    adjusted_spread_ratio = (row['high'] - row['low']) / row['close']
                    original_spread_ratio = original_spreads[idx]
                    
                    # 价差比例应该保持不变（允许小的浮点误差）
                    assert abs(adjusted_spread_ratio - original_spread_ratio) < 0.001, \
                        f"前复权后行{idx}的价差比例改变: " \
                        f"原始{original_spread_ratio:.4f}, 调整后{adjusted_spread_ratio:.4f}"
            
            # 执行后复权
            backward_adjusted = adjuster.backward_adjust(price_data.copy(), stock_code)
            
            # 验证后复权后的价差比例
            for idx, row in backward_adjusted.iterrows():
                if original_spreads[idx] is not None and row['close'] > 0:
                    adjusted_spread_ratio = (row['high'] - row['low']) / row['close']
                    original_spread_ratio = original_spreads[idx]
                    
                    # 价差比例应该保持不变（允许小的浮点误差）
                    assert abs(adjusted_spread_ratio - original_spread_ratio) < 0.001, \
                        f"后复权后行{idx}的价差比例改变: " \
                        f"原始{original_spread_ratio:.4f}, 调整后{adjusted_spread_ratio:.4f}"
