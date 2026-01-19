"""
集成测试：增量更新流程

测试完整的增量更新工作流
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.data_manager import DataManager


@pytest.mark.integration
class TestIncrementalUpdate:
    """测试增量更新完整流程"""
    
    def test_incremental_update_workflow(self, temp_dir):
        """
        测试增量更新完整流程
        
        工作流步骤：
        1. 初始下载历史数据
        2. 保存到本地
        3. 识别最后更新日期
        4. 仅下载新数据
        5. 合并并去重
        6. 验证数据完整性
        
        验证：需求5.3, 5.4, 8.3, 8.5
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        stock_code = '000001.SZ'
        
        # 1. 初始数据（10天）
        initial_data = pd.DataFrame({
            'stock_code': [stock_code] * 10,
            'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
            'open': np.random.uniform(10, 11, 10),
            'high': np.random.uniform(11, 12, 10),
            'low': np.random.uniform(9, 10, 10),
            'close': np.random.uniform(10, 11, 10),
            'volume': np.random.randint(1000000, 2000000, 10),
            'amount': np.random.uniform(10000000, 20000000, 10)
        })
        
        # 保存初始数据
        manager.save_market_data(initial_data, 'daily', stock_code)
        
        # 2. 获取最后更新日期
        last_date = manager.get_last_update_date('daily', stock_code)
        assert last_date == '20240110'
        
        # 3. 新数据（5天，包含1天重复）
        new_data = pd.DataFrame({
            'stock_code': [stock_code] * 5,
            'date': ['20240110', '20240111', '20240112', '20240113', '20240114'],
            'open': np.random.uniform(10, 11, 5),
            'high': np.random.uniform(11, 12, 5),
            'low': np.random.uniform(9, 10, 5),
            'close': np.random.uniform(10, 11, 5),
            'volume': np.random.randint(1000000, 2000000, 5),
            'amount': np.random.uniform(10000000, 20000000, 5)
        })
        
        # 4. Mock增量下载
        with patch.object(retriever, 'download_history_data', return_value=new_data):
            # 执行增量更新
            updated_count = manager.incremental_update(
                retriever,
                [stock_code],
                'daily'
            )
        
        # 5. 验证更新结果
        # 应该只添加4条新记录（去除1条重复）
        assert updated_count == 4
        
        # 6. 加载所有数据
        all_data = manager.load_market_data('daily', stock_code)
        
        # 验证总记录数（10 + 4 = 14）
        assert len(all_data) == 14
        
        # 验证日期范围
        assert all_data['date'].min() == '20240101'
        assert all_data['date'].max() == '20240114'
        
        # 验证无重复日期
        assert len(all_data['date'].unique()) == 14
    
    def test_incremental_update_with_multiple_stocks(self, temp_dir):
        """
        测试多股票增量更新
        
        验证：需求8.1, 8.2, 8.5
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        
        # 为每个股票创建初始数据
        for stock_code in stock_codes:
            initial_data = pd.DataFrame({
                'stock_code': [stock_code] * 5,
                'date': [f'2024010{i}' for i in range(1, 6)],
                'open': np.random.uniform(10, 11, 5),
                'high': np.random.uniform(11, 12, 5),
                'low': np.random.uniform(9, 10, 5),
                'close': np.random.uniform(10, 11, 5),
                'volume': np.random.randint(1000000, 2000000, 5),
                'amount': np.random.uniform(10000000, 20000000, 5)
            })
            manager.save_market_data(initial_data, 'daily', stock_code)
        
        # Mock批量下载新数据
        def mock_download(stock_codes, start_date, end_date, **kwargs):
            all_new_data = []
            for stock_code in stock_codes:
                new_data = pd.DataFrame({
                    'stock_code': [stock_code] * 3,
                    'date': ['20240106', '20240107', '20240108'],
                    'open': np.random.uniform(10, 11, 3),
                    'high': np.random.uniform(11, 12, 3),
                    'low': np.random.uniform(9, 10, 3),
                    'close': np.random.uniform(10, 11, 3),
                    'volume': np.random.randint(1000000, 2000000, 3),
                    'amount': np.random.uniform(10000000, 20000000, 3)
                })
                all_new_data.append(new_data)
            return pd.concat(all_new_data, ignore_index=True)
        
        with patch.object(retriever, 'download_history_data', side_effect=mock_download):
            # 批量增量更新
            total_updated = 0
            for stock_code in stock_codes:
                updated = manager.incremental_update(
                    retriever,
                    [stock_code],
                    'daily'
                )
                total_updated += updated
        
        # 验证：每个股票应该添加3条新记录
        assert total_updated == 9  # 3 stocks * 3 new records
        
        # 验证每个股票的数据
        for stock_code in stock_codes:
            data = manager.load_market_data('daily', stock_code)
            assert len(data) == 8  # 5 initial + 3 new
            assert data['date'].min() == '20240101'
            assert data['date'].max() == '20240108'
    
    def test_incremental_update_with_data_gaps(self, temp_dir):
        """
        测试存在数据缺口时的增量更新
        
        验证：需求9.5
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        stock_code = '000001.SZ'
        
        # 初始数据有缺口（缺少20240103和20240104）
        initial_data = pd.DataFrame({
            'stock_code': [stock_code] * 3,
            'date': ['20240101', '20240102', '20240105'],
            'open': [10.0, 10.5, 10.8],
            'high': [10.8, 10.9, 11.0],
            'low': [9.8, 10.2, 10.5],
            'close': [10.5, 10.3, 10.7],
            'volume': [1000000, 1200000, 1100000],
            'amount': [10500000, 12360000, 11770000]
        })
        
        manager.save_market_data(initial_data, 'daily', stock_code)
        
        # 检测数据缺口
        gaps = manager.detect_data_gaps('daily', stock_code, '20240101', '20240105')
        
        # 验证检测到缺口
        assert len(gaps) > 0
        assert '20240103' in gaps or '20240104' in gaps
        
        # 新数据填补缺口
        new_data = pd.DataFrame({
            'stock_code': [stock_code] * 4,
            'date': ['20240103', '20240104', '20240106', '20240107'],
            'open': [10.3, 10.6, 10.9, 11.0],
            'high': [10.7, 11.0, 11.2, 11.3],
            'low': [10.0, 10.3, 10.6, 10.8],
            'close': [10.6, 10.8, 11.1, 11.2],
            'volume': [900000, 1100000, 1050000, 1080000],
            'amount': [9540000, 11880000, 11655000, 12096000]
        })
        
        with patch.object(retriever, 'download_history_data', return_value=new_data):
            updated = manager.incremental_update(
                retriever,
                [stock_code],
                'daily'
            )
        
        # 验证更新
        assert updated == 4
        
        # 加载所有数据
        all_data = manager.load_market_data('daily', stock_code)
        
        # 验证数据完整性
        assert len(all_data) == 7  # 3 initial + 4 new
        
        # 重新检测缺口
        gaps_after = manager.detect_data_gaps('daily', stock_code, '20240101', '20240107')
        
        # 验证缺口已填补（可能仍有周末等非交易日）
        assert len(gaps_after) <= len(gaps)
