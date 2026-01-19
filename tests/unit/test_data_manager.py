"""
DataManager单元测试

测试数据管理器的基础功能，包括保存、加载、导出和查询
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from src.data_manager import DataManager
from config import StorageError, ValidationError


class TestDataManagerInit:
    """测试DataManager初始化"""
    
    def test_init_with_default_path(self):
        """测试使用默认路径初始化"""
        manager = DataManager()
        assert manager.storage_path is not None
        assert manager.hdf5_path is not None
        assert manager.hdf5_path.name == "market_data.h5"
    
    def test_init_with_custom_path(self, tmp_path):
        """测试使用自定义路径初始化"""
        manager = DataManager(storage_path=str(tmp_path))
        assert manager.storage_path == tmp_path
        assert manager.hdf5_path == tmp_path / "market_data.h5"
    
    def test_storage_directory_created(self, tmp_path):
        """测试存储目录自动创建"""
        custom_path = tmp_path / "custom" / "storage"
        manager = DataManager(storage_path=str(custom_path))
        assert custom_path.exists()


class TestDataManagerSaveLoad:
    """测试数据保存和加载功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    @pytest.fixture
    def sample_daily_data(self):
        """创建示例日线数据"""
        return pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'open': [10.0, 10.5, 10.3, 10.8, 10.6],
            'high': [10.8, 10.9, 10.7, 11.0, 10.9],
            'low': [9.8, 10.2, 10.0, 10.5, 10.3],
            'close': [10.5, 10.3, 10.6, 10.7, 10.8],
            'volume': [1000000, 1200000, 900000, 1100000, 1050000]
        })
    
    def test_save_daily_data(self, manager, sample_daily_data):
        """测试保存日线数据"""
        manager.save_market_data(sample_daily_data, 'daily', '000001.SZ')
        
        # 验证文件已创建
        assert manager.hdf5_path.exists()
    
    def test_load_daily_data(self, manager, sample_daily_data):
        """测试加载日线数据"""
        # 保存数据
        manager.save_market_data(sample_daily_data, 'daily', '000001.SZ')
        
        # 加载数据
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        # 验证数据一致性
        assert len(loaded_data) == len(sample_daily_data)
        assert list(loaded_data.columns) == list(sample_daily_data.columns)
        assert loaded_data['stock_code'].iloc[0] == '000001.SZ'
    
    def test_save_empty_data(self, manager):
        """测试保存空数据"""
        empty_data = pd.DataFrame()
        # 应该不抛出异常，只是记录警告
        manager.save_market_data(empty_data, 'daily', '000001.SZ')
    
    def test_save_none_data(self, manager):
        """测试保存None数据"""
        # 应该不抛出异常，只是记录警告
        manager.save_market_data(None, 'daily', '000001.SZ')
    
    def test_load_nonexistent_data(self, manager):
        """测试加载不存在的数据"""
        loaded_data = manager.load_market_data('daily', '999999.SZ')
        assert loaded_data.empty
    
    def test_save_invalid_data_type(self, manager):
        """测试保存无效数据类型"""
        with pytest.raises(ValidationError):
            manager.save_market_data("not a dataframe", 'daily', '000001.SZ')
    
    def test_invalid_data_type(self, manager, sample_daily_data):
        """测试无效的数据类型参数"""
        with pytest.raises(ValidationError):
            manager.save_market_data(sample_daily_data, 'invalid_type', '000001.SZ')
    
    def test_save_and_merge_data(self, manager, sample_daily_data):
        """测试数据合并功能"""
        # 保存第一批数据
        manager.save_market_data(sample_daily_data, 'daily', '000001.SZ')
        
        # 创建新数据（部分重复）
        new_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240105', '20240106', '20240107'],  # 20240105重复
            'open': [10.8, 10.9, 11.0],
            'high': [11.0, 11.2, 11.3],
            'low': [10.5, 10.7, 10.8],
            'close': [10.9, 11.0, 11.1],
            'volume': [1100000, 1150000, 1200000]
        })
        
        # 保存新数据
        manager.save_market_data(new_data, 'daily', '000001.SZ')
        
        # 加载合并后的数据
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        # 验证：应该有7条记录（5 + 3 - 1重复）
        assert len(loaded_data) == 7
        
        # 验证去重：20240105应该只有一条
        date_counts = loaded_data['date'].value_counts()
        assert date_counts['20240105'] == 1


