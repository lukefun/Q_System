# Week 2 Git 提交计划

按照 tasks.md 的顺序，将所有代码分类提交到 git。

## 提交策略

每个任务对应一个或多个 git commit，commit message 遵循以下格式：
```
feat(week2): Task X.Y - 简短描述

详细说明（可选）
- 实现的功能点1
- 实现的功能点2

需求: X.Y, X.Z
```

---

## Task 1: 设置项目结构和核心配置

### Commit 1.1: 初始化项目结构
```bash
git add config.py requirements.txt requirements-dev.txt
git add src/__init__.py tests/__init__.py examples/__init__.py
git add .gitignore
git commit -m "feat(week2): Task 1 - 初始化项目结构和配置

- 创建 config.py 配置文件
- 创建 requirements.txt 和 requirements-dev.txt
- 设置目录结构: src/, tests/, examples/, data/, docs/
- 配置 .gitignore

需求: 9.6, 10.6"
```

---

## Task 2: 实现XtData客户端封装

### Commit 2.1: XtData客户端实现
```bash
git add src/xtdata_client.py
git commit -m "feat(week2): Task 2.1 - 实现XtData客户端封装

- 实现 XtDataClient 类
- 添加连接管理和认证功能
- 实现错误处理和重试逻辑
- 支持上下文管理器

需求: 1.5"
```

### Commit 2.2: XtData客户端测试
```bash
git add tests/unit/test_xtdata_client.py
git add tests/conftest.py
git commit -m "test(week2): Task 2.2 - XtData客户端单元测试

- 测试连接成功和失败场景
- 测试认证错误处理
- 测试重试机制
- 添加 pytest fixtures

需求: 1.5"
```

---

## Task 3: 实现数据获取器

### Commit 3.1: 数据获取器实现
```bash
git add src/data_retriever.py
git commit -m "feat(week2): Task 3.1 - 实现数据获取器

- 实现 DataRetriever 类
- 支持历史数据下载 (download_history_data)
- 支持实时快照 (get_market_data)
- 支持股票列表获取 (get_all_stock_codes)
- 添加参数验证和错误处理

需求: 1.1, 1.2, 1.3, 1.4, 1.6, 9.1"
```

### Commit 3.2-3.7: 数据获取器属性测试
```bash
git add tests/property/test_properties_retrieval.py
git add tests/property/__init__.py
git commit -m "test(week2): Task 3.2-3.7 - 数据获取器属性测试

- 属性1: 历史数据范围正确性
- 属性2: 市场快照数据完整性
- 属性3: Tick数据时间精度
- 属性4: 日线数据唯一性
- 属性5: API错误处理稳定性
- 属性6: 批量请求完整性

需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6"
```

### Commit 3.8: 数据获取器单元测试
```bash
git add tests/unit/test_data_retriever.py
git commit -m "test(week2): Task 3 - 数据获取器单元测试

- 测试参数验证
- 测试各种数据获取场景
- 测试错误处理

需求: 1.1-1.6, 9.1"
```

---

## Task 4: 检查点 - 数据获取功能

### Commit 4.1: 数据获取示例
```bash
git add examples/01_basic_data_retrieval.py
git commit -m "docs(week2): Task 4 - 数据获取示例脚本

- 创建基础数据获取示例
- 演示历史数据和实时数据获取
- 包含详细注释和说明"
```

---

## Task 5: 实现价格复权处理器

### Commit 5.1: 价格复权实现
```bash
git add src/price_adjuster.py
git commit -m "feat(week2): Task 5.1 - 实现价格复权处理器

- 实现 PriceAdjuster 类
- 支持前复权 (forward_adjust)
- 支持后复权 (backward_adjust)
- 获取复权因子 (get_adjust_factors)
- 保持OHLCV数据一致性

需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6"
```

### Commit 5.2-5.4: 价格复权属性测试
```bash
git add tests/property/test_properties_adjustment.py
git commit -m "test(week2): Task 5.2-5.4 - 价格复权属性测试

- 属性7: 前复权方向正确性
- 属性8: 后复权当前价格不变性
- 属性9: OHLC相对关系不变性

需求: 2.1, 2.2, 2.4, 2.5"
```

### Commit 5.5: 价格复权单元测试
```bash
git add tests/unit/test_price_adjuster.py
git commit -m "test(week2): Task 5.5 - 价格复权单元测试

- 测试默认使用前复权
- 测试复权因子缺失的边缘情况
- 测试OHLC关系保持

需求: 2.3, 2.6"
```

---

## Task 6: 实现基本面数据处理器

