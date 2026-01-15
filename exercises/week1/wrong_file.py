"""
这是一个"错误"的文件
用于演示 git revert 操作
"""

def wrong_function():
    """这个函数是故意创建的错误示例"""
    print("这是一个错误的提交，稍后会被回退")
    # 故意的错误代码
    result = 1 / 0  # 这会导致除零错误
    return result

if __name__ == '__main__':
    wrong_function()
