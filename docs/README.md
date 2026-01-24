# docs/ - 项目文档

此目录包含项目的所有文档资料，按功能分类组织。

## 目录结构

```text
docs/
├── README.md                 # 本文件 - 文档目录说明
├── CODE_DOCUMENTATION.md     # 代码文档标准与规范
│
├── guides/                   # 用户指南
│   ├── LEARNING_GUIDE.md         # 学习路线指南
│   ├── QUICK_REFERENCE.md        # 快速参考手册
│   ├── SETUP_GUIDE.md            # 环境安装指南
│   ├── ENVIRONMENT.md            # 开发环境配置
│   ├── ENVIRONMENT_FIX_SUMMARY.md # 环境问题修复记录
│   ├── STUDY_PATH.md             # 学习路径导航
│   ├── LEARNING_MATERIALS_SUMMARY.md # 学习资料汇总
│   ├── PROJECT_STRUCTURE_ANALYSIS.md # 项目结构分析
│   └── week2_setup_summary.md    # Week2 环境配置总结
│
├── api/                      # API 文档
│   ├── xtdata.md                 # XtData API 完整参考
│   └── xttrader.md               # XtTrader 交易接口参考
│
├── plans/                    # 计划与规划
│   ├── plan.md                   # 项目实施计划
│   ├── GIT_COMMIT_PLAN.md        # Git 提交规范
│   └── Q_System 全栈量化架构师 120天深度养成计划.md
│
├── reports/                  # 任务验证报告
│   ├── TASK_8_CHECKPOINT_SUMMARY.md
│   ├── TASK_9.1_VERIFICATION.md
│   ├── TASK_9.2_VERIFICATION.md
│   ├── TASK_9.3_SUMMARY.md
│   ├── TASK_10.1_VERIFICATION.md
│   ├── TASK_10.2_VERIFICATION.md
│   ├── TASK_10_COMPLETE_SUMMARY.md
│   ├── TASK_11_VERIFICATION.md
│   ├── TASK_12_VERIFICATION.md
│   ├── TASK_13_CHECKPOINT_SUMMARY.md
│   ├── TASK_15.5_VERIFICATION.md
│   ├── TASK_17_FINAL_VERIFICATION_REPORT.md
│   └── WEEK2_COMPLETION_SUMMARY.md
│
└── notes/                    # 学习笔记
    ├── week1_summary.md
    ├── week1_day1_isolation_mode.md
    ├── week1_day5_project_structure.md
    ├── week1_day6_git_version_control.md
    └── task_6.2_property_test_summary.md
```

## 文档分类说明

### guides/ - 用户指南

面向开发者的使用指南，包含环境配置、学习路径、快速参考等。

**推荐阅读顺序：**

1. `SETUP_GUIDE.md` - 首次环境配置
2. `LEARNING_GUIDE.md` - 学习路线概览
3. `QUICK_REFERENCE.md` - 日常开发参考

### api/ - API 文档

XtQuant 数据源的完整 API 参考文档。

| 文档 | 内容 |
| ------ | ------ |
| `xtdata.md` | 行情数据接口（K线、Tick、财务数据） |
| `xttrader.md` | 交易接口（下单、撤单、账户查询） |

### plans/ - 计划文档

项目规划、学习计划、开发规范等长期规划文档。

### reports/ - 验证报告

任务完成验证报告，记录每个开发阶段的验收结果。

### notes/ - 学习笔记

开发过程中的学习记录和技术笔记。

## 文档维护规范

1. **新文档放置原则**
   - 用户指南 → `guides/`
   - API参考 → `api/`
   - 任务报告 → `reports/`
   - 学习笔记 → `notes/`
   - 长期规划 → `plans/`

2. **命名规范**
   - 使用大写字母和下划线：`SETUP_GUIDE.md`
   - 任务报告：`TASK_<编号>_<类型>.md`
   - 周总结：`WEEK<N>_<类型>.md`

3. **更新要求**
   - 代码变更需同步更新相关文档
   - 重大功能需更新 `QUICK_REFERENCE.md`
   - 环境变更需更新 `SETUP_GUIDE.md`
