# Design Document: Week 1 - Python工程化规范学习方案

## Overview

本设计文档为量化交易系统学习计划第一周提供详细的学习方案。采用"每日任务卡"模式，将7天的学习内容分解为可执行的原子任务，每个任务包含理论学习、代码练习和验收检查三个环节。

学习方法论：

- **理论先行**：每个知识点先理解"为什么"
- **代码验证**：通过实际编码巩固理解
- **即时反馈**：每个练习都有明确的验收标准

## Architecture

```plaintext
Week 1 学习架构
├── Day 1: 环境配置 (基础设施)
├── Day 2: Python核心语法 (语言基础)
├── Day 3: Pandas基础 (数据处理)
├── Day 4: Pandas时间序列 (量化核心)
├── Day 5: 项目结构 (工程规范)
├── Day 6: Git版本控制 (协作基础)
└── Day 7: 周复盘 (知识整合)
```

## Components and Interfaces

### 学习模块组件

#### 1. 练习脚本目录结构

```plaintext
exercises/
├── week1/
│   ├── day1_env_check.py      # Day1 环境验证练习
│   ├── day2_python_basics.py  # Day2 Python语法练习
│   ├── day3_pandas_basics.py  # Day3 Pandas基础练习
│   ├── day4_timeseries.py     # Day4 时间序列练习
│   ├── day5_project_structure.py  # Day5 项目结构练习
│   └── day7_refactor.py       # Day7 重构练习
```

#### 2. 每日任务卡接口

每个练习脚本遵循统一结构：

```python
"""
Day X: [主题名称]
学习目标: [具体目标]
预计时间: X小时
"""

# === 理论部分 ===
# 知识点说明（注释形式）

# === 练习部分 ===
def exercise_1():
    """练习1: [练习名称]"""
    # TODO: 完成练习
    pass

# === 验收检查 ===
def verify():
    """运行验收检查"""
    pass

if __name__ == '__main__':
    verify()
```

## Data Models

### 学习进度追踪模型

```python
class DailyProgress:
    day: int                    # 第几天
    topic: str                  # 主题
    exercises_completed: list   # 已完成练习
    time_spent: float          # 花费时间(小时)
    notes: str                 # 学习笔记
    verified: bool             # 是否通过验收
```

## Detailed Daily Plans

### Day 1: 环境配置验证

**学习目标**: 确保Python 3.8环境正确配置，MiniQMT可用

**任务清单**:

1. 运行 `check.bat` 快速检查环境
2. 运行 `python scripts/check_env.py` 详细检查
3. 测试 xtquant 模块导入
4. 理解隔离模式启动的作用

**验收标准**:

- check_env.py 所有检查项显示 PASS
- 能成功 `from xtquant import xtdata`

### Day 2: Python核心语法

**学习目标**: 掌握量化开发常用的Python语法特性

**知识点**:

1. 列表推导式 - 快速处理股票代码列表
2. dict.get() - 安全获取字典值
3. try-except-finally - 异常处理
4. 装饰器 - 函数增强

**练习代码示例**:

```python
# 练习1: 列表推导式
stock_codes = ['000001', '000002', '600000', '600001']
# 任务: 使用列表推导式，给所有代码添加 .SZ 或 .SH 后缀
sz_stocks = [f"{code}.SZ" for code in stock_codes if code.startswith('0')]
sh_stocks = [f"{code}.SH" for code in stock_codes if code.startswith('6')]

# 练习2: dict.get() 安全取值
positions = {'000001.SZ': 1000, '600000.SH': 500}
# 任务: 安全获取持仓，不存在时返回0
vol = positions.get('000002.SZ', 0)  # 返回 0

# 练习3: 异常处理
def safe_get_data(stock_code):
    try:
        # 模拟数据获取
        data = get_market_data(stock_code)
        return data
    except Exception as e:
        print(f"获取 {stock_code} 数据失败: {e}")
        return None
    finally:
        print("数据获取流程结束")

# 练习4: 装饰器
import time
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}秒")
        return result
    return wrapper
```

### Day 3: Pandas数据清洗

**学习目标**: 掌握Pandas核心数据操作

**知识点**:

1. loc/iloc 索引操作
2. fillna/dropna 缺失值处理
3. merge/concat 数据合并

**练习代码示例**:

```python
import pandas as pd
import numpy as np

# 练习1: loc/iloc 索引
df = pd.DataFrame({
    'code': ['000001.SZ', '000002.SZ', '600000.SH'],
    'close': [10.5, 15.2, 8.3],
    'volume': [1000000, 500000, 800000]
})
df.set_index('code', inplace=True)

# 使用 loc (标签索引)
price_000001 = df.loc['000001.SZ', 'close']

# 使用 iloc (位置索引)
first_row = df.iloc[0]

# 练习2: 缺失值处理
df_with_nan = pd.DataFrame({
    'close': [10.5, np.nan, 8.3, np.nan],
    'volume': [1000, 2000, np.nan, 4000]
})
# 填充缺失值
df_filled = df_with_nan.fillna(method='ffill')  # 前向填充
# 删除缺失值
df_dropped = df_with_nan.dropna()

# 练习3: 数据合并
df1 = pd.DataFrame({'code': ['A', 'B'], 'price': [10, 20]})
df2 = pd.DataFrame({'code': ['A', 'B'], 'volume': [100, 200]})
merged = pd.merge(df1, df2, on='code')
```

