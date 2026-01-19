# Week 2 练习：金融数据工程

## 学习目标

通过本周的练习，你将掌握：

1. **XtData API集成**
   - 连接和认证
   - 数据获取接口
   - 错误处理

2. **价格复权机制**
   - 前复权和后复权的区别
   - 复权算法实现
   - 回测中的应用

3. **基本面数据ETL**
   - 财务指标提取
   - 时间点正确性
   - 未来函数防范

4. **行业分类管理**
   - 申万行业体系
   - 历史分类查询
   - 板块分析

5. **数据持久化**
   - HDF5存储
   - 增量更新
   - 数据查询

6. **数据可视化**
   - K线图绘制
   - 技术指标叠加
   - 多股票对比

7. **全市场数据库构建**
   - 批量下载
   - 断点续传
   - 数据质量检查

## 练习进阶路径

```
Day 8: XtData基础接口
    ↓
Day 9: 价格复权处理
    ↓
Day 10: 基本面数据ETL
    ↓
Day 11: 行业分类管理
    ↓
Day 12: 数据持久化
    ↓
Day 13: 数据可视化
    ↓
Day 14: 全市场数据库构建
```

## 练习文件

| 文件 | 主题 | 难度 | 前置知识 |
|------|------|------|----------|
| `day8_xtdata_basics.py` | XtData基础接口 | ⭐ | Python基础 |
| `day9_price_adjustment.py` | 价格复权 | ⭐⭐ | Day 8 |
| `day10_fundamental_data.py` | 财务数据ETL | ⭐⭐ | Day 8 |
| `day11_industry_classification.py` | 行业分类 | ⭐⭐ | Day 8 |
| `day12_data_persistence.py` | 数据持久化 | ⭐⭐⭐ | Day 8-11 |
| `day13_visualization.py` | 可视化 | ⭐⭐ | Day 8-12 |
| `day14_full_market_db.py` | 全市场数据库 | ⭐⭐⭐ | Day 8-13 |

## 使用方法

### 1. 配置环境

确保已完成Week 1的环境配置，并安装了所有依赖：

```bash
conda activate quants
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑项目根目录的 `config.py` 文件，配置你的XtData账户信息：

```python
XTDATA_ACCOUNT_ID = '你的账户ID'
XTDATA_ACCOUNT_KEY = '你的账户密钥'
```

### 3. 运行练习

每个练习文件都是独立的，可以直接运行：

```bash
# 激活环境
conda activate quants

# 运行Day 8练习
python exercises/week2/day8_xtdata_basics.py

# 运行Day 9练习
python exercises/week2/day9_price_adjustment.py

# ... 依此类推
```

### 4. 完成练习

每个练习文件包含：
- **学习目标**：本练习要掌握的知识点
- **练习任务**：需要完成的编程任务
- **提示**：实现思路和关键点
- **预期输出**：程序运行的预期结果
- **扩展挑战**：进阶任务（可选）

按照文件中的说明完成练习任务，运行程序验证结果。

## 学习建议

### 循序渐进

- 按照Day 8 → Day 14的顺序学习
- 每天完成一个练习，不要跳跃
- 确保理解当前内容再进入下一天

### 动手实践

- 不要只看代码，一定要自己动手写
- 尝试修改参数，观察结果变化
- 遇到错误时，先尝试自己调试

### 参考示例

- 每个练习都有对应的示例脚本在 `examples/` 目录
- 遇到困难时可以参考示例代码
- 但要先尝试自己实现，再看示例

### 理解概念

- 重点理解前复权vs后复权的区别
- 掌握未来函数的概念和防范方法
- 理解时间点正确性的重要性

### 查阅文档

- 参考 `docs/CODE_DOCUMENTATION.md` 了解核心概念
- 查看 `docs/xtdata.md` 了解API详情
- 阅读源代码中的文档字符串

## 常见问题

### Q1: XtData连接失败怎么办？

**A:** 检查以下几点：
1. 账户ID和密钥是否正确配置
2. 是否安装了xtquant库：`pip install xtquant`
3. 网络连接是否正常
4. 查看日志文件 `logs/xtdata_system_*.log` 获取详细错误信息

### Q2: 为什么要使用前复权而不是后复权？

**A:** 
- 前复权保持当前价格真实，适合回测
- 后复权使用了未来信息，会导致回测结果过于乐观
- 详见 `examples/10_lookahead_bias_demo.py`

### Q3: 什么是未来函数？如何避免？

**A:**
- 未来函数是在历史分析中使用未来信息的错误
- 避免方法：
  - 使用前复权
  - 基本面数据使用公告日期
  - 行业分类使用历史时点
- 详见 `docs/CODE_DOCUMENTATION.md` 的未来函数章节

### Q4: HDF5文件太大怎么办？

**A:**
- 使用压缩：`complib='blosc', complevel=9`
- 只保存必要的列
- 定期清理旧数据
- 使用增量更新而非全量下载

### Q5: 数据质量有问题怎么办？

**A:**
- 使用 `DataManager.generate_quality_report()` 检查数据质量
- 查看异常值、缺口、缺失值等问题
- 根据报告修复或重新下载数据

## 扩展资源

### 官方文档

- [XtQuant官方文档](https://dict.thinktrader.net/nativeApi/start_now.html)
- [Pandas官方文档](https://pandas.pydata.org/docs/)
- [Matplotlib官方文档](https://matplotlib.org/stable/contents.html)

### 项目文档

- [README.md](../../README.md) - 项目概览
- [docs/CODE_DOCUMENTATION.md](../../docs/CODE_DOCUMENTATION.md) - 核心概念详解
- [docs/xtdata.md](../../docs/xtdata.md) - XtData API参考
- [examples/README.md](../../examples/README.md) - 示例脚本说明

### 学习路径

- Week 1: Python基础和环境配置
- **Week 2: 金融数据工程（当前）**
- Week 3: 策略开发基础
- Week 4: 回测系统设计
- Week 5+: 高级策略和实盘交易

## 完成标准

完成本周练习后，你应该能够：

- [ ] 熟练使用XtData API获取市场数据
- [ ] 理解并正确应用价格复权
- [ ] 处理基本面数据并确保时间点正确性
- [ ] 查询和管理行业分类数据
- [ ] 使用HDF5进行数据持久化
- [ ] 绘制K线图和技术指标
- [ ] 构建和维护本地全市场数据库
- [ ] 理解并避免未来函数

## 反馈与改进

如果你在学习过程中遇到问题或有改进建议，欢迎：

- 提交Issue到项目仓库
- 与导师或同学讨论
- 查看FAQ和文档

祝学习顺利！📈
