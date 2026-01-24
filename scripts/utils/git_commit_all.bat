@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     Week 2 XtData 金融数据工程 - Git 提交脚本            ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo 当前目录: %CD%
echo.
echo 检查 Git 状态...
git status --short
echo.

set /p confirm="是否开始按顺序提交? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    exit /b
)

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 1: 设置项目结构和核心配置
echo ═══════════════════════════════════════════════════════════
git add config.py requirements.txt requirements-dev.txt src/__init__.py tests/__init__.py examples/__init__.py .gitignore
git commit -m "feat(week2): Task 1 - 初始化项目结构和配置" -m "- 创建 config.py 配置文件" -m "- 创建 requirements.txt 和 requirements-dev.txt" -m "- 设置目录结构: src/, tests/, examples/, data/, docs/" -m "- 配置 .gitignore" -m "" -m "需求: 9.6, 10.6"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 2: 实现XtData客户端封装
echo ═══════════════════════════════════════════════════════════
git add src/xtdata_client.py
git commit -m "feat(week2): Task 2.1 - 实现XtData客户端封装" -m "- 实现 XtDataClient 类" -m "- 添加连接管理和认证功能" -m "- 实现错误处理和重试逻辑" -m "- 支持上下文管理器" -m "" -m "需求: 1.5"

git add tests/unit/test_xtdata_client.py tests/conftest.py
git commit -m "test(week2): Task 2.2 - XtData客户端单元测试" -m "- 测试连接成功和失败场景" -m "- 测试认证错误处理" -m "- 测试重试机制" -m "- 添加 pytest fixtures" -m "" -m "需求: 1.5"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 3: 实现数据获取器
echo ═══════════════════════════════════════════════════════════
git add src/data_retriever.py
git commit -m "feat(week2): Task 3.1 - 实现数据获取器" -m "- 实现 DataRetriever 类" -m "- 支持历史数据下载 (download_history_data)" -m "- 支持实时快照 (get_market_data)" -m "- 支持股票列表获取 (get_all_stock_codes)" -m "- 添加参数验证和错误处理" -m "" -m "需求: 1.1, 1.2, 1.3, 1.4, 1.6, 9.1"

git add tests/property/test_properties_retrieval.py tests/property/__init__.py
git commit -m "test(week2): Task 3.2-3.7 - 数据获取器属性测试" -m "- 属性1: 历史数据范围正确性" -m "- 属性2: 市场快照数据完整性" -m "- 属性3: Tick数据时间精度" -m "- 属性4: 日线数据唯一性" -m "- 属性5: API错误处理稳定性" -m "- 属性6: 批量请求完整性" -m "" -m "需求: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6"

git add tests/unit/test_data_retriever.py
git commit -m "test(week2): Task 3 - 数据获取器单元测试" -m "- 测试参数验证" -m "- 测试各种数据获取场景" -m "- 测试错误处理" -m "" -m "需求: 1.1-1.6, 9.1"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 4: 检查点 - 数据获取功能
echo ═══════════════════════════════════════════════════════════
git add examples/01_basic_data_retrieval.py
git commit -m "docs(week2): Task 4 - 数据获取示例脚本" -m "- 创建基础数据获取示例" -m "- 演示历史数据和实时数据获取" -m "- 包含详细注释和说明"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 5: 实现价格复权处理器
echo ═══════════════════════════════════════════════════════════
git add src/price_adjuster.py
git commit -m "feat(week2): Task 5.1 - 实现价格复权处理器" -m "- 实现 PriceAdjuster 类" -m "- 支持前复权 (forward_adjust)" -m "- 支持后复权 (backward_adjust)" -m "- 获取复权因子 (get_adjust_factors)" -m "- 保持OHLCV数据一致性" -m "" -m "需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6"

git add tests/property/test_properties_adjustment.py
git commit -m "test(week2): Task 5.2-5.4 - 价格复权属性测试" -m "- 属性7: 前复权方向正确性" -m "- 属性8: 后复权当前价格不变性" -m "- 属性9: OHLC相对关系不变性" -m "" -m "需求: 2.1, 2.2, 2.4, 2.5"

git add tests/unit/test_price_adjuster.py
git commit -m "test(week2): Task 5.5 - 价格复权单元测试" -m "- 测试默认使用前复权" -m "- 测试复权因子缺失的边缘情况" -m "- 测试OHLC关系保持" -m "" -m "需求: 2.3, 2.6"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 6: 实现基本面数据处理器
echo ═══════════════════════════════════════════════════════════
git add src/fundamental_handler.py
git commit -m "feat(week2): Task 6.1 - 实现基本面数据处理器" -m "- 实现 FundamentalHandler 类" -m "- 获取财务数据 (get_financial_data)" -m "- 计算PE比率 (calculate_pe_ratio)" -m "- 计算PB比率 (calculate_pb_ratio)" -m "- 强制时间点正确性 (使用announce_date)" -m "- 优雅处理缺失数据" -m "" -m "需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 7.2"

