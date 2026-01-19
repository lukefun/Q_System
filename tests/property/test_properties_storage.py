"""
数据管理器属性测试

使用基于属性的测试验证DataManager的通用正确性属性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st, assume
from src.data_manager import DataManager
from src.data_retriever import DataRetriever
from unittest.mock import Mock
from pathlib import Path
import tempfile
import shutil


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


# 日线数据生成策略
@st.composite
def daily_data_strategy(draw):
    """生成有效的日线数据"""
    stock_code = draw(stock_code_strategy())
    num_days = draw(st.integers(min_value=5, max_value=50))
    
    # 生成日期序列
    start_date = datetime.now() - timedelta(days=num_days + 10)
    dates = [
        (start_date + timedelta(days=i)).strftime('%Y%m%d')
        for i in range(num_days)
    ]
    
    # 生成价格数据
    base_price = draw(st.floats(min_value=1.0, max_value=100.0))
    data = []
    
    for date in dates:
        # 生成符合OHLC关系的价格
        low = base_price * draw(st.floats(min_value=0.95, max_value=0.99))
        high = base_price * draw(st.floats(min_value=1.01, max_value=1.10))
        open_price = draw(st.floats(min_value=low, max_value=high))
        close = draw(st.floats(min_value=low, max_value=high))
        volume = draw(st.integers(min_value=100000, max_value=10000000))
        
        data.append({
            'stock_code': stock_code,
            'date': date,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume,
            'amount': round(close * volume, 2)
        })
        
        # 价格随机游走
        base_price = close
    
    return pd.DataFrame(data)



# ============================================================================
# 属性17：存储-加载往返一致性
# ============================================================================

class TestProperty17StorageLoadRoundTripConsistency:
    """属性17：存储-加载往返一致性"""
    
    @given(data=daily_data_strategy())
    @settings(max_examples=20, deadline=None)
    def test_property_17_save_load_consistency(self, data):
        """
        Feature: week2-xtdata-engineering, Property 17: 存储-加载往返一致性
        
        对于任何市场数据，保存到HDF5后再加载，应该得到与原始数据等价的DataFrame
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            stock_code = data['stock_code'].iloc[0]
            
            manager.save_market_data(data, 'daily', stock_code)
            loaded_data = manager.load_market_data('daily', stock_code)
            
            assert not loaded_data.empty
            assert len(loaded_data) == len(data)
            assert set(loaded_data.columns) == set(data.columns)
            assert set(loaded_data['stock_code'].unique()) == set(data['stock_code'].unique())
            assert set(loaded_data['date'].unique()) == set(data['date'].unique())
            
            for col in ['open', 'high', 'low', 'close']:
                if col in data.columns and col in loaded_data.columns:
                    original_sorted = data.sort_values('date')[col].values
                    loaded_sorted = loaded_data.sort_values('date')[col].values
                    assert np.allclose(original_sorted, loaded_sorted, rtol=1e-5)
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)


# ============================================================================
# 属性18：增量更新仅获取新数据
# ============================================================================

class TestProperty18IncrementalUpdateOnlyNewData:
    """属性18：增量更新仅获取新数据"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_old_days=st.integers(min_value=5, max_value=20),
        num_new_days=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_18_incremental_update_only_new(self, stock_code, num_old_days, num_new_days):
        """
        Feature: week2-xtdata-engineering, Property 18: 增量更新仅获取新数据
        
        对于任何增量更新操作，系统应该仅请求最后更新日期之后的数据
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            old_start_date = datetime.now() - timedelta(days=num_old_days + num_new_days + 5)
            old_dates = [(old_start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_old_days)]
            
            old_data = pd.DataFrame({
                'stock_code': [stock_code] * num_old_days,
                'date': old_dates,
                'open': [10.0] * num_old_days,
                'high': [11.0] * num_old_days,
                'low': [9.0] * num_old_days,
                'close': [10.5] * num_old_days,
                'volume': [1000000] * num_old_days,
                'amount': [10500000] * num_old_days
            })
            
            manager.save_market_data(old_data, 'daily', stock_code)
            last_date = manager.get_last_update_date('daily', stock_code)
            assert last_date == old_dates[-1]
            
            mock_retriever = Mock(spec=DataRetriever)
            last_dt = datetime.strptime(last_date, '%Y%m%d')
            new_dates = [(last_dt + timedelta(days=i + 1)).strftime('%Y%m%d') for i in range(num_new_days)]
            
            new_data = pd.DataFrame({
                'stock_code': [stock_code] * num_new_days,
                'date': new_dates,
                'open': [11.0] * num_new_days,
                'high': [12.0] * num_new_days,
                'low': [10.0] * num_new_days,
                'close': [11.5] * num_new_days,
                'volume': [1100000] * num_new_days,
                'amount': [12650000] * num_new_days
            })
            
            mock_retriever.download_history_data.return_value = new_data
            updated_count = manager.incremental_update(mock_retriever, [stock_code], 'daily')
            
            assert updated_count == num_new_days
            
            call_args = mock_retriever.download_history_data.call_args
            if call_args:
                called_start_date = call_args[1]['start_date']
                assert called_start_date > last_date
            
            all_data = manager.load_market_data('daily', stock_code)
            assert len(all_data) == num_old_days + num_new_days
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)



