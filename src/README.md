# src/ - 数据处理模块

此目录包含数据获取、处理、存储和可视化的核心功能模块，基于 XtQuant（国金证券 QMT）数据源构建。

## 模块概览

```
src/
├── __init__.py              # 模块初始化，导出公共接口
├── xtdata_client.py         # XtQuant 数据接口封装
├── data_retriever.py        # 行情数据获取
├── data_manager.py          # 数据存储管理（HDF5）
├── data_alignment.py        # 数据对齐与时间处理
├── price_adjuster.py        # 复权处理
├── fundamental_handler.py   # 财务数据处理
├── industry_mapper.py       # 行业分类映射
├── full_market_downloader.py # 全市场数据下载
└── visualizer.py            # 数据可视化
```

## 文件详细说明

### 数据获取层

| 文件 | 功能 | 主要类/函数 |
|------|------|-------------|
| `xtdata_client.py` | XtQuant API 封装 | `XtDataClient` - 连接管理、请求重试 |
| `data_retriever.py` | 行情数据获取 | `DataRetriever` - 获取K线、Tick数据 |
| `fundamental_handler.py` | 财务数据处理 | `FundamentalHandler` - 财报、估值数据 |
| `industry_mapper.py` | 行业分类 | `IndustryMapper` - 申万行业分类映射 |

### 数据处理层

| 文件 | 功能 | 主要类/函数 |
|------|------|-------------|
| `price_adjuster.py` | 复权计算 | `PriceAdjuster` - 前复权/后复权处理 |
| `data_alignment.py` | 数据对齐 | `DataAligner` - 时间序列对齐、缺失处理 |
| `full_market_downloader.py` | 全市场下载 | `FullMarketDownloader` - 批量下载全市场数据 |

### 数据存储层

| 文件 | 功能 | 主要类/函数 |
|------|------|-------------|
| `data_manager.py` | HDF5 存储管理 | `DataManager` - 数据存取、增量更新、导出 |

### 可视化层

| 文件 | 功能 | 主要类/函数 |
|------|------|-------------|
| `visualizer.py` | 图表绑制 | `Visualizer` - K线图、技术指标、收益曲线 |

## 使用示例

```python
from src.data_retriever import DataRetriever
from src.data_manager import DataManager
from src.price_adjuster import PriceAdjuster
from src.visualizer import Visualizer

# 1. 获取数据
retriever = DataRetriever()
df = retriever.get_kline('000001.SZ', '2023-01-01', '2023-12-31')

# 2. 复权处理
adjuster = PriceAdjuster()
df_adjusted = adjuster.adjust(df, adjust_type='front')

# 3. 存储数据
manager = DataManager()
manager.save_kline('000001.SZ', df_adjusted)

# 4. 可视化
viz = Visualizer()
viz.plot_kline(df_adjusted)
```

## 依赖关系

```
┌──────────────────┐
│   examples/      │  ← 示例代码调用
│   exercises/     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│  data_retriever  │────►│   data_manager   │
│  price_adjuster  │     │    (HDF5存储)    │
│ fundamental_handler    └──────────────────┘
│  industry_mapper │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  xtdata_client   │  ← 底层 XtQuant API
└──────────────────┘
```

## 配置依赖

所有模块从根目录 `config.py` 读取配置：

```python
from config import (
    DATA_DIR,        # 数据目录
    HDF5_PATH,       # HDF5数据库路径
    logger,          # 日志对象
    DataError,       # 数据异常
    ValidationError  # 验证异常
)
```

## 开发规范

- 所有数据处理函数需处理边界情况（空数据、无效日期等）
- 网络请求需包含重试机制（参见 `xtdata_client.py`）
- 数据验证失败应抛出 `ValidationError`
- 所有模块需有对应的单元测试（`tests/unit/`）
