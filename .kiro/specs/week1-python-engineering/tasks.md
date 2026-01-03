# Implementation Plan: Week 1 - Python工程化规范学习

## Overview

本任务清单将第一周的学习内容分解为可执行的原子任务。每个任务都有明确的产出物和验收标准。建议按顺序完成，每完成一个任务就勾选对应的复选框。

## Tasks

- [x] 1. Day 1: 环境配置验证
  - 确保Python 3.8环境正确配置，MiniQMT可用
  - 预计时间: 2-3小时
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 1.1 运行环境快速检查
    - 双击运行 `check.bat`
    - 观察输出，确认无明显错误
    - _Requirements: 1.2_

  - [ ] 1.2 运行详细环境检查脚本
    - 执行 `conda activate quants`
    - 执行 `python scripts/check_env.py`
    - 确认所有检查项显示 PASS
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 1.3 测试xtquant模块导入
    - 创建 `exercises/week1/day1_env_check.py`
    - 编写代码测试 `from xtquant import xtdata` 是否成功
    - 测试 `xtdata.get_trading_dates('SH')` 是否返回数据
    - _Requirements: 1.4_

  - [ ] 1.4 理解隔离模式启动
    - 阅读 `start_isolated.bat` 内容
    - 理解 `PYTHONNOUSERSITE=1` 的作用
    - 在学习笔记中记录理解
    - _Requirements: 1.5_

- [ ] 2. Day 2: Python核心语法特训
  - 掌握量化开发常用的Python语法特性
  - 预计时间: 4-5小时
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 2.1 创建练习文件并完成列表推导式练习
    - 创建 `exercises/week1/day2_python_basics.py`
    - 练习: 将股票代码列表 `['000001', '000002', '600000']` 转换为带后缀格式
    - 使用列表推导式实现: 0开头加.SZ，6开头加.SH
    - _Requirements: 2.1_

  - [ ] 2.2 完成dict.get()安全取值练习
    - 在练习文件中添加持仓字典操作
    - 练习: 安全获取不存在的股票持仓，返回默认值0
    - 对比直接索引 `dict[key]` 和 `dict.get(key, default)` 的区别
    - _Requirements: 2.2_

  - [ ] 2.3 完成异常处理练习
    - 编写 `safe_get_data(stock_code)` 函数
    - 使用 try-except-finally 结构
    - 模拟数据获取失败场景，验证异常被正确捕获
    - _Requirements: 2.3_

  - [ ] 2.4 完成装饰器练习
    - 编写 `@timer` 装饰器，用于计算函数执行时间
    - 将装饰器应用到一个模拟数据处理函数上
    - 验证装饰器正确输出执行时间
    - _Requirements: 2.4_

- [ ] 3. Day 3: Pandas数据清洗
  - 掌握Pandas核心数据操作
  - 预计时间: 4-5小时
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 3.1 创建练习文件并完成索引操作练习
    - 创建 `exercises/week1/day3_pandas_basics.py`
    - 创建包含股票代码、收盘价、成交量的DataFrame
    - 练习使用 `loc` 按标签索引获取数据
    - 练习使用 `iloc` 按位置索引获取数据
    - _Requirements: 3.1_

  - [ ] 3.2 完成缺失值处理练习
    - 创建包含NaN值的DataFrame
    - 练习 `fillna(method='ffill')` 前向填充
    - 练习 `fillna(value)` 指定值填充
    - 练习 `dropna()` 删除缺失值
    - 对比不同方法的结果差异
    - _Requirements: 3.2_

  - [ ] 3.3 完成数据合并练习
    - 创建两个DataFrame: 价格数据和成交量数据
    - 练习 `pd.merge()` 按键合并
    - 练习 `pd.concat()` 纵向拼接
    - 理解 `how='inner'` 和 `how='outer'` 的区别
    - _Requirements: 3.3_

  - [ ] 3.4 完成K线数据NaN处理练习
    - 模拟真实K线数据（包含停牌导致的NaN）
    - 编写函数识别并统计NaN值数量
    - 选择合适的填充策略处理NaN
    - _Requirements: 3.4_

