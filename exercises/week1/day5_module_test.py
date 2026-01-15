"""
Day 5: 创建新模块练习 - 验证脚本

学习目标:
    1. 创建自己的工具模块 (utils/)
    2. 在 __init__.py 中配置导出
    3. 验证可以从外部正确导入

预计时间: 20分钟
"""

# 添加项目根目录到Python路径
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_import_from_utils():
    """
    测试1: 从utils模块导入函数
    """
    print("\n=== 测试1: 从utils模块导入函数 ===")
    
    # 方式1: 完整路径导入
    from exercises.week1.utils.helpers import greet, calculate_sum, format_stock_code
    
    print("✓ 从 exercises.week1.utils.helpers 导入成功")
    print(f"  - greet: {greet}")
    print(f"  - calculate_sum: {calculate_sum}")
    print(f"  - format_stock_code: {format_stock_code}")
    
    return True


def test_import_from_package():
    """
    测试2: 从utils包级导入 (使用__init__.py配置)
    """
    print("\n=== 测试2: 从utils包级导入 ===")
    
    # 方式2: 包级导入 (通过__init__.py配置)
    from exercises.week1.utils import greet, calculate_sum, format_stock_code
    
    print("✓ 从 exercises.week1.utils 导入成功")
    print("  这种方式更简洁，因为我们在 __init__.py 中配置了导出")
    
    return True


def test_function_usage():
    """
    测试3: 验证导入的函数可以正常使用
    """
    print("\n=== 测试3: 验证函数功能 ===")
    
    from exercises.week1.utils import greet, calculate_sum, format_stock_code
    
    # 测试 greet
    result1 = greet("量化学习者")
    print(f"✓ greet('量化学习者') = '{result1}'")
    assert "量化学习者" in result1
    
    # 测试 calculate_sum
    result2 = calculate_sum([1, 2, 3, 4, 5])
    print(f"✓ calculate_sum([1, 2, 3, 4, 5]) = {result2}")
    assert result2 == 15
    
    # 测试 format_stock_code
    result3 = format_stock_code('000001')
    print(f"✓ format_stock_code('000001') = '{result3}'")
    assert result3 == '000001.SZ'
    
    result4 = format_stock_code('600000')
    print(f"✓ format_stock_code('600000') = '{result4}'")
    assert result4 == '600000.SH'
    
    result5 = format_stock_code('300001')
    print(f"✓ format_stock_code('300001') = '{result5}'")
    assert result5 == '300001.SZ'
    
    print("\n✓ 所有函数功能正常!")
    
    return True


def test_all_attribute():
    """
    测试4: 验证 __all__ 属性的作用
    """
    print("\n=== 测试4: 验证 __all__ 属性 ===")
    
    import exercises.week1.utils as utils
    
    # 检查 __all__ 属性
    if hasattr(utils, '__all__'):
        print(f"✓ utils 模块定义了 __all__: {utils.__all__}")
        
        # 验证 __all__ 中的所有函数都可以访问
        for func_name in utils.__all__:
            if hasattr(utils, func_name):
                print(f"  ✓ {func_name} 可以访问")
            else:
                print(f"  ✗ {func_name} 无法访问")
                return False
    else:
        print("✗ utils 模块未定义 __all__")
        return False
    
    return True


def test_practical_example():
    """
    测试5: 实际应用示例
    """
    print("\n=== 测试5: 实际应用示例 ===")
    
    from exercises.week1.utils import format_stock_code, calculate_sum
    
    # 场景1: 批量格式化股票代码
    print("\n场景1: 批量格式化股票代码")
    raw_codes = ['000001', '000002', '600000', '600001', '300001']
    formatted_codes = [format_stock_code(code) for code in raw_codes]
    
    print(f"原始代码: {raw_codes}")
    print(f"格式化后: {formatted_codes}")
    
    # 场景2: 计算持仓总市值
    print("\n场景2: 计算持仓总市值")
    positions = {
        '000001.SZ': {'volume': 1000, 'price': 10.5},
        '600000.SH': {'volume': 500, 'price': 8.3},
        '300001.SZ': {'volume': 800, 'price': 15.2}
    }
    
    market_values = [pos['volume'] * pos['price'] for pos in positions.values()]
    total_value = calculate_sum(market_values)
    
    print(f"各股票市值: {market_values}")
    print(f"总市值: {total_value:.2f} 元")
    
    print("\n✓ 实际应用示例运行成功!")
    
    return True


def verify():
    """
    运行所有测试
    """
    print("=" * 60)
    print("Day 5: 创建新模块练习 - 验收检查")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("测试1: 从utils模块导入函数", test_import_from_utils()))
    except Exception as e:
        print(f"✗ 测试1失败: {e}")
        results.append(("测试1: 从utils模块导入函数", False))
    
    try:
        results.append(("测试2: 从utils包级导入", test_import_from_package()))
    except Exception as e:
        print(f"✗ 测试2失败: {e}")
        results.append(("测试2: 从utils包级导入", False))
    
    try:
        results.append(("测试3: 验证函数功能", test_function_usage()))
    except Exception as e:
        print(f"✗ 测试3失败: {e}")
        results.append(("测试3: 验证函数功能", False))
    
    try:
        results.append(("测试4: 验证__all__属性", test_all_attribute()))
    except Exception as e:
        print(f"✗ 测试4失败: {e}")
        results.append(("测试4: 验证__all__属性", False))
    
    try:
        results.append(("测试5: 实际应用示例", test_practical_example()))
    except Exception as e:
        print(f"✗ 测试5失败: {e}")
        results.append(("测试5: 实际应用示例", False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("验收结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 恭喜! 所有测试通过!")
        print("\n学习收获:")
        print("  1. 成功创建了自己的工具模块 (exercises/week1/utils/)")
        print("  2. 理解了 __init__.py 的配置和作用")
        print("  3. 掌握了包级导入的使用方法")
        print("  4. 学会了如何组织和复用代码")
        print("\n模块结构:")
        print("  exercises/week1/utils/")
        print("  ├── __init__.py       # 包配置，定义导出接口")
        print("  └── helpers.py        # 工具函数实现")
    else:
        print("\n⚠ 部分测试未通过，请检查错误信息")
    
    return all_passed


if __name__ == '__main__':
    verify()
