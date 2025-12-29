# docs\SETUP_GUIDE.md


# 新机器环境配置指南

> 本文档指导如何在一台新电脑上正确配置 Q_System 开发环境

## 前置条件

- Windows 10/11
- 已安装 Git
- 已安装 Miniconda 或 Anaconda
- 已安装国金证券 QMT 客户端 (MiniQMT)

---

## 快速配置 (推荐)

### 步骤 1: 克隆项目

```bash
git clone <repository-url>
cd Q_System
```

### 步骤 2: 一键配置

双击运行：
```
scripts\setup_env.bat
```

该脚本会自动：
1. 检查 conda 是否可用
2. 创建 `quants` 环境 (Python 3.8)
3. 安装依赖包
4. 检查 xtquant
5. 运行环境验证

### 步骤 3: 验证环境

```bash
# 方式一：双击运行
check.bat

# 方式二：命令行
conda activate quants
python scripts/check_env.py
```

---

## 手动配置

如果自动配置失败，按以下步骤手动操作：

### 1. 安装 Miniconda

下载地址: https://docs.conda.io/en/latest/miniconda.html

选择 **Miniconda3 Windows 64-bit**

安装后打开 **Anaconda Prompt** 或 **PowerShell**：
```bash
conda --version   # 验证安装
```

### 2. 创建 Python 3.8 环境

```bash
# 创建环境 (必须是 Python 3.8)
conda create -n quants python=3.8 -y

# 激活环境
conda activate quants

# 验证版本
python --version   # 应显示 Python 3.8.x
```

### 3. 安装依赖

```bash
# 进入项目目录
cd Q_System

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装 xtquant

**方法一：pip 安装 (推荐)**
```bash
pip install xtquant
```

**方法二：QMT 客户端安装**
1. 打开 MiniQMT 客户端
2. 进入「量化」→「Python」模块
3. 客户端会自动配置 Python 环境

**方法三：手动复制**
```bash
# 从 QMT 安装目录复制
copy "D:\国金QMT\bin.x64\Lib\site-packages\xtquant" "%CONDA_PREFIX%\Lib\site-packages\"
```

### 5. 验证安装

```bash
python -c "from xtquant import xtdata; print('OK')"
```

---

## 常见问题

### Q1: conda 命令找不到

**问题**: `'conda' 不是内部或外部命令`

**解决**:
1. 确保 Miniconda 已安装
2. 将 Miniconda 添加到 PATH:
   - 右键「此电脑」→「属性」→「高级系统设置」→「环境变量」
   - 在 PATH 中添加: `D:\ProgramData\miniconda3\Scripts`
3. 或使用 Anaconda Prompt 运行命令

### Q2: Python 版本不对

**问题**: 显示 Python 3.10/3.11 而不是 3.8

**原因**: 系统中有多个 Python 版本，可能激活了错误的环境

**解决**:
```bash
# 确认当前环境
conda info --envs

# 确保激活的是 quants
conda activate quants

# 验证
python --version
which python   # 应指向 conda 环境
```

### Q3: xtquant 导入失败

**问题**: `ModuleNotFoundError: No module named 'xtquant'`

**解决**:
```bash
# 方法一：pip 安装
pip install xtquant

# 方法二：检查安装位置
python -c "import sys; print('\n'.join(sys.path))"

