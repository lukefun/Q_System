# Week 2 示例脚本

本目录包含Week 2金融数据工程系统的示例脚本，演示各个模块的使用方法。

## 示例列表

### 基础功能示例

- `01_basic_data_retrieval.py` - 基本数据获取示例
- `02_price_adjustment.py` - 价格复权示例
- `03_fundamental_data.py` - 基本面数据处理示例
- `04_industry_classification.py` - 行业分类查询示例

### 高级功能示例

- `05_data_persistence.py` - 数据持久化和加载示例
- `06_visualization.py` - K线图和技术指标可视化示例
- `07_incremental_update.py` - 增量更新示例

### 综合示例

- `08_full_workflow.py` - 完整数据工程工作流示例
- `09_build_local_database.py` - 构建本地全市场数据库示例
- `10_lookahead_bias_demo.py` - 未来函数问题演示

## 使用说明

1. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置XtData API凭证（设置环境变量）：
   ```bash
   set XTDATA_ACCOUNT_ID=your_account_id
   set XTDATA_ACCOUNT_KEY=your_account_key
   ```

3. 运行示例脚本：
   ```bash
   python examples/01_basic_data_retrieval.py
   ```

## 注意事项

- 示例脚本需要有效的XtData API凭证才能运行
- 部分示例会下载真实市场数据，请注意API调用限制
- 建议按顺序学习示例，从基础到高级
