"""
Day 5: 工具函数模块

这个模块包含一些简单的辅助函数，用于演示如何创建和组织工具模块。
"""


def greet(name):
    """
    问候函数
    
    参数:
        name (str): 要问候的名字
    
    返回:
        str: 问候语
    
    示例:
        >>> greet("张三")
        '你好, 张三! 欢迎学习量化交易!'
    """
    return f"你好, {name}! 欢迎学习量化交易!"


def calculate_sum(numbers):
    """
    计算数字列表的总和
    
    参数:
        numbers (list): 数字列表
    
    返回:
        float: 总和
    
    示例:
        >>> calculate_sum([1, 2, 3, 4, 5])
        15
    """
    return sum(numbers)


def format_stock_code(code):
    """
    格式化股票代码，自动添加市场后缀
    
    规则:
        - 0开头: 深圳市场，添加 .SZ
        - 6开头: 上海市场，添加 .SH
        - 3开头: 创业板，添加 .SZ
    
    参数:
        code (str): 6位股票代码
    
    返回:
        str: 带市场后缀的股票代码
    
    示例:
        >>> format_stock_code('000001')
        '000001.SZ'
        >>> format_stock_code('600000')
        '600000.SH'
        >>> format_stock_code('300001')
        '300001.SZ'
    """
    if not code or len(code) != 6:
        raise ValueError(f"股票代码必须是6位数字: {code}")
    
    if code.startswith('0') or code.startswith('3'):
        return f"{code}.SZ"
    elif code.startswith('6'):
        return f"{code}.SH"
    else:
        raise ValueError(f"无法识别的股票代码: {code}")


# 如果直接运行此文件，执行测试
if __name__ == '__main__':
    print("=== 测试 helpers.py 模块 ===\n")
    
    # 测试 greet
    print("测试 greet():")
    print(greet("学习者"))
    print()
    
    # 测试 calculate_sum
    print("测试 calculate_sum():")
    test_numbers = [10, 20, 30, 40, 50]
    print(f"数字列表: {test_numbers}")
    print(f"总和: {calculate_sum(test_numbers)}")
    print()
    
    # 测试 format_stock_code
    print("测试 format_stock_code():")
    test_codes = ['000001', '600000', '300001', '002594']
    for code in test_codes:
        formatted = format_stock_code(code)
        print(f"{code} -> {formatted}")
