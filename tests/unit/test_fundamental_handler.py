"""
基本面数据处理器单元测试

测试FundamentalHandler类的核心功能
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.fundamental_handler import FundamentalHandler
from src.xtdata_client import XtDataClient


class TestFundamentalHandlerInit:
    """测试FundamentalHandler初始化"""
    
    def test_init_with_valid_client(self, mock_xtdata_client):
        """测试使用有效客户端初始化"""
        handler = FundamentalHandler(mock_xtdata_client)
        assert handler.client == mock_xtdata_client
    
    def test_init_with_none_client(self):
        """测试使用None客户端初始化应该失败"""
        with pytest.raises(ValueError, match="XtDataClient不能为None"):
            FundamentalHandler(None)


class TestGetFinancialData:
    """测试get_financial_data方法"""
    
    def test_get_financial_data_basic(self, mock_xtdata_client):
        """测试基本的财务数据获取"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        data = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe', 'pb', 'roe'],
            as_of_date='20240430'
        )
        
        # 验证返回的是DataFrame
        assert isinstance(data, pd.DataFrame)
        
        # 验证包含必需的列
        assert 'stock_code' in data.columns
        assert 'report_date' in data.columns
        assert 'announce_date' in data.columns
        
        # 验证包含请求的指标
        assert 'pe' in data.columns
        assert 'pb' in data.columns
        assert 'roe' in data.columns
    
    def test_get_financial_data_time_point_correctness(self, mock_xtdata_client):
        """测试时间点正确性：只返回as_of_date之前公告的数据"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 使用较早的日期，应该返回更少的数据
        data_early = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe'],
            as_of_date='20230501'  # 只能看到4月30日之前公告的数据
        )
        
        # 使用较晚的日期，应该返回更多的数据
        data_late = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe'],
            as_of_date='20240430'  # 可以看到更多公告的数据
        )
        
        # 验证所有公告日期都在as_of_date之前
        if not data_early.empty:
            for announce_date in data_early['announce_date']:
                assert announce_date <= '20230501'
        
        if not data_late.empty:
            for announce_date in data_late['announce_date']:
                assert announce_date <= '20240430'
    
    def test_get_financial_data_multiple_stocks(self, mock_xtdata_client):
        """测试获取多只股票的财务数据"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        data = handler.get_financial_data(
            stock_codes=stock_codes,
            indicators=['pe', 'pb'],
            as_of_date='20240430'
        )
        
        # 验证返回的股票代码
        if not data.empty:
            returned_codes = data['stock_code'].unique()
            # 至少应该有一些股票的数据
            assert len(returned_codes) > 0
    
    def test_get_financial_data_invalid_stock_code(self, mock_xtdata_client):
        """测试无效股票代码应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的股票代码"):
            handler.get_financial_data(
                stock_codes=['INVALID'],
                indicators=['pe'],
                as_of_date='20240430'
            )
    
    def test_get_financial_data_invalid_indicator(self, mock_xtdata_client):
        """测试无效指标应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="不支持的指标"):
            handler.get_financial_data(
                stock_codes=['000001.SZ'],
                indicators=['invalid_indicator'],
                as_of_date='20240430'
            )
    
    def test_get_financial_data_invalid_date(self, mock_xtdata_client):
        """测试无效日期格式应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的日期格式"):
            handler.get_financial_data(
                stock_codes=['000001.SZ'],
                indicators=['pe'],
                as_of_date='2024-04-30'  # 错误格式
            )
    
    def test_get_financial_data_empty_stock_codes(self, mock_xtdata_client):
        """测试空股票代码列表应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="股票代码列表不能为空"):
            handler.get_financial_data(
                stock_codes=[],
                indicators=['pe'],
                as_of_date='20240430'
            )
    
    def test_get_financial_data_empty_indicators(self, mock_xtdata_client):
        """测试空指标列表应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="指标列表不能为空"):
            handler.get_financial_data(
                stock_codes=['000001.SZ'],
                indicators=[],
                as_of_date='20240430'
            )


class TestCalculatePERatio:
    """测试calculate_pe_ratio方法"""
    
    def test_calculate_pe_ratio_basic(self, mock_xtdata_client):
        """测试基本的PE比率计算"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 准备价格数据
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ', '000001.SZ'],
            'date': ['20240429', '20240430'],
            'close': [10.5, 10.8]
        })
        
        pe = handler.calculate_pe_ratio(
            stock_code='000001.SZ',
            date='20240430',
            price_data=price_data
        )
        
        # PE应该是一个正数（如果数据可用）
        if pe is not None:
            assert isinstance(pe, (int, float))
            assert pe > 0
    
    def test_calculate_pe_ratio_missing_price_data(self, mock_xtdata_client):
        """测试缺失价格数据应该返回None"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 价格数据中没有指定日期
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240429'],
            'close': [10.5]
        })
        
        pe = handler.calculate_pe_ratio(
            stock_code='000001.SZ',
            date='20240430',  # 这个日期不在price_data中
            price_data=price_data
        )
        
        # 应该返回None而不是抛出异常
        assert pe is None
    
    def test_calculate_pe_ratio_invalid_stock_code(self, mock_xtdata_client):
        """测试无效股票代码应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240430'],
            'close': [10.5]
        })
        
        with pytest.raises(ValueError, match="无效的股票代码"):
            handler.calculate_pe_ratio(
                stock_code='INVALID',
                date='20240430',
                price_data=price_data
            )
    
    def test_calculate_pe_ratio_invalid_price_data(self, mock_xtdata_client):
        """测试无效价格数据应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 缺少必需的列
        invalid_price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240430']
            # 缺少close列
        })
        
        with pytest.raises(ValueError, match="价格数据缺少必需的列"):
            handler.calculate_pe_ratio(
                stock_code='000001.SZ',
                date='20240430',
                price_data=invalid_price_data
            )


class TestCalculatePBRatio:
    """测试calculate_pb_ratio方法"""
    
    def test_calculate_pb_ratio_basic(self, mock_xtdata_client):
        """测试基本的PB比率计算"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 准备价格数据
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ', '000001.SZ'],
            'date': ['20240429', '20240430'],
            'close': [10.5, 10.8]
        })
        
        pb = handler.calculate_pb_ratio(
            stock_code='000001.SZ',
            date='20240430',
            price_data=price_data
        )
        
        # PB应该是一个正数（如果数据可用）
        if pb is not None:
            assert isinstance(pb, (int, float))
            assert pb > 0
    
    def test_calculate_pb_ratio_missing_price_data(self, mock_xtdata_client):
        """测试缺失价格数据应该返回None"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 价格数据中没有指定日期
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240429'],
            'close': [10.5]
        })
        
        pb = handler.calculate_pb_ratio(
            stock_code='000001.SZ',
            date='20240430',  # 这个日期不在price_data中
            price_data=price_data
        )
        
        # 应该返回None而不是抛出异常
        assert pb is None
    
    def test_calculate_pb_ratio_invalid_stock_code(self, mock_xtdata_client):
        """测试无效股票代码应该抛出异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240430'],
            'close': [10.5]
        })
        
        with pytest.raises(ValueError, match="无效的股票代码"):
            handler.calculate_pb_ratio(
                stock_code='INVALID',
                date='20240430',
                price_data=price_data
            )