class TestDataManagerDateFiltering:
    """测试日期过滤功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    @pytest.fixture
    def sample_data_with_dates(self):
        """创建带日期的示例数据"""
        return pd.DataFrame({
            'stock_code': ['000001.SZ'] * 10,
            'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
            'close': [10.0 + i * 0.1 for i in range(10)]
        })
    
    def test_load_with_date_range(self, manager, sample_data_with_dates):
        """测试按日期范围加载数据"""
        # 保存数据
        manager.save_market_data(sample_data_with_dates, 'daily', '000001.SZ')
        
        # 加载指定日期范围的数据
        loaded_data = manager.load_market_data(
            'daily',
            '000001.SZ',
            start_date='20240103',
            end_date='20240107'
        )
        
        # 验证：应该有5条记录（20240103-20240107）
        assert len(loaded_data) == 5
        assert loaded_data['date'].min() == '20240103'
        assert loaded_data['date'].max() == '20240107'
    
    def test_load_with_start_date_only(self, manager, sample_data_with_dates):
        """测试只指定开始日期"""
        manager.save_market_data(sample_data_with_dates, 'daily', '000001.SZ')
        
        loaded_data = manager.load_market_data(
            'daily',
            '000001.SZ',
            start_date='20240105'
        )
        
        # 验证：应该有6条记录（20240105-20240110）
        assert len(loaded_data) == 6
        assert loaded_data['date'].min() == '20240105'
    
    def test_load_with_end_date_only(self, manager, sample_data_with_dates):
        """测试只指定结束日期"""
        manager.save_market_data(sample_data_with_dates, 'daily', '000001.SZ')
        
        loaded_data = manager.load_market_data(
            'daily',
            '000001.SZ',
            end_date='20240105'
        )
        
        # 验证：应该有5条记录（20240101-20240105）
        assert len(loaded_data) == 5
        assert loaded_data['date'].max() == '20240105'
    
    def test_invalid_date_range(self, manager):
        """测试无效的日期范围"""
        with pytest.raises(ValidationError):
            manager.load_market_data(
                'daily',
                '000001.SZ',
                start_date='20240110',
                end_date='20240101'  # 结束日期早于开始日期
            )


class TestDataManagerLastUpdateDate:
    """测试获取最后更新日期功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_get_last_update_date(self, manager):
        """测试获取最后更新日期"""
        # 创建测试数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.1, 10.2, 10.3, 10.4]
        })
        
        # 保存数据
        manager.save_market_data(data, 'daily', '000001.SZ')
        
        # 获取最后更新日期
        last_date = manager.get_last_update_date('daily', '000001.SZ')
        
        # 验证
        assert last_date == '20240105'
    
    def test_get_last_update_date_no_data(self, manager):
        """测试没有数据时获取最后更新日期"""
        last_date = manager.get_last_update_date('daily', '999999.SZ')
        assert last_date is None
    
    def test_get_last_update_date_tick_data(self, manager):
        """测试Tick数据的最后更新日期"""
        # 创建Tick数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'timestamp': [1704067200000, 1704153600000, 1704240000000],  # 毫秒时间戳
            'price': [10.0, 10.1, 10.2]
        })
        
        # 保存数据
        manager.save_market_data(data, 'tick', '000001.SZ')
        
        # 获取最后更新日期（时间戳）
        last_timestamp = manager.get_last_update_date('tick', '000001.SZ')
        
        # 验证
        assert last_timestamp == '1704240000000'


