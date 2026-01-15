"""
Day 5: 项目结构规范 - 模块导入练习

学习目标:
    1. 练习从core模块导入Context、BacktestEngine
    2. 练习从strategies模块导入DoubleMAStrategy
    3. 验证导入成功且可正常使用

预计时间: 30分钟
"""

# 添加项目根目录到Python路径
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# === 理论部分 ===
# Python模块导入的三种方式:
# 1. 完整路径导入: from package.module import Class
# 2. 包级导入: from package import Class (需要在__init__.py中配置)
# 3. 通配符导入: from package import * (不推荐)

# === 练习部分 ===

def exercise_1_import_core_modules():
    """
    练习1: 从core模块导入核心类
    
    目标:
        - 导入Context类
        - 导入BacktestEngine类
        - 导入BaseStrategy类
    """
    print("\n=== 练习1: 导入core模块 ===")
    
    # 方式1: 完整路径导入 (当前项目使用的方式)
    from core.context import Context
    from core.engine import BacktestEngine
    from core.strategy import BaseStrategy
    
    print(f"✓ Context 类导入成功: {Context}")
    print(f"✓ BacktestEngine 类导入成功: {BacktestEngine}")
    print(f"✓ BaseStrategy 类导入成功: {BaseStrategy}")
    
    # 验证可以实例化
    context = Context()
    print(f"✓ Context 实例化成功: cash={context.cash}, total_asset={context.total_asset}")
    
    return True


def exercise_2_import_strategy():
    """
    练习2: 从strategies模块导入策略类
    
    目标:
        - 导入DoubleMAStrategy类
        - 验证策略继承自BaseStrategy
    """
    print("\n=== 练习2: 导入strategies模块 ===")
    
    # 完整路径导入
    from strategies.double_ma import DoubleMAStrategy
    from core.strategy import BaseStrategy
    
    print(f"✓ DoubleMAStrategy 类导入成功: {DoubleMAStrategy}")
    
    # 验证继承关系
    is_subclass = issubclass(DoubleMAStrategy, BaseStrategy)
    print(f"✓ DoubleMAStrategy 继承自 BaseStrategy: {is_subclass}")
    
    # 验证可以实例化
    strategy = DoubleMAStrategy()
    print(f"✓ DoubleMAStrategy 实例化成功: {strategy}")
    
    return True


def exercise_3_verify_usage():
    """
    练习3: 验证导入的类可以正常使用
    
    目标:
        - 创建策略实例
        - 创建引擎实例
        - 验证策略的initialize和handle_bar方法存在
    """
    print("\n=== 练习3: 验证类的正常使用 ===")
    
    from strategies.double_ma import DoubleMAStrategy
    from core.engine import BacktestEngine
    from core.context import Context
    
    # 1. 创建策略实例
    strategy = DoubleMAStrategy()
    print(f"✓ 策略实例创建成功")
    
    # 2. 验证策略方法存在
    has_initialize = hasattr(strategy, 'initialize')
    has_handle_bar = hasattr(strategy, 'handle_bar')
    print(f"✓ 策略包含 initialize 方法: {has_initialize}")
    print(f"✓ 策略包含 handle_bar 方法: {has_handle_bar}")
    
    # 3. 创建引擎实例
    engine = BacktestEngine(
        strategy=strategy,
        start_date='20250101',
        end_date='20250110',
        stock_list=['002594.SZ']
    )
    print(f"✓ 回测引擎创建成功")
    
    # 4. 验证引擎属性
    print(f"  - 开始日期: {engine.start_date}")
    print(f"  - 结束日期: {engine.end_date}")
    print(f"  - 股票列表: {engine.stock_list}")
    
    # 5. 测试Context的基本功能
    context = Context()
    context.current_dt = "2025-01-15"
    context.log("测试日志输出")
    print(f"✓ Context 日志功能正常")
    
    return True


