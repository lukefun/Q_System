# tests/ - 测试套件

此目录包含项目的完整测试套件，采用分层测试架构：单元测试、属性测试、集成测试。

## 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和共享 fixtures
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_xtdata_client.py
│   ├── test_data_retriever.py
│   ├── test_data_manager.py
│   ├── test_price_adjuster.py
│   ├── test_fundamental_handler.py
│   ├── test_industry_mapper.py
│   ├── test_full_market_downloader.py
│   └── test_visualizer.py
├── property/                # 属性测试（基于 Hypothesis）
│   ├── __init__.py
│   ├── test_properties_retrieval.py
│   ├── test_properties_adjustment.py
│   ├── test_properties_alignment.py
│   ├── test_properties_fundamental.py
│   ├── test_properties_industry.py
│   ├── test_properties_storage.py
│   ├── test_properties_error_handling.py
│   └── test_properties_documentation.py
└── integration/             # 集成测试
    ├── __init__.py
    ├── test_full_workflow.py
    ├── test_incremental_update.py
    └── test_full_market_database.py
```

## 测试分层说明

| 层级 | 目录 | 目的 | 运行频率 |
|------|------|------|----------|
| **单元测试** | `unit/` | 测试单个函数/类的行为 | 每次提交 |
| **属性测试** | `property/` | 验证系统核心不变量（100+迭代） | 每次提交 |
| **集成测试** | `integration/` | 测试模块间协作 | 每日/发布前 |

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定类型测试
pytest -m unit_test          # 仅单元测试
pytest -m property_test      # 仅属性测试
pytest -m integration_test   # 仅集成测试

# 运行单个测试文件
pytest tests/unit/test_data_manager.py

# 运行带覆盖率报告
pytest --cov=src --cov-report=html

# 详细输出
pytest -v
```

## 测试标记（Markers）

在 `conftest.py` 中定义的标记：

```python
@pytest.mark.unit_test        # 单元测试
@pytest.mark.property_test    # 属性测试
@pytest.mark.integration_test # 集成测试
@pytest.mark.slow             # 耗时测试
```

## 共享 Fixtures

`conftest.py` 提供的公共 fixtures：

```python
@pytest.fixture
def sample_kline_data():
    """提供标准K线测试数据"""
    ...

@pytest.fixture
def mock_xtdata_client():
    """模拟XtQuant客户端"""
    ...

@pytest.fixture
def temp_hdf5_path(tmp_path):
    """提供临时HDF5文件路径"""
    ...
```

## 属性测试说明

属性测试使用 Hypothesis 框架，验证系统核心正确性属性：

```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0.01, max_value=10000))
def test_price_always_positive(price):
    """Property: 价格始终为正数"""
    assert price > 0
```

属性测试配置（环境变量）：
- `HYPOTHESIS_MAX_EXAMPLES=100` - 每个属性测试的迭代次数

## 覆盖率要求

- 单元测试覆盖率目标：≥80%
- 属性测试覆盖核心业务逻辑
- 查看覆盖率报告：`htmlcov/index.html`

## 编写测试规范

1. **命名规范**
   - 测试文件：`test_<模块名>.py`
   - 测试函数：`test_<功能>_<场景>`

2. **测试结构**（AAA 模式）
   ```python
   def test_something():
       # Arrange（准备）
       data = setup_test_data()

       # Act（执行）
       result = function_under_test(data)

       # Assert（断言）
       assert result == expected
   ```

3. **Mock 外部依赖**
   ```python
   from unittest.mock import patch, MagicMock

   @patch('src.xtdata_client.xtdata')
   def test_with_mock(mock_xtdata):
       mock_xtdata.get_market_data.return_value = {...}
   ```
