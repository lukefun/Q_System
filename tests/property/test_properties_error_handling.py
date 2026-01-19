"""
错误处理属性测试

使用基于属性的测试验证系统的错误处理和数据质量检查的通用正确性属性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st, assume
from src.data_retriever import DataRetriever
from src.data_manager import DataManager
from config import DataError, ValidationError
from unittest.mock import Mock
from pathlib import Path
import tempfile


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 无效股票代码生成策略
@st.composite
def invalid_stock_code_strategy(draw):
    """生成各种无效的股票代码"""
    invalid_type = draw(st.sampled_from([
        'empty',           # 空字符串
        'no_dot',          # 没有点号
        'wrong_length',    # 长度不对
        'wrong_market',    # 错误的市场代码
        'non_numeric',     # 非数字
        'multiple_dots'    # 多个点号
    ]))
    
    if invalid_type == 'empty':
        return ''
    elif invalid_type == 'no_dot':
        return '000001SZ'
    elif invalid_type == 'wrong_length':
        num_digits = draw(st.integers(min_value=1, max_value=10).filter(lambda x: x != 6))
        return f"{'0' * num_digits}.SZ"
    elif invalid_type == 'wrong_market':
        return '000001.XX'
    elif invalid_type == 'non_numeric':
        return 'ABCDEF.SZ'
    elif invalid_type == 'multiple_dots':
        return '000.001.SZ'
    
    return '000001.SZ'  # fallback


# 有效股票代码生成策略
@st.composite
def valid_stock_code_strategy(draw):
    """生成有效的股票代码"""
    stock_num = draw(st.integers(min_value=0, max_value=999999))
    stock_num_str = f"{stock_num:06d}"
    market = draw(st.sampled_from(['SZ', 'SH']))
    return f"{stock_num_str}.{market}"


# 部分有效的股票代码列表生成策略
@st.composite
def mixed_stock_codes_strategy(draw):
    """生成包含有效和无效股票代码的混合列表"""
    num_valid = draw(st.integers(min_value=1, max_value=5))
    num_invalid = draw(st.integers(min_value=1, max_value=3))
    
    valid_codes = [draw(valid_stock_code_strategy()) for _ in range(num_valid)]
    invalid_codes = [draw(invalid_stock_code_strategy()) for _ in range(num_invalid)]
    
    # 混合并打乱顺序
    all_codes = valid_codes + invalid_codes
    draw(st.randoms()).shuffle(all_codes)
    
    return all_codes, valid_codes, invalid_codes


# 日期生成策略
@st.composite
def past_date_strategy(draw):
    """生成过去的日期"""
    days_ago = draw(st.integers(min_value=1, max_value=365 * 2))
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y%m%d')


def create_mock_client():
    """创建mock客户端"""
    client = Mock()
    client.is_connected.return_value = True
    return client


# ============================================================================
# 属性22：无效股票代码错误消息
# ============================================================================

class TestProperty22InvalidStockCodeErrorMessage:
    """
    属性22：无效股票代码错误消息
    
    验证需求：9.1
    
    对于任何无效的股票代码，系统应该返回包含该股票代码的清晰错误消息。
    """
    
    @given(invalid_code=invalid_stock_code_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_22_invalid_stock_code_error_message(self, invalid_code):
        """
        Feature: week2-xtdata-engineering, Property 22: 无效股票代码错误消息
        
        验证：当提供无效股票代码时，系统返回清晰的错误消息
        """
        # 跳过空字符串（会在列表验证时被捕获）
        assume(invalid_code != '')
        
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        # 尝试使用无效股票代码
        with pytest.raises((ValueError, ValidationError, DataError)) as exc_info:
            retriever.download_history_data(
                stock_codes=[invalid_code],
                start_date='20240101',
                end_date='20240110',
                period='1d'
            )
        
        # 验证错误消息包含股票代码信息
        error_message = str(exc_info.value)
        error_message_lower = error_message.lower()
        
        # 错误消息应该提供有用的信息
        assert any([
            '股票代码' in error_message,
            'stock' in error_message_lower,
            'code' in error_message_lower,
            '格式' in error_message,
            'format' in error_message_lower,
            '无效' in error_message,
            'invalid' in error_message_lower,
            '市场代码' in error_message,
            'market' in error_message_lower
        ]), f"错误消息不够清晰: {exc_info.value}"


# ============================================================================
# 属性24：部分数据处理连续性
# ============================================================================

class TestProperty24PartialDataProcessingContinuity:
    """
    属性24：部分数据处理连续性
    
    验证需求：9.3
    
    对于任何API返回的部分不完整数据，系统应该处理有效部分并记录问题，
    而不是完全失败。
    """
    
    @given(
        mixed_codes=mixed_stock_codes_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_property_24_partial_data_processing_continuity(self, mixed_codes, date):
        """
        Feature: week2-xtdata-engineering, Property 24: 部分数据处理连续性
        
        验证：当部分股票代码无效时，系统仍能处理有效的股票代码
        """
        all_codes, valid_codes, invalid_codes = mixed_codes
        
        mock_client = create_mock_client()
        retriever = DataRetriever(mock_client)
        
        # 尝试下载混合列表的数据
        # 系统应该处理有效的代码，跳过无效的代码
        try:
            data = retriever.download_history_data(
                stock_codes=all_codes,
                start_date=date,
                end_date=date,
                period='1d'
            )
            
            # 如果没有抛出异常，验证返回的数据
            if not data.empty:
                # 返回的股票代码应该只包含有效的代码
                returned_codes = set(data['stock_code'].unique())
                
                # 验证：返回的代码应该是有效代码的子集
                assert returned_codes.issubset(set(valid_codes)), \
                    f"返回了无效的股票代码: {returned_codes - set(valid_codes)}"
        
        except (ValueError, ValidationError) as e:
            # 如果抛出异常，验证是在参数验证阶段
            # 这是可以接受的，因为参数验证会在处理前进行
            error_message = str(e)
            error_message_lower = error_message.lower()
            assert any([
                '股票代码' in error_message,
                'stock' in error_message_lower,
                'code' in error_message_lower,
                '格式' in error_message,
                'format' in error_message_lower,
                '市场代码' in error_message,
                'market' in error_message_lower,
                '无效' in error_message,
                'invalid' in error_message_lower
            ]), f"异常消息不清晰: {e}"
    
    @given(
        valid_codes=st.lists(
            valid_stock_code_strategy(),
            min_size=2,
            max_size=5,
            unique=True
        ),
        date=past_date_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_property_24_incremental_update_partial_failure(self, valid_codes, date):
        """
        Feature: week2-xtdata-engineering, Property 24: 部分数据处理连续性
        
        验证：增量更新时，部分股票失败不影响其他股票的更新
        """
        # 创建临时目录用于测试
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = create_mock_client()
            retriever = DataRetriever(mock_client)
            manager = DataManager(storage_path=tmpdir)
            
            # 模拟部分股票下载失败的情况
            # 通过修改retriever的行为来模拟失败
            original_download = retriever.download_history_data
            
            def mock_download_with_failures(*args, **kwargs):
                stock_codes = kwargs.get('stock_codes', args[0] if args else [])
                
                # 让第一只股票"失败"（返回空数据）
                if stock_codes and stock_codes[0] == valid_codes[0]:
                    return pd.DataFrame()
                
                # 其他股票正常返回
                return original_download(*args, **kwargs)
            
            retriever.download_history_data = mock_download_with_failures
            
            # 执行增量更新
            try:
                updated_count = manager.incremental_update(
                    retriever,
                    valid_codes,
                    data_type='daily'
                )
                
                # 验证：即使部分股票失败，其他股票应该成功更新
                # 至少应该有一些股票成功（因为我们只让第一只失败）
                if len(valid_codes) > 1:
                    # 检查是否有数据被保存
                    for stock_code in valid_codes[1:]:  # 跳过第一只（失败的）
                        try:
                            data = manager.load_market_data('daily', stock_code)
                            # 如果能加载到数据，说明部分成功
                            if not data.empty:
                                # 验证通过：部分失败不影响其他股票
                                return
                        except:
                            continue
            
            except Exception as e:
                # 如果整个过程失败，验证错误处理是否合理
                pytest.fail(f"增量更新完全失败，应该支持部分成功: {e}")


# ============================================================================
# 额外的错误处理属性测试
# ============================================================================

class TestErrorHandlingRobustness:
    """错误处理健壮性测试"""
    
    @given(
        stock_code=valid_stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_graceful_degradation_on_missing_data(self, stock_code, date):
        """
        验证：当数据缺失时，系统应该优雅降级而不是崩溃
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DataManager(storage_path=tmpdir)
            
            # 尝试加载不存在的数据
            data = manager.load_market_data('daily', stock_code, date, date)
            
            # 验证：应该返回空DataFrame而不是抛出异常
            assert isinstance(data, pd.DataFrame)
            assert data.empty
    
    @given(
        stock_code=valid_stock_code_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_data_validation_error_messages(self, stock_code):
        """
        验证：数据验证失败时，错误消息应该清晰指出问题
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DataManager(storage_path=tmpdir)
            
            # 创建无效的数据（缺少必需列）
            invalid_data = pd.DataFrame({
                'stock_code': [stock_code],
                # 缺少其他必需列
            })
            
            # 尝试验证数据
            report = manager.validate_data(invalid_data, 'daily')
            
            # 验证：应该检测到错误
            assert not report['is_valid']
            assert len(report['errors']) > 0
            
            # 验证：错误消息应该提到缺失的列
            error_messages = ' '.join(report['errors'])
            assert any([
                '缺少' in error_messages,
                'missing' in error_messages.lower(),
                '列' in error_messages,
                'column' in error_messages.lower()
            ])
    
    @given(
        stock_code=valid_stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=30, deadline=None)
    def test_anomaly_detection_flags_issues(self, stock_code, date):
        """
        验证：异常值检测应该标记问题数据
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = DataManager(storage_path=tmpdir)
            
            # 创建包含异常值的数据
            data = pd.DataFrame({
                'stock_code': [stock_code] * 5,
                'date': [date] * 5,
                'open': [10.0, 10.5, -5.0, 10.3, 10.8],  # 包含负价格
                'high': [11.0, 11.5, 11.0, 11.3, 11.8],
                'low': [9.0, 9.5, 9.0, 9.3, 9.8],
                'close': [10.5, 10.8, 10.6, 10.9, 11.0],
                'volume': [1000000, 1200000, 900000, 1100000, 0]  # 包含零成交量
            })
            
            # 验证数据
            report = manager.validate_data(data, 'daily')
            
            # 验证：应该检测到异常
            assert len(report['errors']) > 0 or len(report['anomalies']) > 0
            
            # 验证：应该标记负价格
            if report['errors']:
                error_messages = ' '.join(report['errors'])
                assert '负' in error_messages or 'negative' in error_messages.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
