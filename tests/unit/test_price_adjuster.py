"""
单元测试：价格复权处理器

测试PriceAdjuster类的基本功能和边缘情况
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock
from src.price_adjuster import PriceAdjuster
from src.xtdata_client import XtDataClient
from config import DataError, ValidationError


class TestPriceAdjusterInit:
    """测试PriceAdjuster初始化"""
    
    def test_init_with_valid_client(self, mock_xtdata_client):
        """测试使用有效客户端初始化"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        assert adjuster.client == mock_xtdata_client
    
    def test_init_with_none_client(self):
        """测试使用None客户端初始化应该失败"""
        with pytest.raises(ValueError, match="XtDataClient不能为None"):
            PriceAdjuster(None)


class TestGetAdjustFactors:
    """测试获取复权因子"""
    
    def test_get_adjust_factors_basic(self, mock_xtdata_client):
        """测试基本的复权因子获取"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        factors = adjuster.get_adjust_factors(
            '000001.SZ',
            '20240101',
            '20240105'
        )
        
        assert factors is not None
        assert isinstance(factors, pd.DataFrame)
        assert 'date' in factors.columns
        assert 'adjust_factor' in factors.columns
        assert len(factors) > 0
    
    def test_get_adjust_factors_invalid_stock_code(self, mock_xtdata_client):
        """测试无效股票代码"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的股票代码"):
            adjuster.get_adjust_factors('INVALID', '20240101', '20240105')
    
    def test_get_adjust_factors_invalid_date_format(self, mock_xtdata_client):
        """测试无效日期格式"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的开始日期格式"):
            adjuster.get_adjust_factors('000001.SZ', '2024-01-01', '20240105')
    
    def test_get_adjust_factors_date_range_reversed(self, mock_xtdata_client):
        """测试日期范围颠倒"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="不能晚于结束日期"):
            adjuster.get_adjust_factors('000001.SZ', '20240105', '20240101')
    
    def test_get_adjust_factors_client_not_connected(self):
        """测试客户端未连接时获取复权因子"""
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        factors = adjuster.get_adjust_factors(
            '000001.SZ',
            '20240101',
            '20240105'
        )
        
        # 应该返回None而不是抛出异常
        assert factors is None


class TestForwardAdjust:
    """测试前复权"""
    
    def test_forward_adjust_basic(self, mock_xtdata_client, sample_price_data):
        """测试基本的前复权功能"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_price_data)
        assert all(col in result.columns for col in ['date', 'open', 'high', 'low', 'close', 'volume'])
    
    def test_forward_adjust_preserves_ohlc_relationships(self, mock_xtdata_client, sample_price_data):
        """测试前复权保持OHLC关系"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证 high >= max(open, close) >= min(open, close) >= low
        for idx, row in result.iterrows():
            assert row['high'] >= row['open'] - 0.01, f"行 {idx}: high < open"
            assert row['high'] >= row['close'] - 0.01, f"行 {idx}: high < close"
            assert row['low'] <= row['open'] + 0.01, f"行 {idx}: low > open"
            assert row['low'] <= row['close'] + 0.01, f"行 {idx}: low > close"
    
    def test_forward_adjust_empty_data(self, mock_xtdata_client):
        """测试空数据的前复权"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        empty_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        result = adjuster.forward_adjust(empty_data, '000001.SZ')
        
        assert len(result) == 0
    
    def test_forward_adjust_missing_columns(self, mock_xtdata_client):
        """测试缺少必需列的数据"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        invalid_data = pd.DataFrame({
            'date': ['20240101'],
            'close': [10.0]
            # 缺少 open, high, low, volume
        })
        
        with pytest.raises(ValueError, match="数据缺少必需的列"):
            adjuster.forward_adjust(invalid_data, '000001.SZ')
    
    def test_forward_adjust_invalid_data_type(self, mock_xtdata_client):
        """测试无效的数据类型"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="数据必须是pandas DataFrame类型"):
            adjuster.forward_adjust("not a dataframe", '000001.SZ')
    
    def test_forward_adjust_none_data(self, mock_xtdata_client):
        """测试None数据"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="数据不能为None"):
            adjuster.forward_adjust(None, '000001.SZ')