# ============================================================================
# 属性19：重复数据去重
# ============================================================================

class TestProperty19DuplicateDataDeduplication:
    """属性19：重复数据去重"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_days=st.integers(min_value=5, max_value=20),
        duplicate_ratio=st.floats(min_value=0.1, max_value=0.5)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_19_duplicate_removal(self, stock_code, num_days, duplicate_ratio):
        """
        Feature: week2-xtdata-engineering, Property 19: 重复数据去重
        
        对于任何包含重复记录的数据更新，存储后查询相同的股票代码和日期组合应该只返回一条记录
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            start_date = datetime.now() - timedelta(days=num_days + 10)
            dates = [(start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_days)]
            
            original_data = pd.DataFrame({
                'stock_code': [stock_code] * num_days,
                'date': dates,
                'open': [10.0 + i * 0.1 for i in range(num_days)],
                'high': [11.0 + i * 0.1 for i in range(num_days)],
                'low': [9.0 + i * 0.1 for i in range(num_days)],
                'close': [10.5 + i * 0.1 for i in range(num_days)],
                'volume': [1000000 + i * 10000 for i in range(num_days)],
                'amount': [10500000 + i * 100000 for i in range(num_days)]
            })
            
            manager.save_market_data(original_data, 'daily', stock_code)
            
            num_duplicates = max(1, int(num_days * duplicate_ratio))
            duplicate_dates = dates[:num_duplicates]
            
            duplicate_data = pd.DataFrame({
                'stock_code': [stock_code] * num_duplicates,
                'date': duplicate_dates,
                'open': [11.0] * num_duplicates,
                'high': [12.0] * num_duplicates,
                'low': [10.0] * num_duplicates,
                'close': [11.5] * num_duplicates,
                'volume': [1100000] * num_duplicates,
                'amount': [12650000] * num_duplicates
            })
            
            manager.save_market_data(duplicate_data, 'daily', stock_code)
            all_data = manager.load_market_data('daily', stock_code)
            
            date_counts = all_data.groupby('date').size()
            assert (date_counts == 1).all(), "存在重复的日期记录"
            assert len(all_data) == len(dates)
            assert set(all_data['date'].unique()) == set(dates)
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)


# ============================================================================
# 属性20：查询过滤正确性
# ============================================================================

class TestProperty20QueryFilteringCorrectness:
    """属性20：查询过滤正确性"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_days=st.integers(min_value=20, max_value=50)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_20_date_range_filtering(self, stock_code, num_days):
        """
        Feature: week2-xtdata-engineering, Property 20: 查询过滤正确性
        
        对于任何带有日期范围过滤条件的查询，返回的所有记录都应该满足指定的过滤条件
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            start_date = datetime.now() - timedelta(days=num_days + 10)
            dates = [(start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_days)]
            
            data = pd.DataFrame({
                'stock_code': [stock_code] * num_days,
                'date': dates,
                'open': [10.0 + i * 0.1 for i in range(num_days)],
                'high': [11.0 + i * 0.1 for i in range(num_days)],
                'low': [9.0 + i * 0.1 for i in range(num_days)],
                'close': [10.5 + i * 0.1 for i in range(num_days)],
                'volume': [1000000 + i * 10000 for i in range(num_days)],
                'amount': [10500000 + i * 100000 for i in range(num_days)]
            })
            
            manager.save_market_data(data, 'daily', stock_code)
            
            filter_start_idx = num_days // 4
            filter_end_idx = num_days * 3 // 4
            filter_start_date = dates[filter_start_idx]
            filter_end_date = dates[filter_end_idx]
            
            filtered_data = manager.load_market_data('daily', stock_code, start_date=filter_start_date, end_date=filter_end_date)
            
            assert not filtered_data.empty
            
            for date in filtered_data['date']:
                assert filter_start_date <= date <= filter_end_date
            
            assert (filtered_data['stock_code'] == stock_code).all()
            
            expected_count = filter_end_idx - filter_start_idx + 1
            assert len(filtered_data) == expected_count
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)



# ============================================================================
# 属性23：数据异常标记
# ============================================================================

