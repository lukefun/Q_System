"""
数据获取器单元测试

测试DataRetriever类的基本功能和错误处理
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch
from src.data_retriever import DataRetriever
from config import DataError, ValidationError, ConnectionError


class TestDataRetrieverInit:
    """测试DataRetriever初始化"""
    
    def test_init_with_valid_client(self, mock_xtdata_client):
        """测试使用有效客户端初始化"""
        retriever = DataRetriever(mock_xtdata_client)
        
        assert retriever.client == mock_xtdata_client
        assert retriever.rate_limit_delay > 0
        assert retriever.batch_size > 0
    
    def test_init_with_none_client(self):
        """测试使用None客户端初始化应该失败"""
        with pytest.raises(ValueError, match="XtDataClient不能为None"):
            DataRetriever(None)


class TestStockCodeValidation:
    """测试股票代码验证"""
    
    def test_valid_stock_codes(self, mock_xtdata_client):
        """测试有效的股票代码"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 不应该抛出异常
        retriever._validate_stock_codes(['000001.SZ'])
        retriever._validate_stock_codes(['600000.SH'])
        retriever._validate_stock_codes(['000001.SZ', '600000.SH'])
    
    def test_empty_stock_codes(self, mock_xtdata_client):
        """测试空股票代码列表"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="股票代码列表不能为空"):
            retriever._validate_stock_codes([])
    
    def test_invalid_stock_code_format(self, mock_xtdata_client):
        """测试无效的股票代码格式"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 缺少市场代码
        with pytest.raises(ValueError, match="无效的股票代码格式"):
            retriever._validate_stock_codes(['000001'])
        
        # 股票代码不是6位数字
        with pytest.raises(ValueError, match="无效的股票代码"):
            retriever._validate_stock_codes(['00001.SZ'])
        
        # 无效的市场代码
        with pytest.raises(ValueError, match="无效的市场代码"):
            retriever._validate_stock_codes(['000001.XX'])


