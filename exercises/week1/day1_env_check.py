#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Day 1: 环境配置验证
学习目标: 确保Python 3.8环境正确配置，MiniQMT可用
预计时间: 2-3小时

运行方式:
    conda activate quants
    python exercises/week1/day1_env_check.py
"""

import sys

# === 练习1: 检查Python版本 ===
def exercise_1_check_python_version():
    """
    练习1: 检查Python版本是否为3.8.x
    
    知识点:
    - sys.version_info 返回Python版本信息
    - MiniQMT 要求 Python 3.8.x
    """
    print("=" * 50)
    print("练习1: 检查Python版本")
    print("=" * 50)
    
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    print(f"Python执行路径: {sys.executable}")
    
    if version.major == 3 and version.minor == 8:
        print("✓ Python版本正确 (3.8.x)")
        return True
    else:
        print("✗ Python版本不正确，需要3.8.x")
        return False


# === 练习2: 测试xtquant导入 ===
def exercise_2_test_xtquant_import():
    """
    练习2: 测试xtquant模块是否可以正常导入
    
    知识点:
    - xtquant 是国金证券QMT的Python接口
    - xtdata 用于获取行情数据
    - xttrader 用于交易操作
    """
    print("\n" + "=" * 50)
    print("练习2: 测试xtquant导入")
    print("=" * 50)
    
    try:
        from xtquant import xtdata
        print("✓ xtdata 模块导入成功")
        
        # 测试获取交易日列表
        trading_dates = xtdata.get_trading_dates('SH')
        if trading_dates and len(trading_dates) > 0:
            print(f"✓ 获取交易日成功，共 {len(trading_dates)} 个交易日")
            print(f"  最近5个交易日: {trading_dates[-5:]}")
        else:
            print("⚠ 获取交易日返回空数据")
            
        return True
        
    except ImportError as e:
        print(f"✗ xtquant 导入失败: {e}")
        print("  请确保已安装: pip install xtquant")
        return False
    except Exception as e:
        print(f"⚠ xtquant 导入成功，但测试时出错: {e}")
        print("  这可能是因为MiniQMT未启动")
        return True  # 导入成功即可


# === 练习3: 测试项目模块导入 ===
def exercise_3_test_project_import():
    """
    练习3: 测试项目核心模块是否可以正常导入
    
    知识点:
    - 项目采用模块化设计
    - core/ 包含核心组件
    - strategies/ 包含策略实现
    """
    print("\n" + "=" * 50)
    print("练习3: 测试项目模块导入")
    print("=" * 50)
    
    import os
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    modules_to_test = [
        ('core.context', 'Context'),
        ('core.engine', 'BacktestEngine'),
        ('core.strategy', 'BaseStrategy'),
        ('strategies.double_ma', 'DoubleMAStrategy'),
    ]
    
    all_ok = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"✗ {module_name}.{class_name} - {e}")
            all_ok = False
    
    return all_ok


# === 验收检查 ===
def verify():
    """运行所有验收检查"""
    print("\n" + "=" * 50)
    print("Day 1 环境验证 - 开始")
    print("=" * 50)
    
    results = {
        'Python版本': exercise_1_check_python_version(),
        'xtquant导入': exercise_2_test_xtquant_import(),
        '项目模块导入': exercise_3_test_project_import(),
    }
    
    print("\n" + "=" * 50)
    print("验收结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Day 1 环境验证全部通过！")
        print("   可以继续 Day 2 的学习了")
    else:
        print("⚠ 存在未通过的检查项，请根据提示修复")
    print("=" * 50)
    
    return all_passed


if __name__ == '__main__':
    verify()