- [ ] 4. Day 4: Pandas时间序列处理
  - 掌握K线数据处理和技术指标计算
  - 预计时间: 5-6小时
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 4.1 创建练习文件并完成resample练习
    - 创建 `exercises/week1/day4_timeseries.py`
    - 生成模拟的1分钟K线数据（240根，代表一个交易日）
    - 使用 `resample('5min')` 转换为5分钟K线
    - 使用 `resample('1h')` 转换为小时K线
    - 验证OHLCV的聚合逻辑是否正确
    - _Requirements: 4.1_

  - [ ] 4.2 完成rolling移动平均练习
    - 计算MA5（5日均线）和MA20（20日均线）
    - 观察前几行的NaN值（数据不足时的边界情况）
    - 绘制收盘价与均线的对比图（可选）
    - _Requirements: 4.2_

  - [ ] 4.3 完成shift/diff涨跌计算练习
    - 使用 `shift(1)` 获取前一根K线数据
    - 使用 `diff()` 计算涨跌额
    - 使用 `pct_change()` 计算涨跌幅
    - 验证计算结果的正确性
    - _Requirements: 4.3_

  - [ ] 4.4 完成边界情况处理练习
    - 测试rolling在数据不足时的行为
    - 测试shift在第一行的行为
    - 编写函数安全处理这些边界情况
    - _Requirements: 4.4_

- [ ] 5. Day 5: 项目结构规范
  - 理解并遵循标准Python项目结构
  - 预计时间: 3-4小时
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 5.1 分析现有项目结构
    - 阅读项目根目录下的所有文件和文件夹
    - 绘制项目结构图（可用文本形式）
    - 理解每个目录的职责
    - _Requirements: 5.1_

  - [ ] 5.2 学习__init__.py的作用
    - 阅读 `core/__init__.py` 和 `strategies/__init__.py`
    - 理解 `__all__` 变量的作用
    - 在学习笔记中记录理解
    - _Requirements: 5.2_

  - [ ] 5.3 练习模块导入
    - 创建 `exercises/week1/day5_import_test.py`
    - 练习从core模块导入Context、BacktestEngine
    - 练习从strategies模块导入DoubleMAStrategy
    - 验证导入成功且可正常使用
    - _Requirements: 5.3_

  - [ ] 5.4 创建新模块练习
    - 在 `exercises/week1/` 下创建 `utils/` 子目录
    - 创建 `utils/__init__.py`
    - 创建 `utils/helpers.py` 包含一个简单函数
    - 验证可从外部正确导入
    - _Requirements: 5.4_

- [ ] 6. Day 6: Git版本控制
  - 掌握Git基本操作，建立代码备份习惯
  - 预计时间: 3-4小时
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 6.1 Git基础操作练习
    - 确认项目已有 `.git` 目录（已初始化）
    - 执行 `git status` 查看当前状态
    - 执行 `git log --oneline` 查看提交历史
    - _Requirements: 6.1_

  - [ ] 6.2 提交练习代码
    - 执行 `git add exercises/`
    - 执行 `git commit -m "Week1: 添加练习代码"`
    - 验证提交成功
    - _Requirements: 6.2_

  - [ ] 6.3 分支操作练习
    - 执行 `git branch dev` 创建开发分支
    - 执行 `git checkout dev` 切换到开发分支
    - 在dev分支上做一些修改并提交
    - 切换回main分支，观察文件变化
    - _Requirements: 6.3_

  - [ ] 6.4 回退操作练习
    - 故意做一个"错误"的提交
    - 使用 `git revert HEAD` 回退该提交
    - 验证代码恢复到之前状态
    - _Requirements: 6.4_

- [ ] 7. Day 7: 周复盘与代码重构
  - 整理本周代码，形成可复用的函数库
  - 预计时间: 4-5小时
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 7.1 整理练习代码为函数库
    - 创建 `exercises/week1/utils/data_utils.py`
    - 将Day3、Day4的数据处理函数整理到此文件
    - 确保函数命名清晰、职责单一
    - _Requirements: 7.1_

  - [ ] 7.2 添加docstring文档
    - 为每个函数添加docstring
    - 包含: 函数说明、参数说明、返回值说明
    - 参考Google风格或NumPy风格
    - _Requirements: 7.2_

  - [ ] 7.3 清理代码
    - 删除调试用的print语句
    - 删除注释掉的废弃代码
    - 统一代码风格（缩进、空行等）
    - _Requirements: 7.3_

  - [ ] 7.4 验证模块可正确导入
    - 创建 `exercises/week1/day7_verify.py`
    - 导入所有整理好的模块
    - 调用主要函数验证功能正常
    - _Requirements: 7.4_

- [ ] 8. Checkpoint - 周学习总结
  - 确保所有练习完成，整理学习笔记
  - 如有问题请提出讨论

## Notes

- 每个任务完成后，建议立即用Git提交，养成版本控制习惯
- 遇到不理解的概念，先查阅文档，再动手实验
- 学习笔记可以记录在 `docs/` 目录下
- 如果某天任务提前完成，可以预习下一天内容
- 每天学习结束后，回顾三个问题：学到什么？难点是什么？如何应用？