class TestBackwardAdjust:
    """测试后复权"""
    
    def test_backward_adjust_basic(self, mock_xtdata_client, sample_price_data):
        """测试基本的后复权功能"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_price_data)
        assert all(col in result.columns for col in ['date', 'open', 'high', 'low', 'close', 'volume'])
    
    def test_backward_adjust_preserves_latest_price(self, mock_xtdata_client, sample_price_data):
        """测试后复权保持最新价格不变"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        original_latest_close = sample_price_data.iloc[-1]['close']
        result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        adjusted_latest_close = result.iloc[-1]['close']
        
        # 最新收盘价应该保持不变（允许小的浮点误差）
        assert abs(adjusted_latest_close - original_latest_close) < 0.01
    
    def test_backward_adjust_preserves_ohlc_relationships(self, mock_xtdata_client, sample_price_data):
        """测试后复权保持OHLC关系"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        
        # 验证 high >= max(open, close) >= min(open, close) >= low
        for idx, row in result.iterrows():
            assert row['high'] >= row['open'] - 0.01, f"行 {idx}: high < open"
            assert row['high'] >= row['close'] - 0.01, f"行 {idx}: high < close"
            assert row['low'] <= row['open'] + 0.01, f"行 {idx}: low > open"
            assert row['low'] <= row['close'] + 0.01, f"行 {idx}: low > close"
    
    def test_backward_adjust_empty_data(self, mock_xtdata_client):
        """测试空数据的后复权"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        empty_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        result = adjuster.backward_adjust(empty_data, '000001.SZ')
        
        assert len(result) == 0


class TestAdjustmentWithMissingFactors:
    """测试复权因子缺失时的处理"""
    
    def test_forward_adjust_with_no_factors(self, sample_price_data):
        """测试没有复权因子时的前复权"""
        # 创建一个未连接的客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 应该返回原始数据并记录警告
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 数据应该保持不变
        pd.testing.assert_frame_equal(result, sample_price_data)
    
    def test_backward_adjust_with_no_factors(self, sample_price_data):
        """测试没有复权因子时的后复权"""
        # 创建一个未连接的客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 应该返回原始数据并记录警告
        result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        
        # 数据应该保持不变
        pd.testing.assert_frame_equal(result, sample_price_data)


class TestDataValidation:
    """测试数据验证"""
    
    def test_validate_invalid_ohlc_relationships(self, mock_xtdata_client):
        """测试OHLC关系异常的数据（应该发出警告但不失败）"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        # 创建OHLC关系异常的数据
        invalid_data = pd.DataFrame({
            'date': ['20240101', '20240102'],
            'open': [10.0, 10.5],
            'high': [9.0, 10.0],  # high < open，异常
            'low': [8.0, 9.5],
            'close': [9.5, 10.3],
            'volume': [1000000, 1200000]
        })
        
        # 应该发出警告但不抛出异常
        result = adjuster.forward_adjust(invalid_data, '000001.SZ')
        assert isinstance(result, pd.DataFrame)


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_single_row_data(self, mock_xtdata_client):
        """测试单行数据"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        single_row = pd.DataFrame({
            'date': ['20240101'],
            'open': [10.0],
            'high': [10.5],
            'low': [9.5],
            'close': [10.2],
            'volume': [1000000]
        })
        
        result = adjuster.forward_adjust(single_row, '000001.SZ')
        assert len(result) == 1
    
    def test_unsorted_data(self, mock_xtdata_client):
        """测试未排序的数据（应该自动排序）"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        unsorted_data = pd.DataFrame({
            'date': ['20240103', '20240101', '20240102'],
            'open': [10.3, 10.0, 10.5],
            'high': [10.7, 10.8, 10.9],
            'low': [10.0, 9.8, 10.2],
            'close': [10.6, 10.5, 10.3],
            'volume': [900000, 1000000, 1200000]
        })
        
        result = adjuster.forward_adjust(unsorted_data, '000001.SZ')
        
        # 验证结果已排序
        assert result['date'].tolist() == ['20240101', '20240102', '20240103']
    
    def test_data_with_existing_adjust_factor_column(self, mock_xtdata_client):
        """测试已包含复权因子列的数据"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        data_with_factor = pd.DataFrame({
            'date': ['20240101', '20240102'],
            'open': [10.0, 10.5],
            'high': [10.8, 10.9],
            'low': [9.8, 10.2],
            'close': [10.5, 10.3],
            'volume': [1000000, 1200000],
            'adjust_factor': [1.0, 1.0]  # 已有复权因子列
        })
        
        result = adjuster.forward_adjust(data_with_factor, '000001.SZ')
        
        # 应该保留复权因子列
        assert 'adjust_factor' in result.columns


