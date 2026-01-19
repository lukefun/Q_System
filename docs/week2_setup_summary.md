# Week 2 项目结构设置总结

## 已完成的设置

### 1. 目录结构 ✓

创建了以下目录结构：

```
Q_System/
├── src/                    # 源代码目录
│   └── __init__.py
├── tests/                  # 测试目录
│   ├── unit/              # 单元测试
│   ├── property/          # 属性测试
│   ├── integration/       # 集成测试
│   ├── __init__.py
│   └── conftest.py        # pytest配置和fixtures
├── examples/              # 示例脚本
│   └── README.md
├── data/                  # 数据存储
│   ├── cache/            # 缓存目录
│   └── csv_exports/      # CSV导出目录
└── logs/                  # 日志目录
```

### 2. 配置文件 ✓

#### config.py
完整的配置管理系统，包括：
- **路径配置**：项目根目录、数据目录、HDF5路径、日志目录等
- **API配置**：XtData账户配置、超时设置、重试机制、速率限制
- **数据配置**：默认周期、复权类型、数据质量阈值
- **存储配置**：HDF5压缩设置、日期格式
- **可视化配置**：图表样式、中国市场颜色惯例
- **日志配置**：日志级别、格式、文件轮转
- **自定义异常类**：XtDataError、ConnectionError、DataError、ValidationError、StorageError

#### .env.example
环境变量配置示例，包含：
- XtData API凭证配置说明
- 日志级别配置
- 数据存储路径配置

### 3. 依赖管理 ✓

#### requirements.txt
更新了依赖列表，包含：
- **数据处理**：pandas, numpy
- **可视化**：matplotlib
- **HDF5存储**：tables (PyTables)
- **测试框架**：pytest, pytest-cov, hypothesis
- **配置管理**：pydantic, python-dotenv
- **网络请求**：requests, tqdm

### 4. 测试基础设施 ✓

#### tests/conftest.py
提供了完整的测试支持：
- **pytest配置**：测试标记（slow, integration, property）
- **临时目录fixtures**：temp_dir, temp_hdf5_path
- **Mock对象fixtures**：mock_xtdata_client
- **示例数据fixtures**：
  - sample_stock_codes
  - sample_date_range
  - sample_daily_data
  - sample_tick_data
  - sample_fundamental_data
  - sample_industry_structure
  - sample_adjust_factors
- **测试工具函数**：
  - assert_dataframe_equal
  - generate_random_ohlcv

### 5. 日志系统 ✓

- 自动创建logs目录
- 支持文件和控制台双输出
- 日志文件按日期命名
- 支持日志轮转（10MB，保留5个备份）
- 可配置的日志级别

### 6. 错误处理 ✓

定义了完整的异常层次结构：
- `XtDataError`：基础异常类
- `ConnectionError`：API连接错误
- `DataError`：数据相关错误
- `ValidationError`：数据验证错误
- `StorageError`：存储相关错误

### 7. 文档 ✓

- `examples/README.md`：示例脚本使用说明
- `docs/week2_setup_summary.md`：本文档

### 8. 验证脚本 ✓

创建了 `scripts/verify_week2_setup.py`，可以验证：
- 目录结构完整性
- 关键文件存在性
- Python模块可导入性
- 配置正确性

## 待安装的依赖

运行以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

特别注意：
- `matplotlib`：可视化库（必需）
- `tables`：PyTables，用于HDF5存储（强烈推荐）
- `xtquant`：需要单独安装或从QMT客户端获取

## 配置步骤

### 1. 设置环境变量

复制 `.env.example` 为 `.env`：
```bash
copy .env.example .env
```

编辑 `.env` 文件，填入你的XtData API凭证：
```
XTDATA_ACCOUNT_ID=your_actual_account_id
XTDATA_ACCOUNT_KEY=your_actual_account_key
```

### 2. 验证设置

运行验证脚本：
```bash
python scripts/verify_week2_setup.py
```

应该看到类似输出：
```
验证结果: 21/23 项通过 (91.3%)
```

## 使用示例

### 导入配置

```python
import config

# 使用配置
print(f"数据目录: {config.DATA_DIR}")
print(f"HDF5路径: {config.HDF5_PATH}")

# 使用logger
config.logger.info("开始数据处理")

# 使用异常
try:
    # 某些操作
    pass
except Exception as e:
    raise config.DataError(f"数据处理失败: {e}")
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行单元测试
pytest tests/unit/

# 运行属性测试
pytest tests/property/

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 下一步

项目结构已经设置完成，可以开始实现具体功能模块：

1. **Task 2**：实现XtData客户端封装
2. **Task 3**：实现数据获取器
3. **Task 4**：检查点 - 确保数据获取功能正常
4. 继续后续任务...

## 注意事项

1. **敏感信息**：不要将 `.env` 文件提交到版本控制系统
2. **数据目录**：`data/` 目录已在 `.gitignore` 中，不会被提交
3. **日志文件**：日志文件会自动轮转，避免占用过多磁盘空间
4. **API凭证**：确保XtData API凭证正确配置后再运行数据获取功能

## 验证清单

- [x] 创建目录结构：src/, tests/, examples/, data/, logs/
- [x] 创建配置文件 config.py
- [x] 设置日志配置
- [x] 定义自定义异常类
- [x] 更新 requirements.txt
- [x] 创建测试基础设施（conftest.py）
- [x] 创建 .env.example
- [x] 更新 .gitignore
- [x] 创建验证脚本
- [x] 创建文档

所有任务已完成！✓
