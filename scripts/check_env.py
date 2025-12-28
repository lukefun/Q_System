#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Environment verification script - Check if current environment meets Q_System requirements

Usage:
    python scripts/check_env.py

Checks:
    1. Python version (must be 3.8.x)
    2. Conda environment name
    3. Core dependencies
    4. xtquant availability
    5. Project module imports
"""

import sys
import os
import platform
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Disable colors for compatibility (avoid encoding issues)
GREEN = ""
RED = ""
YELLOW = ""
CYAN = ""
RESET = ""


def print_header(title):
    print(f"\n{CYAN}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{RESET}\n")


def print_ok(msg):
    print(f"  {GREEN}[OK]{RESET} {msg}")


def print_fail(msg):
    print(f"  {RED}[FAIL]{RESET} {msg}")


def print_warn(msg):
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def print_info(msg):
    print(f"  {CYAN}[INFO]{RESET} {msg}")


def check_python_version():
    """检查 Python 版本"""
    print_header("1. Python 版本检查")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"当前版本: Python {version_str}")
    print_info(f"执行路径: {sys.executable}")

    if version.major == 3 and version.minor == 8:
        print_ok(f"Python 3.8.x - 符合 miniQMT 要求")
        return True
    else:
        print_fail(f"需要 Python 3.8.x, 当前 {version_str}")
        print_info("miniQMT 仅支持 Python 3.8")
        return False


def check_conda_env():
    """检查 Conda 环境"""
    print_header("2. Conda 环境检查")

    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')

    if conda_prefix:
        print_ok(f"Conda 环境已激活")
        print_info(f"环境名称: {conda_env}")
        print_info(f"环境路径: {conda_prefix}")

        if conda_env == 'quants':
            print_ok("环境名称为 'quants' - 符合项目规范")
            return True
        else:
            print_warn(f"建议使用环境名 'quants', 当前为 '{conda_env}'")
            return True  # 不强制要求名称
    else:
        print_fail("未检测到 Conda 环境")
        print_info("请运行: conda activate quants")
        return False


def check_core_packages():
    """检查核心依赖包"""
    print_header("3. 核心依赖包检查")

    packages = {
        'pandas': {'required': True, 'min_version': '2.0.0'},
        'numpy': {'required': True, 'min_version': '1.24.0'},
        'matplotlib': {'required': False, 'min_version': '3.7.0'},
        'pydantic': {'required': False, 'min_version': '2.0.0'},
        'requests': {'required': True, 'min_version': '2.30.0'},
    }

    all_ok = True

    for pkg_name, info in packages.items():
        try:
            pkg = __import__(pkg_name)
            version = getattr(pkg, '__version__', 'unknown')
            print_ok(f"{pkg_name} {version}")
        except ImportError:
            if info['required']:
                print_fail(f"{pkg_name} - 未安装 (必需)")
                all_ok = False
            else:
                print_warn(f"{pkg_name} - 未安装 (可选)")

    return all_ok


def check_xtquant():
    """检查 xtquant"""
    print_header("4. XtQuant 检查")

    try:
        import xtquant
        version = getattr(xtquant, '__version__', 'unknown')
        print_ok(f"xtquant {version}")
        print_info(f"安装路径: {xtquant.__file__}")

        # 测试核心模块
        try:
            from xtquant import xtdata
            print_ok("xtdata 模块可用")
        except ImportError as e:
            print_fail(f"xtdata 模块导入失败: {e}")
            return False

        try:
            from xtquant.xttrader import XtQuantTrader
            print_ok("xttrader 模块可用")
        except ImportError as e:
            print_warn(f"xttrader 模块导入失败: {e}")

        try:
            from xtquant import xtconstant
            print_ok("xtconstant 模块可用")
        except ImportError as e:
            print_warn(f"xtconstant 模块导入失败: {e}")

        return True

    except ImportError:
        print_fail("xtquant 未安装")
        print_info("安装方法:")
        print_info("  1. pip install xtquant")
        print_info("  2. 或通过 QMT 客户端自动配置")
        return False


def check_project_import():
    """检查项目模块导入"""
    print_header("5. 项目模块导入测试")

    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    modules = [
        ('core.strategy', 'BaseStrategy'),
        ('core.context', 'Context'),
        ('core.engine', 'BacktestEngine'),
        ('core.live_runner', 'LiveRunner'),
        ('strategies.double_ma', 'DoubleMAStrategy'),
    ]

    all_ok = True

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_ok(f"{module_name}.{class_name}")
        except ImportError as e:
            print_fail(f"{module_name} - {e}")
            all_ok = False
        except Exception as e:
            print_fail(f"{module_name} - {e}")
            all_ok = False

    return all_ok


def check_sys_path():
    """检查 Python 路径"""
    print_header("6. Python 路径检查")

    print_info("sys.path 顺序:")
    for i, path in enumerate(sys.path[:10]):  # 只显示前10个
        print(f"      {i}: {path}")

    if len(sys.path) > 10:
        print(f"      ... 还有 {len(sys.path) - 10} 个路径")

    # 检查是否有多个 Python 版本的 site-packages
    site_packages = [p for p in sys.path if 'site-packages' in p]
    if len(site_packages) > 2:
        print_warn(f"检测到 {len(site_packages)} 个 site-packages 路径，可能存在版本混乱")
    else:
        print_ok("site-packages 路径正常")

    return True


def generate_report(results):
    """生成检查报告"""
    print_header("检查报告")

    total = len(results)
    passed = sum(results.values())

    print(f"  通过: {passed}/{total}")
    print()

    for name, ok in results.items():
        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {name}")

    print()

    if passed == total:
        print(f"  {GREEN}环境检查全部通过，可以正常使用！{RESET}")
        return 0
    else:
        print(f"  {RED}存在 {total - passed} 项问题，请根据上述提示修复。{RESET}")
        return 1


def main():
    print(f"\n{CYAN}Q_System 环境检查工具{RESET}")
    print(f"运行时间: {platform.node()}")
    print(f"操作系统: {platform.system()} {platform.release()}")

    results = {}

    results['Python 版本'] = check_python_version()
    results['Conda 环境'] = check_conda_env()
    results['核心依赖包'] = check_core_packages()
    results['XtQuant'] = check_xtquant()
    results['项目模块'] = check_project_import()
    check_sys_path()  # 仅信息展示，不计入结果

    exit_code = generate_report(results)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