class TestDefaultAdjustmentType:
    """
    测试默认复权类型
    
    需求2.3: WHEN 处理回测数据时，THE 复权处理器 SHALL 默认使用前复权以避免未来函数
    """
    
    def test_default_adjust_type_is_forward(self):
        """测试系统默认复权类型为前复权"""
        from config import DEFAULT_ADJUST_TYPE
        
        # 验证默认复权类型是前复权（front）
        assert DEFAULT_ADJUST_TYPE == "front", \
            "默认复权类型应该是'front'（前复权），以避免回测中的未来函数"
    
    def test_forward_adjust_recommended_for_backtesting(self, mock_xtdata_client, sample_price_data):
        """
        测试前复权适用于回测场景
        
        前复权保持当前价格不变，向前调整历史价格，确保在任何历史时点
        都不会使用未来信息，这是回测的标准做法。
        """
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        # 执行前复权
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证前复权成功执行
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_price_data)
        
        # 验证OHLC关系保持正确（这是避免未来函数的关键）
        for idx, row in result.iterrows():
            assert row['high'] >= row['open'] - 0.01
            assert row['high'] >= row['close'] - 0.01
            assert row['low'] <= row['open'] + 0.01
            assert row['low'] <= row['close'] + 0.01
    
    def test_forward_adjust_docstring_mentions_backtesting(self, mock_xtdata_client):
        """测试前复权方法的文档字符串明确说明用于回测"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        # 获取forward_adjust方法的文档字符串
        docstring = adjuster.forward_adjust.__doc__
        
        # 验证文档字符串提到回测和未来函数
        assert docstring is not None
        assert '回测' in docstring or 'backtest' in docstring.lower(), \
            "前复权方法的文档应该说明其用于回测场景"
        assert '未来函数' in docstring or 'lookahead' in docstring.lower() or 'future' in docstring.lower(), \
            "前复权方法的文档应该说明其避免未来函数"
    
    def test_backward_adjust_not_recommended_for_backtesting(self, mock_xtdata_client):
        """测试后复权方法的文档字符串说明不适合回测"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        
        # 获取backward_adjust方法的文档字符串
        docstring = adjuster.backward_adjust.__doc__
        
        # 验证文档字符串说明后复权不适合回测
        assert docstring is not None
        assert '不适合' in docstring or '不适用' in docstring or 'not suitable' in docstring.lower(), \
            "后复权方法的文档应该说明其不适合回测场景"


