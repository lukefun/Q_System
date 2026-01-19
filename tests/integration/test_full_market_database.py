"""
集成测试：全市场数据库构建

测试完整的全市场数据库构建流程
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.data_manager import DataManager
from src.full_market_downloader import download_full_market


@pytest.mark.integration
@pytest.mark.slow
class TestFullMarketDatabase:
    """测试全市场数据库构建流程"""
    
    def test_full_market_download_workflow(self, temp_dir):
        """
        测试全市场下载完整流程
        
        工作流步骤：
        1. 获取所有股票代码
        2. 批量下载日线数据
        3. 处理API速率限制
        4. 保存到本地数据库
        5. 生成汇总统计
        
        验证：需求8.1, 8.2, 8.5, 8.6
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        # Mock股票代码列表（使用小样本）
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH', '600001.SH', '600002.SH']
        
        with patch.object(retriever, 'get_all_stock_codes', return_value=stock_codes):
            # Mock批量下载
            def mock_download(codes, start_date, end_date, **kwargs):
                all_data = []
                for code in codes:
                    data = pd.DataFrame({
                        'stock_code': [code] * 10,
                        'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
                        'open': np.random.uniform(10, 11, 10),
                        'high': np.random.uniform(11, 12, 10),
                        'low': np.random.uniform(9, 10, 10),
                        'close': np.random.uniform(10, 11, 10),
                        'volume': np.random.randint(1000000, 2000000, 10),
                        'amount': np.random.uniform(10000000, 20000000, 10)
                    })
                    all_data.append(data)
                return pd.concat(all_data, ignore_index=True)
            
            with patch.object(retriever, 'download_history_data', side_effect=mock_download):
                # 执行全市场下载
                progress_reports = []
                
                def progress_callback(current, total, stock_code):
                    progress_reports.append({
                        'current': current,
                        'total': total,
                        'stock_code': stock_code
                    })
                
                summary = download_full_market(
                    retriever=retriever,
                    manager=manager,
                    start_date='20240101',
                    end_date='20240110',
                    progress_callback=progress_callback,
                    delay_seconds=0.01  # 快速测试
                )
        
        # 验证进度报告
        assert len(progress_reports) == len(stock_codes)
        assert progress_reports[-1]['current'] == len(stock_codes)
        
        # 验证汇总统计
        assert summary['total_stocks'] == len(stock_codes)
        assert summary['successful_downloads'] == len(stock_codes)
        assert summary['failed_downloads'] == 0
        assert summary['total_records'] == len(stock_codes) * 10
        
        # 验证数据已保存
        for stock_code in stock_codes:
            data = manager.load_market_data('daily', stock_code)
            assert len(data) == 10
            assert data['stock_code'].iloc[0] == stock_code
    
    def test_full_market_download_with_failures(self, temp_dir):
        """
        测试全市场下载时的错误处理
        
        验证：需求9.3
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        stock_codes = ['000001.SZ', '000002.SZ', 'INVALID.XX', '600000.SH']
        
        with patch.object(retriever, 'get_all_stock_codes', return_value=stock_codes):
            # Mock下载，INVALID.XX会失败
            def mock_download_with_failure(codes, start_date, end_date, **kwargs):
                all_data = []
                for code in codes:
                    if code == 'INVALID.XX':
                        raise ValueError(f"Invalid stock code: {code}")
                    
                    data = pd.DataFrame({
                        'stock_code': [code] * 5,
                        'date': [f'2024010{i}' for i in range(1, 6)],
                        'open': np.random.uniform(10, 11, 5),
                        'high': np.random.uniform(11, 12, 5),
                        'low': np.random.uniform(9, 10, 5),
                        'close': np.random.uniform(10, 11, 5),
                        'volume': np.random.randint(1000000, 2000000, 5),
                        'amount': np.random.uniform(10000000, 20000000, 5)
                    })
                    all_data.append(data)
                
                if all_data:
                    return pd.concat(all_data, ignore_index=True)
                return pd.DataFrame()
            
            with patch.object(retriever, 'download_history_data', side_effect=mock_download_with_failure):
                summary = download_full_market(
                    retriever=retriever,
                    manager=manager,
                    start_date='20240101',
                    end_date='20240105',
                    delay_seconds=0.01
                )
        
        # 验证部分成功
        assert summary['total_stocks'] == len(stock_codes)
        assert summary['successful_downloads'] == 3  # 3个有效股票
        assert summary['failed_downloads'] == 1  # 1个失败
        assert 'INVALID.XX' in summary['failed_stocks']
        
        # 验证成功的股票数据已保存
        valid_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        for stock_code in valid_codes:
            data = manager.load_market_data('daily', stock_code)
            assert len(data) == 5
    
    def test_full_market_download_resume(self, temp_dir):
        """
        测试全市场下载的断点续传
        
        验证：需求8.3
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH', '600001.SH']
        
        # 第一次下载：只下载前2个股票
        first_batch = stock_codes[:2]
        
        with patch.object(retriever, 'get_all_stock_codes', return_value=stock_codes):
            def mock_download_first(codes, start_date, end_date, **kwargs):
                all_data = []
                for code in codes:
                    if code in first_batch:
                        data = pd.DataFrame({
                            'stock_code': [code] * 5,
                            'date': [f'2024010{i}' for i in range(1, 6)],
                            'close': np.random.uniform(10, 11, 5),
                            'volume': [1000000] * 5
                        })
                        all_data.append(data)
                if all_data:
                    return pd.concat(all_data, ignore_index=True)
                return pd.DataFrame()
            
            with patch.object(retriever, 'download_history_data', side_effect=mock_download_first):
                # 保存前2个股票的数据
                for code in first_batch:
                    data = retriever.download_history_data([code], '20240101', '20240105')
                    if not data.empty:
                        manager.save_market_data(data, 'daily', code)
        
        # 验证前2个股票已保存
        for code in first_batch:
            assert manager.get_last_update_date('daily', code) is not None
        
        # 第二次下载：续传剩余股票
        remaining_batch = stock_codes[2:]
        
        with patch.object(retriever, 'get_all_stock_codes', return_value=stock_codes):
            def mock_download_remaining(codes, start_date, end_date, **kwargs):
                all_data = []
                for code in codes:
                    if code in remaining_batch:
                        data = pd.DataFrame({
                            'stock_code': [code] * 5,
                            'date': [f'2024010{i}' for i in range(1, 6)],
                            'close': np.random.uniform(10, 11, 5),
                            'volume': [1000000] * 5
                        })
                        all_data.append(data)
                if all_data:
                    return pd.concat(all_data, ignore_index=True)
                return pd.DataFrame()
            
            with patch.object(retriever, 'download_history_data', side_effect=mock_download_remaining):
                # 只下载未完成的股票
                for code in remaining_batch:
                    data = retriever.download_history_data([code], '20240101', '20240105')
                    if not data.empty:
                        manager.save_market_data(data, 'daily', code)
        
        # 验证所有股票都已保存
        for code in stock_codes:
            data = manager.load_market_data('daily', code)
            assert len(data) == 5