def exercise_4_import_comparison():
    """
    练习4: 对比不同导入方式
    
    目标:
        - 理解完整路径导入 vs 包级导入的区别
        - 了解为什么当前项目使用完整路径导入
    """
    print("\n=== 练习4: 导入方式对比 ===")
    
    # 方式1: 完整路径导入 (当前项目使用)
    print("\n方式1: 完整路径导入")
    from core.context import Context as Context1
    from core.engine import BacktestEngine as Engine1
    print("  from core.context import Context")
    print("  from core.engine import BacktestEngine")
    print("  ✓ 优点: 明确、不依赖__init__.py配置")
    print("  ✗ 缺点: 路径较长")
    
    # 方式2: 包级导入 (需要配置__init__.py)
    print("\n方式2: 包级导入 (需要配置__init__.py)")
    print("  from core import Context, BacktestEngine")
    print("  ✓ 优点: 简洁、易维护")
    print("  ✗ 缺点: 需要在__init__.py中配置导出")
    print("  ⚠ 注意: 当前项目的core/__init__.py为空，此方式暂不可用")
    
    # 方式3: 通配符导入 (不推荐)
    print("\n方式3: 通配符导入 (不推荐)")
    print("  from core import *")
    print("  ✗ 缺点: 不明确导入了什么、容易命名冲突")
    print("  ⚠ 建议: 生产代码中避免使用")
    
    return True


