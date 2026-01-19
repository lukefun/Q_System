# Week 1 Day 6: Git版本控制学习笔记

**学习日期**: 2026-01-15  
**学习主题**: Git版本控制基础操作  
**预计时间**: 3-4小时  
**实际完成**: ✓

---

## 一、学习目标

掌握Git基本操作，建立代码备份习惯，为团队协作和代码管理打下基础。

---

## 二、核心知识点

### 2.1 Git基础概念

**什么是Git？**
- 分布式版本控制系统
- 记录代码的每一次变更
- 支持多人协作开发
- 可以回退到任意历史版本

**为什么量化开发需要Git？**
- 策略代码需要版本管理
- 回测参数调整需要记录
- 团队协作需要代码同步
- 生产环境代码需要可追溯

### 2.2 Git工作区域

```plaintext
工作区 (Working Directory)
    ↓ git add
暂存区 (Staging Area)
    ↓ git commit
本地仓库 (Local Repository)
    ↓ git push
远程仓库 (Remote Repository)
```

---

## 三、实践练习总结

### 练习1: Git基础操作

**命令实践**:
```bash
# 查看仓库状态
git status

# 查看提交历史
git log --oneline
```

**学习要点**:
- `git status` 显示当前工作区状态（已修改、未跟踪文件）
- `git log --oneline` 以简洁格式显示提交历史
- 确认项目已有 `.git` 目录（仓库已初始化）

**实际输出示例**:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   .kiro/specs/week1-python-engineering/tasks.md

Untracked files:
  exercises/week1/day2_python_basics.py
  exercises/week1/day3_pandas_basics.py
```

### 练习2: 提交练习代码

**命令实践**:
```bash
# 添加文件到暂存区
git add exercises/

# 提交到本地仓库
git commit -m "Week1: 添加练习代码"

# 验证提交
git log --oneline -1
```

**学习要点**:
- `git add` 将文件添加到暂存区
- `git commit -m` 提交并附带说明信息
- 提交信息应清晰描述本次变更内容

**提交结果**:
```
[main b044601] Week1: 添加练习代码
 7 files changed, 1700 insertions(+)
 create mode 100644 exercises/week1/day2_python_basics.py
 create mode 100644 exercises/week1/day3_pandas_basics.py
 create mode 100644 exercises/week1/day4_timeseries.py
 create mode 100644 exercises/week1/day5_import_test.py
 create mode 100644 exercises/week1/day5_module_test.py
 create mode 100644 exercises/week1/utils/__init__.py
 create mode 100644 exercises/week1/utils/helpers.py
```

### 练习3: 分支操作

**命令实践**:
```bash
# 创建新分支
git branch dev

# 切换到新分支
git checkout dev

# 在dev分支上做修改并提交
git add exercises/week1/day6_git_practice.py
git commit -m "Week1 Day6: 在dev分支上添加Git练习文件"

# 切换回主分支
git checkout main

# 查看所有分支
git branch
```

**学习要点**:
- 分支是独立的开发线
- 在dev分支上的修改不会影响main分支
- 切换分支时，工作区文件会自动变化
- 分支适用于功能开发、bug修复等场景

**分支使用场景**:
- `main` 分支: 稳定的生产代码
- `dev` 分支: 开发测试代码
- `feature-xxx` 分支: 新功能开发
- `hotfix-xxx` 分支: 紧急bug修复

**实践验证**:
```bash
# 在main分支上，dev分支创建的文件不存在
$ dir exercises\week1\day6_git_practice.py
Cannot find path ... because it does not exist.
```

### 练习4: 回退操作

**命令实践**:
```bash
# 故意创建一个错误提交
git add exercises/week1/wrong_file.py
git commit -m "错误提交: 添加了有bug的代码"

# 使用revert回退
git revert HEAD --no-edit