git add tests/property/test_properties_fundamental.py
git commit -m "test(week2): Task 6.2-6.5 - 基本面数据属性测试" -m "- 属性10: 时间点正确性" -m "- 属性11: PE比率计算正确性" -m "- 属性12: PB比率计算正确性" -m "- 属性13: 基本面数据缺失处理" -m "" -m "需求: 3.1, 3.2, 3.3, 3.5, 3.6, 7.2"

git add tests/unit/test_fundamental_handler.py
git commit -m "test(week2): Task 6 - 基本面数据单元测试" -m "- 测试财务数据获取" -m "- 测试PE/PB计算" -m "- 测试时间点正确性" -m "- 测试缺失数据处理" -m "" -m "需求: 3.1-3.6, 7.2"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 7: 实现行业分类映射器
echo ═══════════════════════════════════════════════════════════
git add src/industry_mapper.py
git commit -m "feat(week2): Task 7.1 - 实现行业分类映射器" -m "- 实现 IndustryMapper 类" -m "- 获取申万行业结构 (get_industry_structure)" -m "- 查询股票行业 (get_stock_industry)" -m "- 获取行业成分股 (get_industry_constituents)" -m "- 支持历史日期查询" -m "- 实现缓存机制" -m "" -m "需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6"

git add tests/property/test_properties_industry.py
git commit -m "test(week2): Task 7.2-7.4 - 行业分类属性测试" -m "- 属性14: 行业成分股一致性" -m "- 属性15: 历史行业分类时间点正确性" -m "- 属性16: 行业查询方式一致性" -m "" -m "需求: 4.3, 4.4, 4.5, 4.6"

git add tests/unit/test_industry_mapper.py
git commit -m "test(week2): Task 7.5 - 行业分类单元测试" -m "- 测试行业结构返回完整层级" -m "- 测试缓存机制" -m "- 测试历史查询" -m "- 测试按代码和名称查询" -m "" -m "需求: 4.1-4.6"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 8: 检查点 - 数据处理功能
echo ═══════════════════════════════════════════════════════════
git add examples/02_price_adjustment.py examples/03_fundamental_data.py examples/04_industry_classification.py
git commit -m "docs(week2): Task 8 - 数据处理示例脚本" -m "- 价格复权演示" -m "- 基本面数据演示" -m "- 行业分类演示" -m "- 包含详细注释和说明"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 9: 实现数据管理器
echo ═══════════════════════════════════════════════════════════
git add src/data_manager.py
git commit -m "feat(week2): Task 9.1-9.3 - 实现数据管理器" -m "基础功能:" -m "- HDF5数据存储 (save_market_data)" -m "- HDF5数据加载 (load_market_data)" -m "- 获取最后更新日期 (get_last_update_date)" -m "- CSV导出 (export_to_csv)" -m "" -m "增量更新:" -m "- 实现 incremental_update 方法" -m "- 重复数据检测和去重" -m "- 进度报告回调" -m "" -m "数据验证:" -m "- 数据类型和范围验证" -m "- 异常值检测" -m "- 数据缺口检测" -m "" -m "需求: 5.1, 5.2, 5.3, 5.4, 5.7, 8.4, 8.5, 9.2, 9.4, 9.5"

git add tests/property/test_properties_storage.py tests/property/test_properties_error_handling.py tests/unit/test_data_manager.py
git commit -m "test(week2): Task 9.4-9.8 - 数据管理器测试" -m "属性测试:" -m "- 属性17: 存储-加载往返一致性" -m "- 属性18: 增量更新仅获取新数据" -m "- 属性19: 重复数据去重" -m "- 属性20: 查询过滤正确性" -m "- 属性23: 数据异常标记" -m "- 属性25: 数据类型验证" -m "- 属性26: 数据缺口检测" -m "" -m "单元测试:" -m "- 测试HDF5存储和加载" -m "- 测试增量更新" -m "- 测试数据验证" -m "" -m "需求: 5.1, 5.3, 5.4, 5.7, 9.2, 9.4, 9.5"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 10: 实现可视化器
echo ═══════════════════════════════════════════════════════════
git add src/visualizer.py
git commit -m "feat(week2): Task 10.1 - 实现可视化器" -m "- 实现 Visualizer 类" -m "- K线图绘制 (plot_kline)" -m "- 成交量图绘制 (plot_volume)" -m "- 多股票对比 (plot_multiple_stocks)" -m "- 移动平均线叠加" -m "- 图表保存功能" -m "- 中国市场颜色惯例（红涨绿跌）" -m "" -m "需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7"

git add tests/unit/test_visualizer.py
git commit -m "test(week2): Task 10.2 - 可视化器单元测试" -m "- 测试图表生成不抛出异常" -m "- 测试图表文件保存成功" -m "- 测试多子图布局" -m "" -m "需求: 6.7"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 11: 实现全市场数据库构建功能
echo ═══════════════════════════════════════════════════════════
git add src/full_market_downloader.py
git commit -m "feat(week2): Task 11.1 - 实现全市场数据库构建" -m "- 实现 FullMarketDownloader 类" -m "- 全市场数据下载 (download_full_market)" -m "- 断点续传功能" -m "- API速率限制处理" -m "- 进度报告和汇总统计" -m "" -m "需求: 8.1, 8.2, 8.3, 8.5, 8.6"

