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
├── core/
│   ├── engine.py        # 回测引擎
│   ├── live_runner.py   # 实盘引擎
│   ├── strategy.py      # 策略基类
│   └── context.py       # 上下文对象 (核心交互接口)
├── strategies/
│   └── double_ma.py     # 双均线策略示例
└── data/                # 本地数据存储
```

## 快速开始

### 环境要求

- Python 3.x
- XtQuant (国金证券 QMT 客户端)
- pandas

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