class TestDataManagerExportCSV:
    """测试CSV导出功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        return pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.1, 10.2, 10.3, 10.4]
        })
    
    def test_export_to_csv(self, manager, sample_data, tmp_path):
        """测试导出CSV"""
        # 保存数据
        manager.save_market_data(sample_data, 'daily', '000001.SZ')
        
        # 导出CSV
        csv_path = tmp_path / "export.csv"
        manager.export_to_csv('daily', str(csv_path), '000001.SZ')
        
        # 验证文件已创建
        assert csv_path.exists()
        
        # 验证CSV内容
        exported_data = pd.read_csv(csv_path)
        assert len(exported_data) == len(sample_data)
        assert list(exported_data.columns) == list(sample_data.columns)
    
    def test_export_with_date_range(self, manager, sample_data, tmp_path):
        """测试导出指定日期范围的CSV"""
        # 保存数据
        manager.save_market_data(sample_data, 'daily', '000001.SZ')
        
        # 导出部分数据
        csv_path = tmp_path / "export_partial.csv"
        manager.export_to_csv(
            'daily',
            str(csv_path),
            '000001.SZ',
            start_date='20240102',
            end_date='20240104'
        )
        
        # 验证CSV内容
        exported_data = pd.read_csv(csv_path)
        assert len(exported_data) == 3  # 3条记录
    
    def test_export_no_data(self, manager, tmp_path):
        """测试导出不存在的数据"""
        csv_path = tmp_path / "export_empty.csv"
        # 应该不抛出异常，只是记录警告
        manager.export_to_csv('daily', str(csv_path), '999999.SZ')
        
        # 文件不应该被创建
        assert not csv_path.exists()
    
    def test_export_creates_directory(self, manager, sample_data, tmp_path):
        """测试导出时自动创建目录"""
        # 保存数据
        manager.save_market_data(sample_data, 'daily', '000001.SZ')
        
        # 导出到不存在的目录
        csv_path = tmp_path / "subdir" / "nested" / "export.csv"
        manager.export_to_csv('daily', str(csv_path), '000001.SZ')
        
        # 验证目录和文件已创建
        assert csv_path.exists()
        assert csv_path.parent.exists()


class TestDataManagerMultipleStocks:
    """测试多股票数据管理"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_save_multiple_stocks(self, manager):
        """测试保存多只股票数据"""
        stocks = ['000001.SZ', '000002.SZ', '600000.SH']
        
        for stock in stocks:
            data = pd.DataFrame({
                'stock_code': [stock] * 3,
                'date': ['20240101', '20240102', '20240103'],
                'close': [10.0, 10.1, 10.2]
            })
            manager.save_market_data(data, 'daily', stock)
        
        # 验证每只股票的数据都能加载
        for stock in stocks:
            loaded_data = manager.load_market_data('daily', stock)
            assert len(loaded_data) == 3
            assert loaded_data['stock_code'].iloc[0] == stock
    
    def test_load_all_stocks(self, manager):
        """测试加载全市场数据"""
        # 创建多股票数据
        all_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3 + ['000002.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'] * 2,
            'close': [10.0, 10.1, 10.2, 20.0, 20.1, 20.2]
        })
        
        # 保存为全市场数据
        manager.save_market_data(all_data, 'daily', None)
        
        # 加载全市场数据
        loaded_data = manager.load_market_data('daily', None)
        
        # 验证
        assert len(loaded_data) == 6
        assert len(loaded_data['stock_code'].unique()) == 2