### Commit 6.1: 基本面数据处理器实现
```bash
git add src/fundamental_handler.py
git commit -m "feat(week2): Task 6.1 - 实现基本面数据处理器

- 实现 FundamentalHandler 类
- 获取财务数据 (get_financial_data)
- 计算PE比率 (calculate_pe_ratio)
- 计算PB比率 (calculate_pb_ratio)
- 强制时间点正确性 (使用announce_date)
- 优雅处理缺失数据

需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 7.2"
```

### Commit 6.2-6.5: 基本面数据属性测试
```bash
git add tests/property/test_properties_fundamental.py
git commit -m "test(week2): Task 6.2-6.5 - 基本面数据属性测试

- 属性10: 时间点正确性
- 属性11: PE比率计算正确性
- 属性12: PB比率计算正确性
- 属性13: 基本面数据缺失处理

需求: 3.1, 3.2, 3.3, 3.5, 3.6, 7.2"
```

### Commit 6.6: 基本面数据单元测试
```bash
git add tests/unit/test_fundamental_handler.py
git commit -m "test(week2): Task 6 - 基本面数据单元测试

- 测试财务数据获取
- 测试PE/PB计算
- 测试时间点正确性
- 测试缺失数据处理

需求: 3.1-3.6, 7.2"
```

---

## Task 7: 实现行业分类映射器

### Commit 7.1: 行业分类映射器实现
```bash
git add src/industry_mapper.py
git commit -m "feat(week2): Task 7.1 - 实现行业分类映射器

- 实现 IndustryMapper 类
- 获取申万行业结构 (get_industry_structure)
- 查询股票行业 (get_stock_industry)
- 获取行业成分股 (get_industry_constituents)
- 支持历史日期查询
- 实现缓存机制

需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6"
```

### Commit 7.2-7.4: 行业分类属性测试
```bash
git add tests/property/test_properties_industry.py
git commit -m "test(week2): Task 7.2-7.4 - 行业分类属性测试

- 属性14: 行业成分股一致性
- 属性15: 历史行业分类时间点正确性
- 属性16: 行业查询方式一致性

需求: 4.3, 4.4, 4.5, 4.6"
```

### Commit 7.5: 行业分类单元测试
```bash
git add tests/unit/test_industry_mapper.py
git commit -m "test(week2): Task 7.5 - 行业分类单元测试

- 测试行业结构返回完整层级
- 测试缓存机制
- 测试历史查询
- 测试按代码和名称查询

需求: 4.1-4.6"
```

---

## Task 8: 检查点 - 数据处理功能

### Commit 8.1: 数据处理示例脚本
```bash
git add examples/02_price_adjustment.py
git add examples/03_fundamental_data.py
git add examples/04_industry_classification.py
git commit -m "docs(week2): Task 8 - 数据处理示例脚本

- 价格复权演示
- 基本面数据演示
- 行业分类演示
- 包含详细注释和说明"
```

---

## Task 9: 实现数据管理器

### Commit 9.1: 数据管理器基础功能
```bash
git add src/data_manager.py
git commit -m "feat(week2): Task 9.1 - 实现数据管理器基础功能

- 实现 DataManager 类
- HDF5数据存储 (save_market_data)
- HDF5数据加载 (load_market_data)
- 获取最后更新日期 (get_last_update_date)
- CSV导出 (export_to_csv)
- 设计HDF5存储结构

需求: 5.1, 5.2, 5.7"
```

### Commit 9.2: 增量更新功能
```bash
git add src/data_manager.py
git commit -m "feat(week2): Task 9.2 - 实现增量更新功能

- 实现 incremental_update 方法
- 识别最后更新日期
- 重复数据检测和去重
- 进度报告回调

需求: 5.3, 5.4, 8.5"
```

### Commit 9.3: 数据验证和质量检查
```bash
git add src/data_manager.py
git commit -m "feat(week2): Task 9.3 - 添加数据验证和质量检查

- 数据类型和范围验证
- 异常值检测（负价格、极端值）
- 数据缺口检测
- 数据完整性验证

需求: 9.2, 9.4, 9.5, 8.4"
```

### Commit 9.4-9.8: 数据管理器测试
```bash
git add tests/property/test_properties_storage.py
git add tests/property/test_properties_error_handling.py
git add tests/unit/test_data_manager.py
git commit -m "test(week2): Task 9.4-9.8 - 数据管理器测试

属性测试:
- 属性17: 存储-加载往返一致性
- 属性18: 增量更新仅获取新数据
- 属性19: 重复数据去重
- 属性20: 查询过滤正确性
- 属性23: 数据异常标记
- 属性25: 数据类型验证
- 属性26: 数据缺口检测

单元测试:
- 测试HDF5存储和加载
- 测试增量更新
- 测试数据验证

需求: 5.1, 5.3, 5.4, 5.7, 9.2, 9.4, 9.5"
```

