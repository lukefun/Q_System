# Q_System 快速参考指南

> 快速查找常用命令、代码片段和最佳实践

## 📋 目录

- [环境管理](#环境管理)
- [数据获取](#数据获取)
- [数据处理](#数据处理)
- [数据存储](#数据存储)
- [测试运行](#测试运行)
- [常用代码片段](#常用代码片段)

---

## 🔧 环境管理

### 创建和激活环境
```bash
# 创建环境
conda create -n quants python=3.8

# 激活环境
conda activate quants

# 安装依赖
pip install -r requirements.txt

# 验证环境
python -c "import pandas; import numpy; print('环境配置成功')"
```

### 环境问题排查
```bash
# 查看当前Python路径
python -c "import sys; print(sys.executable)"

# 查看已安装包
pip list

# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

---

## 📊 数据获取

### 获取单只股票数据
```python
from src.data_retriever import DataRetriever

retriever = DataRetriever()

# 获取日线数据
df = retriever.get_market_data(
    stock_code='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31',
    period='1d'
)
```

### 批量获取多只股票
```python
# 获取多只股票
stock_list = ['000001.SZ', '600000.SH', '000002.SZ']

data_dict = {}
for stock in stock_list:
    data_dict[stock] = retriever.get_market_data(
        stock_code=stock,
        start_date='2023-01-01',
        end_date='2023-12-31'
    )
```

### 获取分钟数据
```python
# 获取5分钟K线
df_5min = retriever.get_market_data(
    stock_code='000001.SZ',
    start_date='2023-12-01',
    end_date='2023-12-31',
    period='5m'
)
```

---

## 🔄 数据处理

### 价格复权
```python
from src.price_adjuster import PriceAdjuster

adjuster = PriceAdjuster()

# 前复权
df_forward = adjuster.adjust_price(
    df,
    method='forward',
    adjust_columns=['open', 'high', 'low', 'close']
)

# 后复权
df_backward = adjuster.adjust_price(
    df,
    method='backward',
    adjust_columns=['open', 'high', 'low', 'close']
)
```

### 数据对齐
```python
from src.data_alignment import DataAlignment

aligner = DataAlignment()

# 对齐多只股票数据
aligned_data = aligner.align_multiple_stocks(
    data_dict,
    method='ffill'  # 前向填充
)

# 检测前视偏差
bias_report = aligner.detect_lookahead_bias(
    strategy_data=strategy_df,
    market_data=market_df
)
```

### 计算技术指标
```python
# 移动平均线
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()

# 收益率
df['returns'] = df['close'].pct_change()

# 波动率(20日)
df['volatility'] = df['returns'].rolling(window=20).std()

# MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
```

### 基本面数据
```python
from src.fundamental_handler import FundamentalHandler

handler = FundamentalHandler()

# 获取财务数据
financial = handler.get_financial_data(
    stock_code='000001.SZ',
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# 计算财务指标
metrics = handler.calculate_metrics(financial)
```

### 行业分类
```python
from src.industry_mapper import IndustryMapper

mapper = IndustryMapper()

# 获取股票行业
industry = mapper.get_stock_industry('000001.SZ')

# 获取行业内股票
stocks = mapper.get_industry_stocks('银行')
```

---

## 💾 数据存储

### 保存数据到HDF5
```python
from src.data_manager import DataManager

manager = DataManager(db_path='data/market_data.h5')

# 保存单只股票
manager.save_stock_data(
    stock_code='000001.SZ',
    data=df,
    data_type='daily'
)

# 批量保存
for stock_code, data in data_dict.items():
    manager.save_stock_data(
        stock_code=stock_code,
        data=data,
        data_type='daily'
    )
```

### 读取数据
```python
# 读取单只股票
df = manager.load_stock_data(
    stock_code='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 读取多只股票
stock_list = ['000001.SZ', '600000.SH']
data_dict = manager.load_multiple_stocks(
    stock_list=stock_list,
    start_date='2023-01-01',
    end_date='2023-12-31'
)
```

### 增量更新
```python
# 更新单只股票
manager.update_stock_data(
    stock_code='000001.SZ',
    new_data=new_df
)

# 批量增量更新
from src.full_market_downloader import FullMarketDownloader

downloader = FullMarketDownloader()
downloader.incremental_update(
    stock_list=stock_list,
    update_days=1  # 更新最近1天
)
```

---

## 📈 数据可视化

### K线图
```python
from src.visualizer import Visualizer

viz = Visualizer()

# 基础K线图
viz.plot_candlestick(
    df,
    title='000001.SZ K线图',
    show_volume=True
)

# 添加移动平均线
viz.plot_candlestick_with_ma(
    df,
    ma_periods=[5, 10, 20],
    title='000001.SZ K线图(含均线)'
)
```

### 收益率分析
```python
# 收益率分布
viz.plot_returns_distribution(
    df['returns'],
    title='收益率分布'
)

# 累计收益曲线
df['cumulative_returns'] = (1 + df['returns']).cumprod()
viz.plot_line(
    df['cumulative_returns'],
    title='累计收益曲线'
)
```

---

## 🧪 测试运行

### 运行所有测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行并显示覆盖率
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
start htmlcov/index.html  # Windows
```

### 运行特定测试
```bash
# 运行单元测试
pytest tests/unit/ -v

# 运行属性测试
pytest tests/property/ -v

# 运行集成测试
pytest tests/integration/ -v

# 运行特定文件
pytest tests/unit/test_data_retriever.py -v

# 运行特定测试函数
pytest tests/unit/test_data_retriever.py::test_get_market_data -v
```

### 调试测试
```bash
# 显示print输出
pytest tests/unit/test_data_retriever.py -v -s

# 在第一个失败处停止
pytest tests/ -x

# 显示最慢的10个测试
pytest tests/ --durations=10
```

---

## 📝 常用代码片段

### 1. 完整数据获取流程
```python
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from src.data_manager import DataManager

# 初始化
retriever = DataRetriever()
adjuster = PriceAdjuster()
manager = DataManager()

# 获取数据
df = retriever.get_market_data(
    stock_code='000001.SZ',
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# 复权
df_adjusted = adjuster.adjust_price(df, method='forward')

# 保存
manager.save_stock_data(
    stock_code='000001.SZ',
    data=df_adjusted,
    data_type='daily'
)
```

### 2. 批量下载全市场数据
```python
from src.full_market_downloader import FullMarketDownloader

downloader = FullMarketDownloader()

# 获取股票列表
stock_list = downloader.get_all_stocks()

# 批量下载
downloader.download_all_stocks(
    stock_list=stock_list,
    start_date='2020-01-01',
    end_date='2023-12-31',
    workers=4  # 4个并行线程
)
```

### 3. 数据质量检查
```python
# 检查缺失值
print(f"缺失值数量: {df.isnull().sum()}")

# 检查重复值
print(f"重复行数: {df.duplicated().sum()}")

# 检查数据范围
print(f"日期范围: {df.index.min()} 到 {df.index.max()}")
print(f"价格范围: {df['close'].min()} 到 {df['close'].max()}")

# 检查异常值
returns = df['close'].pct_change()
outliers = returns[abs(returns) > 0.2]  # 涨跌幅超过20%
print(f"异常值数量: {len(outliers)}")
```

### 4. 避免前视偏差
```python
# 错误: 使用当天数据
signal = df['close'] > df['close'].rolling(20).mean()

# 正确: 使用前一天数据
signal = df['close'].shift(1) > df['close'].shift(1).rolling(20).mean()

# 或者整体shift
df_lagged = df.shift(1)
signal = df_lagged['close'] > df_lagged['close'].rolling(20).mean()
```

### 5. 性能优化
```python
# 使用向量化操作而非循环
# 慢速方法
returns = []
for i in range(1, len(df)):
    ret = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1]
    returns.append(ret)

# 快速方法
returns = df['close'].pct_change()

# 使用numba加速
from numba import jit

@jit(nopython=True)
def calculate_indicator(prices):
    # 计算逻辑
    return result
```

### 6. 错误处理
```python
import logging

logger = logging.getLogger(__name__)

try:
    df = retriever.get_market_data(
        stock_code='000001.SZ',
        start_date='2023-01-01',
        end_date='2023-12-31'
    )
except Exception as e:
    logger.error(f"数据获取失败: {e}")
    # 重试或使用缓存数据
    df = manager.load_stock_data('000001.SZ')
```

### 7. 配置管理
```python
# config.py
import os
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
LOG_DIR = PROJECT_ROOT / 'logs'

# XtData配置
XTDATA_ACCOUNT_ID = os.getenv('XTDATA_ACCOUNT_ID', '')
XTDATA_ACCOUNT_KEY = os.getenv('XTDATA_ACCOUNT_KEY', '')

# 数据库配置
DB_PATH = DATA_DIR / 'market_data.h5'

# 使用配置
from config import DB_PATH
manager = DataManager(db_path=str(DB_PATH))
```

---

## 🔍 常见问题快速解决

### 问题1: ModuleNotFoundError
```bash
# 确保在正确的环境中
conda activate quants

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2: XtData连接失败
```python
# 检查配置
import os
print(os.getenv('XTDATA_ACCOUNT_ID'))
print(os.getenv('XTDATA_ACCOUNT_KEY'))

# 测试连接
from src.xtdata_client import XtDataClient
client = XtDataClient()
client.connect()
```

### 问题3: 数据为空
```python
# 检查日期范围
print(f"开始日期: {start_date}")
print(f"结束日期: {end_date}")

# 检查股票代码格式
# 正确: '000001.SZ', '600000.SH'
# 错误: '000001', 'SZ000001'
```

### 问题4: 内存不足
```python
# 分批处理
batch_size = 100
for i in range(0, len(stock_list), batch_size):
    batch = stock_list[i:i+batch_size]
    process_batch(batch)
    
# 使用生成器
def data_generator(stock_list):
    for stock in stock_list:
        yield load_data(stock)
```

### 问题5: 测试失败
```bash
# 查看详细错误
pytest tests/unit/test_data_retriever.py -v -s

# 只运行失败的测试
pytest --lf

# 跳过慢速测试
pytest -m "not slow"
```

---

## 📚 快速链接

### 文档
- [完整学习指南](LEARNING_GUIDE.md)
- [环境配置指南](ENVIRONMENT.md)
- [代码文档](CODE_DOCUMENTATION.md)
- [XtData API文档](xtdata.md)

### 示例代码
- [基础数据获取](../examples/01_basic_data_retrieval.py)
- [价格复权](../examples/02_price_adjustment.py)
- [完整工作流](../examples/08_full_workflow.py)
- [前视偏差演示](../examples/10_lookahead_bias_demo.py)

### 练习
- [Week1练习](../exercises/week1/)
- [Week2练习](../exercises/week2/)

---

## 💡 最佳实践

1. **始终在虚拟环境中工作**
2. **使用版本控制(Git)**
3. **编写测试代码**
4. **添加详细注释**
5. **定期备份数据**
6. **注意前视偏差**
7. **验证数据质量**
8. **优化代码性能**

---

**最后更新**: 2026-01-20
