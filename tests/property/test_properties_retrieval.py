"""
数据获取器属性测试

使用基于属性的测试验证DataRetriever的通用正确性属性
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from src.data_retriever import DataRetriever
from unittest.mock import Mock


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


# 股票代码列表生成策略
stock_codes_list = st.lists(
    stock_code_strategy(),
    min_size=1,
    max_size=10,
    unique=True
)


# 日期范围生成策略
@st.composite
def date_range_strategy(draw):
    """生成有效的日期范围"""
    start_days_ago = draw(st.integers(min_value=10, max_value=365 * 4))
    end_days_ago = draw(st.integers(min_value=1, max_value=start_days_ago - 1))
    
    start_date = (datetime.now() - timedelta(days=start_days_ago)).strftime('%Y%m%d')
    end_date = (datetime.now() - timedelta(days=end_days_ago)).strftime('%Y%m%d')
    
    return start_date, end_date


# 日期生成策略（过去的日期）
@st.composite
def past_date_strategy(draw):
    """生成过去的日期"""
    days_ago = draw(st.integers(min_value=1, max_value=365 * 4))
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y%m%d')


def create_mock_client():
    """创建mock客户端"""
    client = Mock()
    client.is_connected.return_value = True
    return client


# ============================================================================
# 属性1：历史数据范围正确性
# ============================================================================

class TestProperty1HistoricalDataRangeCorrectness:
    """属性1：历史数据范围正确性"""
    
    @given(
        stock_codes=stock_codes_list,
        date_range=date_range_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_1_date_range_correctness(self, stock_codes, date_range):
        """Feature: week2-xtdata-engineering, Property 1: 历史数据范围正确性"""
        start_date, end_date = date_range
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period='1d'
        )
        
        assert isinstance(data, pd.DataFrame)
        
        if not data.empty:
            for date_str in data['date'].unique():
                assert start_date <= date_str <= end_date
            
            returned_codes = set(data['stock_code'].unique())
            requested_codes = set(stock_codes)
            assert returned_codes == requested_codes


# ============================================================================
# 属性2：市场快照数据完整性
# ============================================================================

class TestProperty2MarketSnapshotDataCompleteness:
    """属性2：市场快照数据完整性"""
    
    @given(stock_codes=stock_codes_list)
    @settings(max_examples=100, deadline=None)
    def test_property_2_all_stocks_in_snapshot(self, stock_codes):
        """Feature: week2-xtdata-engineering, Property 2: 市场快照数据完整性"""
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        data = retriever.get_market_data(stock_codes)
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        
        returned_codes = set(data['stock_code'].tolist())
        requested_codes = set(stock_codes)
        assert returned_codes == requested_codes
        assert len(data) == len(stock_codes)


# ============================================================================
# 属性3：Tick数据时间精度
# ============================================================================

class TestProperty3TickDataTimePrecision:
    """属性3：Tick数据时间精度"""
    
    @given(
        stock_codes=stock_codes_list,
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_3_tick_has_timestamp(self, stock_codes, date):
        """Feature: week2-xtdata-engineering, Property 3: Tick数据时间精度"""
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=date,
            end_date=date,
            period='tick'
        )
        
        if not data.empty:
            assert 'timestamp' in data.columns
            assert not data['timestamp'].isnull().any()
            assert data['timestamp'].dtype in [int, 'int64']
            
            for ts in data['timestamp']:
                assert ts > 1000000000000


# ============================================================================
# 属性4：日线数据唯一性
# ============================================================================

class TestProperty4DailyDataUniqueness:
    """属性4：日线数据唯一性"""
    
    @given(
        stock_codes=stock_codes_list,
        date_range=date_range_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_4_no_duplicate_records(self, stock_codes, date_range):
        """Feature: week2-xtdata-engineering, Property 4: 日线数据唯一性"""
        start_date, end_date = date_range
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period='1d'
        )
        
        if not data.empty:
            duplicates = data.duplicated(subset=['stock_code', 'date'])
            assert not duplicates.any()
            
            grouped = data.groupby(['stock_code', 'date']).size()
            assert (grouped == 1).all()


# ============================================================================
# 属性5：API错误处理稳定性
# ============================================================================

class TestProperty5APIErrorHandlingStability:
    """属性5：API错误处理稳定性"""
    
    @given(
        stock_codes=stock_codes_list,
        date_range=date_range_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_5_disconnected_client_raises_error(self, stock_codes, date_range):
        """Feature: week2-xtdata-engineering, Property 5: API错误处理稳定性"""
        start_date, end_date = date_range
        
        disconnected_client = Mock()
        disconnected_client.is_connected.return_value = False
        
        retriever = DataRetriever(disconnected_client)
        
        with pytest.raises(Exception) as exc_info:
            retriever.download_history_data(
                stock_codes=stock_codes,
                start_date=start_date,
                end_date=end_date
            )
        
        error_msg = str(exc_info.value)
        assert len(error_msg) > 0
        assert "连接" in error_msg or "connect" in error_msg.lower()


# ============================================================================
# 属性6：批量请求完整性
# ============================================================================

class TestProperty6BatchRequestCompleteness:
    """属性6：批量请求完整性"""
    
    @given(
        stock_codes=st.lists(
            stock_code_strategy(),
            min_size=2,
            max_size=20,
            unique=True
        ),
        date_range=date_range_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_6_batch_request_completeness(self, stock_codes, date_range):
        """Feature: week2-xtdata-engineering, Property 6: 批量请求完整性"""
        start_date, end_date = date_range
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period='1d'
        )
        
        if not data.empty:
            returned_codes = set(data['stock_code'].unique())
            requested_codes = set(stock_codes)
            assert returned_codes == requested_codes
            
            for stock_code in stock_codes:
                stock_data = data[data['stock_code'] == stock_code]
                assert not stock_data.empty
