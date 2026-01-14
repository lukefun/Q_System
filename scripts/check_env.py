# scripts\check_env.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
Q_System 环境验证脚本 - Environment Verification Script
=============================================================================

【设计概念 Design Concept】
---------------------------------------------------------------------------
本脚本是 Q_System 量化交易系统的环境诊断工具，用于在开发和部署阶段快速
验证运行环境是否满足系统要求。采用模块化检查设计，每个检查项独立执行，
最终生成综合报告。

核心设计理念：
1. 渐进式检查：从基础环境到高级功能，逐层验证
2. 友好提示：失败时提供明确的修复建议
3. 兼容性优先：处理 Windows 编码问题，确保跨平台运行
4. 信息完整：不仅检查是否安装，还验证版本和可用性

【实现逻辑 Implementation Logic】
---------------------------------------------------------------------------
执行流程：
    main() 
      ├─> check_python_version()      # 步骤1: Python版本检查
      ├─> check_conda_env()            # 步骤2: Conda环境检查
      ├─> check_core_packages()        # 步骤3: 核心依赖包检查
      ├─> check_xtquant()              # 步骤4: XtQuant模块检查
      ├─> check_project_import()       # 步骤5: 项目模块导入测试
      ├─> check_sys_path()             # 步骤6: Python路径诊断
      └─> generate_report()            # 生成最终报告

检查项说明：
1. Python 版本：必须是 3.8.x（miniQMT 限制）
2. Conda 环境：验证是否在正确的虚拟环境中
3. 核心依赖：pandas, numpy, requests 等必需包
4. XtQuant：QMT 量化接口的可用性
5. 项目模块：验证自定义策略和引擎能否正常导入
6. 路径诊断：检测潜在的包冲突问题

输出标记说明：
    [OK]   - 绿色，检查通过
    [FAIL] - 红色，检查失败，需要修复
    [WARN] - 黄色，警告信息，建议关注
    [INFO] - 青色，提示信息

【使用方法 Usage】
---------------------------------------------------------------------------
    # 在项目根目录执行
    python scripts/check_env.py
    
    # 或在 conda 环境中
    conda activate quants
    python scripts/check_env.py

【返回值 Exit Code】
---------------------------------------------------------------------------
    0 - 所有检查通过
    1 - 存在失败项，需要修复

