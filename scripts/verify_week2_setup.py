"""
验证Week 2项目结构和配置

检查所有必需的目录、文件和依赖是否正确设置
"""

import sys
from pathlib import Path
import importlib.util


def check_directory(path: Path, name: str) -> bool:
    """检查目录是否存在"""
    if path.exists() and path.is_dir():
        print(f"✓ {name}: {path}")
        return True
    else:
        print(f"✗ {name}: {path} (不存在)")
        return False


def check_file(path: Path, name: str) -> bool:
    """检查文件是否存在"""
    if path.exists() and path.is_file():
        print(f"✓ {name}: {path}")
        return True
    else:
        print(f"✗ {name}: {path} (不存在)")
        return False


def check_module(module_name: str) -> bool:
    """检查Python模块是否可导入"""
    try:
        importlib.import_module(module_name)
        print(f"✓ 模块 {module_name} 可导入")
        return True
    except ImportError as e:
        print(f"✗ 模块 {module_name} 无法导入: {e}")
        return False


def main():
    """主验证函数"""
    print("=" * 60)
    print("Week 2 项目结构验证")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, str(project_root))
    
    all_checks = []
    
    # 检查目录结构
    print("\n[1] 检查目录结构...")
    directories = [
        (project_root / "src", "源代码目录"),
        (project_root / "tests", "测试目录"),
        (project_root / "tests" / "unit", "单元测试目录"),
        (project_root / "tests" / "property", "属性测试目录"),
        (project_root / "tests" / "integration", "集成测试目录"),
        (project_root / "examples", "示例目录"),
        (project_root / "data", "数据目录"),
        (project_root / "data" / "cache", "缓存目录"),
        (project_root / "data" / "csv_exports", "CSV导出目录"),
        (project_root / "logs", "日志目录"),
    ]
    
    for path, name in directories:
        all_checks.append(check_directory(path, name))
    
    # 检查关键文件
    print("\n[2] 检查关键文件...")
    files = [
        (project_root / "config.py", "配置文件"),
        (project_root / "requirements.txt", "依赖文件"),
        (project_root / ".env.example", "环境变量示例"),
        (project_root / "tests" / "conftest.py", "pytest配置"),
        (project_root / "src" / "__init__.py", "src包初始化"),
        (project_root / "tests" / "__init__.py", "tests包初始化"),
    ]
    
    for path, name in files:
        all_checks.append(check_file(path, name))
    
    # 检查Python模块
    print("\n[3] 检查Python模块...")
    modules = [
        "config",
        "pandas",
        "numpy",
        "matplotlib",
        "pytest",
        "hypothesis",
    ]
    
    for module in modules:
        all_checks.append(check_module(module))
    
    # 检查可选模块
    print("\n[4] 检查可选模块...")
    optional_modules = [
        "tables",  # PyTables for HDF5
    ]
    
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✓ 可选模块 {module} 已安装")
        except ImportError:
            print(f"⚠ 可选模块 {module} 未安装 (建议安装)")
    
    # 检查配置
    print("\n[5] 检查配置...")
    try:
        import config
        print(f"✓ 配置模块加载成功")
        print(f"  - 项目根目录: {config.PROJECT_ROOT}")
        print(f"  - 数据目录: {config.DATA_DIR}")
        print(f"  - HDF5路径: {config.HDF5_PATH}")
        print(f"  - 日志级别: {config.LOG_LEVEL}")
        
        if config.XTDATA_ACCOUNT_ID and config.XTDATA_ACCOUNT_KEY:
            print(f"✓ XtData API凭证已配置")
            all_checks.append(True)
        else:
            print(f"⚠ XtData API凭证未配置 (需要设置环境变量)")
            all_checks.append(False)
    except Exception as e:
        print(f"✗ 配置模块加载失败: {e}")
        all_checks.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"验证结果: {passed}/{total} 项通过 ({success_rate:.1f}%)")
    
    if passed == total:
        print("✓ 所有检查通过！Week 2项目结构设置完成。")
        return 0
    else:
        print("⚠ 部分检查未通过，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