class TestDateValidation:
    """测试日期验证"""
    
    def test_valid_date_range(self, mock_xtdata_client):
        """测试有效的日期范围"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 不应该抛出异常
        retriever._validate_date_range('20240101', '20240110')
    
    def test_invalid_date_format(self, mock_xtdata_client):
        """测试无效的日期格式"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的开始日期格式"):
            retriever._validate_date_range('2024-01-01', '20240110')
        
        with pytest.raises(ValueError, match="无效的结束日期格式"):
            retriever._validate_date_range('20240101', '2024-01-10')
    
    def test_start_date_after_end_date(self, mock_xtdata_client):
        """测试开始日期晚于结束日期"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="开始日期.*不能晚于结束日期"):
            retriever._validate_date_range('20240110', '20240101')
    
    def test_future_date(self, mock_xtdata_client):
        """测试未来日期"""
        retriever = DataRetriever(mock_xtdata_client)
        
        future_date = datetime.now().strftime('%Y%m%d')
        # 使用明年的日期
        future_year = str(int(future_date[:4]) + 1)
        future_date = future_year + future_date[4:]
        
        with pytest.raises(ValueError, match="不能是未来日期"):
            retriever._validate_date_range('20240101', future_date)


class TestPeriodValidation:
    """测试周期验证"""
    
    def test_valid_periods(self, mock_xtdata_client):
        """测试有效的数据周期"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 不应该抛出异常
        retriever._validate_period('tick')
        retriever._validate_period('1d')
    
    def test_invalid_period(self, mock_xtdata_client):
        """测试无效的数据周期"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的数据周期"):
            retriever._validate_period('5m')
        
        with pytest.raises(ValueError, match="无效的数据周期"):
            retriever._validate_period('1h')


class TestAdjustTypeValidation:
    """测试复权类型验证"""
    
    def test_valid_adjust_types(self, mock_xtdata_client):
        """测试有效的复权类型"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 不应该抛出异常
        retriever._validate_adjust_type('none')
        retriever._validate_adjust_type('front')
        retriever._validate_adjust_type('back')
    
    def test_invalid_adjust_type(self, mock_xtdata_client):
        """测试无效的复权类型"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的复权类型"):
            retriever._validate_adjust_type('invalid')


class TestDownloadHistoryData:
    """测试历史数据下载"""
    
    def test_download_with_disconnected_client(self, mock_xtdata_client):
        """测试客户端未连接时下载数据"""
        mock_xtdata_client.is_connected.return_value = False
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ConnectionError, match="XtData客户端未连接"):
            retriever.download_history_data(
                stock_codes=['000001.SZ'],
                start_date='20240101',
                end_date='20240110'
            )
    
    def test_download_daily_data(self, mock_xtdata_client):
        """测试下载日线数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        data = retriever.download_history_data(
            stock_codes=['000001.SZ'],
            start_date='20240101',
            end_date='20240105',
            period='1d'
        )
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert 'stock_code' in data.columns
        assert 'date' in data.columns
        assert 'open' in data.columns
        assert 'high' in data.columns
        assert 'low' in data.columns
        assert 'close' in data.columns
        assert 'volume' in data.columns
    
    def test_download_tick_data(self, mock_xtdata_client):
        """测试下载tick数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        data = retriever.download_history_data(
            stock_codes=['000001.SZ'],
            start_date='20240101',
            end_date='20240101',
            period='tick'
        )
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert 'stock_code' in data.columns
        assert 'timestamp' in data.columns
        assert 'price' in data.columns
    
    def test_download_multiple_stocks(self, mock_xtdata_client):
        """测试下载多只股票数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date='20240101',
            end_date='20240105',
            period='1d'
        )
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        
        # 验证所有股票都有数据
        returned_codes = data['stock_code'].unique()
        assert len(returned_codes) == len(stock_codes)
    
    def test_download_with_invalid_parameters(self, mock_xtdata_client):
        """测试使用无效参数下载数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        # 无效的股票代码
        with pytest.raises(ValueError):
            retriever.download_history_data(
                stock_codes=['invalid'],
                start_date='20240101',
                end_date='20240110'
            )
        
        # 无效的日期范围
        with pytest.raises(ValueError):
            retriever.download_history_data(
                stock_codes=['000001.SZ'],
                start_date='20240110',
                end_date='20240101'
            )
        
        # 无效的周期
        with pytest.raises(ValueError):
            retriever.download_history_data(
                stock_codes=['000001.SZ'],
                start_date='20240101',
                end_date='20240110',
                period='invalid'
            )


class TestGetMarketData:
    """测试市场快照数据获取"""
    
    def test_get_market_data_with_disconnected_client(self, mock_xtdata_client):
        """测试客户端未连接时获取快照数据"""
        mock_xtdata_client.is_connected.return_value = False
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ConnectionError, match="XtData客户端未连接"):
            retriever.get_market_data(['000001.SZ'])
    
    def test_get_market_data_single_stock(self, mock_xtdata_client):
        """测试获取单只股票快照数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        data = retriever.get_market_data(['000001.SZ'])
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) == 1
        assert 'stock_code' in data.columns
        assert 'timestamp' in data.columns
        assert 'last_price' in data.columns
    
    def test_get_market_data_multiple_stocks(self, mock_xtdata_client):
        """测试获取多只股票快照数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        data = retriever.get_market_data(stock_codes)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == len(stock_codes)
        
        # 验证所有股票都有数据
        returned_codes = set(data['stock_code'].tolist())
        assert returned_codes == set(stock_codes)
    
    def test_get_market_data_with_invalid_codes(self, mock_xtdata_client):
        """测试使用无效股票代码获取快照数据"""
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ValueError):
            retriever.get_market_data(['invalid'])


class TestGetAllStockCodes:
    """测试获取所有股票代码"""
    
    def test_get_all_stock_codes_with_disconnected_client(self, mock_xtdata_client):
        """测试客户端未连接时获取股票代码列表"""
        mock_xtdata_client.is_connected.return_value = False
        retriever = DataRetriever(mock_xtdata_client)
        
        with pytest.raises(ConnectionError, match="XtData客户端未连接"):
            retriever.get_all_stock_codes()
    
    def test_get_all_stock_codes(self, mock_xtdata_client):
        """测试获取所有股票代码"""
        retriever = DataRetriever(mock_xtdata_client)
        
        codes = retriever.get_all_stock_codes()
        
        assert isinstance(codes, list)
        assert len(codes) > 0
        
        # 验证返回的都是有效的股票代码格式
        for code in codes:
            assert isinstance(code, str)
            assert '.' in code
            parts = code.split('.')
            assert len(parts) == 2
            assert parts[1] in ['SZ', 'SH']
