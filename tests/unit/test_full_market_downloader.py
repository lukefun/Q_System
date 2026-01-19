"""
FullMarketDownloader单元测试

测试全市场数据下载器的功能，包括断点续传、进度报告和汇总统计
"""

import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from src.full_market_downloader import FullMarketDownloader, download_full_market
from config import DataError, ValidationError


class TestFullMarketDownloaderInit:
    """测试FullMarketDownloader初始化"""
    
    def test_init_with_valid_params(self, tmp_path):
        """测试使用有效参数初始化"""
        mock_retriever = Mock()
        mock_manager = Mock()
        
        downloader = FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager,
            state_file=tmp_path / "state.json"
        )
        
        assert downloader.retriever == mock_retriever
        assert downloader.data_manager == mock_manager
        assert downloader.state_file == tmp_path / "state.json"
    
    def test_init_with_none_retriever(self):
        """测试retriever为None时抛出异常"""
        mock_manager = Mock()
        
        with pytest.raises(ValueError, match="retriever不能为None"):
            FullMarketDownloader(
                retriever=None,
                data_manager=mock_manager
            )
    
    def test_init_with_none_manager(self):
        """测试data_manager为None时抛出异常"""
        mock_retriever = Mock()
        
        with pytest.raises(ValueError, match="data_manager不能为None"):
            FullMarketDownloader(
                retriever=mock_retriever,
                data_manager=None
            )
    
    def test_init_with_default_state_file(self):
        """测试使用默认状态文件路径"""
        mock_retriever = Mock()
        mock_manager = Mock()
        
        downloader = FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager
        )
        
        assert downloader.state_file is not None
        assert downloader.state_file.name == "download_state.json"


class TestFullMarketDownloaderStateManagement:
    """测试状态管理功能"""
    
    @pytest.fixture
    def downloader(self, tmp_path):
        """创建临时FullMarketDownloader实例"""
        mock_retriever = Mock()
        mock_manager = Mock()
        
        return FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager,
            state_file=tmp_path / "state.json"
        )
    
    def test_save_and_load_state(self, downloader):
        """测试保存和加载状态"""
        # 创建测试状态
        test_state = {
            'start_date': '20240101',
            'end_date': '20240110',
            'data_type': 'daily',
            'completed_stocks': ['000001.SZ', '000002.SZ'],
            'failed_stocks': []
        }
        
        # 保存状态
        downloader._save_state(test_state)
        
        # 验证文件已创建
        assert downloader.state_file.exists()
        
        # 加载状态
        loaded_state = downloader._load_state()
        
        # 验证状态一致性
        assert loaded_state['start_date'] == test_state['start_date']
        assert loaded_state['end_date'] == test_state['end_date']
        assert loaded_state['data_type'] == test_state['data_type']
        assert len(loaded_state['completed_stocks']) == 2
    
    def test_load_nonexistent_state(self, downloader):
        """测试加载不存在的状态文件"""
        # 确保状态文件不存在
        if downloader.state_file.exists():
            downloader.state_file.unlink()
        
        # 加载状态应返回空字典
        state = downloader._load_state()
        assert state == {}
    
    def test_clear_state(self, downloader):
        """测试清理状态文件"""
        # 创建状态文件
        test_state = {'test': 'data'}
        downloader._save_state(test_state)
        
        # 验证文件存在
        assert downloader.state_file.exists()
        
        # 清理状态
        downloader._clear_state()
        
        # 验证文件已删除
        assert not downloader.state_file.exists()
    
    def test_get_download_progress_no_state(self, downloader):
        """测试获取下载进度（无状态文件）"""
        # 确保状态文件不存在
        if downloader.state_file.exists():
            downloader.state_file.unlink()
        
        progress = downloader.get_download_progress()
        
        assert progress['is_downloading'] == False
        assert progress['completed_count'] == 0
        assert progress['failed_count'] == 0
    
    def test_get_download_progress_with_state(self, downloader):
        """测试获取下载进度（有状态文件）"""
        # 创建状态
        test_state = {
            'start_date': '20240101',
            'end_date': '20240110',
            'data_type': 'daily',
            'completed_stocks': ['000001.SZ', '000002.SZ', '000003.SZ'],
            'failed_stocks': [{'stock_code': '000004.SZ', 'error': 'test error'}]
        }
        downloader._save_state(test_state)
        
        progress = downloader.get_download_progress()
        
        assert progress['is_downloading'] == True
        assert progress['completed_count'] == 3
        assert progress['failed_count'] == 1
        assert progress['start_date'] == '20240101'
        assert progress['end_date'] == '20240110'
        assert progress['data_type'] == 'daily'


