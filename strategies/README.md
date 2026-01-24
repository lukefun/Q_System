# strategies/ - 交易策略模块

此目录存放所有交易策略实现。每个策略都必须继承 `core.strategy.BaseStrategy` 基类。

## 文件说明

| 文件 | 策略名称 | 说明 |
|------|----------|------|
| `__init__.py` | 模块初始化 | 导出可用策略 |
| `double_ma.py` | 双均线策略 | 基于 MA5/MA20 交叉的趋势跟踪策略 |

## 策略开发指南

### 1. 创建新策略

```python
# strategies/my_strategy.py
from core.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    """我的自定义策略"""

    def initialize(self, context):
        """策略初始化（仅执行一次）"""
        # 设置策略参数
        context.user_data['fast_period'] = 5
        context.user_data['slow_period'] = 20
        context.log("策略初始化完成")

    def handle_bar(self, context, bar_dict):
        """每根K线调用一次"""
        # 获取当前K线数据
        current_bar = bar_dict[context.stock_code]

        # 策略信号判断
        if should_buy:
            context.order(context.stock_code, 100)  # 买入100股
        elif should_sell:
            context.order(context.stock_code, -100)  # 卖出100股

    def finalize(self, context):
        """回测结束时调用（可选）"""
        context.log(f"最终收益: {context.total_asset}")
```

### 2. 必须实现的方法

| 方法 | 调用时机 | 是否必须 |
|------|----------|----------|
| `initialize(context)` | 策略启动时，执行一次 | 是 |
| `handle_bar(context, bar_dict)` | 每根K线执行一次 | 是 |
| `finalize(context)` | 回测结束时执行一次 | 否 |

### 3. Context 对象可用属性

```python
context.cash          # 可用资金
context.total_asset   # 总资产
context.positions     # 持仓字典 {stock_code: volume}
context.current_dt    # 当前时间
context.user_data     # 自定义数据存储字典
context.stock_code    # 当前标的代码
```

### 4. Context 对象可用方法

```python
context.order(stock_code, volume)  # 下单：正数买入，负数卖出
context.log(message)               # 打印日志
```

## 策略回测

```python
# main.py 中使用新策略
from strategies.my_strategy import MyStrategy

strategy = MyStrategy()
engine = BacktestEngine(strategy, stock_code='000001.SZ')
engine.load_data('2023-01-01', '2023-12-31')
engine.run()
```

## 命名规范

- 文件名使用小写字母和下划线：`double_ma.py`, `momentum_strategy.py`
- 类名使用大驼峰：`DoubleMaStrategy`, `MomentumStrategy`
- 策略文件需包含文档字符串说明策略原理