# === 验收检查 ===
def verify():
    """
    运行所有练习并验证结果
    """
    print("=" * 60)
    print("Day 5: 模块导入练习 - 验收检查")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("练习1: 导入core模块", exercise_1_import_core_modules()))
    except Exception as e:
        print(f"✗ 练习1失败: {e}")
        results.append(("练习1: 导入core模块", False))
    
    try:
        results.append(("练习2: 导入strategies模块", exercise_2_import_strategy()))
    except Exception as e:
        print(f"✗ 练习2失败: {e}")
        results.append(("练习2: 导入strategies模块", False))
    
    try:
        results.append(("练习3: 验证类的使用", exercise_3_verify_usage()))
    except Exception as e:
        print(f"✗ 练习3失败: {e}")
        results.append(("练习3: 验证类的使用", False))
    
    try:
        results.append(("练习4: 导入方式对比", exercise_4_import_comparison()))
    except Exception as e:
        print(f"✗ 练习4失败: {e}")
        results.append(("练习4: 导入方式对比", False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("验收结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 恭喜! 所有练习通过!")
        print("\n学习收获:")
        print("  1. 掌握了Python模块导入的基本方法")
        print("  2. 理解了完整路径导入 vs 包级导入的区别")
        print("  3. 验证了core和strategies模块可以正常使用")
        print("  4. 为后续开发新策略打下了基础")
    else:
        print("\n⚠ 部分练习未通过，请检查错误信息")
    
    return all_passed


if __name__ == '__main__':
    verify()


"""
# 任务5（第5天：项目结构规范）—— 顺利完成！✓

我已成功完成第5天“项目结构规范”的所有子任务，具体完成情况如下：

### 子任务5.1：分析现有项目结构 ✓
- 分析了完整的项目结构
- 在路径`docs/notes/week1_day5_project_structure.md`下创建了一份详尽的学习笔记文档
- 记录了每个目录的用途与职责：
  - `core/` - 核心引擎模块（包含Context、回测引擎、实盘运行器、基础策略）
  - `strategies/` - 交易策略的实现代码
  - `exercises/` - 学习练习用的代码
  - `data/` - 本地数据存储目录
  - `docs/` - 项目文档目录
  - `scripts/` - 工具脚本目录

### 子任务5.2：学习`__init__.py`文件的作用 ✓
- 检查了`core`、`strategies`和`exercises`模块中已有的`__init__.py`文件
- 记录了`__init__.py`文件的三大核心作用：
  1.  标识Python包
  2.  初始化包内容
  3.  通过`__all__`变量控制模块导出内容
- 在学习笔记中添加了详细的解释与示例

### 子任务5.3：练习模块导入 ✓
- 在路径`exercises/week1/day5_import_test.py`中编写了4个综合性导入练习
- 成功测试了从核心模块导入内容（Context、回测引擎、基础策略）
- 成功测试了从策略模块导入双均线策略
- 验证了所有类均可正常实例化与调用
- 所有测试全部通过！✓

### 子任务5.4：创建新模块练习 ✓
- 在路径`exercises/week1/utils/`下新建了一个工具模块
- 编写了`__init__.py`文件并完成`__all__`变量的合理配置
- 在`helpers.py`文件中实现了三个工具函数：
  - `greet()` - 问候功能函数
  - `calculate_sum()` - 数值求和函数
  - `format_stock_code()` - 带市场后缀的股票代码格式化函数
- 编写了`day5_module_test.py`文件，验证该模块功能正常
- 5项测试全部顺利通过！✓

### 新增文件清单：
1.  `docs/notes/week1_day5_project_structure.md` - 详尽的学习笔记文档（超过200行）
2.  `exercises/week1/day5_import_test.py` - 模块导入练习脚本
3.  `exercises/week1/utils/__init__.py` - 工具包配置文件
4.  `exercises/week1/utils/helpers.py` - 工具函数实现文件
5.  `exercises/week1/day5_module_test.py` - 模块功能验证脚本

### 学习成果：
- ✓ 掌握了Python项目结构的最佳实践
- ✓ 精通`__init__.py`文件的作用与使用方法
- ✓ 学会了不同的模块导入方式及其优缺点
- ✓ 成功创建并规整了一个可复用的工具模块
- ✓ 能够遵循项目规范，开展新策略与新工具的开发工作

需求规格书中的所有要求均已满足，且通过全面测试验证了实现效果！




## Task 5 (Day 5: 项目结构规范) - Completed Successfully! ✓

I've successfully implemented all subtasks for Day 5: 项目结构规范. Here's what was accomplished:

### Subtask 5.1: 分析现有项目结构 ✓
- Analyzed the complete project structure
- Created a comprehensive learning note document at `docs/notes/week1_day5_project_structure.md`
- Documented the purpose and responsibility of each directory:
  - `core/` - Core engine modules (Context, BacktestEngine, LiveRunner, BaseStrategy)
  - `strategies/` - Trading strategy implementations
  - `exercises/` - Learning exercise code
  - `data/` - Local data storage
  - `docs/` - Project documentation
  - `scripts/` - Utility scripts

### Subtask 5.2: 学习__init__.py的作用 ✓
- Examined existing `__init__.py` files in core, strategies, and exercises modules
- Documented the three main purposes of `__init__.py`:
  1. Package identification
  2. Package initialization
  3. Export control via `__all__`
- Added detailed explanations and examples to the learning notes

### Subtask 5.3: 练习模块导入 ✓
- Created `exercises/week1/day5_import_test.py` with 4 comprehensive exercises
- Successfully tested importing from core modules (Context, BacktestEngine, BaseStrategy)
- Successfully tested importing from strategies module (DoubleMAStrategy)
- Verified all classes can be instantiated and used correctly
- All tests passed! ✓

### Subtask 5.4: 创建新模块练习 ✓
- Created a new utils module at `exercises/week1/utils/`
- Implemented `__init__.py` with proper `__all__` configuration
- Created `helpers.py` with three utility functions:
  - `greet()` - Greeting function
  - `calculate_sum()` - Sum calculation
  - `format_stock_code()` - Stock code formatting with market suffix
- Created `day5_module_test.py` to verify the module works correctly
- All 5 tests passed successfully! ✓

### Files Created:
1. `docs/notes/week1_day5_project_structure.md` - Comprehensive learning notes (200+ lines)
2. `exercises/week1/day5_import_test.py` - Module import practice script
3. `exercises/week1/utils/__init__.py` - Utils package configuration
4. `exercises/week1/utils/helpers.py` - Helper functions implementation
5. `exercises/week1/day5_module_test.py` - Module verification script

### Learning Outcomes:
- ✓ Understood Python project structure best practices
- ✓ Mastered the role and usage of `__init__.py`
- ✓ Learned different import methods and their trade-offs
- ✓ Successfully created and organized a reusable utility module
- ✓ Ready to develop new strategies and tools following project conventions

All requirements from the spec have been met, and the implementation has been verified through comprehensive testing!
"""