class TestValidationMethods:
    """测试验证方法"""
    
    def test_validate_stock_code_valid(self, mock_xtdata_client):
        """测试有效股票代码验证"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 这些应该不抛出异常
        handler._validate_stock_code('000001.SZ')
        handler._validate_stock_code('600000.SH')
        handler._validate_stock_code('000002.SZ')
    
    def test_validate_stock_code_invalid_format(self, mock_xtdata_client):
        """测试无效格式的股票代码"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        invalid_codes = [
            '',  # 空字符串
            '000001',  # 缺少市场代码
            '000001.XX',  # 无效市场代码
            '00001.SZ',  # 股票代码不是6位
            'ABCDEF.SZ',  # 股票代码不是数字
        ]
        
        for code in invalid_codes:
            with pytest.raises(ValueError):
                handler._validate_stock_code(code)
    
    def test_validate_indicators_valid(self, mock_xtdata_client):
        """测试有效指标验证"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 这些应该不抛出异常
        handler._validate_indicators(['pe'])
        handler._validate_indicators(['pe', 'pb'])
        handler._validate_indicators(['pe', 'pb', 'roe'])
        handler._validate_indicators(['revenue', 'net_profit'])
    
    def test_validate_indicators_invalid(self, mock_xtdata_client):
        """测试无效指标"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="不支持的指标"):
            handler._validate_indicators(['invalid_indicator'])
    
    def test_validate_date_valid(self, mock_xtdata_client):
        """测试有效日期验证"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 这些应该不抛出异常
        handler._validate_date('20240430')
        handler._validate_date('20231231')
        handler._validate_date('20240101')
    
    def test_validate_date_invalid_format(self, mock_xtdata_client):
        """测试无效日期格式"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        invalid_dates = [
            '',  # 空字符串
            '2024-04-30',  # 错误格式
            '20240431',  # 无效日期（4月没有31日）
            'abcd1234',  # 非数字
        ]
        
        for date in invalid_dates:
            with pytest.raises(ValueError):
                handler._validate_date(date)


class TestGracefulErrorHandling:
    """测试优雅的错误处理"""
    
    def test_missing_financial_data_returns_none(self, mock_xtdata_client):
        """测试缺失财务数据时返回None而非异常"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20200101'],  # 很早的日期，可能没有财务数据
            'close': [10.5]
        })
        
        # 应该返回None而不是抛出异常
        pe = handler.calculate_pe_ratio(
            stock_code='000001.SZ',
            date='20200101',
            price_data=price_data
        )
        
        # 可能返回None（如果没有数据）或一个有效值
        assert pe is None or isinstance(pe, (int, float))
    
    def test_empty_result_returns_empty_dataframe(self, mock_xtdata_client):
        """测试没有数据时返回空DataFrame"""
        handler = FundamentalHandler(mock_xtdata_client)
        
        # 使用很早的日期，可能没有任何公告数据
        data = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe'],
            as_of_date='20000101'
        )
        
        # 应该返回空DataFrame而不是抛出异常
        assert isinstance(data, pd.DataFrame)
