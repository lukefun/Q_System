"""
pytest配置和共享fixtures

提供测试所需的mock对象、示例数据和测试工具
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock
from pathlib import Path
import tempfile
import shutil


# ============================================================================
# pytest配置
# ============================================================================

def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "property: marks tests as property-based tests"
    )


# ============================================================================
# 临时目录fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_hdf5_path(temp_dir):
    """临时HDF5文件路径"""
    return temp_dir / "test_market_data.h5"


# ============================================================================
# Mock对象fixtures
# ============================================================================

@pytest.fixture
def mock_xtdata_client():
    """Mock XtData客户端"""
    client = Mock()
    client.is_connected.return_value = True
    client.connect.return_value = True
    client.disconnect.return_value = None
    return client


# ============================================================================
# 示例数据fixtures
# ============================================================================

@pytest.fixture
def sample_stock_codes():
    """示例股票代码列表"""
    return ["000001.SZ", "600000.SH", "000002.SZ"]


@pytest.fixture
def sample_date_range():
    """示例日期范围"""
    return {
        "start_date": "20240101",
        "end_date": "20240110"
    }


@pytest.fixture
def sample_daily_data():
    """
    示例日线数据
    
    包含5个交易日的OHLCV数据
    """
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    
    return pd.DataFrame({
        "stock_code": ["000001.SZ"] * 5,
        "date": [d.strftime("%Y%m%d") for d in dates],
        "open": [10.0, 10.5, 10.3, 10.8, 10.6],
        "high": [10.8, 10.9, 10.7, 11.0, 10.9],
        "low": [9.8, 10.2, 10.0, 10.5, 10.3],
        "close": [10.5, 10.3, 10.6, 10.7, 10.8],
        "volume": [1000000, 1200000, 900000, 1100000, 1050000],
        "amount": [10500000, 12360000, 9540000, 11770000, 11340000]
    })


@pytest.fixture
def sample_tick_data():
    """
    示例tick数据
    
    包含10条tick记录
    """
    base_time = datetime(2024, 1, 1, 9, 30, 0)
    
    return pd.DataFrame({
        "stock_code": ["000001.SZ"] * 10,
        "timestamp": [
            int((base_time + timedelta(seconds=i)).timestamp() * 1000)
            for i in range(10)
        ],
        "price": [10.0 + i * 0.1 for i in range(10)],
        "volume": [100 * (i + 1) for i in range(10)],
        "bid_price": [10.0 + i * 0.1 - 0.01 for i in range(10)],
        "ask_price": [10.0 + i * 0.1 + 0.01 for i in range(10)],
        "bid_volume": [1000 * (i + 1) for i in range(10)],
        "ask_volume": [1000 * (i + 1) for i in range(10)]
    })


@pytest.fixture
def sample_fundamental_data():
    """
    示例基本面数据
    
    包含财务指标数据
    """
    return pd.DataFrame({
        "stock_code": ["000001.SZ", "000001.SZ", "000002.SZ"],
        "report_date": ["20231231", "20230930", "20231231"],
        "announce_date": ["20240330", "20231030", "20240330"],
        "pe_ratio": [15.5, 14.8, 20.3],
        "pb_ratio": [1.8, 1.7, 2.5],
        "roe": [0.12, 0.11, 0.15],
        "revenue": [1000000000, 750000000, 500000000],
        "net_profit": [120000000, 82500000, 75000000],
        "total_assets": [5000000000, 4800000000, 2000000000],
        "total_equity": [1000000000, 950000000, 500000000]
    })


@pytest.fixture
def sample_industry_structure():
    """
    示例行业分类结构
    
    申万行业三级分类
    """
    return {
        "level1": {
            "code": "801010",
            "name": "农林牧渔",
            "level2": [
                {
                    "code": "801011",
                    "name": "农业",
                    "level3": [
                        {"code": "801012", "name": "种植业"},
                        {"code": "801013", "name": "养殖业"}
                    ]
                }
            ]
        }
    }


@pytest.fixture
def sample_adjust_factors():
    """
    示例复权因子数据
    """
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    
    return pd.DataFrame({
        "date": [d.strftime("%Y%m%d") for d in dates],
        "adjust_factor": [1.0, 1.0, 1.05, 1.05, 1.05]  # 第3天有分红
    })


@pytest.fixture
def sample_price_data():
    """
    示例价格数据（用于复权测试）
    
    包含5个交易日的OHLCV数据
    """
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    
    return pd.DataFrame({
        "date": [d.strftime("%Y%m%d") for d in dates],
        "open": [10.0, 10.5, 10.3, 10.8, 10.6],
        "high": [10.8, 10.9, 10.7, 11.0, 10.9],
        "low": [9.8, 10.2, 10.0, 10.5, 10.3],
        "close": [10.5, 10.3, 10.6, 10.7, 10.8],
        "volume": [1000000, 1200000, 900000, 1100000, 1050000]
    })


# ============================================================================
# 测试工具函数
# ============================================================================

def assert_dataframe_equal(df1: pd.DataFrame, df2: pd.DataFrame, **kwargs):
    """
    断言两个DataFrame相等
    
    封装pandas.testing.assert_frame_equal，提供更好的错误消息
    """
    try:
        pd.testing.assert_frame_equal(df1, df2, **kwargs)
    except AssertionError as e:
        print(f"\nDataFrame comparison failed:")
        print(f"Expected:\n{df2}")
        print(f"Got:\n{df1}")
        raise e


def generate_random_ohlcv(num_days: int = 10, base_price: float = 10.0):
    """
    生成随机OHLCV数据用于测试
    
    Args:
        num_days: 生成天数
        base_price: 基础价格
    
    Returns:
        包含OHLCV数据的DataFrame
    """
    dates = pd.date_range("2024-01-01", periods=num_days, freq="D")
    data = []
    
    for i, date in enumerate(dates):
        # 生成符合OHLC关系的价格
        low = base_price * (0.95 + np.random.random() * 0.05)
        high = base_price * (1.0 + np.random.random() * 0.1)
        open_price = low + (high - low) * np.random.random()
        close = low + (high - low) * np.random.random()
        volume = int(1000000 * (0.5 + np.random.random()))
        
        data.append({
            "stock_code": "000001.SZ",
            "date": date.strftime("%Y%m%d"),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": volume,
            "amount": round(close * volume, 2)
        })
        
        # 价格随机游走
        base_price = close
    
    return pd.DataFrame(data)