class TestProperty23DataAnomalyDetection:
    """属性23：数据异常标记"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_normal=st.integers(min_value=10, max_value=30),
        num_anomalies=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_23_negative_price_detection(self, stock_code, num_normal, num_anomalies):
        """
        Feature: week2-xtdata-engineering, Property 23: 数据异常标记
        
        对于任何包含异常值（如负价格）的数据，系统应该标记这些记录或发出警告
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            start_date = datetime.now() - timedelta(days=num_normal + num_anomalies + 10)
            dates = [(start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_normal + num_anomalies)]
            
            prices = []
            for i in range(num_normal):
                prices.append(10.0 + i * 0.1)
            
            for i in range(num_anomalies):
                prices.append(-5.0 - i)
            
            data = pd.DataFrame({
                'stock_code': [stock_code] * (num_normal + num_anomalies),
                'date': dates,
                'open': prices,
                'high': [abs(p) + 1.0 for p in prices],
                'low': [abs(p) - 1.0 if abs(p) > 1.0 else 0.1 for p in prices],
                'close': prices,
                'volume': [1000000] * (num_normal + num_anomalies),
                'amount': [10500000] * (num_normal + num_anomalies)
            })
            
            validation_result = manager.validate_data(data, 'daily')
            
            assert not validation_result['is_valid']
            assert len(validation_result['errors']) > 0
            
            error_messages = ' '.join(validation_result['errors'])
            assert '负值' in error_messages or '负' in error_messages
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)


# ============================================================================
# 属性25：数据类型验证
# ============================================================================

class TestProperty25DataTypeValidation:
    """属性25：数据类型验证"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_days=st.integers(min_value=5, max_value=20)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_25_correct_data_types(self, stock_code, num_days):
        """
        Feature: week2-xtdata-engineering, Property 25: 数据类型验证
        
        对于任何待存储的数据，如果包含错误的数据类型，系统应该检测到验证错误
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            start_date = datetime.now() - timedelta(days=num_days + 10)
            dates = [(start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_days)]
            
            correct_data = pd.DataFrame({
                'stock_code': [stock_code] * num_days,
                'date': dates,
                'open': [10.0 + i * 0.1 for i in range(num_days)],
                'high': [11.0 + i * 0.1 for i in range(num_days)],
                'low': [9.0 + i * 0.1 for i in range(num_days)],
                'close': [10.5 + i * 0.1 for i in range(num_days)],
                'volume': [1000000 + i * 10000 for i in range(num_days)],
                'amount': [10500000 + i * 100000 for i in range(num_days)]
            })
            
            validation_result = manager.validate_data(correct_data, 'daily')
            
            type_errors = [err for err in validation_result['errors'] if '数据类型' in err or 'dtype' in err]
            assert len(type_errors) == 0
            
            wrong_data = correct_data.copy()
            wrong_data['close'] = wrong_data['close'].astype(str)
            
            validation_result_wrong = manager.validate_data(wrong_data, 'daily')
            # Should have type errors when close column is string instead of numeric
            assert len(validation_result_wrong['errors']) > 0 or len(validation_result_wrong['warnings']) > 0
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)


# ============================================================================
# 属性26：数据缺口检测
# ============================================================================

class TestProperty26DataGapDetection:
    """属性26：数据缺口检测"""
    
    @given(
        stock_code=stock_code_strategy(),
        num_before_gap=st.integers(min_value=5, max_value=15),
        gap_days=st.integers(min_value=5, max_value=20),
        num_after_gap=st.integers(min_value=5, max_value=15)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_26_gap_detection(self, stock_code, num_before_gap, gap_days, num_after_gap):
        """
        Feature: week2-xtdata-engineering, Property 26: 数据缺口检测
        
        对于任何时间序列数据，如果存在缺失的交易日，系统应该能够检测并报告缺失的日期范围
        """
        temp_storage = tempfile.mkdtemp()
        
        try:
            manager = DataManager(storage_path=temp_storage)
            
            start_date = datetime.now() - timedelta(days=num_before_gap + gap_days + num_after_gap + 10)
            
            dates_before = [(start_date + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_before_gap)]
            
            gap_start = start_date + timedelta(days=num_before_gap)
            gap_end = gap_start + timedelta(days=gap_days)
            
            dates_after = [(gap_end + timedelta(days=i)).strftime('%Y%m%d') for i in range(num_after_gap)]
            
            all_dates = dates_before + dates_after
            num_total = len(all_dates)
            
            data = pd.DataFrame({
                'stock_code': [stock_code] * num_total,
                'date': all_dates,
                'open': [10.0 + i * 0.1 for i in range(num_total)],
                'high': [11.0 + i * 0.1 for i in range(num_total)],
                'low': [9.0 + i * 0.1 for i in range(num_total)],
                'close': [10.5 + i * 0.1 for i in range(num_total)],
                'volume': [1000000] * num_total,
                'amount': [10500000] * num_total
            })
            
            gaps = manager.detect_data_gaps(data, 'daily', stock_code)
            
            assert len(gaps) > 0, "应该检测到数据缺口"
            
            for gap in gaps:
                assert gap['gap_days'] > 3
            
            max_gap = max(gaps, key=lambda g: g['gap_days'])
            assert max_gap['gap_days'] >= gap_days
        
        finally:
            shutil.rmtree(temp_storage, ignore_errors=True)
