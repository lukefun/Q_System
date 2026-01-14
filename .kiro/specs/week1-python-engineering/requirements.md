# Requirements Document

## Introduction

本规范定义了量化交易系统学习计划第一周（Day 1-7）的学习目标和验收标准。第一周聚焦于环境搭建与Python工程化规范，为后续量化开发奠定坚实基础。

## Glossary

- **Q_System**: 基于XtQuant的量化交易回测与实盘框架
- **MiniQMT**: 国金证券提供的量化交易终端
- **XtQuant**: 国金证券QMT交易接口Python库
- **Conda_Environment**: 使用Conda管理的Python隔离环境
- **Check_Script**: 环境验证脚本，用于检测依赖是否正确安装

## Requirements

### Requirement 1: 环境配置验证

**User Story:** 作为量化学习者，我希望拥有一个纯净且正确配置的Python 3.8环境，以便能够运行MiniQMT和XtQuant相关代码。

#### pandas数据清洗的验收标准（Acceptance Criteria for Pandas Data Cleaning）

1. THE Conda_Environment SHALL 使用Python 3.8.x版本
2. WHEN 执行 `python scripts/check_env.py` 时，THE Check_Script SHALL 显示所有检查项为PASS状态
3. THE Conda_Environment SHALL 包含pandas、numpy、xtquant等核心依赖
4. WHEN 导入xtquant.xtdata模块时，THE System SHALL 成功导入无报错
5. IF 环境存在多Python版本冲突，THEN THE System SHALL 通过隔离模式启动解决

### Requirement 2: Python核心语法掌握

**User Story:** 作为量化学习者，我希望掌握量化开发常用的Python语法特性，以便能够编写高效的数据处理代码。

#### Python核心语法掌握的验收标准（Acceptance Criteria for Python Core Syntax Mastery）

1. THE Learner SHALL 能够使用列表推导式处理股票代码列表
2. THE Learner SHALL 能够使用dict.get()安全获取字典值并设置默认值
3. THE Learner SHALL 能够使用try-except-finally处理数据获取异常
4. THE Learner SHALL 能够编写简单的装饰器用于函数计时或日志记录

### Requirement 3: Pandas数据清洗能力

**User Story:** 作为量化学习者，我希望掌握Pandas的核心数据操作，以便能够清洗和处理金融数据。

#### Acceptance Criteria for Environment Configuration

1. THE Learner SHALL 能够使用loc/iloc进行DataFrame索引操作
2. THE Learner SHALL 能够使用fillna/dropna处理缺失值
3. THE Learner SHALL 能够使用merge/concat合并多个数据源
4. WHEN 处理K线数据时，THE Learner SHALL 能够正确识别并处理NaN值

### Requirement 4: Pandas时间序列处理

**User Story:** 作为量化学习者，我希望掌握Pandas时间序列操作，以便能够进行K线周期转换和技术指标计算。

#### Acceptance Criteria for Pandas Time Series Processing

1. THE Learner SHALL 能够使用resample将1分钟K线转换为5分钟/日线
2. THE Learner SHALL 能够使用rolling计算移动平均线(MA5, MA20)
3. THE Learner SHALL 能够使用shift/diff计算涨跌幅和涨跌额
4. WHEN 计算技术指标时，THE System SHALL 正确处理时间序列的边界情况

### Requirement 5: 项目结构规范

**User Story:** 作为量化学习者，我希望理解并遵循标准的Python项目结构，以便代码具有良好的可维护性。

#### Acceptance Criteria for Git Version Control

1. THE Project SHALL 包含core、data、strategies、logs、config等标准目录
2. THE Learner SHALL 理解__init__.py文件的作用和使用方式
3. THE Learner SHALL 能够正确组织模块导入关系
4. WHEN 创建新模块时，THE Learner SHALL 遵循项目既有的目录结构规范

### Requirement 6: Git版本控制

**User Story:** 作为量化学习者，我希望掌握Git基本操作，以便能够安全地管理和备份代码。

#### Acceptance Criteria for Weekly Review and Refactoring

1. THE Learner SHALL 能够执行git init初始化仓库
2. THE Learner SHALL 能够执行git add和git commit提交代码变更
3. THE Learner SHALL 能够使用git branch创建和切换分支
4. THE Learner SHALL 能够使用git revert回退错误的提交
5. IF 代码出现问题，THEN THE Learner SHALL 能够通过Git历史恢复

### Requirement 7: 周复盘与代码重构

**User Story:** 作为量化学习者，我希望在每周结束时整理和重构代码，以便形成可复用的函数库。

#### Acceptance Criteria

1. THE Learner SHALL 将零散脚本整理为结构化的函数库
2. THE Learner SHALL 为每个函数添加docstring文档
3. THE Learner SHALL 删除调试代码和冗余注释
4. WHEN 周复盘完成时，THE Code_Library SHALL 可被其他模块正确导入使用
