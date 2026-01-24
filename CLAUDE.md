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

# 运行实盘（模拟模式）
python run_live.py

# 运行测试
pytest tests/

# 环境检查
python scripts/verify/check_env.py
```

## 项目结构

```plaintext
Q_System/
├── main.py              # 回测启动脚本
├── run_live.py          # 实盘启动脚本
├── config.py            # 配置文件（被广泛引用，勿移动）
│
├── core/                # 核心引擎模块
│   ├── engine.py            # 回测引擎
│   ├── live_runner.py       # 实盘引擎
│   ├── strategy.py          # 策略基类
│   └── context.py           # 上下文对象（策略-引擎桥梁）
│
├── src/                 # 数据工程模块
│   ├── xtdata_client.py     # XtData API 封装
│   ├── data_retriever.py    # 行情数据获取
│   ├── data_manager.py      # HDF5 数据存储
│   ├── price_adjuster.py    # 复权处理
│   ├── fundamental_handler.py # 财务数据处理
│   ├── industry_mapper.py   # 行业分类映射
│   ├── visualizer.py        # 可视化
│   ├── data_alignment.py    # 数据对齐
│   └── full_market_downloader.py # 全市场下载
│
├── strategies/          # 策略实现
│   └── double_ma.py         # 双均线策略示例
│
├── tests/               # 测试套件
│   ├── unit/                # 单元测试
│   ├── property/            # 属性测试（Hypothesis）
│   └── integration/         # 集成测试
│
├── examples/            # 示例脚本
├── exercises/           # 学习练习
│   ├── week1/               # Python 基础
│   └── week2/               # 数据工程
│
├── data/                # 数据存储
├── logs/                # 日志目录
│
├── scripts/             # 工具脚本
│   ├── setup/               # 环境配置脚本
│   ├── verify/              # 验证脚本
│   └── utils/               # 工具脚本
│
└── docs/                # 文档
    ├── guides/              # 用户指南
    ├── api/                 # API 文档
    ├── plans/               # 计划文档
    ├── reports/             # 任务验证报告
    └── notes/               # 学习笔记

更新时间：2025/01/23
```

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

### 数据流

```text
XtQuant API → DataRetriever → DataManager (HDF5)
                    ↓
BacktestEngine.load_data() → Engine.run() → Strategy.handle_bar()
                                               ↓
                                        Context.order()
```

## 添加新策略

1. 在 `strategies/` 目录创建新文件
2. 继承 `BaseStrategy`，实现 `initialize` 和 `handle_bar`
3. 在 `main.py` 中替换策略实例

## 数据源

- 使用 XtQuant (`xtquant.xtdata`) 获取历史行情
- 数据格式：日 K 线 OHLCV + 预计算技术指标
- 时间索引已转换为 `datetime` 格式

## 文档导航

- 用户指南: `docs/guides/`
- API 文档: `docs/api/`
- 学习计划: `docs/plans/`
- 任务报告: `docs/reports/`