class TestAdjustmentFactorMissingEdgeCases:
    """
    测试复权因子缺失的边缘情况
    
    需求2.6: WHEN 复权因子不可用时，THE 复权处理器 SHALL 返回未复权数据并发出警告
    """
    
    def test_forward_adjust_returns_original_data_when_no_factors(self, sample_price_data):
        """
        测试前复权在没有复权因子时返回原始数据
        
        当复权因子不可用时，系统应该返回未复权的原始数据，
        而不是抛出异常或返回错误数据。
        """
        # 创建一个未连接的客户端（模拟无法获取复权因子）
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 执行前复权
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证返回的是原始数据（未复权）
        pd.testing.assert_frame_equal(result, sample_price_data)
    
    def test_backward_adjust_returns_original_data_when_no_factors(self, sample_price_data):
        """
        测试后复权在没有复权因子时返回原始数据
        
        当复权因子不可用时，系统应该返回未复权的原始数据。
        """
        # 创建一个未连接的客户端（模拟无法获取复权因子）
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 执行后复权
        result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        
        # 验证返回的是原始数据（未复权）
        pd.testing.assert_frame_equal(result, sample_price_data)
    
    def test_forward_adjust_logs_warning_when_no_factors(self, sample_price_data, caplog):
        """
        测试前复权在没有复权因子时记录警告日志
        
        系统应该发出警告，告知用户返回的是未复权数据。
        """
        import logging
        
        # 创建一个未连接的客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 设置日志级别以捕获警告
        with caplog.at_level(logging.WARNING):
            result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证记录了警告日志
        assert any('没有复权因子' in record.message for record in caplog.records), \
            "应该记录警告日志，说明没有复权因子数据"
        assert any('返回未复权数据' in record.message for record in caplog.records), \
            "应该记录警告日志，说明返回未复权数据"
    
    def test_backward_adjust_logs_warning_when_no_factors(self, sample_price_data, caplog):
        """
        测试后复权在没有复权因子时记录警告日志
        """
        import logging
        
        # 创建一个未连接的客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 设置日志级别以捕获警告
        with caplog.at_level(logging.WARNING):
            result = adjuster.backward_adjust(sample_price_data, '000001.SZ')
        
        # 验证记录了警告日志
        assert any('没有复权因子' in record.message for record in caplog.records), \
            "应该记录警告日志，说明没有复权因子数据"
    
    def test_adjust_with_empty_factors_dataframe(self, sample_price_data):
        """
        测试复权因子为空DataFrame时的处理
        
        当get_adjust_factors返回空DataFrame时，应该返回原始数据。
        """
        # 创建一个mock客户端，返回空的复权因子
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors返回空DataFrame
        adjuster.get_adjust_factors = Mock(return_value=pd.DataFrame())
        
        # 执行前复权
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证返回原始数据
        pd.testing.assert_frame_equal(result, sample_price_data)
    
    def test_adjust_with_none_factors(self, sample_price_data):
        """
        测试复权因子为None时的处理
        
        当get_adjust_factors返回None时，应该返回原始数据。
        """
        # 创建一个mock客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        adjuster = PriceAdjuster(mock_client)
        
        # Mock get_adjust_factors返回None
        adjuster.get_adjust_factors = Mock(return_value=None)
        
        # 执行前复权
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证返回原始数据
        pd.testing.assert_frame_equal(result, sample_price_data)
    
    def test_adjust_preserves_data_integrity_when_no_factors(self, sample_price_data):
        """
        测试没有复权因子时数据完整性保持不变
        
        返回的未复权数据应该与原始数据完全一致，包括所有列和数据类型。
        """
        # 创建一个未连接的客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = False
        
        adjuster = PriceAdjuster(mock_client)
        
        # 执行前复权
        result = adjuster.forward_adjust(sample_price_data, '000001.SZ')
        
        # 验证数据完整性
        assert list(result.columns) == list(sample_price_data.columns), \
            "返回的数据应该包含所有原始列"
        assert len(result) == len(sample_price_data), \
            "返回的数据行数应该与原始数据相同"
        assert result.dtypes.equals(sample_price_data.dtypes), \
            "返回的数据类型应该与原始数据相同"
        
        # 验证数据值完全相同
        pd.testing.assert_frame_equal(result, sample_price_data)


class TestRepr:
    """测试字符串表示"""
    
    def test_repr(self, mock_xtdata_client):
        """测试__repr__方法"""
        adjuster = PriceAdjuster(mock_xtdata_client)
        repr_str = repr(adjuster)
        
        assert 'PriceAdjuster' in repr_str
        assert 'client=' in repr_str