---

## Task 10: 实现可视化器

### Commit 10.1: 可视化器实现
```bash
git add src/visualizer.py
git commit -m "feat(week2): Task 10.1 - 实现可视化器

- 实现 Visualizer 类
- K线图绘制 (plot_kline)
- 成交量图绘制 (plot_volume)
- 多股票对比 (plot_multiple_stocks)
- 移动平均线叠加
- 图表保存功能
- 中国市场颜色惯例（红涨绿跌）

需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7"
```

### Commit 10.2: 可视化器测试
```bash
git add tests/unit/test_visualizer.py
git commit -m "test(week2): Task 10.2 - 可视化器单元测试

- 测试图表生成不抛出异常
- 测试图表文件保存成功
- 测试多子图布局

需求: 6.7"
```

---

## Task 11: 实现全市场数据库构建功能

### Commit 11.1: 全市场下载器实现
```bash
git add src/full_market_downloader.py
git commit -m "feat(week2): Task 11.1 - 实现全市场数据库构建

- 实现 FullMarketDownloader 类
- 全市场数据下载 (download_full_market)
- 断点续传功能
- API速率限制处理
- 进度报告和汇总统计

需求: 8.1, 8.2, 8.3, 8.5, 8.6"
```

### Commit 11.2: 全市场下载器测试
```bash
git add tests/unit/test_full_market_downloader.py
git commit -m "test(week2): Task 11.2 - 全市场下载器测试

- 测试断点续传功能
- 测试进度报告
- 测试汇总统计
- 测试状态管理

需求: 8.3, 8.5, 8.6"
```

---

## Task 12: 实现数据对齐和未来函数防范

### Commit 12.1: 数据对齐工具
```bash
git add src/data_alignment.py
git commit -m "feat(week2): Task 12.1 - 实现数据对齐工具

- 实现 align_data_sources 函数
- 保守日期匹配策略
- 时间点正确性验证
- 未来函数防范文档

需求: 7.1, 7.4, 7.5"
```

### Commit 12.2: 数据对齐测试
```bash
git add tests/property/test_properties_alignment.py
git commit -m "test(week2): Task 12.2 - 数据对齐属性测试

- 属性21: 保守日期对齐

需求: 7.5"
```

---

## Task 13: 检查点 - 存储和可视化功能

### Commit 13.1: 存储和可视化示例
```bash
git add examples/05_data_persistence.py
git add examples/06_visualization.py
git add examples/07_incremental_update.py
git commit -m "docs(week2): Task 13 - 存储和可视化示例脚本

- 数据持久化演示
- K线图和技术指标演示
- 增量更新演示
- 包含详细注释和说明"
```

---

## Task 14: 添加错误处理和日志

### Commit 14.1-14.3: 错误处理和日志
```bash
git add src/*.py
git add tests/property/test_properties_error_handling.py
git commit -m "feat(week2): Task 14 - 完善错误处理和日志

- 自定义异常类
- 详细错误消息
- 优雅降级处理
- 完整日志系统
- 属性22: 无效股票代码错误消息
- 属性24: 部分数据处理连续性

需求: 9.1, 9.3, 9.6"
```

---

## Task 15: 创建教学文档和示例

### Commit 15.1: README文档
```bash
git add README.md
git commit -m "docs(week2): Task 15.1 - 编写README文档

- 项目简介和学习目标
- 安装和配置说明
- 快速开始指南
- API文档链接

需求: 10.6"
```

### Commit 15.2: 代码文档
```bash
git add src/*.py
git commit -m "docs(week2): Task 15.2 - 完善代码文档

- 所有公共类和函数的文档字符串
- 复杂逻辑的注释
- 前复权vs后复权说明
- 未来函数示例说明

需求: 10.1, 10.3, 10.4, 10.5"
```

### Commit 15.3: 综合示例脚本
```bash
git add examples/08_full_workflow.py
git add examples/09_build_local_database.py
git add examples/10_lookahead_bias_demo.py
git add examples/README.md
git commit -m "docs(week2): Task 15.3 - 创建综合示例脚本

- 完整工作流演示
- 本地数据库构建演示
- 未来函数问题演示
- 示例说明文档

需求: 10.2, 10.4"
```

### Commit 15.4: 练习结构
```bash
git add exercises/week2/*.py
git add exercises/week2/README.md
git commit -m "docs(week2): Task 15.4 - 创建练习结构

- Day 8-14 练习文件
- 练习说明文档
- 学习目标概述
- 前置知识标注

需求: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6"
```