class TestFullMarketDownloaderDownload:
    """测试下载功能"""
    
    @pytest.fixture
    def mock_retriever(self):
        """创建mock retriever"""
        retriever = Mock()
        
        # Mock get_all_stock_codes
        retriever.get_all_stock_codes.return_value = [
            '000001.SZ',
            '000002.SZ',
            '000003.SZ'
        ]
        
        # Mock download_history_data
        def mock_download(stock_codes, start_date, end_date, period, adjust_type):
            # 返回模拟数据
            return pd.DataFrame({
                'stock_code': stock_codes * 5,
                'date': ['20240101', '20240102', '20240103', '20240104', '20240105'] * len(stock_codes),
                'close': [10.0, 10.5, 10.3, 10.8, 10.6] * len(stock_codes),
                'volume': [1000000] * 5 * len(stock_codes)
            })
        
        retriever.download_history_data.side_effect = mock_download
        
        return retriever
    
    @pytest.fixture
    def mock_manager(self):
        """创建mock data manager"""
        manager = Mock()
        
        # Mock save_market_data
        manager.save_market_data.return_value = None
        
        # Mock load_market_data
        def mock_load(data_type, stock_code, start_date=None, end_date=None):
            # 返回模拟数据
            return pd.DataFrame({
                'stock_code': [stock_code] * 5,
                'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
                'close': [10.0, 10.5, 10.3, 10.8, 10.6]
            })
        
        manager.load_market_data.side_effect = mock_load
        
        return manager
    
    @pytest.fixture
    def downloader(self, mock_retriever, mock_manager, tmp_path):
        """创建downloader实例"""
        return FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager,
            state_file=tmp_path / "state.json",
            rate_limit_delay=0.01  # 使用很短的延迟以加快测试
        )
    
    def test_download_full_market_success(self, downloader):
        """测试成功下载全市场数据"""
        # 执行下载
        stats = downloader.download_full_market(
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=False
        )
        
        # 验证统计信息
        assert stats['total_stocks'] == 3
        assert stats['success_count'] == 3
        assert stats['failed_count'] == 0
        assert stats['total_records'] == 15  # 3 stocks * 5 records
        assert stats['start_time'] is not None
        assert stats['end_time'] is not None
        assert stats['duration_seconds'] > 0
    
    def test_download_full_market_with_progress_callback(self, downloader):
        """测试带进度回调的下载"""
        # 创建进度回调
        progress_calls = []
        
        def progress_callback(current, total, stock_code):
            progress_calls.append((current, total, stock_code))
        
        # 执行下载
        stats = downloader.download_full_market(
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=False,
            progress_callback=progress_callback
        )
        
        # 验证进度回调被调用
        assert len(progress_calls) == 3  # 3只股票
        assert progress_calls[0] == (1, 3, '000001.SZ')
        assert progress_calls[1] == (2, 3, '000002.SZ')
        assert progress_calls[2] == (3, 3, '000003.SZ')
    
    def test_download_full_market_with_resume(self, downloader):
        """测试断点续传功能"""
        # 创建已完成部分股票的状态
        initial_state = {
            'start_date': '20240101',
            'end_date': '20240110',
            'data_type': 'daily',
            'completed_stocks': ['000001.SZ'],  # 第一只股票已完成
            'failed_stocks': []
        }
        downloader._save_state(initial_state)
        
        # 执行下载（resume=True）
        stats = downloader.download_full_market(
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=True
        )
        
        # 验证统计信息
        assert stats['total_stocks'] == 3
        assert stats['skipped_count'] == 1  # 跳过了已完成的股票
        assert stats['success_count'] == 2  # 只下载了剩余2只股票
        assert stats['failed_count'] == 0
    
    def test_download_full_market_with_failures(self, downloader, mock_retriever):
        """测试部分股票下载失败的情况"""
        # Mock download_history_data使第二只股票失败
        def mock_download_with_failure(stock_codes, start_date, end_date, period, adjust_type):
            if stock_codes[0] == '000002.SZ':
                raise Exception("模拟下载失败")
            
            return pd.DataFrame({
                'stock_code': stock_codes * 5,
                'date': ['20240101', '20240102', '20240103', '20240104', '20240105'] * len(stock_codes),
                'close': [10.0, 10.5, 10.3, 10.8, 10.6] * len(stock_codes),
                'volume': [1000000] * 5 * len(stock_codes)
            })
        
        mock_retriever.download_history_data.side_effect = mock_download_with_failure
        
        # 执行下载
        stats = downloader.download_full_market(
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=False
        )
        
        # 验证统计信息
        assert stats['total_stocks'] == 3
        assert stats['success_count'] == 2  # 2只成功
        assert stats['failed_count'] == 1  # 1只失败
        assert len(stats['failed_stocks']) == 1
        assert stats['failed_stocks'][0]['stock_code'] == '000002.SZ'
    
    def test_download_full_market_no_stocks(self, downloader, mock_retriever):
        """测试没有股票代码的情况"""
        # Mock get_all_stock_codes返回空列表
        mock_retriever.get_all_stock_codes.return_value = []
        
        # 执行下载
        stats = downloader.download_full_market(
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=False
        )
        
        # 验证统计信息
        assert stats['total_stocks'] == 0
        assert stats['success_count'] == 0
        assert stats['failed_count'] == 0


