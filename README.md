# Q_System - 量化交易全栈培训系统

基于 XtQuant（国金证券 QMT）的量化交易回测与实盘框架。采用策略-引擎分离架构，支持自定义策略的回测验证与实盘交易。

本项目是120天量化交易培训计划的实践平台，涵盖从数据工程到策略开发的完整技术栈。

## 🚀 快速导航

**新手入门？** 请从这里开始：

- 📖 [**学习路径导航**](docs/guides/STUDY_PATH.md) - 完整的两周学习路线图
- 📚 [**完整学习指南**](docs/guides/LEARNING_GUIDE.md) - 详细的每日学习计划
- ⚡ [**快速参考手册**](docs/guides/QUICK_REFERENCE.md) - 常用命令和代码速查

**已经熟悉项目？** 快速跳转：

- [环境配置](#环境配置)
- [快速开始](#快速开始)
- [API文档](#api文档)

## 学习目标

通过本项目，你将掌握：

1. **金融数据工程** (Week 2)
   - XtData API集成与市场数据获取
   - 价格复权机制（前复权/后复权）
   - 基本面数据ETL与时间点正确性
   - 行业分类管理与板块分析
   - 数据持久化与增量更新
   - 金融数据可视化
   - 未来函数防范与回测真实性

2. **量化策略开发** (Week 3+)
   - 策略-引擎分离架构
   - 回测与实盘统一接口
   - 风险控制与资金管理
   - 策略性能评估

3. **生产级系统设计**
   - 模块化架构设计
   - 错误处理与日志管理
   - 数据质量检查
   - 性能优化与扩展性

## 功能特性

### 数据工程模块 (Week 2)

- **XtData API集成**: 封装XtData接口，支持历史数据和实时数据获取
- **价格复权处理**: 实现前复权和后复权算法，确保回测准确性
- **基本面数据ETL**: 处理财务指标（PE、PB、ROE），严格时间点正确性
- **行业分类管理**: 支持申万行业分类查询和历史变更追踪
- **数据持久化**: HDF5高效存储，支持增量更新和CSV导出
- **数据可视化**: K线图、成交量、技术指标可视化
- **数据质量检查**: 异常值检测、缺口识别、完整性验证

### 交易系统模块

- **策略-引擎分离**: 策略逻辑与执行引擎解耦，便于策略复用与测试
- **双模式运行**: 支持回测模式 (`BacktestEngine`) 和实盘模式 (`LiveRunner`)
- **安全机制**: 内置运行模式锁 + 人工确认防火墙，防止误操作
- **统一接口**: 策略通过 `Context` 对象与引擎交互，回测与实盘代码一致

## 项目结构

```plaintext
Q_System/
├── main.py              # 回测启动脚本
├── run_live.py          # 实盘启动脚本
├── config.py            # 配置文件（API密钥、存储路径）
├── requirements.txt     # 生产依赖
├── requirements-dev.txt # 开发依赖
├── environment.yml      # Conda 环境配置
│
├── core/                # 核心引擎模块
│   ├── README.md            # 模块说明
│   ├── engine.py            # 回测引擎
│   ├── live_runner.py       # 实盘引擎
│   ├── strategy.py          # 策略基类
│   └── context.py           # 上下文对象 (核心交互接口)
│
├── src/                 # 数据工程模块
│   ├── README.md            # 模块说明
│   ├── xtdata_client.py     # XtData API客户端封装
│   ├── data_retriever.py    # 数据获取器
│   ├── price_adjuster.py    # 价格复权处理器
│   ├── fundamental_handler.py # 基本面数据处理器
│   ├── industry_mapper.py   # 行业分类映射器
│   ├── data_manager.py      # 数据持久化管理器
│   ├── visualizer.py        # 金融数据可视化器
│   ├── data_alignment.py    # 数据对齐工具
│   └── full_market_downloader.py  # 全市场数据下载
│
├── strategies/          # 策略实现
│   ├── README.md            # 策略开发指南
│   └── double_ma.py         # 双均线策略示例
│
├── examples/            # 示例脚本
│   ├── README.md            # 示例说明文档
│   ├── 01_basic_data_retrieval.py
│   ├── 02_price_adjustment.py
│   └── ...
│
├── exercises/           # 学习练习
│   ├── README.md            # 练习说明
│   ├── week1/               # 第一周：Python基础
│   └── week2/               # 第二周：数据工程
│
├── tests/               # 测试套件
│   ├── README.md            # 测试说明
│   ├── conftest.py          # pytest 配置
│   ├── unit/                # 单元测试
│   ├── property/            # 属性测试
│   └── integration/         # 集成测试
│
├── data/                # 本地数据存储
│   ├── README.md            # 数据目录说明
│   ├── market_data.h5       # HDF5数据库
│   ├── cache/               # 缓存目录
│   └── csv_exports/         # CSV导出文件
│
├── logs/                # 日志文件
│
├── scripts/             # 工具脚本
│   ├── README.md            # 脚本说明
│   ├── setup/               # 环境配置脚本
│   │   ├── setup_env.bat
│   │   ├── setup_env.ps1
│   │   ├── scripts\setup\start_isolated.bat
│   │   └── start_isolated.ps1
│   ├── verify/              # 验证脚本
│   │   ├── check_env.py
│   │   └── verify_week2_setup.py
│   └── utils/               # 工具脚本
│       ├── scripts\utils\check.bat
│       └── git_commit_all.bat
│
└── docs/                # 文档
    ├── README.md            # 文档目录说明
    ├── guides/              # 用户指南
    │   ├── LEARNING_GUIDE.md
    │   ├── QUICK_REFERENCE.md
    │   ├── SETUP_GUIDE.md
    │   └── STUDY_PATH.md
    ├── api/                 # API 文档
    │   ├── xtdata.md
    │   └── xttrader.md
    ├── plans/               # 计划文档
    │   └── plan.md
    ├── reports/             # 任务验证报告
    │   └── TASK_*.md
    └── notes/               # 学习笔记
        └── week1_*.md
```

## 环境配置

### 系统要求

| 项目 | 要求 |
| ------ | ------ |
| Python | **3.8.x** (miniQMT 硬性要求) |
| 操作系统 | Windows (QMT 仅支持 Windows) |
| Conda | 推荐使用 Miniconda |
| QMT | 国金证券 MiniQMT 客户端 |

### 核心依赖

| 包名 | 版本 | 说明 |
| ------ | ------ | ------ |
| xtquant | 250516+ | 国金证券 QMT 交易接口 |
| pandas | 2.0+ | 数据处理 |
| numpy | 1.24+ | 数值计算 |

---

## 初始化项目 (按场景选择)

### 场景一：新电脑首次配置 (推荐)

适用于：刚克隆项目，电脑上没有 quants 环境

```bash
# 1. 克隆项目
git clone <repository-url>
cd Q_System

# 2. 一键配置 (双击运行)
scripts\setup\setup_env.bat
```

该脚本会自动：创建 quants 环境 → 安装依赖 → 安装 xtquant → 验证环境

### 场景二：已有 quants 环境

适用于：电脑上已存在 quants conda 环境

```bash
# 1. 激活环境
conda activate quants

# 2. 验证环境
python scripts/verify/check_env.py

# 3. 如有缺失依赖，补充安装
pip install -r requirements.txt
```

### 场景三：多 Python 版本混乱的电脑

适用于：系统安装了多个 Python 版本，存在包加载混乱

**症状检测**：

```bash
conda activate quants
python scripts/verify/check_env.py
# 如果看到 "[WARN] 检测到 X 个 site-packages 路径，可能存在版本混乱"
```

**解决方案 A - 使用隔离模式启动 (推荐)**：

```bash
# 双击此脚本启动开发环境
scripts\setup\start_isolated.bat
```

该脚本设置 `PYTHONNOUSERSITE=1`，禁用用户全局包，确保只使用 conda 环境。

**解决方案 B - 修复环境隔离**：

```bash
# 重新安装包到 conda 环境
scripts\setup\fix_env_isolation.bat
```

### 场景四：手动从零创建环境

适用于：需要完全控制环境配置

```bash
# 1. 创建 Python 3.8 环境 (版本必须是 3.8)
conda create -n quants python=3.8 -y

# 2. 激活环境
conda activate quants

# 3. 安装依赖
pip install -r requirements.txt

    ```text
    完整命令示例 (以阿里源为例):
    requirements-dev.txt
    
    运行
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    常用国内镜像源地址：
    阿里云 (推荐): https://mirrors.aliyun.com/pypi/simple/
    清华大学: https://pypi.tuna.tsinghua.edu.cn/simple/
    华为云: https://repo.huaweicloud.com/repository/pypi/simple/
    豆瓣: http://pypi.douban.com/simple/
    中国科学技术大学: https://pypi.mirrors.ustc.edu.cn/simple/
    ```

# 4. 安装 xtquant
pip install xtquant

# 5. 验证
python scripts/verify/check_env.py
```

### 场景五：从 environment.yml 恢复环境

适用于：需要完全复制现有环境配置

```bash
# 1. 从 YAML 创建环境
conda env create -f environment.yml

# 2. 激活环境
conda activate quants

# 3. 安装 xtquant (YAML 中未包含)
pip install xtquant
```

---

## 日常开发启动

### 方式一：隔离模式启动 (推荐)

```bash
# 双击运行，自动配置隔离环境
scripts\setup\start_isolated.bat

# 然后在打开的窗口中运行
python main.py
```

### 方式二：常规启动

```bash
# 激活环境
conda activate quants

# 运行项目
python main.py
```

### 方式三：命令行一步启动

```bash
# 使用 conda run (无需激活)
conda run -n quants python main.py
```

---

## 环境验证

### 快速检查

```bash
# 双击运行
scripts\utils\check.bat
```

### 详细检查

```bash
conda activate quants
python scripts/verify/check_env.py
```

### 验证通过标准

```text
[PASS] Python 版本     ← 3.8.x
[PASS] Conda 环境      ← quants
[PASS] 核心依赖包      ← pandas, numpy
[PASS] XtQuant         ← xtdata 可用
[PASS] 项目模块        ← 全部可导入
```

> 详细文档: [docs/guides/ENVIRONMENT.md](docs/guides/ENVIRONMENT.md) | [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md)

## 快速开始

### Week 2: 金融数据工程快速入门

#### 1. 配置XtData API

编辑 `config.py` 文件，配置你的XtData账户信息：

```python
# XtData API配置
XTDATA_ACCOUNT_ID = '你的账户ID'
XTDATA_ACCOUNT_KEY = '你的账户密钥'

# 数据存储路径
DATA_STORAGE_PATH = './data'
```

#### 2. 运行示例脚本

```bash
# 激活环境
conda activate quants

# 示例1: 获取市场数据
python examples/01_basic_data_retrieval.py

# 示例2: 价格复权处理
python examples/02_price_adjustment.py

# 示例3: 基本面数据分析
python examples/03_fundamental_data.py

# 示例4: 行业分类查询
python examples/04_industry_classification.py

# 示例5: 数据持久化
python examples/05_data_persistence.py

# 示例6: K线图可视化
python examples/06_visualization.py

# 示例7: 增量更新
python examples/07_incremental_update.py
```

#### 3. 构建本地数据库

```bash
# 下载全市场日线数据（需要较长时间）
python examples/09_build_local_database.py
```

#### 4. 数据工程API使用示例

```python
from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from src.data_manager import DataManager
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY, DATA_STORAGE_PATH

# 1. 初始化客户端
client = XtDataClient(XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY)
client.connect()

# 2. 获取历史数据
retriever = DataRetriever(client)
data = retriever.download_history_data(
    stock_codes=['000001.SZ', '600000.SH'],
    start_date='20240101',
    end_date='20241231',
    period='1d'
)

# 3. 应用前复权（回测推荐）
adjuster = PriceAdjuster(client)
adjusted_data = adjuster.forward_adjust(data, '000001.SZ')

# 4. 保存到本地数据库
manager = DataManager(DATA_STORAGE_PATH)
manager.save_market_data(adjusted_data, 'daily', '000001.SZ')

# 5. 增量更新
new_records = manager.incremental_update(
    retriever,
    ['000001.SZ', '600000.SH'],
    'daily'
)
print(f"更新了 {new_records} 条新记录")

# 6. 查询数据
loaded_data = manager.load_market_data(
    'daily',
    stock_code='000001.SZ',
    start_date='20240601',
    end_date='20240630'
)
```

### 策略开发快速入门

### 运行回测

```bash
python main.py
```

默认配置：

- 标的: 比亚迪 (002594.SZ)
- 时间: 2025-01-01 ~ 2025-12-25
- 策略: 双均线策略 (MA5/MA20)

### 运行实盘 (模拟模式)

```bash
python run_live.py
```

> 首次运行默认为 `sim` 模拟模式，不会发送真实订单。

## 策略开发

所有策略需继承 `BaseStrategy` 并实现两个抽象方法：

```python
from core.strategy import BaseStrategy

class MyStrategy(BaseStrategy):

    def initialize(self, context):
        """策略初始化，只执行一次"""
        context.user_data['target'] = '000001.SZ'

    def handle_bar(self, context, bar_dict):
        """每根 K 线执行一次"""
        stock = context.user_data['target']
        if stock not in bar_dict:
            return

        bar = bar_dict[stock]
        # 策略逻辑...

        if should_buy:
            context.order(stock, 1000)   # 买入 1000 股
        elif should_sell:
            context.order(stock, -1000)  # 卖出 1000 股
```

### Context 对象

| 属性/方法 | 说明 |
| ---------- | ------ |
| `cash` | 可用资金 |
| `total_asset` | 总资产 |
| `positions` | 持仓字典 `{stock_code: volume}` |
| `current_dt` | 当前时间 |
| `user_data` | 策略自定义变量存储 |
| `order(stock, volume)` | 下单 (正数买入，负数卖出) |
| `log(msg)` | 日志输出 |

## 安全机制

实盘模式内置双重保护：

### 1. 运行模式锁

```python
RUN_MODE = 'sim'   # 'sim' 模拟模式 | 'real' 实盘模式
```

只有明确设置为 `'real'` 时才会发送真实订单。

### 2. 人工确认防火墙

```python
MANUAL_CONFIRM = True  # 下单前必须手动输入 'y' 确认
```

实盘模式下，每笔订单都会阻塞等待用户确认：

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!! [教学实盘拦截] 正准备发送交易指令 !!!
!!! 标的: 002594.SZ
!!! 方向: 买入
!!! 数量: 1000
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
>>> 请输入 'y' 确认下单，输入其他任意键取消:
```

## 数据流

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   XtQuant   │────▶│   Engine    │────▶│  Strategy   │
│  (数据源)   │     │ (时间循环)  │     │ (交易逻辑)  │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                          │                   │
                          ▼                   ▼
                    ┌─────────────────────────────┐
                    │          Context            │
                    │  (资金/持仓/下单/日志)       │
                    └─────────────────────────────┘
```

## 配置说明

### 回测配置 (main.py)

```python
start_date = '20250101'      # 回测开始日期
end_date = '20251225'        # 回测结束日期
stock_list = ['002594.SZ']   # 股票列表
```

### 实盘配置 (run_live.py)

```python
MINI_QMT_PATH = r'D:\迅投极速交易终端\userdata_mini'  # QMT 路径
ACCOUNT_ID = '您的账号'       # 资金账号
RUN_MODE = 'sim'             # 运行模式
MANUAL_CONFIRM = True        # 人工确认
```

## License

MIT

---

## API文档

### 核心模块文档

- **XtDataClient**: [src/xtdata_client.py](src/xtdata_client.py) - XtData API客户端封装
- **DataRetriever**: [src/data_retriever.py](src/data_retriever.py) - 市场数据获取器
- **PriceAdjuster**: [src/price_adjuster.py](src/price_adjuster.py) - 价格复权处理器
- **FundamentalHandler**: [src/fundamental_handler.py](src/fundamental_handler.py) - 基本面数据处理器
- **IndustryMapper**: [src/industry_mapper.py](src/industry_mapper.py) - 行业分类映射器
- **DataManager**: [src/data_manager.py](src/data_manager.py) - 数据持久化管理器
- **Visualizer**: [src/visualizer.py](src/visualizer.py) - 金融数据可视化器

### 详细文档

- [XtData API参考](docs/api/xtdata.md) - XtData接口详细说明
- [示例脚本说明](examples/README.md) - 所有示例脚本的使用指南
- [120天学习计划](docs/plans/plan.md) - 完整的培训计划和学习路径

### 在线资源

- [XtQuant官方文档](https://dict.thinktrader.net/nativeApi/start_now.html)
- [Pandas官方文档](https://pandas.pydata.org/docs/)
- [Hypothesis测试库](https://hypothesis.readthedocs.io/)

---

## 常见问题

### Q1: 如何获取XtData账户？

访问国金证券QMT官网注册账户，获取API密钥。

### Q2: 前复权和后复权有什么区别？

- **前复权**: 保持当前价格不变，向前调整历史价格。适用于回测，避免未来函数。
- **后复权**: 保持历史价格不变，向后调整当前价格。适用于展示，保持价格连续性。

详见：[examples/02_price_adjustment.py](examples/02_price_adjustment.py)

### Q3: 什么是未来函数？如何避免？

未来函数是指在历史分析中使用了未来信息的错误。系统通过以下机制防范：

1. 基本面数据使用公告日期（announce_date）而非报告期
2. 回测默认使用前复权
3. 数据对齐采用保守策略

详见：[examples/10_lookahead_bias_demo.py](examples/10_lookahead_bias_demo.py)

### Q4: 如何处理数据缺失？

系统提供多层数据质量检查：

```python
from src.data_manager import DataManager

manager = DataManager('./data')
# 数据验证会自动检测：
# - 异常值（负价格、极端值）
# - 数据缺口
# - 数据类型错误
```

### Q5: 增量更新如何工作？

增量更新自动识别最后更新日期，仅获取新数据：

```python
# 首次运行：下载全部历史数据
manager.incremental_update(retriever, ['000001.SZ'], 'daily')

# 后续运行：仅下载新增数据
manager.incremental_update(retriever, ['000001.SZ'], 'daily')
```

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 运行属性测试
pytest tests/property/ -v --hypothesis-show-statistics

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码规范

- 遵循PEP 8代码风格
- 所有公共函数必须有文档字符串
- 新功能需要添加单元测试和属性测试
- 提交前运行完整测试套件

---

## 致谢

本项目基于国金证券XtQuant平台开发，感谢国金证券提供的API支持。

---

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮件: <your-email@example.com>

---

## Happy Quant Trading! 📈