# 方法三：从用户目录找
dir %APPDATA%\Python\Python38\site-packages\xtquant
```

### Q4: 项目模块导入失败

**问题**: `ModuleNotFoundError: No module named 'core'`

**解决**: 确保从项目根目录运行
```bash
cd Q_System
python main.py   # ✓ 正确
python D:\path\to\Q_System\main.py   # ✗ 可能失败
```

### Q5: 多个 Python 版本冲突

**问题**: 系统中有 Python 3.9, 3.10, 3.11 等多个版本

**解决**:
1. 始终使用 `conda activate quants` 激活环境
2. 确认当前 Python 路径:
   ```bash
   where python
   # 应显示 D:\ProgramData\miniconda3\envs\quants\python.exe
   ```
3. 避免使用 `py` 命令 (Windows Python Launcher)
4. 必要时在 IDE 中明确指定解释器路径

---

## 环境验证清单

运行 `python scripts/check_env.py` 后，确保以下项目全部通过：

| 检查项 | 期望结果 |
|--------|----------|
| Python 版本 | 3.8.x |
| Conda 环境 | quants |
| pandas | 2.0+ |
| numpy | 1.24+ |
| xtquant | 已安装 |
| xtdata 模块 | 可导入 |
| 项目模块 | 全部可导入 |

---

## IDE 配置

### VS Code

1. 安装 Python 扩展
2. `Ctrl+Shift+P` → `Python: Select Interpreter`
3. 选择 `quants` 环境:
   ```
   Python 3.8.x ('quants')
   D:\ProgramData\miniconda3\envs\quants\python.exe
   ```

### PyCharm

1. `File` → `Settings` → `Project` → `Python Interpreter`
2. 点击齿轮 → `Add`
3. 选择 `Conda Environment` → `Existing environment`
4. 路径: `D:\ProgramData\miniconda3\envs\quants\python.exe`

---

## 最佳实践总结

1. **始终使用 conda 环境**: 避免系统 Python 版本混乱
2. **锁定 Python 3.8**: miniQMT 硬性要求
3. **激活后再操作**: 每次打开终端先 `conda activate quants`
4. **从项目根目录运行**: 确保模块路径正确
5. **定期运行检查**: `python scripts/check_env.py`

---

## 高级: 环境隔离问题

### 问题现象

运行 `python scripts/check_env.py` 时看到警告:
```
[WARN] 检测到 3 个 site-packages 路径，可能存在版本混乱
```

包加载自用户全局目录而非 conda 环境:
```
pandas:  C:\Users\xxx\AppData\Roaming\Python\Python38\site-packages\...
numpy:   C:\Users\xxx\AppData\Roaming\Python\Python38\site-packages\...
```

### 为什么会这样?

1. 系统安装了全局 Python 3.8
2. 使用 `pip install --user` 安装过包
3. Python 默认会先搜索用户级 site-packages

### 潜在风险

- 不同项目可能需要不同版本的包
- conda 环境无法真正隔离
- 更新包时可能影响其他项目

### 解决方案

#### 方案一: 使用隔离模式启动 (推荐)

双击 `start_isolated.bat` 启动开发环境:
```batch
:: 设置环境变量禁用用户级 site-packages
set PYTHONNOUSERSITE=1
conda activate quants
```

这会禁用用户全局包，只使用 conda 环境中的包。

#### 方案二: 重新安装包到 conda 环境

运行修复脚本:
```
scripts\fix_env_isolation.bat
```

该脚本会:
1. 使用 `pip install --no-user` 强制安装到 conda 环境
2. 验证包路径是否正确

#### 方案三: 配置 pip 默认行为

创建 `%APPDATA%\pip\pip.ini`:
```ini
[install]
no-user = true
```

#### 方案四: 清理用户全局包 (谨慎)

如果确认不需要用户全局包:
```bash
# 查看用户级包
pip list --user

# 逐个卸载 (谨慎操作)
pip uninstall --user pandas numpy
```

### 验证隔离是否生效

```python
# 检查包加载路径
import pandas
print(pandas.__file__)
# 期望: D:\...\miniconda3\envs\quants\lib\site-packages\pandas\...
# 不期望: C:\Users\...\AppData\Roaming\Python\...
```

### 最终建议

对于新机器，从一开始就遵循:
1. 只通过 `conda activate quants` 后使用 `pip install` (不加 --user)
2. 不在全局 Python 中安装包
3. 每个项目使用独立的 conda 环境
