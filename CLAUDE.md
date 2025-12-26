# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

```
Q_System/
├── core/           # 核心引擎模块
│   ├── engine.py   # BacktestEngine - 回测引擎，负责数据加载和时间循环驱动
│   ├── context.py  # Context - 上下文对象，存储账户状态和交易接口
│   └── strategy.py # BaseStrategy - 策略抽象基类，定义 initialize/handle_bar 接口
├── strategies/     # 策略实现
│   └── double_ma.py # DoubleMAStrategy - 双均线策略示例
├── data/           # 数据存储目录
├── config.py       # 配置文件
└── main.py         # 启动入口
```

### 数据流

1. `main.py` 实例化策略和引擎
2. `BacktestEngine.load_data()` 通过 XtQuant 下载历史 K 线数据，预计算技术指标 (MA5/MA20)
3. `BacktestEngine.run()` 驱动时间循环，逐根 K 线调用策略的 `handle_bar()`
4. 策略通过 `context.order()` 发出交易信号

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
