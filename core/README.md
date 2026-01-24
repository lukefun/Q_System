# core/ - 核心引擎模块

此目录包含量化回测系统的核心引擎组件，是整个系统的运行基础。

## 文件说明

| 文件 | 功能 | 说明 |
| ------ | ------ | ------ |
| `__init__.py` | 模块初始化 | 导出核心类供外部使用 |
| `strategy.py` | 策略基类 | 定义 `BaseStrategy` 抽象基类，所有策略必须继承此类 |
| `engine.py` | 回测引擎 | `BacktestEngine` 类，驱动历史数据回放和策略执行 |
| `context.py` | 上下文对象 | `Context` 类，策略与引擎的桥梁，管理账户状态、持仓、下单接口 |
| `live_runner.py` | 实盘引擎 | `LiveRunner` 类，继承回测引擎，支持实盘交易 |

## 架构关系

```text
┌─────────────────┐
│   main.py       │  ← 入口脚本
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BacktestEngine  │  ← engine.py
│  - load_data()  │
│  - run()        │
│  - save_results()│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│    Context      │◄────│  BaseStrategy   │
│  - cash         │     │  - initialize() │
│  - positions    │     │  - handle_bar() │
│  - order()      │     │  - finalize()   │
└─────────────────┘     └─────────────────┘
     context.py              strategy.py
```

## 使用示例

```python
from core.strategy import BaseStrategy
from core.engine import BacktestEngine
from core.context import Context

# 1. 创建策略（继承BaseStrategy）
class MyStrategy(BaseStrategy):
    def initialize(self, context):
        context.user_data['fast_ma'] = 5

    def handle_bar(self, context, bar_dict):
        # 策略逻辑
        pass

# 2. 实例化并运行
strategy = MyStrategy()
engine = BacktestEngine(strategy, stock_code='000001.SZ')
engine.load_data('2023-01-01', '2023-12-31')
engine.run()
```

## 开发规范

- 所有核心类的修改需同步更新单元测试
- `Context.order()` 方法是唯一的下单接口，禁止绕过
- 实盘模式下 `live_runner.py` 会自动加锁保护关键操作
