# scripts/ - 工具脚本

此目录包含项目的各类工具脚本，按功能分类组织。

## 目录结构

```text
scripts/
├── README.md           # 本文件 - 脚本目录说明
│
├── setup/              # 环境配置脚本
│   ├── setup_env.bat       # Windows 环境初始化（CMD）
│   ├── setup_env.ps1       # Windows 环境初始化（PowerShell）
│   ├── start_isolated.bat  # 启动隔离环境（CMD）
│   ├── start_isolated.ps1  # 启动隔离环境（PowerShell）
│   └── fix_env_isolation.bat # 修复环境隔离问题
│
├── verify/             # 验证脚本
│   ├── check_env.py        # 环境检查（Python 版本、依赖）
│   ├── verify_week2_setup.py # Week2 环境验证
│   └── verify_documentation.py # 文档完整性验证
│
└── utils/              # 工具脚本
    ├── check.bat           # 快速代码检查
    ├── git_commit_all.bat  # 批量 Git 提交
    └── git_commit_week2.ps1 # Week2 代码提交
```

## 脚本分类说明

### setup/ - 环境配置

用于初始化和配置开发环境的脚本。

| 脚本 | 用途 | 使用方式 |
| ------ | ------ | ---------- |
| `setup_env.bat` | 首次环境配置 | 双击运行或 `cmd /c setup_env.bat` |
| `setup_env.ps1` | 首次环境配置 (PowerShell) | `powershell -ExecutionPolicy Bypass -File setup_env.ps1` |
| `start_isolated.bat` | 启动隔离开发环境 | 双击运行 |
| `start_isolated.ps1` | 启动隔离开发环境 (PowerShell) | `.\start_isolated.ps1` |
| `fix_env_isolation.bat` | 修复环境隔离问题 | 遇到环境冲突时运行 |

### verify/ - 验证脚本

用于验证环境和代码状态的 Python 脚本。

| 脚本 | 用途 | 运行命令 |
| ------ | ------ | ---------- |
| `check_env.py` | 检查 Python 环境和依赖 | `python scripts/verify/check_env.py` |
| `verify_week2_setup.py` | 验证 Week2 环境配置 | `python scripts/verify/verify_week2_setup.py` |
| `verify_documentation.py` | 验证文档完整性 | `python scripts/verify/verify_documentation.py` |

### utils/ - 工具脚本

日常开发中使用的便捷工具。

| 脚本 | 用途 | 运行命令 |
| ------ | ------ | ---------- |
| `check.bat` | 运行代码检查（lint + test） | `scripts\utils\check.bat` |
| `git_commit_all.bat` | 批量提交所有变更 | `scripts\utils\git_commit_all.bat` |
| `git_commit_week2.ps1` | 提交 Week2 代码 | `.\scripts\utils\git_commit_week2.ps1` |

## 使用示例

### 首次环境配置

```batch
# Windows CMD
cd Q_System
scripts\setup\setup_env.bat
```

```powershell
# PowerShell
cd Q_System
.\scripts\setup\setup_env.ps1
```

### 验证环境

```bash
python scripts/verify/check_env.py
```

### 日常开发

```batch
# 运行代码检查
scripts\utils\check.bat
```

## 脚本开发规范

1. **命名规范**
   - 环境脚本：`setup_*.bat/ps1`, `start_*.bat/ps1`
   - 验证脚本：`verify_*.py`, `check_*.py`
   - 工具脚本：描述性名称

2. **注释要求**
   - 脚本开头需包含用途说明
   - 复杂逻辑需添加行内注释

3. **错误处理**
   - 批处理脚本需检查前置条件
   - Python 脚本需使用 try-except
