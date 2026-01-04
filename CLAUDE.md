# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
此文件为Claude Code（claude.ai/code）在处理此仓库中的代码时提供指导。

## 项目概述

Q_System 是一个量化交易回测框架，基于 XtQuant（国金证券 QMT）数据源构建。项目采用策略-引擎分离架构，支持自定义策略的回测验证。

**技术栈**: Python 3.x, XtQuant, pandas

## 运行命令

```bash
# 运行回测
python main.py
```

## 架构设计

### 核心组件

```plaintext
Q_System/
├── main.py              # (W1D2) 回测启动脚本 (无需修改)
├── run_live.py          # (W1D3) [新增] 实盘启动脚本
├── core/
│   ├── __init__.py      # (空文件)
│   ├── engine.py        # (W1D2) 回测引擎 (无需修改)
│   ├── strategy.py      # (W1D1) 策略基类 (无需修改)
│   ├── live_runner.py   # (W1D3) [新增] 实盘引擎
│   └── context.py       # (W1D3) [修改] 上下文对象 (核心安全锁)
├── strategies/
│   ├── __init__.py      # (空文件)
│   └── double_ma.py     # (W1D2) 双均线策略 (无需修改)
└── data/                # 本地数据存储

更新时间：2025/12/16 20:52
```

### 数据流

1. `main.py` 实例化策略和引擎
2. `BacktestEngine.load_data()` 通过 XtQuant 下载历史 K 线数据，预计算技术指标 (MA5/MA20)
3. `BacktestEngine.run()` 驱动时间循环，逐根 K 线调用策略的 `handle_bar()`
4. 策略通过 `context.order()` 发出交易信号
5. `BacktestEngine.run()` 执行完所有 K 线后，调用策略的 `finalize(context)` 进行收尾工作
6. `BacktestEngine.save_results()` 保存回测结果
7. `main.py` 读取回测结果，绘制图表
8. `main.py` 运行结束，保存结果
9. 实盘模式：`run_live.py` 实盘启动脚本
10. 实盘模式：`live_runner.py` 实盘引擎
11. 实盘模式：`context.py` 实盘上下文对象，包含：
    - `cash` / `total_asset`: 资金账户信息
    - `positions`: 持仓字典 `{stock_code: volume}`
    - `current_dt`: 当前时间
    - `user_data`: 策略自定义变量存储
    - `order(stock_code, volume)`: 下单接口（正数买入，负数卖出）
    - `log(msg)`: 日志打印
12. 实盘模式：`live_runner.py` 实盘引擎，继承 `BacktestEngine`
13. 实盘模式：`live_runner.py` 实盘引擎，实现 `handle_bar()` 方法
14. 实盘模式：`live_runner.py` 实盘引擎，实现 `finalize(context)` 方法
15. 实盘模式：`live_runner.py` 实盘引擎，实现 `save_results()` 方法
16. 实盘模式：`live_runner.py` 实盘引擎，实现 `load_data()` 方法
17. 实盘模式：`live_runner.py` 实盘引擎，实现 `run()` 方法
18. 实盘模式：`live_runner.py` 实盘引擎，实现 `connect()` 方法，连接 QMT 实盘账户
19. 实盘模式：`live_runner.py` 实盘引擎，实现 `disconnect()` 方法，断开 QMT 实盘账户连接
20. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_positions()` 方法，获取当前持仓信息
21. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_account_info()` 方法，获取当前账户信息
22. 实盘模式：`live_runner.py` 实盘引擎，实现 `cancel_order(order_id)` 方法，取消指定订单
23. 实盘模式：`live_runner.py` 实盘引擎，实现 `place_order(stock_code, volume, price, order_type)` 方法，下单接口（支持限价、市价、止损、止盈）
24. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_order_status(order_id)` 方法，获取指定订单状态
25. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_order_history()` 方法，获取订单历史记录
26. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_trade_history()` 方法，获取成交记录
27. 实盘模式：`live_runner.py` 实盘引擎，实现 `get_contract_info(stock_code)` 方法，获取指定股票合约信息

### 策略开发模式

所有策略必须继承 `BaseStrategy` 并实现两个抽象方法：

- `initialize(context)`: 策略启动时执行一次，用于设置参数
- `handle_bar(context, bar_dict)`: 每根 K 线执行一次，用于信号判断和下单

### Context 对象

`Context` 是策略与引擎的桥梁，包含：

- `cash` / `total_asset`: 资金账户信息
- `positions`: 持仓字典 `{stock_code: volume}`
- `current_dt`: 当前时间
- `user_data`: 策略自定义变量存储
- `order(stock_code, volume)`: 下单接口（正数买入，负数卖出）
- `log(msg)`: 日志打印

## 添加新策略

1. 在 `strategies/` 目录创建新文件
2. 继承 `BaseStrategy`，实现 `initialize` 和 `handle_bar`
3. 在 `main.py` 中替换策略实例

## 数据源

- 使用 XtQuant (`xtquant.xtdata`) 获取历史行情
- 数据格式：日 K 线 OHLCV + 预计算技术指标
- 时间索引已转换为 `datetime` 格式