class TestDataManagerStorageInfo:
    """测试存储信息功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_get_storage_info_empty(self, manager):
        """测试获取空存储信息"""
        info = manager.get_storage_info()
        
        assert info['file_exists'] == False
        assert info['file_size_mb'] == 0
        assert info['total_records'] == 0
    
    def test_get_storage_info_with_data(self, manager):
        """测试获取有数据的存储信息"""
        # 保存一些数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.1, 10.2, 10.3, 10.4]
        })
        manager.save_market_data(data, 'daily', '000001.SZ')
        
        # 获取存储信息
        info = manager.get_storage_info()
        
        assert info['file_exists'] == True
        assert info['file_size_mb'] > 0
        assert 'daily' in info['data_types']
        assert info['total_records'] >= 5


class TestDataManagerEdgeCases:
    """测试边缘情况"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_stock_code_with_special_characters(self, manager):
        """测试包含特殊字符的股票代码"""
        # 股票代码中的.会被替换为_
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240101'],
            'close': [10.0]
        })
        
        manager.save_market_data(data, 'daily', '000001.SZ')
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        assert len(loaded_data) == 1
    
    def test_large_dataset(self, manager):
        """测试大数据集"""
        # 创建较大的数据集（1000条记录）
        large_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 1000,
            'date': [f'20240101' for _ in range(1000)],
            'close': [10.0 + i * 0.01 for i in range(1000)]
        })
        
        # 保存和加载应该正常工作
        manager.save_market_data(large_data, 'daily', '000001.SZ')
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        # 由于去重，实际记录数会少于1000
        assert len(loaded_data) > 0
    
    def test_unicode_in_data(self, manager):
        """测试数据中包含Unicode字符"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240101'],
            'close': [10.0],
            'name': ['平安银行']  # 中文名称
        })
        
        manager.save_market_data(data, 'daily', '000001.SZ')
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        
        assert len(loaded_data) == 1
        assert loaded_data['name'].iloc[0] == '平安银行'


class TestDataManagerRepr:
    """测试字符串表示"""
    
    def test_repr(self, tmp_path):
        """测试__repr__方法"""
        manager = DataManager(storage_path=str(tmp_path))
        repr_str = repr(manager)
        
        assert 'DataManager' in repr_str
        assert str(tmp_path) in repr_str
        assert 'market_data.h5' in repr_str


class TestDataManagerIncrementalUpdate:
    """测试增量更新功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    @pytest.fixture
    def mock_retriever(self):
        """创建模拟的DataRetriever"""
        from unittest.mock import Mock
        retriever = Mock()
        return retriever
    
    def test_incremental_update_no_existing_data(self, manager, mock_retriever):
        """测试没有历史数据时的增量更新"""
        # 模拟返回新数据
        new_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.1, 10.2, 10.3, 10.4]
        })
        mock_retriever.download_history_data.return_value = new_data
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ'],
            'daily'
        )
        
        # 验证：应该更新5条记录
        assert updated == 5
        
        # 验证数据已保存
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        assert len(loaded_data) == 5
    
    def test_incremental_update_with_existing_data(self, manager, mock_retriever):
        """测试有历史数据时的增量更新"""
        # 先保存一些历史数据
        existing_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        manager.save_market_data(existing_data, 'daily', '000001.SZ')
        
        # 模拟返回新数据（从20240104开始）
        new_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240104', '20240105', '20240106'],
            'close': [10.3, 10.4, 10.5]
        })
        mock_retriever.download_history_data.return_value = new_data
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ'],
            'daily'
        )
        
        # 验证：应该更新3条新记录
        assert updated == 3
        
        # 验证总数据量
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        assert len(loaded_data) == 6  # 3 + 3
    
    def test_incremental_update_with_duplicates(self, manager, mock_retriever):
        """测试增量更新时处理重复数据"""
        # 先保存历史数据
        existing_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        manager.save_market_data(existing_data, 'daily', '000001.SZ')
        
        # 模拟返回的新数据包含重复日期
        new_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 4,
            'date': ['20240103', '20240104', '20240105', '20240106'],  # 20240103重复
            'close': [10.2, 10.3, 10.4, 10.5]
        })
        mock_retriever.download_history_data.return_value = new_data
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ'],
            'daily'
        )
        
        # 验证：应该只更新3条新记录（跳过重复的20240103）
        assert updated == 3
        
        # 验证总数据量
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        assert len(loaded_data) == 6  # 3 + 3（去重后）
    
    def test_incremental_update_no_new_data(self, manager, mock_retriever):
        """测试没有新数据时的增量更新"""
        # 先保存历史数据
        existing_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        manager.save_market_data(existing_data, 'daily', '000001.SZ')
        
        # 模拟返回空数据
        mock_retriever.download_history_data.return_value = pd.DataFrame()
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ'],
            'daily'
        )
        
        # 验证：没有更新
        assert updated == 0
    
    def test_incremental_update_multiple_stocks(self, manager, mock_retriever):
        """测试多只股票的增量更新"""
        # 模拟每只股票返回不同的数据
        def mock_download(stock_codes, start_date, end_date, period, adjust_type):
            stock_code = stock_codes[0]
            if stock_code == '000001.SZ':
                return pd.DataFrame({
                    'stock_code': [stock_code] * 3,
                    'date': ['20240101', '20240102', '20240103'],
                    'close': [10.0, 10.1, 10.2]
                })
            elif stock_code == '000002.SZ':
                return pd.DataFrame({
                    'stock_code': [stock_code] * 2,
                    'date': ['20240101', '20240102'],
                    'close': [20.0, 20.1]
                })
            else:
                return pd.DataFrame()
        
        mock_retriever.download_history_data.side_effect = mock_download
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ', '000002.SZ'],
            'daily'
        )
        
        # 验证：应该更新5条记录（3 + 2）
        assert updated == 5
        
        # 验证每只股票的数据
        data1 = manager.load_market_data('daily', '000001.SZ')
        assert len(data1) == 3
        
        data2 = manager.load_market_data('daily', '000002.SZ')
        assert len(data2) == 2
    
    def test_incremental_update_with_progress_callback(self, manager, mock_retriever):
        """测试增量更新的进度回调"""
        # 模拟返回数据
        mock_retriever.download_history_data.return_value = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 2,
            'date': ['20240101', '20240102'],
            'close': [10.0, 10.1]
        })
        
        # 记录进度回调
        progress_calls = []
        
        def progress_callback(current, total, stock_code):
            progress_calls.append((current, total, stock_code))
        
        # 执行增量更新
        manager.incremental_update(
            mock_retriever,
            ['000001.SZ', '000002.SZ'],
            'daily',
            progress_callback=progress_callback
        )
        
        # 验证进度回调被调用
        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2, '000001.SZ')
        assert progress_calls[1] == (2, 2, '000002.SZ')
    
    def test_incremental_update_single_stock_failure(self, manager, mock_retriever):
        """测试单只股票失败不影响其他股票"""
        # 模拟第一只股票失败，第二只成功
        def mock_download(stock_codes, start_date, end_date, period, adjust_type):
            stock_code = stock_codes[0]
            if stock_code == '000001.SZ':
                raise Exception("API错误")
            else:
                return pd.DataFrame({
                    'stock_code': [stock_code] * 2,
                    'date': ['20240101', '20240102'],
                    'close': [20.0, 20.1]
                })
        
        mock_retriever.download_history_data.side_effect = mock_download
        
        # 执行增量更新（不应该抛出异常）
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ', '000002.SZ'],
            'daily'
        )
        
        # 验证：只更新了第二只股票
        assert updated == 2
        
        # 验证第二只股票的数据已保存
        data2 = manager.load_market_data('daily', '000002.SZ')
        assert len(data2) == 2
    
    def test_incremental_update_empty_stock_list(self, manager, mock_retriever):
        """测试空股票列表"""
        with pytest.raises(ValidationError):
            manager.incremental_update(
                mock_retriever,
                [],
                'daily'
            )
    
    def test_incremental_update_invalid_data_type(self, manager, mock_retriever):
        """测试无效的数据类型"""
        with pytest.raises(ValidationError):
            manager.incremental_update(
                mock_retriever,
                ['000001.SZ'],
                'invalid_type'
            )
    
    def test_incremental_update_none_retriever(self, manager):
        """测试retriever为None"""
        with pytest.raises(ValidationError):
            manager.incremental_update(
                None,
                ['000001.SZ'],
                'daily'
            )
    
    def test_incremental_update_data_already_latest(self, manager, mock_retriever):
        """测试数据已是最新的情况"""
        # 保存今天的数据
        today = datetime.now().strftime('%Y%m%d')
        existing_data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': [today],
            'close': [10.0]
        })
        manager.save_market_data(existing_data, 'daily', '000001.SZ')
        
        # 执行增量更新
        updated = manager.incremental_update(
            mock_retriever,
            ['000001.SZ'],
            'daily'
        )
        
        # 验证：没有更新（数据已是最新）
        assert updated == 0


