# Day 1 学习笔记：隔离模式启动

## 什么是隔离模式？

隔离模式是一种Python环境启动方式，通过设置环境变量 `PYTHONNOUSERSITE=1` 来禁用用户级别的 `site-packages` 目录，确保Python只使用当前conda环境中的包。

## `PYTHONNOUSERSITE=1` 的作用

### 问题背景

在Windows系统中，Python会从多个位置加载包：

1. **系统级 site-packages**: Python安装目录下的包
2. **用户级 site-packages**: 用户目录下的包（如 `%APPDATA%\Python\Python38\site-packages`）
3. **Conda环境 site-packages**: 当前激活的conda环境中的包

当系统中存在多个Python版本或用户曾经用 `pip install --user` 安装过包时，可能会出现**版本冲突**问题。

### 解决方案

设置 `PYTHONNOUSERSITE=1` 后：

- Python启动时会**跳过**用户级 `site-packages` 目录
- 只加载conda环境中的包
- 避免不同来源的包版本冲突

### 验证方法

启动隔离模式后，脚本会执行以下验证代码：

```python
import sys
sp = [p for p in sys.path if 'site-packages' in p and 'vendor' not in p]
print('site-packages 路径:')
for p in sp:
    print(f'  {p}')
```

正常情况下，输出应该只显示conda环境的 `site-packages` 路径，不应包含用户目录下的路径。

## 何时需要使用隔离模式？

1. **xtquant导入失败**: 如果正常启动时 `from xtquant import xtdata` 报错
2. **版本不匹配**: 某些包的版本与预期不符
3. **奇怪的导入错误**: 导入模块时出现意外的错误

## 使用方法

### 方法1: 双击批处理文件

```powershell
双击 start_isolated.bat
```

### 方法2: PowerShell执行

```powershell
.\start_isolated.ps1
```

### 方法3: 手动设置（临时）

```cmd
set PYTHONNOUSERSITE=1
conda activate quants
python your_script.py
```

## 关键要点总结

|环境变量|值|作用|
|--------|---|------|
|`PYTHONNOUSERSITE`|`1`|禁用用户级site-packages|
|`PYTHONNOUSERSITE`|未设置或`0`|正常加载所有site-packages|

## 学习收获

1. 理解了Python包加载的多层级机制

    ```text
    Python 包加载多层级机制的核心要点：

    - 查找优先级：局部命名空间 > 当前工作目录 > 标准库 > site-packages > PYTHONPATH；
    - 具象化载体是sys.path列表，按顺序遍历查找；
    - 包的识别依赖__init__.py（规范方案），多层级包内部支持绝对 / 相对导入；
    - 核心逻辑是 “从近到远”，优先加载更贴近当前执行环境的包 / 模块。
    ```

2. 学会了使用环境变量控制Python行为

3. 掌握了解决多Python版本冲突的方法

4. 这种隔离思想在量化开发中很重要，确保环境的一致性和可复现性

---
*记录日期: Week 1 Day 1*
*相关文件: start_isolated.bat, start_isolated.ps1*