### Commit 15.5: 文档完整性验证
```bash
git add tests/property/test_properties_documentation.py
git commit -m "test(week2): Task 15.5 - 文档完整性验证

- 属性27: 公共API文档完整性

需求: 10.1"
```

---

## Task 16: 运行完整测试套件和集成测试

### Commit 16.1: 集成测试
```bash
git add tests/integration/test_full_workflow.py
git add tests/integration/test_incremental_update.py
git add tests/integration/test_full_market_database.py
git add tests/integration/__init__.py
git commit -m "test(week2): Task 16.1 - 编写集成测试

- 完整工作流集成测试
- 增量更新集成测试
- 全市场数据库集成测试

需求: 所有需求"
```

### Commit 16.2: 测试配置和覆盖率
```bash
git add pytest.ini
git add .coveragerc
git commit -m "test(week2): Task 16.2 - 测试配置和覆盖率

- pytest 配置
- 覆盖率配置
- 测试运行脚本"
```

---

## Task 17: 最终检查点

### Commit 17.1: 验证报告和总结
```bash
git add TASK_17_FINAL_VERIFICATION_REPORT.md
git add WEEK2_COMPLETION_SUMMARY.md
git add ENVIRONMENT_FIX_SUMMARY.md
git commit -m "docs(week2): Task 17 - 最终验证报告

- 完整性验证报告
- Week 2 完成总结
- 环境修复总结
- 所有需求验证完成"
```

### Commit 17.2: 其他文档和演示文件
```bash
git add examples/demo_*.py
git add examples/industry_mapper_demo.py
git add TASK_*.md
git commit -m "docs(week2): 补充文档和演示文件

- 演示脚本
- 任务验证文档
- 检查点总结"
```

---

## 执行脚本

为了方便执行，我创建了一个 PowerShell 脚本来自动执行所有提交：

```powershell
# 保存为 git_commit_week2.ps1
# 使用方法: .\git_commit_week2.ps1

# 确保在正确的目录
cd D:\_QMT\_qt_lab\_dev\4.week1.day1\Q_System

# 检查 git 状态
git status

# 询问用户是否继续
$continue = Read-Host "是否开始按顺序提交? (y/n)"
if ($continue -ne "y") {
    Write-Host "已取消"
    exit
}

# Task 1
Write-Host "`n=== Task 1: 项目结构 ===" -ForegroundColor Green
git add config.py requirements.txt requirements-dev.txt
git add src/__init__.py tests/__init__.py examples/__init__.py
git add .gitignore
git commit -m "feat(week2): Task 1 - 初始化项目结构和配置

- 创建 config.py 配置文件
- 创建 requirements.txt 和 requirements-dev.txt
- 设置目录结构: src/, tests/, examples/, data/, docs/
- 配置 .gitignore

需求: 9.6, 10.6"

# Task 2
Write-Host "`n=== Task 2: XtData客户端 ===" -ForegroundColor Green
git add src/xtdata_client.py
git commit -m "feat(week2): Task 2.1 - 实现XtData客户端封装

- 实现 XtDataClient 类
- 添加连接管理和认证功能
- 实现错误处理和重试逻辑
- 支持上下文管理器

需求: 1.5"

git add tests/unit/test_xtdata_client.py tests/conftest.py
git commit -m "test(week2): Task 2.2 - XtData客户端单元测试

- 测试连接成功和失败场景
- 测试认证错误处理
- 测试重试机制
- 添加 pytest fixtures

需求: 1.5"

# ... 继续其他任务 ...

Write-Host "`n=== 所有提交完成! ===" -ForegroundColor Green
git log --oneline -20
```

---

## 注意事项

1. **提交前检查**: 每次提交前运行 `git status` 确认要提交的文件
2. **测试验证**: 每个功能提交后运行相关测试确保通过
3. **提交消息**: 遵循约定的格式，便于后续查看和管理
4. **分支管理**: 建议在 feature 分支上开发，完成后合并到主分支
5. **代码审查**: 重要提交前进行代码审查

## 推荐工作流

```bash
# 1. 创建 feature 分支
git checkout -b feature/week2-xtdata-engineering

# 2. 按顺序提交（使用上面的脚本或手动）
# ...

# 3. 推送到远程
git push origin feature/week2-xtdata-engineering

# 4. 创建 Pull Request 进行代码审查

# 5. 审查通过后合并到主分支
git checkout main
git merge feature/week2-xtdata-engineering
git push origin main
```