class TestDataManagerValidation:
    """测试数据验证功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    @pytest.fixture
    def valid_daily_data(self):
        """创建有效的日线数据"""
        return pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'open': [10.0, 10.5, 10.3, 10.8, 10.6],
            'high': [10.8, 10.9, 10.7, 11.0, 10.9],
            'low': [9.8, 10.2, 10.0, 10.5, 10.3],
            'close': [10.5, 10.3, 10.6, 10.7, 10.8],
            'volume': [1000000, 1200000, 900000, 1100000, 1050000]
        })
    
    def test_validate_valid_data(self, manager, valid_daily_data):
        """测试验证有效数据"""
        report = manager.validate_data(valid_daily_data, 'daily')
        
        assert report['is_valid'] == True
        assert len(report['errors']) == 0
    
    def test_validate_empty_data(self, manager):
        """测试验证空数据"""
        empty_data = pd.DataFrame()
        report = manager.validate_data(empty_data, 'daily')
        
        assert report['is_valid'] == False
        assert len(report['errors']) > 0
        assert '数据为空或None' in report['errors'][0]
    
    def test_validate_none_data(self, manager):
        """测试验证None数据"""
        report = manager.validate_data(None, 'daily')
        
        assert report['is_valid'] == False
        assert len(report['errors']) > 0
    
    def test_validate_negative_prices(self, manager):
        """测试检测负价格"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, -5.0, 10.3],  # 负价格
            'high': [10.8, 10.9, 10.7],
            'low': [9.8, 10.2, 10.0],
            'close': [10.5, 10.3, 10.6],
            'volume': [1000000, 1200000, 900000]
        })
        
        report = manager.validate_data(data, 'daily')
        
        assert report['is_valid'] == False
        assert any('负值' in error for error in report['errors'])
    
    def test_validate_negative_volume(self, manager):
        """测试检测负成交量"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 10.5, 10.3],
            'high': [10.8, 10.9, 10.7],
            'low': [9.8, 10.2, 10.0],
            'close': [10.5, 10.3, 10.6],
            'volume': [1000000, -500000, 900000]  # 负成交量
        })
        
        report = manager.validate_data(data, 'daily')
        
        assert report['is_valid'] == False
        assert any('成交量' in error and '负值' in error for error in report['errors'])
    
    def test_validate_invalid_ohlc_relationship(self, manager):
        """测试检测无效的OHLC关系"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 10.5, 10.3],
            'high': [9.5, 10.9, 10.7],  # high < open，不合理
            'low': [9.8, 10.2, 10.0],
            'close': [10.5, 10.3, 10.6],
            'volume': [1000000, 1200000, 900000]
        })
        
        report = manager.validate_data(data, 'daily')
        
        # 应该有警告
        assert len(report['warnings']) > 0
        assert any('最高价' in warning for warning in report['warnings'])
    
    def test_validate_missing_required_columns(self, manager):
        """测试检测缺失必需列"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103']
            # 缺少close列
        })
        
        report = manager.validate_data(data, 'daily')
        
        assert report['is_valid'] == False
        assert any('缺少必需列' in error for error in report['errors'])
    
    def test_validate_null_values(self, manager):
        """测试检测缺失值"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ', '000001.SZ', None],  # 包含None
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        
        report = manager.validate_data(data, 'daily')
        
        assert report['is_valid'] == False
        assert any('缺失值' in error for error in report['errors'])
    
    def test_validate_statistics_generated(self, manager, valid_daily_data):
        """测试生成统计信息"""
        report = manager.validate_data(valid_daily_data, 'daily')
        
        assert 'statistics' in report
        assert 'record_count' in report['statistics']
        assert report['statistics']['record_count'] == 5
        assert 'price_stats' in report['statistics']
        assert 'volume_stats' in report['statistics']