### Day 4: Pandas时间序列

**学习目标**: 掌握K线数据处理和技术指标计算

**知识点**:

1. resample - K线周期转换
2. rolling - 移动平均计算
3. shift/diff - 涨跌计算

**练习代码示例**:

```python
import pandas as pd

# 模拟1分钟K线数据
dates = pd.date_range('2024-01-01 09:30', periods=240, freq='1min')
df = pd.DataFrame({
    'close': np.random.randn(240).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 240)
}, index=dates)

# 练习1: resample 周期转换 (1分钟 -> 5分钟)
df_5min = df.resample('5min').agg({
    'close': 'last',
    'volume': 'sum'
})

# 练习2: rolling 移动平均
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma20'] = df['close'].rolling(window=20).mean()

# 练习3: shift/diff 涨跌计算
df['prev_close'] = df['close'].shift(1)  # 前一根K线收盘价
df['change'] = df['close'].diff()        # 涨跌额
df['pct_change'] = df['close'].pct_change() * 100  # 涨跌幅(%)
```

### Day 5: 项目结构规范

**学习目标**: 理解并遵循标准Python项目结构

**知识点**:

1. 目录结构设计
2. `__init__.py` 的作用
3. 模块导入规范

**项目结构说明**:

```plaintext
Q_System/
├── core/              # 核心模块
│   ├── __init__.py   # 包标识文件，可定义公开接口
│   ├── context.py    # 上下文对象
│   ├── engine.py     # 回测引擎
│   └── strategy.py   # 策略基类
├── strategies/        # 策略模块
│   ├── __init__.py
│   └── double_ma.py  # 双均线策略
├── data/             # 数据存储
├── logs/             # 日志文件
├── scripts/          # 工具脚本
└── config.py         # 配置文件
```

**`__init__.py` 示例**:

```python
# core/__init__.py
from .context import Context
from .engine import BacktestEngine
from .strategy import BaseStrategy

__all__ = ['Context', 'BacktestEngine', 'BaseStrategy']
```

### Day 6: Git版本控制

**学习目标**: 掌握Git基本操作，建立代码备份习惯

**命令清单**:

```bash
# 初始化仓库
git init

# 查看状态
git status

# 添加文件到暂存区
git add .                    # 添加所有文件
git add exercises/           # 添加指定目录

# 提交
git commit -m "Day1: 完成环境配置"

# 分支操作
git branch dev              # 创建分支
git checkout dev            # 切换分支
git checkout -b feature     # 创建并切换

# 回退操作
git log --oneline           # 查看提交历史
git revert HEAD             # 回退最近一次提交
git checkout -- file.py     # 撤销文件修改
```

### Day 7: 周复盘与代码重构

**学习目标**: 整理本周代码，形成可复用的函数库

**重构任务**:

1. 将练习代码整理为 `utils/` 工具库
2. 为每个函数添加 docstring
3. 删除调试代码和冗余注释
4. 验证模块可正确导入

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

由于本规范是学习计划而非软件开发，大部分验收标准通过示例验证。以下是可形式化的属性：

**Property 1: 时间序列边界处理**
*For any* DataFrame使用rolling(window=n)计算时，前n-1行的结果应为NaN
**Validates: Requirements 4.4**

**Property 2: 函数文档完整性**
*For any* 重构后的函数，应包含非空的docstring
**Validates: Requirements 7.2**

## Error Handling

### 常见错误及解决方案

| 错误类型 | 可能原因 | 解决方案 |
| --------- | --------- | --------- |
| ModuleNotFoundError: xtquant | 环境未正确配置 | 运行 `pip install xtquant` |
| Python版本不匹配 | 使用了非3.8版本 | 重新创建conda环境 |
| 多版本冲突 | 系统存在多个Python | 使用 `start_isolated.bat` |
| NaN值导致计算错误 | 未处理缺失值 | 使用 `fillna()` 或 `dropna()` |

## Testing Strategy

### 验收测试方法

**单元测试**: 每个练习脚本包含 `verify()` 函数，运行后自动检查练习是否正确完成。

**集成测试**: Day 7 周复盘时，验证所有模块可正确导入和调用。

**手动验证清单**:

- [ ] Day 1: check_env.py 全部 PASS
- [ ] Day 2: 4个Python语法练习完成
- [ ] Day 3: 3个Pandas练习完成
- [ ] Day 4: 3个时间序列练习完成
- [ ] Day 5: 理解项目结构
- [ ] Day 6: 至少3次git commit
- [ ] Day 7: 代码重构完成，可正确导入

### 学习效果评估

每日学习结束后，回答以下问题：

1. 今天学到了什么新知识？
2. 哪个知识点最难理解？
3. 这些知识如何应用到量化交易中？