class TestFullMarketDownloaderValidation:
    """测试数据验证功能"""
    
    @pytest.fixture
    def downloader(self, tmp_path):
        """创建downloader实例"""
        mock_retriever = Mock()
        mock_manager = Mock()
        
        return FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager,
            state_file=tmp_path / "state.json"
        )
    
    def test_validate_downloaded_data(self, downloader):
        """测试数据完整性验证"""
        # Mock load_market_data
        def mock_load(data_type, stock_code):
            if stock_code == '000001.SZ':
                return pd.DataFrame({'data': [1, 2, 3]})
            elif stock_code == '000002.SZ':
                return pd.DataFrame()  # 空数据
            else:
                raise Exception("加载失败")
        
        downloader.data_manager.load_market_data.side_effect = mock_load
        
        # 执行验证
        stock_codes = ['000001.SZ', '000002.SZ', '000003.SZ']
        validation_result = downloader._validate_downloaded_data(
            stock_codes,
            'daily'
        )
        
        # 验证结果
        assert validation_result['total_stocks'] == 3
        assert validation_result['stocks_with_data'] == 1
        assert validation_result['stocks_without_data'] == 2
        assert '000002.SZ' in validation_result['missing_stocks']
        assert '000003.SZ' in validation_result['missing_stocks']


class TestDownloadFullMarketFunction:
    """测试便捷函数"""
    
    def test_download_full_market_function(self, tmp_path):
        """测试download_full_market便捷函数"""
        # 创建mock对象
        mock_retriever = Mock()
        mock_manager = Mock()
        
        # Mock get_all_stock_codes
        mock_retriever.get_all_stock_codes.return_value = ['000001.SZ']
        
        # Mock download_history_data
        mock_retriever.download_history_data.return_value = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.5, 10.3, 10.8, 10.6]
        })
        
        # Mock save_market_data
        mock_manager.save_market_data.return_value = None
        
        # Mock load_market_data
        mock_manager.load_market_data.return_value = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.5, 10.3, 10.8, 10.6]
        })
        
        # 执行下载
        stats = download_full_market(
            retriever=mock_retriever,
            data_manager=mock_manager,
            start_date='20240101',
            end_date='20240110',
            data_type='daily',
            resume=False,
            state_file=tmp_path / "state.json"
        )
        
        # 验证统计信息
        assert stats['total_stocks'] == 1
        assert stats['success_count'] == 1
        assert stats['failed_count'] == 0


class TestFullMarketDownloaderRepr:
    """测试字符串表示"""
    
    def test_repr(self, tmp_path):
        """测试__repr__方法"""
        mock_retriever = Mock()
        mock_manager = Mock()
        
        downloader = FullMarketDownloader(
            retriever=mock_retriever,
            data_manager=mock_manager,
            state_file=tmp_path / "state.json"
        )
        
        repr_str = repr(downloader)
        
        assert "FullMarketDownloader" in repr_str
        assert "state_file" in repr_str