git add tests/unit/test_full_market_downloader.py
git commit -m "test(week2): Task 11.2 - 全市场下载器测试" -m "- 测试断点续传功能" -m "- 测试进度报告" -m "- 测试汇总统计" -m "- 测试状态管理" -m "" -m "需求: 8.3, 8.5, 8.6"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 12: 实现数据对齐和未来函数防范
echo ═══════════════════════════════════════════════════════════
git add src/data_alignment.py
git commit -m "feat(week2): Task 12.1 - 实现数据对齐工具" -m "- 实现 align_data_sources 函数" -m "- 保守日期匹配策略" -m "- 时间点正确性验证" -m "- 未来函数防范文档" -m "" -m "需求: 7.1, 7.4, 7.5"

git add tests/property/test_properties_alignment.py
git commit -m "test(week2): Task 12.2 - 数据对齐属性测试" -m "- 属性21: 保守日期对齐" -m "" -m "需求: 7.5"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 13: 检查点 - 存储和可视化功能
echo ═══════════════════════════════════════════════════════════
git add examples/05_data_persistence.py examples/06_visualization.py examples/07_incremental_update.py
git commit -m "docs(week2): Task 13 - 存储和可视化示例脚本" -m "- 数据持久化演示" -m "- K线图和技术指标演示" -m "- 增量更新演示" -m "- 包含详细注释和说明"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 14: 添加错误处理和日志
echo ═══════════════════════════════════════════════════════════
git add src/*.py tests/property/test_properties_error_handling.py
git commit -m "feat(week2): Task 14 - 完善错误处理和日志" -m "- 自定义异常类" -m "- 详细错误消息" -m "- 优雅降级处理" -m "- 完整日志系统" -m "- 属性22: 无效股票代码错误消息" -m "- 属性24: 部分数据处理连续性" -m "" -m "需求: 9.1, 9.3, 9.6"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 15: 创建教学文档和示例
echo ═══════════════════════════════════════════════════════════
git add README.md
git commit -m "docs(week2): Task 15.1 - 编写README文档" -m "- 项目简介和学习目标" -m "- 安装和配置说明" -m "- 快速开始指南" -m "- API文档链接" -m "" -m "需求: 10.6"

git add src/*.py
git commit -m "docs(week2): Task 15.2 - 完善代码文档" -m "- 所有公共类和函数的文档字符串" -m "- 复杂逻辑的注释" -m "- 前复权vs后复权说明" -m "- 未来函数示例说明" -m "" -m "需求: 10.1, 10.3, 10.4, 10.5"

git add examples/08_full_workflow.py examples/09_build_local_database.py examples/10_lookahead_bias_demo.py examples/README.md
git commit -m "docs(week2): Task 15.3 - 创建综合示例脚本" -m "- 完整工作流演示" -m "- 本地数据库构建演示" -m "- 未来函数问题演示" -m "- 示例说明文档" -m "" -m "需求: 10.2, 10.4"

git add exercises/week2/*.py exercises/week2/README.md
git commit -m "docs(week2): Task 15.4 - 创建练习结构" -m "- Day 8-14 练习文件" -m "- 练习说明文档" -m "- 学习目标概述" -m "- 前置知识标注" -m "" -m "需求: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6"

git add tests/property/test_properties_documentation.py
git commit -m "test(week2): Task 15.5 - 文档完整性验证" -m "- 属性27: 公共API文档完整性" -m "" -m "需求: 10.1"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 16: 运行完整测试套件和集成测试
echo ═══════════════════════════════════════════════════════════
git add tests/integration/*.py pytest.ini .coveragerc
git commit -m "test(week2): Task 16 - 集成测试和配置" -m "集成测试:" -m "- 完整工作流集成测试" -m "- 增量更新集成测试" -m "- 全市场数据库集成测试" -m "" -m "配置:" -m "- pytest 配置" -m "- 覆盖率配置" -m "" -m "需求: 所有需求"

echo.
echo ═══════════════════════════════════════════════════════════
echo Task 17: 最终检查点
echo ═══════════════════════════════════════════════════════════
git add TASK_17_FINAL_VERIFICATION_REPORT.md WEEK2_COMPLETION_SUMMARY.md ENVIRONMENT_FIX_SUMMARY.md GIT_COMMIT_PLAN.md
git commit -m "docs(week2): Task 17 - 最终验证报告" -m "- 完整性验证报告" -m "- Week 2 完成总结" -m "- 环境修复总结" -m "- Git 提交计划" -m "- 所有需求验证完成"

git add examples/demo_*.py examples/industry_mapper_demo.py TASK_*.md
git commit -m "docs(week2): 补充文档和演示文件" -m "- 演示脚本" -m "- 任务验证文档" -m "- 检查点总结"

echo.
echo ═══════════════════════════════════════════════════════════
echo 所有提交完成!
echo ═══════════════════════════════════════════════════════════
echo.
echo 最近的提交:
git log --oneline -20
echo.
echo 提示: 使用 'git push' 推送到远程仓库
pause
