# exercises/ - 学习练习

此目录包含量化交易系统学习课程的实践练习代码，按周组织。

## 目录结构

```text
exercises/
├── __init__.py         # 模块初始化
├── README.md           # 本文件 - 练习目录说明
│
├── week1/              # 第1周：Python 工程基础
│   ├── __init__.py
│   ├── day1_env_check.py       # Day1: 环境检查
│   ├── day2_python_basics.py   # Day2: Python 基础
│   ├── day3_pandas_basics.py   # Day3: Pandas 基础
│   ├── day4_timeseries.py      # Day4: 时间序列处理
│   ├── day5_import_test.py     # Day5: 模块导入测试
│   ├── day5_module_test.py     # Day5: 模块组织
│   ├── day7_verify.py          # Day7: 综合验证
│   └── utils/                  # Week1 工具模块
│       ├── __init__.py
│       ├── data_utils.py
│       └── helpers.py
│
└── week2/              # 第2周：XtData 金融数据工程
    ├── __init__.py
    ├── README.md               # Week2 练习说明
    ├── day8_xtdata_basics.py   # Day8: XtData 基础
    ├── day9_price_adjustment.py # Day9: 复权处理
    ├── day10_fundamental_data.py # Day10: 财务数据
    ├── day11_industry_classification.py # Day11: 行业分类
    ├── day12_data_persistence.py # Day12: 数据持久化
    ├── day13_visualization.py   # Day13: 数据可视化
    └── day14_full_market_db.py  # Day14: 全市场数据库
```

## 学习路径

### Week 1: Python 工程基础

| 天数 | 主题 | 练习文件 | 学习目标 |
| ------ | ------ | ---------- | ---------- |
| Day 1 | 环境配置 | `day1_env_check.py` | 验证 Python 环境和依赖 |
| Day 2 | Python 基础 | `day2_python_basics.py` | 列表、字典、函数、类 |
| Day 3 | Pandas 基础 | `day3_pandas_basics.py` | DataFrame 操作、数据清洗 |
| Day 4 | 时间序列 | `day4_timeseries.py` | 日期处理、重采样 |
| Day 5 | 模块组织 | `day5_*.py` | 包结构、导入机制 |
| Day 7 | 综合验证 | `day7_verify.py` | 本周知识点综合测试 |

### Week 2: XtData 金融数据工程

| 天数 | 主题 | 练习文件 | 学习目标 |
| ------ | ------ | ---------- | ---------- |
| Day 8 | XtData 入门 | `day8_xtdata_basics.py` | API 连接、获取行情 |
| Day 9 | 复权处理 | `day9_price_adjustment.py` | 前/后复权计算 |
| Day 10 | 财务数据 | `day10_fundamental_data.py` | 财报、估值数据获取 |
| Day 11 | 行业分类 | `day11_industry_classification.py` | 申万行业映射 |
| Day 12 | 数据持久化 | `day12_data_persistence.py` | HDF5 存储与读取 |
| Day 13 | 可视化 | `day13_visualization.py` | K线图、技术指标图 |
| Day 14 | 全市场数据 | `day14_full_market_db.py` | 批量下载、数据库构建 |

## 运行练习

```bash
# 运行单个练习
python exercises/week1/day1_env_check.py
python exercises/week2/day8_xtdata_basics.py

# 作为模块运行
python -m exercises.week1.day2_python_basics
```

## 练习要求

1. **顺序完成** - 后续练习依赖前面的知识
2. **阅读注释** - 每个文件包含详细的说明注释
3. **动手实践** - 修改代码，观察结果变化
4. **完成作业** - 文件末尾的 `# TODO` 标记为课后作业

## 与 examples/ 的区别

| 目录 | 用途 | 特点 |
| ------ | ------ | ------ |
| `exercises/` | 学习练习 | 循序渐进、包含 TODO 作业 |
| `examples/` | 参考示例 | 完整功能展示、可直接运行 |

## 注意事项

- 练习代码可能需要配置 `config.py` 中的 API 凭证
- Week2 练习需要 XtQuant 环境（参见 `docs/guides/SETUP_GUIDE.md`）
- 遇到问题可参考 `examples/` 中的完整示例
