# docs\ENVIRONMENT.md

# 开发环境管理文档

> 最后更新: 2025-12-27

## 环境概览

| 项目 | 值 |
|------|-----|
| Conda 版本 | 25.7.0 |
| 环境名称 | `quants` |
| Python 版本 | 3.8.20 |
| 环境路径 | `D:\ProgramData\miniconda3\envs\quants` |
| miniQMT 要求 | Python 3.8 ✓ |

## 快速开始

```bash
# 激活环境
conda activate quants

# 验证环境
python --version          # 应显示 Python 3.8.x
python -c "from xtquant import xtdata; print('xtquant OK')"

# 运行项目
python main.py            # 回测
python run_live.py        # 实盘 (模拟模式)
```

---

## 环境调查报告

### 1. 已安装的核心包

#### 数据处理 (Data Processing)
| 包名 | 版本 | 状态 | 说明 |
|------|------|------|------|
| pandas | 2.0.3 | ✅ 已安装 | 数据分析核心库 |
| numpy | 1.24.4 | ✅ 已安装 | 数值计算库 |
| matplotlib | 3.7.5 | ✅ 已安装 | 数据可视化 |

#### 交易接口 (Trading API)
| 包名 | 版本 | 状态 | 说明 |
|------|------|------|------|
| xtquant | 250516.1.1 | ✅ 已安装 | 国金证券 QMT 接口 |

> **注意**: xtquant 安装在用户全局路径:
> `C:\Users\fangc\AppData\Roaming\Python\Python38\site-packages`
> 通过 Python 的 sys.path 机制可正常导入。

#### 测试框架 (Testing)
| 包名 | 版本 | 状态 | 说明 |
|------|------|------|------|
| pytest | 8.3.5 | ✅ 已安装 | 测试框架 |
| pytest-asyncio | 0.24.0 | ✅ 已安装 | 异步测试支持 |
| pytest-cov | 5.0.0 | ✅ 已安装 | 覆盖率报告 |
| pytest-xdist | 3.6.1 | ✅ 已安装 | 并行测试 |
| hypothesis | 6.113.0 | ✅ 已安装 | 属性测试 |
| coverage | 7.6.1 | ✅ 已安装 | 代码覆盖率 |

#### 配置管理 (Configuration)
| 包名 | 版本 | 状态 | 说明 |
|------|------|------|------|
| pydantic | 2.10.6 | ✅ 已安装 | 数据验证 |
| pydantic-settings | 2.8.1 | ✅ 已安装 | 配置管理 |
| python-dotenv | 1.0.1 | ✅ 已安装 | 环境变量 |

#### 其他工具
| 包名 | 版本 | 状态 | 说明 |
|------|------|------|------|
| requests | 2.32.4 | ✅ 已安装 | HTTP 客户端 |
| jieba | 0.42.1 | ✅ 已安装 | 中文分词 |
| tqdm | 4.67.1 | ✅ 已安装 | 进度条 |

### 2. Q_System 项目依赖评估

#### 当前项目所需依赖
```
xtquant        ✅ 已满足
pandas         ✅ 已满足
numpy          ✅ 已满足 (xtquant 依赖)
abc            ✅ Python 标准库
sys            ✅ Python 标准库
time           ✅ Python 标准库
datetime       ✅ Python 标准库
random         ✅ Python 标准库
```

**结论: Q_System 项目的所有依赖已满足，可正常运行。**

### 3. 父项目 (ai_quant_app) 依赖缺口分析

如果需要运行完整的 ai_quant_app 项目，以下是缺失的依赖：

#### 必须安装 (Web 框架)
```
fastapi        ❌ 缺失
uvicorn        ❌ 缺失
```

#### 必须安装 (数据库)
```
pymongo        ❌ 缺失
redis          ❌ 缺失
motor          ❌ 缺失
```

#### 必须安装 (数据处理)
```
scipy          ❌ 缺失
```

#### 可选安装 (机器学习)
```
scikit-learn   ❌ 缺失
tensorflow     ❌ 缺失 (大型包，按需安装)
torch          ❌ 缺失 (大型包，按需安装)
transformers   ❌ 缺失 (大型包，按需安装)
```

#### 可选安装 (开发工具)
```
black          ❌ 缺失 (代码格式化)
flake8         ❌ 缺失 (代码检查)
mypy           ❌ 缺失 (类型检查)
```

---