# 查看提交历史
git log --oneline -3
```

**学习要点**:
- `git revert` 创建一个新提交来撤销之前的提交
- 不会删除历史记录，保持完整的提交链
- 适用于已经推送到远程的提交

**提交历史**:
```
8bef152 (HEAD -> main) Revert "错误提交: 添加了有bug的代码"
1286f83 错误提交: 添加了有bug的代码
b044601 Week1: 添加练习代码
```

---

## 四、Git常用命令速查表

### 基础操作
```bash
git init                    # 初始化仓库
git status                  # 查看状态
git add <file>              # 添加文件到暂存区
git add .                   # 添加所有文件
git commit -m "message"     # 提交
git log                     # 查看提交历史
git log --oneline           # 简洁格式查看历史
```

### 分支操作
```bash
git branch                  # 查看所有分支
git branch <name>           # 创建分支
git checkout <name>         # 切换分支
git checkout -b <name>      # 创建并切换分支
git merge <branch>          # 合并分支
git branch -d <name>        # 删除分支
```

### 撤销操作
```bash
git checkout -- <file>      # 撤销工作区修改
git reset HEAD <file>       # 取消暂存
git revert <commit>         # 回退某次提交
git reset --hard <commit>   # 重置到某次提交（危险操作）
```

### 远程操作
```bash
git remote -v               # 查看远程仓库
git push                    # 推送到远程
git pull                    # 从远程拉取
git clone <url>             # 克隆仓库
```

---

## 五、量化开发中的Git最佳实践

### 5.1 提交信息规范

**格式**: `<type>(<scope>): <subject>`

**类型(type)**:
- `feat`: 新功能（如新策略）
- `fix`: 修复bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具变动

**示例**:
```bash
git commit -m "feat(strategy): 添加双均线策略"
git commit -m "fix(backtest): 修复K线数据缺失处理bug"
git commit -m "docs(README): 更新环境配置说明"
```

### 5.2 分支管理策略

**主分支**:
- `main`: 生产环境代码，只接受合并
- `dev`: 开发环境代码，日常开发

**功能分支**:
- `feature/ma-strategy`: 开发均线策略
- `feature/risk-control`: 开发风控模块

**修复分支**:
- `hotfix/order-bug`: 紧急修复下单bug

### 5.3 提交频率建议

**量化开发场景**:
- 完成一个函数 → 提交
- 完成一个策略逻辑 → 提交
- 回测参数调整 → 提交
- 每日学习结束 → 提交

**提交粒度**:
- ✓ 每个提交只做一件事
- ✓ 提交信息清晰描述变更
- ✗ 不要把多天的修改一次性提交
- ✗ 不要提交无法运行的代码

### 5.4 .gitignore配置

**量化项目应忽略的文件**:
```gitignore
# Python
__pycache__/
*.pyc
*.pyo

# 数据文件
data/*.csv
data/*.h5
*.pkl

# 日志文件
logs/*.log

# 配置文件（包含敏感信息）
config_local.py
*.env

# IDE配置
.vscode/
.idea/

# 回测结果
backtest_results/
```

---

## 六、常见问题与解决方案

### Q1: 提交了错误的代码怎么办？

**场景**: 刚刚提交，还没推送到远程
```bash
# 方法1: 修改最后一次提交
git add <fixed_file>
git commit --amend

# 方法2: 回退到上一次提交
git reset --soft HEAD~1  # 保留修改
git reset --hard HEAD~1  # 丢弃修改（危险）
```

**场景**: 已经推送到远程
```bash
# 使用revert创建新提交来撤销
git revert HEAD
git push
```

### Q2: 切换分支时提示有未提交的修改？

```bash
# 方法1: 先提交
git add .
git commit -m "WIP: 临时保存"

# 方法2: 使用stash暂存
git stash              # 暂存修改
git checkout dev       # 切换分支
git stash pop          # 恢复修改
```

### Q3: 如何查看某个文件的修改历史？

```bash
# 查看文件提交历史
git log --oneline -- strategies/double_ma.py

# 查看文件具体修改内容
git log -p -- strategies/double_ma.py
```

### Q4: 如何比较两个分支的差异？

```bash
# 查看分支差异
git diff main..dev

# 查看具体文件差异
git diff main..dev -- strategies/double_ma.py
```

---

## 七、学习反思

### 今天学到了什么？

1. **Git基础操作**: 掌握了status、add、commit、log等基本命令
2. **分支管理**: 理解了分支的概念和使用场景
3. **版本回退**: 学会了使用revert安全地撤销提交
4. **工作流程**: 建立了"修改→暂存→提交"的工作习惯

### 哪个知识点最难理解？

**分支的概念**:
- 初学时容易混淆分支和目录
- 理解关键: 分支是指向提交的指针，切换分支就是移动指针
- 实践验证: 在不同分支上创建文件，切换后观察文件的存在性

### 如何应用到量化交易中？

1. **策略开发**: 每个新策略在独立分支开发，测试通过后合并
2. **参数优化**: 每次参数调整都提交，方便对比不同参数的回测结果
3. **风险控制**: 生产环境代码在main分支，严格审查后才能合并
4. **团队协作**: 多人开发时，通过分支避免代码冲突
5. **问题追溯**: 出现bug时，通过历史记录快速定位问题代码

---

## 八、下一步学习计划

### Day 7: 周复盘与代码重构
- 整理本周练习代码
- 提取可复用函数到工具库
- 添加完整的文档注释
- 使用Git管理重构过程

### 延伸学习（可选）
- [ ] 学习Git图形化工具（如GitKraken、SourceTree）
- [ ] 了解GitHub/GitLab的Pull Request流程
- [ ] 学习Git Hook自动化（如提交前自动运行测试）
- [ ] 研究Git子模块管理（用于管理第三方库）

---

## 九、实用资源

### 官方文档
- [Git官方文档](https://git-scm.com/doc)
- [Pro Git电子书](https://git-scm.com/book/zh/v2)

### 可视化学习
- [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN) - 交互式Git学习
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf) - 命令速查表

### 量化开发相关
- 策略代码版本管理最佳实践
- 回测结果的Git管理方案
- 团队协作的分支策略

---

**学习完成时间**: 2026-01-15 18:24  
**总结**: Git是量化开发的必备技能，通过版本控制可以安全地管理策略代码，追溯历史变更，支持团队协作。今天的练习让我建立了良好的代码管理习惯，为后续的策略开发打下基础。

**下次学习提醒**: 明天进行Week 1的周复盘，整理本周所有练习代码，形成可复用的函数库！
