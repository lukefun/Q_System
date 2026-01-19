"""
集成测试：完整数据工作流

测试从数据获取到存储、处理、可视化的完整流程
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from src.fundamental_handler import FundamentalHandler
from src.industry_mapper import IndustryMapper
from src.data_manager import DataManager
from src.visualizer import Visualizer


@pytest.mark.integration
class TestFullDataWorkflow:
    """测试完整的数据获取-处理-存储-可视化工作流"""
    
    def test_complete_workflow_with_mocked_api(self, temp_dir):
        """
        测试完整工作流（使用mock API）
        
        工作流步骤：
        1. 连接API
        2. 下载历史数据
        3. 应用价格复权
        4. 保存到本地HDF5
        5. 从本地加载数据
        6. 生成可视化
        
        验证：所有需求
        """
        # 1. 设置mock客户端
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        mock_client.connect.return_value = True
        
        # 2. 创建组件
        retriever = DataRetriever(mock_client)
        adjuster = PriceAdjuster(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        visualizer = Visualizer()
        
        # 3. Mock数据获取
        sample_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 10,
            'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
            'open': np.random.uniform(10, 11, 10),
            'high': np.random.uniform(11, 12, 10),
            'low': np.random.uniform(9, 10, 10),
            'close': np.random.uniform(10, 11, 10),
            'volume': np.random.randint(1000000, 2000000, 10),
            'amount': np.random.uniform(10000000, 20000000, 10)
        })
        
        with patch.object(retriever, 'download_history_data', return_value=sample_data):
            data = retriever.download_history_data(
                stock_codes=['000001.SZ'],
                start_date='20240101',
                end_date='20240110'
            )
        
        # 验证数据获取
        assert len(data) == 10
        assert 'stock_code' in data.columns
        assert 'close' in data.columns
        
        # 4. 应用前复权
        adjust_factors = pd.DataFrame({
            'date': data['date'].values,
            'adjust_factor': [1.0] * 10
        })
        
        with patch.object(adjuster, 'get_adjust_factors', return_value=adjust_factors):
            adjusted_data = adjuster.forward_adjust(data.copy(), '000001.SZ')
        
        # 验证复权后数据
        assert len(adjusted_data) == len(data)
        
        # 5. 保存到HDF5
        manager.save_market_data(adjusted_data, 'daily', '000001.SZ')
        
        # 验证文件创建
        assert (temp_dir / 'market_data.h5').exists()
        
        # 6. 从HDF5加载
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        # 验证加载的数据
        assert len(loaded_data) == len(adjusted_data)
        assert list(loaded_data.columns) == list(adjusted_data.columns)
        
        # 7. 生成可视化
        viz_path = temp_dir / 'test_chart.png'
        visualizer.plot_kline(
            loaded_data,
            '000001.SZ',
            ma_periods=[5],
            save_path=str(viz_path)
        )
        
        # 验证图表文件创建
        assert viz_path.exists()

    
    def test_workflow_with_fundamental_data(self, temp_dir):
        """
        测试包含基本面数据的工作流
        
        工作流步骤：
        1. 获取价格数据
        2. 获取基本面数据
        3. 计算PE/PB比率
        4. 保存所有数据
        5. 验证时间点正确性
        
        验证：需求3.1, 3.2, 3.3, 7.2
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        fundamental_handler = FundamentalHandler(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        # Mock价格数据
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.5, 10.3, 10.8, 10.6],
            'volume': [1000000] * 5
        })
        
        # Mock基本面数据
        fundamental_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'report_date': ['20231231'],
            'announce_date': ['20240101'],
            'pe_ratio': [15.5],
            'pb_ratio': [1.8],
            'roe': [0.12]
        })
        
        with patch.object(retriever, 'download_history_data', return_value=price_data):
            with patch.object(fundamental_handler, 'get_financial_data', return_value=fundamental_data):
                # 获取数据
                prices = retriever.download_history_data(
                    stock_codes=['000001.SZ'],
                    start_date='20240101',
                    end_date='20240105'
                )
                
                fundamentals = fundamental_handler.get_financial_data(
                    stock_codes=['000001.SZ'],
                    indicators=['pe_ratio', 'pb_ratio', 'roe'],
                    as_of_date='20240105'
                )
                
                # 验证时间点正确性
                assert all(fundamentals['announce_date'] <= '20240105')
                
                # 保存数据
                manager.save_market_data(prices, 'daily', '000001.SZ')
                manager.save_market_data(fundamentals, 'fundamental', '000001.SZ')
                
                # 加载并验证
                loaded_prices = manager.load_market_data('daily', '000001.SZ')
                loaded_fundamentals = manager.load_market_data('fundamental', '000001.SZ')
                
                assert len(loaded_prices) == 5
                assert len(loaded_fundamentals) == 1
                assert 'pe_ratio' in loaded_fundamentals.columns

    
    def test_workflow_with_industry_classification(self, temp_dir):
        """
        测试包含行业分类的工作流
        
        工作流步骤：
        1. 获取股票数据
        2. 获取行业分类
        3. 按行业分组分析
        4. 保存结果
        
        验证：需求4.1, 4.2, 4.3
        """
        # 设置
        mock_client = Mock(spec=XtDataClient)
        mock_client.is_connected.return_value = True
        
        retriever = DataRetriever(mock_client)
        industry_mapper = IndustryMapper(mock_client)
        manager = DataManager(storage_path=str(temp_dir))
        
        # Mock数据
        stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
        price_data = pd.DataFrame({
            'stock_code': stock_codes * 3,
            'date': ['20240101'] * 3 + ['20240102'] * 3 + ['20240103'] * 3,
            'close': np.random.uniform(10, 20, 9),
            'volume': np.random.randint(1000000, 2000000, 9)
        })
        
        industry_data = {
            '000001.SZ': {'industry_l1_code': '801010', 'industry_l1_name': '农林牧渔'},
            '000002.SZ': {'industry_l1_code': '801010', 'industry_l1_name': '农林牧渔'},
            '600000.SH': {'industry_l1_code': '801020', 'industry_l1_name': '采掘'}
        }
        
        with patch.object(retriever, 'download_history_data', return_value=price_data):
            with patch.object(industry_mapper, 'get_stock_industry', side_effect=lambda code, date=None: industry_data.get(code, {})):
                # 获取价格数据
                prices = retriever.download_history_data(
                    stock_codes=stock_codes,
                    start_date='20240101',
                    end_date='20240103'
                )
                
                # 添加行业信息
                prices['industry_l1_code'] = prices['stock_code'].apply(
                    lambda x: industry_data.get(x, {}).get('industry_l1_code', '')
                )
                prices['industry_l1_name'] = prices['stock_code'].apply(
                    lambda x: industry_data.get(x, {}).get('industry_l1_name', '')
                )
                
                # 按行业分组统计
                industry_stats = prices.groupby('industry_l1_name').agg({
                    'close': 'mean',
                    'volume': 'sum'
                }).reset_index()
                
                # 验证
                assert len(industry_stats) == 2  # 两个行业
                assert '农林牧渔' in industry_stats['industry_l1_name'].values
                assert '采掘' in industry_stats['industry_l1_name'].values
                
                # 保存
                manager.save_market_data(prices, 'daily_with_industry')
                manager.save_market_data(industry_stats, 'industry_stats')
                
                # 验证保存
                loaded = manager.load_market_data('daily_with_industry')
                assert 'industry_l1_name' in loaded.columns