class TestDataManagerAnomalyDetection:
    """测试异常值检测功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_detect_price_anomalies(self, manager):
        """测试检测价格异常"""
        # 创建包含异常值的数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 10,
            'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
            'open': [10.0] * 9 + [100.0],  # 最后一个是异常值
            'high': [10.5] * 9 + [105.0],
            'low': [9.5] * 9 + [95.0],
            'close': [10.0] * 9 + [100.0],
            'volume': [1000000] * 10
        })
        
        report = manager.validate_data(data, 'daily')
        
        # 应该检测到异常值
        assert len(report['anomalies']) > 0
        assert any(a['type'] == '价格异常' for a in report['anomalies'])
    
    def test_detect_zero_volume(self, manager):
        """测试检测零成交量"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'open': [10.0, 10.5, 10.3, 10.8, 10.6],
            'high': [10.8, 10.9, 10.7, 11.0, 10.9],
            'low': [9.8, 10.2, 10.0, 10.5, 10.3],
            'close': [10.5, 10.3, 10.6, 10.7, 10.8],
            'volume': [1000000, 0, 900000, 1100000, 1050000]  # 包含零成交量
        })
        
        report = manager.validate_data(data, 'daily')
        
        # 应该检测到零成交量异常
        assert len(report['anomalies']) > 0
        assert any(
            a['type'] == '成交量异常' and a['value'] == 0
            for a in report['anomalies']
        )
    
    def test_detect_extreme_volume(self, manager):
        """测试检测极端成交量"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 10,
            'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
            'open': [10.0] * 10,
            'high': [10.5] * 10,
            'low': [9.5] * 10,
            'close': [10.0] * 10,
            'volume': [1000000] * 9 + [100000000]  # 最后一个是极端值
        })
        
        report = manager.validate_data(data, 'daily')
        
        # 应该检测到极端成交量
        assert len(report['anomalies']) > 0
        assert any(
            a['type'] == '成交量异常' and '极端' in a['reason']
            for a in report['anomalies']
        )


class TestDataManagerGapDetection:
    """测试数据缺口检测功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_detect_gaps_no_gaps(self, manager):
        """测试没有缺口的数据"""
        # 连续的交易日数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'close': [10.0, 10.1, 10.2, 10.3, 10.4]
        })
        
        gaps = manager.detect_data_gaps(data, 'daily', '000001.SZ')
        
        # 连续日期，不应该有缺口
        assert len(gaps) == 0
    
    def test_detect_gaps_with_gap(self, manager):
        """测试有缺口的数据"""
        # 有缺口的数据（20240103到20240110之间有缺口）
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 4,
            'date': ['20240101', '20240102', '20240103', '20240110'],  # 缺口
            'close': [10.0, 10.1, 10.2, 10.3]
        })
        
        gaps = manager.detect_data_gaps(data, 'daily', '000001.SZ')
        
        # 应该检测到缺口
        assert len(gaps) > 0
        assert gaps[0]['start_date'] == '20240103'
        assert gaps[0]['end_date'] == '20240110'
        assert gaps[0]['gap_days'] == 7
    
    def test_detect_gaps_empty_data(self, manager):
        """测试空数据的缺口检测"""
        empty_data = pd.DataFrame()
        gaps = manager.detect_data_gaps(empty_data, 'daily', '000001.SZ')
        
        assert len(gaps) == 0
    
    def test_detect_gaps_single_record(self, manager):
        """测试单条记录的缺口检测"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'],
            'date': ['20240101'],
            'close': [10.0]
        })
        
        gaps = manager.detect_data_gaps(data, 'daily', '000001.SZ')
        
        # 单条记录无法检测缺口
        assert len(gaps) == 0
    
    def test_detect_gaps_weekend_not_gap(self, manager):
        """测试周末不应被视为缺口"""
        # 周五到周一（跨周末）
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 2,
            'date': ['20240105', '20240108'],  # 周五到周一，间隔3天
            'close': [10.0, 10.1]
        })
        
        gaps = manager.detect_data_gaps(data, 'daily', '000001.SZ')
        
        # 3天间隔（周末）不应被视为缺口
        assert len(gaps) == 0
    
    def test_detect_gaps_tick_data(self, manager):
        """测试Tick数据的缺口检测"""
        # Tick数据（时间戳）
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'timestamp': [
                1704067200000,  # 2024-01-01 00:00:00
                1704070800000,  # 2024-01-01 01:00:00
                1704078000000   # 2024-01-01 03:00:00（间隔2小时）
            ],
            'price': [10.0, 10.1, 10.2]
        })
        
        gaps = manager.detect_data_gaps(data, 'tick', '000001.SZ')
        
        # 应该检测到时间间隔
        assert len(gaps) > 0


class TestDataManagerQualityReport:
    """测试数据质量报告功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_generate_quality_report_no_data(self, manager):
        """测试没有数据时生成质量报告"""
        report = manager.generate_quality_report('daily', '999999.SZ')
        
        assert report['summary']['status'] == '无数据'
    
    def test_generate_quality_report_valid_data(self, manager):
        """测试有效数据的质量报告"""
        # 保存有效数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
            'open': [10.0, 10.5, 10.3, 10.8, 10.6],
            'high': [10.8, 10.9, 10.7, 11.0, 10.9],
            'low': [9.8, 10.2, 10.0, 10.5, 10.3],
            'close': [10.5, 10.3, 10.6, 10.7, 10.8],
            'volume': [1000000, 1200000, 900000, 1100000, 1050000]
        })
        manager.save_market_data(data, 'daily', '000001.SZ')
        
        # 生成质量报告
        report = manager.generate_quality_report('daily', '000001.SZ')
        
        # 验证报告结构
        assert 'data_info' in report
        assert 'validation_result' in report
        assert 'gaps' in report
        assert 'summary' in report
        
        # 验证数据信息
        assert report['data_info']['record_count'] == 5
        assert report['data_info']['stock_code'] == '000001.SZ'
        
        # 验证质量摘要
        assert 'quality_score' in report['summary']
        assert 'completeness' in report['summary']
        assert 'status' in report['summary']
        
        # 有效数据应该有高质量评分
        assert report['summary']['quality_score'] >= 90
    
    def test_generate_quality_report_with_issues(self, manager):
        """测试有问题数据的质量报告"""
        # 保存有问题的数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 5,
            'date': ['20240101', '20240102', '20240103', '20240110', '20240111'],  # 有缺口
            'open': [10.0, -5.0, 10.3, 10.8, 10.6],  # 有负价格
            'high': [10.8, 10.9, 10.7, 11.0, 10.9],
            'low': [9.8, 10.2, 10.0, 10.5, 10.3],
            'close': [10.5, 10.3, 10.6, 10.7, 10.8],
            'volume': [1000000, 0, 900000, 1100000, 1050000]  # 有零成交量
        })
        manager.save_market_data(data, 'daily', '000001.SZ')
        
        # 生成质量报告
        report = manager.generate_quality_report('daily', '000001.SZ')
        
        # 应该检测到问题
        assert report['summary']['error_count'] > 0
        assert report['summary']['anomaly_count'] > 0
        assert len(report['gaps']) > 0
        
        # 质量评分应该较低
        assert report['summary']['quality_score'] < 90
    
    def test_quality_report_includes_date_range(self, manager):
        """测试质量报告包含日期范围"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        manager.save_market_data(data, 'daily', '000001.SZ')
        
        report = manager.generate_quality_report('daily', '000001.SZ')
        
        assert 'date_range' in report['data_info']
        assert report['data_info']['date_range']['start'] == '20240101'
        assert report['data_info']['date_range']['end'] == '20240103'


class TestDataManagerValidationIntegration:
    """测试数据验证集成功能"""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """创建临时DataManager实例"""
        return DataManager(storage_path=str(tmp_path))
    
    def test_save_with_validation(self, manager):
        """测试保存时进行验证"""
        # 创建有效数据
        valid_data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 10.5, 10.3],
            'high': [10.8, 10.9, 10.7],
            'low': [9.8, 10.2, 10.0],
            'close': [10.5, 10.3, 10.6],
            'volume': [1000000, 1200000, 900000]
        })
        
        # 保存数据（应该成功）
        manager.save_market_data(valid_data, 'daily', '000001.SZ')
        
        # 验证数据已保存
        loaded_data = manager.load_market_data('daily', '000001.SZ')
        assert len(loaded_data) == 3
    
    def test_validation_report_structure(self, manager):
        """测试验证报告结构完整性"""
        data = pd.DataFrame({
            'stock_code': ['000001.SZ'] * 3,
            'date': ['20240101', '20240102', '20240103'],
            'close': [10.0, 10.1, 10.2]
        })
        
        report = manager.validate_data(data, 'daily')
        
        # 验证报告包含所有必需字段
        assert 'is_valid' in report
        assert 'errors' in report
        assert 'warnings' in report
        assert 'anomalies' in report
        assert 'statistics' in report
        
        # 验证字段类型
        assert isinstance(report['is_valid'], bool)
        assert isinstance(report['errors'], list)
        assert isinstance(report['warnings'], list)
        assert isinstance(report['anomalies'], list)
        assert isinstance(report['statistics'], dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
