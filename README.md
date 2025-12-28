# Q_System

基于 XtQuant（国金证券 QMT）的量化交易回测与实盘框架。采用策略-引擎分离架构，支持自定义策略的回测验证与实盘交易。

## 功能特性

- **策略-引擎分离**: 策略逻辑与执行引擎解耦，便于策略复用与测试
- **双模式运行**: 支持回测模式 (`BacktestEngine`) 和实盘模式 (`LiveRunner`)
- **安全机制**: 内置运行模式锁 + 人工确认防火墙，防止误操作
- **统一接口**: 策略通过 `Context` 对象与引擎交互，回测与实盘代码一致

## 项目结构

```
Q_System/
├── main.py              # 回测启动脚本
├── run_live.py          # 实盘启动脚本
├── check.bat            # 环境快速检查 (双击运行)
├── start_isolated.bat   # 隔离模式启动器 (推荐)
├── requirements.txt     # 生产依赖
├── requirements-dev.txt # 开发依赖
├── environment.yml      # Conda 环境配置
├── core/
│   ├── engine.py        # 回测引擎
│   ├── live_runner.py   # 实盘引擎
│   ├── strategy.py      # 策略基类
│   └── context.py       # 上下文对象 (核心交互接口)
├── strategies/
│   └── double_ma.py     # 双均线策略示例
├── scripts/
│   ├── check_env.py     # 环境验证脚本
│   ├── setup_env.bat    # 一键环境配置
│   └── fix_env_isolation.bat  # 环境隔离修复
├── data/                # 本地数据存储
└── docs/
    ├── ENVIRONMENT.md   # 环境管理详细文档
    └── SETUP_GUIDE.md   # 新机器配置指南
```

## 环境配置

### 系统要求

| 项目 | 要求 |
|------|------|
| Python | **3.8.x** (miniQMT 硬性要求) |
| 操作系统 | Windows (QMT 仅支持 Windows) |
| Conda | 推荐使用 Miniconda |
| QMT | 国金证券 MiniQMT 客户端 |

### 核心依赖

| 包名 | 版本 | 说明 |
|------|------|------|
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
scripts\setup_env.bat
```

该脚本会自动：创建 quants 环境 → 安装依赖 → 安装 xtquant → 验证环境

### 场景二：已有 quants 环境

适用于：电脑上已存在 quants conda 环境

```bash
# 1. 激活环境
conda activate quants

# 2. 验证环境
python scripts/check_env.py

# 3. 如有缺失依赖，补充安装
pip install -r requirements.txt
```

### 场景三：多 Python 版本混乱的电脑

适用于：系统安装了多个 Python 版本，存在包加载混乱

**症状检测**：
```bash
conda activate quants
python scripts/check_env.py
# 如果看到 "[WARN] 检测到 X 个 site-packages 路径，可能存在版本混乱"
```

**解决方案 A - 使用隔离模式启动 (推荐)**：
```bash
# 双击此脚本启动开发环境
start_isolated.bat
```
该脚本设置 `PYTHONNOUSERSITE=1`，禁用用户全局包，确保只使用 conda 环境。

**解决方案 B - 修复环境隔离**：
```bash
# 重新安装包到 conda 环境
scripts\fix_env_isolation.bat
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

# 4. 安装 xtquant
pip install xtquant

# 5. 验证
python scripts/check_env.py
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
start_isolated.bat

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
check.bat
```

### 详细检查
```bash
conda activate quants
python scripts/check_env.py
```

### 验证通过标准
```
[PASS] Python 版本     ← 3.8.x
[PASS] Conda 环境      ← quants
[PASS] 核心依赖包      ← pandas, numpy
[PASS] XtQuant         ← xtdata 可用
[PASS] 项目模块        ← 全部可导入
```

> 详细文档: [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

## 快速开始

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
|-----------|------|
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

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!! [教学实盘拦截] 正准备发送交易指令 !!!
!!! 标的: 002594.SZ
!!! 方向: 买入
!!! 数量: 1000
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
>>> 请输入 'y' 确认下单，输入其他任意键取消:
```

## 数据流

```
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