=============================================================================
"""

# =============================================================================
# 导入标准库 Import Standard Libraries
# =============================================================================
import sys        # 系统相关功能：版本信息、路径管理、退出码
import os         # 操作系统接口：环境变量、路径操作
import platform   # 平台信息：操作系统、主机名
import io         # IO流处理：解决 Windows 编码问题

# =============================================================================
# Windows 编码问题修复 Fix Windows Encoding Issues
# =============================================================================
# 问题：Windows 默认使用 GBK 编码，中文输出可能乱码
# 解决：强制使用 UTF-8 编码，并在遇到无法编码字符时替换而非报错
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# =============================================================================
# 输出颜色配置 Output Color Configuration
# =============================================================================
# 注意：为了兼容性，这里禁用了 ANSI 颜色代码
# 如需启用彩色输出，可以使用 colorama 库或 ANSI 转义序列
# 例如：GREEN = "\033[92m", RED = "\033[91m" 等
GREEN = ""    # 成功标记颜色（绿色）
RED = ""      # 失败标记颜色（红色）
YELLOW = ""   # 警告标记颜色（黄色）
CYAN = ""     # 信息标记颜色（青色）
RESET = ""    # 重置颜色

# =============================================================================
# 输出格式化函数 Output Formatting Functions
# =============================================================================

def print_header(title):
    """
    打印章节标题
    
    Args:
        title: 标题文本
        
    输出格式：
        ============================================================
         标题文本
        ============================================================
    """
    print(f"\n{CYAN}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{RESET}\n")


def print_ok(msg):
    """
    打印成功信息 - 标记为 [OK]
    
    Args:
        msg: 消息内容
        
    输出示例：
        [OK] Python 3.8.x - 符合 miniQMT 要求
    """
    print(f"  {GREEN}[OK]{RESET} {msg}")


def print_fail(msg):
    """
    打印失败信息 - 标记为 [FAIL]
    
    Args:
        msg: 消息内容
        
    输出示例：
        [FAIL] 需要 Python 3.8.x, 当前 3.9.0
    """
    print(f"  {RED}[FAIL]{RESET} {msg}")


def print_warn(msg):
    """
    打印警告信息 - 标记为 [WARN]
    
    Args:
        msg: 消息内容
        
    输出示例：
        [WARN] 建议使用环境名 'quants', 当前为 'base'
    """
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def print_info(msg):
    """
    打印提示信息 - 标记为 [INFO]
    
    Args:
        msg: 消息内容
        
    输出示例：
        [INFO] 当前版本: Python 3.8.10
    """
    print(f"  {CYAN}[INFO]{RESET} {msg}")


# =============================================================================
# 检查函数 Check Functions
# =============================================================================

def check_python_version():
    """
    检查 Python 版本是否符合要求
    
    要求：Python 3.8.x（miniQMT 仅支持此版本）
    
    检查内容：
        1. 获取当前 Python 版本号
        2. 显示 Python 可执行文件路径
        3. 验证主版本号和次版本号
    
    Returns:
        bool: True=版本符合要求, False=版本不符合
        
    输出标记：
        [INFO] 当前版本: Python x.x.x
        [INFO] 执行路径: /path/to/python
        [OK]   Python 3.8.x - 符合 miniQMT 要求
        [FAIL] 需要 Python 3.8.x, 当前 x.x.x
    """
    print_header("1. Python 版本检查")

    # 获取版本信息：major.minor.micro (例如 3.8.10)
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    # 显示当前版本和执行路径
    print_info(f"当前版本: Python {version_str}")
    print_info(f"执行路径: {sys.executable}")

    # 验证版本：必须是 Python 3.8.x
    if version.major == 3 and version.minor == 8:
        print_ok(f"Python 3.8.x - 符合 miniQMT 要求")
        return True
    else:
        print_fail(f"需要 Python 3.8.x, 当前 {version_str}")
        print_info("miniQMT 仅支持 Python 3.8")
        return False


def check_conda_env():
    """
    检查 Conda 虚拟环境状态
    
    目的：确保在独立的 Conda 环境中运行，避免包冲突
    
    检查内容：
        1. 读取环境变量 CONDA_PREFIX（Conda 安装路径）
        2. 读取环境变量 CONDA_DEFAULT_ENV（当前环境名）
        3. 验证是否在推荐的 'quants' 环境中
    
    Returns:
        bool: True=在Conda环境中, False=不在Conda环境中
        
    输出标记：
        [OK]   Conda 环境已激活
        [INFO] 环境名称: quants
        [INFO] 环境路径: /path/to/conda/envs/quants
        [OK]   环境名称为 'quants' - 符合项目规范
        [WARN] 建议使用环境名 'quants', 当前为 'xxx'
        [FAIL] 未检测到 Conda 环境
    """
    print_header("2. Conda 环境检查")

    # 从环境变量获取 Conda 信息
    conda_prefix = os.environ.get('CONDA_PREFIX', '')      # Conda 环境路径
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')    # 当前环境名称

    if conda_prefix:
        # 检测到 Conda 环境
        print_ok(f"Conda 环境已激活")
        print_info(f"环境名称: {conda_env}")
        print_info(f"环境路径: {conda_prefix}")

        # 检查环境名称是否为推荐的 'quants'
        if conda_env == 'quants':
            print_ok("环境名称为 'quants' - 符合项目规范")
            return True
        else:
            print_warn(f"建议使用环境名 'quants', 当前为 '{conda_env}'")
            return True  # 不强制要求名称，只是警告
    else:
        # 未检测到 Conda 环境
        print_fail("未检测到 Conda 环境")
        print_info("请运行: conda activate quants")
        return False


def check_core_packages():
    """
    检查核心 Python 依赖包
    
    目的：验证量化交易所需的基础库是否已安装且版本合适
    
    检查的包：
        - pandas: 数据处理（必需）
        - numpy: 数值计算（必需）
        - matplotlib: 数据可视化（可选）
        - pydantic: 数据验证（可选）
        - requests: HTTP请求（必需）
    
    Returns:
        bool: True=所有必需包已安装, False=缺少必需包
        
    输出标记：
        [OK]   package_name x.x.x
        [FAIL] package_name - 未安装 (必需)
        [WARN] package_name - 未安装 (可选)
    """
    print_header("3. 核心依赖包检查")

    # 定义需要检查的包及其要求
    packages = {
        'pandas': {'required': True, 'min_version': '2.0.0'},       # 数据分析核心库
        'numpy': {'required': True, 'min_version': '1.24.0'},       # 数值计算基础
        'matplotlib': {'required': False, 'min_version': '3.7.0'},  # 图表绘制
        'pydantic': {'required': False, 'min_version': '2.0.0'},    # 数据验证
        'requests': {'required': True, 'min_version': '2.30.0'},    # HTTP 请求
    }

    all_ok = True  # 标记是否所有必需包都已安装

    # 逐个检查包
    for pkg_name, info in packages.items():
        try:
            # 尝试导入包
            pkg = __import__(pkg_name)
            # 获取版本号（如果有）
            version = getattr(pkg, '__version__', 'unknown')
            print_ok(f"{pkg_name} {version}")
        except ImportError:
            # 导入失败，根据是否必需给出不同提示
            if info['required']:
                print_fail(f"{pkg_name} - 未安装 (必需)")
                all_ok = False
            else:
                print_warn(f"{pkg_name} - 未安装 (可选)")

    return all_ok


def check_xtquant():
    """
    检查 XtQuant 量化接口
    
    目的：验证迅投 QMT 量化接口是否正确安装和配置
    
    XtQuant 是迅投 QMT 提供的 Python 量化接口，包含：
        - xtdata: 行情数据接口（必需）
        - xttrader: 交易接口（实盘必需，回测可选）
        - xtconstant: 常量定义（可选）
    
    检查内容：
        1. xtquant 主包是否已安装
        2. xtdata 模块是否可用（行情数据）
        3. xttrader 模块是否可用（交易功能）
        4. xtconstant 模块是否可用（常量定义）
    
    Returns:
        bool: True=xtquant可用, False=xtquant不可用
        
    输出标记：
        [OK]   xtquant x.x.x
        [INFO] 安装路径: /path/to/xtquant
        [OK]   xtdata 模块可用
        [OK]   xttrader 模块可用
        [WARN] xttrader 模块导入失败（回测模式下可忽略）
        [FAIL] xtquant 未安装
    """
    print_header("4. XtQuant 检查")

    try:
        # 尝试导入 xtquant 主包
        import xtquant
        version = getattr(xtquant, '__version__', 'unknown')
        print_ok(f"xtquant {version}")
        print_info(f"安装路径: {xtquant.__file__}")

        # 测试核心模块 1: xtdata（行情数据接口）
        try:
            from xtquant import xtdata
            print_ok("xtdata 模块可用")
        except ImportError as e:
            print_fail(f"xtdata 模块导入失败: {e}")
            return False  # xtdata 是必需的，失败则返回 False

        # 测试核心模块 2: xttrader（交易接口）
        try:
            from xtquant.xttrader import XtQuantTrader
            print_ok("xttrader 模块可用")
        except ImportError as e:
            # xttrader 在回测模式下不是必需的，只给出警告
            print_warn(f"xttrader 模块导入失败: {e}")

        # 测试核心模块 3: xtconstant（常量定义）
        try:
            from xtquant import xtconstant
            print_ok("xtconstant 模块可用")
        except ImportError as e:
            # xtconstant 不是必需的，只给出警告
            print_warn(f"xtconstant 模块导入失败: {e}")

        return True

    except ImportError:
        # xtquant 主包未安装
        print_fail("xtquant 未安装")
        print_info("安装方法:")
        print_info("  1. pip install xtquant")
        print_info("  2. 或通过 QMT 客户端自动配置")
        return False


def check_project_import():
    """
    检查项目自定义模块导入
    
    目的：验证 Q_System 项目的核心模块是否能正常导入
    
    检查的模块：
        - core.strategy.BaseStrategy: 策略基类
        - core.context.Context: 上下文管理
        - core.engine.BacktestEngine: 回测引擎
        - core.live_runner.LiveRunner: 实盘运行器
        - strategies.double_ma.DoubleMAStrategy: 双均线策略示例
    
    实现逻辑：
        1. 将项目根目录添加到 sys.path（确保能找到模块）
        2. 逐个尝试导入模块和类
        3. 记录导入失败的模块
    
    Returns:
        bool: True=所有模块导入成功, False=存在导入失败
        
    输出标记：
        [OK]   module_name.ClassName
        [FAIL] module_name - ImportError: xxx
    """
    print_header("5. 项目模块导入测试")

    # 添加项目根目录到 Python 路径
    # 获取当前脚本所在目录的父目录（即项目根目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)  # 插入到最前面，优先搜索

    # 定义需要检查的模块和类
    # 格式：(模块路径, 类名)
    modules = [
        ('core.strategy', 'BaseStrategy'),              # 策略基类
        ('core.context', 'Context'),                    # 上下文对象
        ('core.engine', 'BacktestEngine'),              # 回测引擎
        ('core.live_runner', 'LiveRunner'),             # 实盘运行器
        ('strategies.double_ma', 'DoubleMAStrategy'),   # 双均线策略
    ]

    all_ok = True  # 标记是否所有模块都导入成功

    # 逐个尝试导入
    for module_name, class_name in modules:
        try:
            # 动态导入模块
            # fromlist 参数确保导入子模块而不是顶层包
            module = __import__(module_name, fromlist=[class_name])
            # 获取类对象
            cls = getattr(module, class_name)
            print_ok(f"{module_name}.{class_name}")
        except ImportError as e:
            # 模块导入失败
            print_fail(f"{module_name} - {e}")
            all_ok = False
        except Exception as e:
            # 其他异常（如类不存在）
            print_fail(f"{module_name} - {e}")
            all_ok = False

    return all_ok


def check_sys_path():
    """
    检查 Python 模块搜索路径
    
    目的：诊断潜在的包冲突和路径问题
    
    sys.path 是 Python 搜索模块的路径列表，顺序很重要：
        - Python 按顺序搜索，找到第一个匹配的模块就停止
        - 如果有多个版本的包，前面的会覆盖后面的
        - site-packages 过多可能导致版本混乱
    
    检查内容：
        1. 显示 sys.path 的前 10 个路径（最重要的）
        2. 统计 site-packages 目录数量
        3. 如果 site-packages 过多（>2），给出警告
    
    Returns:
        bool: 始终返回 True（仅用于信息展示）
        
    输出标记：
        [INFO] sys.path 顺序: ...
        [OK]   site-packages 路径正常
        [WARN] 检测到 X 个 site-packages 路径，可能存在版本混乱
    """
    print_header("6. Python 路径检查")

    print_info("sys.path 顺序:")
    # 只显示前 10 个路径，避免输出过长
    for i, path in enumerate(sys.path[:10]):
        print(f"      {i}: {path}")

    # 如果路径超过 10 个，显示省略信息
    if len(sys.path) > 10:
        print(f"      ... 还有 {len(sys.path) - 10} 个路径")

    # 检查 site-packages 数量
    # site-packages 是第三方包的安装目录
    site_packages = [p for p in sys.path if 'site-packages' in p]
    
    if len(site_packages) > 2:
        # 过多的 site-packages 可能意味着：
        # - 混用了多个 Python 环境
        # - 同时安装了 conda 和 pip 的包
        # - 可能导致版本冲突
        print_warn(f"检测到 {len(site_packages)} 个 site-packages 路径，可能存在版本混乱")
    else:
        print_ok("site-packages 路径正常")

    return True


def generate_report(results):
    """
    生成最终检查报告
    
    目的：汇总所有检查项的结果，给出总体评估
    
    Args:
        results: 字典，格式 {检查项名称: 是否通过}
                例如：{'Python 版本': True, 'Conda 环境': False}
    
    报告内容：
        1. 统计通过/失败的检查项数量
        2. 列出每个检查项的状态（PASS/FAIL）
        3. 给出总体结论
    
    Returns:
        int: 退出码
             0 = 所有检查通过
             1 = 存在失败项
             
    输出标记：
        通过: X/Y
        [PASS] 检查项名称
        [FAIL] 检查项名称
        环境检查全部通过，可以正常使用！
        存在 X 项问题，请根据上述提示修复。
    """
    print_header("检查报告")

    # 统计通过和总数
    total = len(results)                    # 总检查项数
    passed = sum(results.values())          # 通过的检查项数（True=1, False=0）

    print(f"  通过: {passed}/{total}")
    print()

    # 逐项显示结果
    for name, ok in results.items():
        # 根据结果显示 PASS 或 FAIL
        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {name}")

    print()

    # 给出总体结论
    if passed == total:
        # 全部通过
        print(f"  {GREEN}环境检查全部通过，可以正常使用！{RESET}")
        return 0  # 退出码 0 表示成功
    else:
        # 存在失败项
        print(f"  {RED}存在 {total - passed} 项问题，请根据上述提示修复。{RESET}")
        return 1  # 退出码 1 表示失败


# =============================================================================
# 主函数 Main Function
# =============================================================================

def main():
    """
    主函数 - 执行所有环境检查并生成报告
    
    执行流程：
        1. 打印脚本标题和系统信息
        2. 依次执行 6 项检查：
           - Python 版本检查
           - Conda 环境检查
           - 核心依赖包检查
           - XtQuant 检查
           - 项目模块导入测试
           - Python 路径检查（仅信息展示）
        3. 生成综合报告
        4. 根据结果返回退出码
    
    检查结果存储：
        results 字典记录每项检查的通过/失败状态
        格式：{'检查项名称': True/False}
    
    退出码：
        0 - 所有检查通过，环境正常
        1 - 存在失败项，需要修复
        
    输出示例：
        Q_System 环境检查工具
        运行时间: DESKTOP-XXX
        操作系统: Windows 10
        
        ============================================================
         1. Python 版本检查
        ============================================================
        ...
    """
    # 打印脚本标题
    print(f"\n{CYAN}Q_System 环境检查工具{RESET}")
    print(f"运行时间: {platform.node()}")           # 主机名
    print(f"操作系统: {platform.system()} {platform.release()}")  # 操作系统信息

    # 创建结果字典，用于记录每项检查的结果
    results = {}

    # 执行各项检查，并将结果存入 results 字典
    # 注意：check_sys_path() 不计入结果，仅用于信息展示
    results['Python 版本'] = check_python_version()      # 检查 1
    results['Conda 环境'] = check_conda_env()            # 检查 2
    results['核心依赖包'] = check_core_packages()        # 检查 3
    results['XtQuant'] = check_xtquant()                 # 检查 4
    results['项目模块'] = check_project_import()         # 检查 5
    check_sys_path()  # 检查 6 - 仅信息展示，不计入结果

    # 生成综合报告并获取退出码
    exit_code = generate_report(results)
    
    # 退出程序，返回退出码
    # 退出码 0 表示成功，1 表示失败
    # 可以在 shell 中通过 $? (Linux/Mac) 或 %ERRORLEVEL% (Windows) 获取
    sys.exit(exit_code)


# =============================================================================
# 脚本入口 Script Entry Point
# =============================================================================

if __name__ == '__main__':
    """
    脚本入口点
    
    当直接运行此脚本时（python check_env.py），执行 main() 函数
    当作为模块导入时（import check_env），不会自动执行
    
    这是 Python 的标准做法，确保脚本既可以独立运行，也可以被导入使用
    """
    main()