## 环境管理规范

### 1. 环境文件结构

```
Q_System/
├── docs/
│   └── ENVIRONMENT.md        # 本文档
├── requirements.txt          # 生产依赖 (待创建)
├── requirements-dev.txt      # 开发依赖 (待创建)
└── environment.yml           # Conda 环境导出 (待创建)
```

### 2. 依赖管理原则

1. **锁定 Python 版本**: 必须使用 Python 3.8.x (miniQMT 硬性要求)
2. **优先 conda 安装**: 基础包使用 conda 安装，保证二进制兼容性
3. **pip 补充安装**: conda 没有的包使用 pip 安装
4. **xtquant 特殊处理**: xtquant 通过 QMT 客户端安装，不在 requirements 中列出

### 3. 环境操作命令

#### 创建新环境 (首次)
```bash
# 从零开始创建
conda create -n quants python=3.8 -y
conda activate quants

# 安装基础包
pip install pandas numpy matplotlib
pip install pytest pytest-cov hypothesis
pip install pydantic pydantic-settings python-dotenv
```

#### 导出环境
```bash
# 导出为 YAML (推荐)
conda env export -n quants --no-builds > environment.yml

# 导出 pip 包列表
conda run -n quants pip freeze > requirements.txt
```

#### 从文件恢复环境
```bash
# 从 YAML 恢复
conda env create -f environment.yml

# 从 requirements.txt 恢复
conda create -n quants python=3.8 -y
conda activate quants
pip install -r requirements.txt
```

#### 更新依赖
```bash
# 更新单个包
conda run -n quants pip install --upgrade pandas

# 更新所有包 (谨慎操作)
conda run -n quants pip list --outdated
```

---

## xtquant 安装说明

xtquant 是国金证券提供的量化交易 SDK，需要特殊安装方式：

### 安装路径
```
当前安装位置: C:\Users\fangc\AppData\Roaming\Python\Python38\site-packages\xtquant
版本: 250516.1.1
```

### 安装方法 (如需重新安装)

1. **方法一: 通过 QMT 客户端自动安装**
   - 打开 MiniQMT 客户端
   - 进入"量化"模块
   - 客户端会自动配置 Python 环境

2. **方法二: 手动 pip 安装**
   ```bash
   pip install xtquant
   ```

3. **方法三: 从 QMT 目录复制**
   - 复制 `QMT安装目录\Lib\site-packages\xtquant` 到 Python 环境

### 验证安装
```python
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount
print("xtquant 导入成功")
```

---

## 常见问题

### Q1: conda activate 失败
```bash
# 错误: Run 'conda init' before 'conda activate'
# 解决: 初始化 conda
conda init powershell  # 或 conda init cmd.exe
# 重新打开终端
```

### Q2: xtquant 导入失败
```bash
# 检查 Python 版本
python --version  # 必须是 3.8.x

# 检查安装位置
python -c "import xtquant; print(xtquant.__file__)"

# 检查 sys.path
python -c "import sys; print('\n'.join(sys.path))"
```

### Q3: 包版本冲突
```bash
# 查看冲突
pip check

# 强制重装指定版本
pip install numpy==1.24.4 --force-reinstall
```

---

## 附录: 完整包列表

### Conda 包 (conda list)
```
python         3.8.20
pip            24.3.1
setuptools     75.3.0
wheel          0.45.1
```

### Pip 包 (pip list)
```
Package             Version
------------------- -----------
annotated-types     0.7.0
certifi             2025.11.12
colorama            0.4.6
contourpy           1.1.1
coverage            7.6.1
cycler              0.12.1
fonttools           4.57.0
hypothesis          6.113.0
jieba               0.42.1
kiwisolver          1.4.7
matplotlib          3.7.5
numpy               1.24.4
packaging           25.0
pandas              2.0.3
pillow              10.4.0
pluggy              1.5.0
pydantic            2.10.6
pydantic_core       2.27.2
pydantic-settings   2.8.1
pyparsing           3.1.4
pytest              8.3.5
pytest-asyncio      0.24.0
pytest-cov          5.0.0
pytest-timeout      2.4.0
pytest-xdist        3.6.1
python-dateutil     2.9.0.post0
python-dotenv       1.0.1
requests            2.32.4
sortedcontainers    2.4.0
tqdm                4.67.1
typing_extensions   4.13.2
xtquant             250516.1.1
```
