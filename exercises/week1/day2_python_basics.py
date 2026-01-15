"""
Day 2: Python核心语法特训
学习目标: 掌握量化开发常用的Python语法特性
预计时间: 4-5小时
"""

# === 练习1: 列表推导式 ===
def exercise_1_list_comprehension():
    """练习1: 列表推导式 - 股票代码格式转换"""
    print("\n=== 练习1: 列表推导式 ===")
    
    # 原始股票代码列表
    stock_codes = ['000001', '000002', '600000']
    
    # 使用列表推导式: 0开头加.SZ，6开头加.SH
    formatted_codes = [
        f"{code}.SZ" if code.startswith('0') else f"{code}.SH"
        for code in stock_codes
    ]
    
    print(f"原始代码: {stock_codes}")
    print(f"格式化后: {formatted_codes}")
    
    # 验证结果
    expected = ['000001.SZ', '000002.SZ', '600000.SH']
    assert formatted_codes == expected, f"期望 {expected}, 实际 {formatted_codes}"
    print("✓ 列表推导式练习通过")
    
    return formatted_codes


# === 练习2: dict.get()安全取值 ===
def exercise_2_dict_get():
    """练习2: dict.get() - 安全获取字典值"""
    print("\n=== 练习2: dict.get()安全取值 ===")
    
    # 持仓字典
    positions = {'000001.SZ': 1000, '600000.SH': 500}
    
    # 方法1: 直接索引 (不安全，会抛出KeyError)
    print("\n方法1: 直接索引 dict[key]")
    try:
        vol = positions['000002.SZ']
        print(f"持仓量: {vol}")
    except KeyError as e:
        print(f"✗ KeyError: {e} - 股票不存在于持仓中")
    
    # 方法2: dict.get() (安全，返回默认值)
    print("\n方法2: dict.get(key, default)")
    vol = positions.get('000002.SZ', 0)
    print(f"持仓量: {vol} (不存在时返回默认值0)")
    
    # 验证已存在的股票
    vol_exists = positions.get('000001.SZ', 0)
    print(f"000001.SZ 持仓量: {vol_exists}")
    
    # 验证结果
    assert vol == 0, "不存在的股票应返回0"
    assert vol_exists == 1000, "存在的股票应返回实际持仓"
    print("✓ dict.get()练习通过")
    
    return positions


# === 练习3: 异常处理 ===
def exercise_3_exception_handling():
    """练习3: try-except-finally - 异常处理"""
    print("\n=== 练习3: 异常处理 ===")
    
    def safe_get_data(stock_code):
        """安全获取股票数据"""
        try:
            print(f"正在获取 {stock_code} 的数据...")
            
            # 模拟数据获取失败场景
            if stock_code == 'INVALID':
                raise ValueError(f"无效的股票代码: {stock_code}")
            
            # 模拟成功获取数据
            data = {'code': stock_code, 'price': 10.5, 'volume': 1000000}
            print(f"✓ 成功获取数据: {data}")
            return data
            
        except ValueError as e:
            print(f"✗ 数据获取失败: {e}")
            return None
        except Exception as e:
            print(f"✗ 未知错误: {e}")
            return None
        finally:
            print(f"数据获取流程结束 (stock_code={stock_code})")
    
    # 测试成功场景
    result1 = safe_get_data('000001.SZ')
    assert result1 is not None, "正常股票代码应返回数据"
    
    # 测试失败场景
    result2 = safe_get_data('INVALID')
    assert result2 is None, "无效股票代码应返回None"
    
    print("✓ 异常处理练习通过")
    return safe_get_data


# === 练习4: 装饰器 ===
def exercise_4_decorator():
    """练习4: 装饰器 - 函数计时"""
    print("\n=== 练习4: 装饰器 ===")
    
    import time
    
    def timer(func):
        """计时装饰器"""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"[Timer] {func.__name__} 耗时: {elapsed:.4f}秒")
            return result
        return wrapper
    
    @timer
    def process_stock_data(stock_codes):
        """模拟数据处理函数"""
        print(f"处理 {len(stock_codes)} 只股票的数据...")
        time.sleep(0.1)  # 模拟耗时操作
        return [f"{code}.processed" for code in stock_codes]
    
    # 测试装饰器
    codes = ['000001', '000002', '600000']
    result = process_stock_data(codes)
    
    # 验证结果
    expected = ['000001.processed', '000002.processed', '600000.processed']
    assert result == expected, f"期望 {expected}, 实际 {result}"
    print("✓ 装饰器练习通过")
    
    return timer


# === 验收检查 ===
def verify():
    """运行所有练习的验收检查"""
    print("=" * 60)
    print("Day 2: Python核心语法特训 - 验收检查")
    print("=" * 60)
    
    try:
        # 练习1: 列表推导式
        exercise_1_list_comprehension()
        
        # 练习2: dict.get()
        exercise_2_dict_get()
        
        # 练习3: 异常处理
        exercise_3_exception_handling()
        
        # 练习4: 装饰器
        exercise_4_decorator()
        
        print("\n" + "=" * 60)
        print("✓✓✓ 所有练习通过！Day 2 完成！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 验收失败: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 运行错误: {e}")
        return False
    
    return True


if __name__ == '__main__':
    verify()


"""
## 任务完成！✓

我已成功完成**第二天：Python核心语法特训**的所有四个子任务：

### 已实现内容：

**创建了`exercises/week1/day2_python_basics.py`**，包含：

1. **列表推导式（List Comprehension）** - 将股票代码转换为正确格式：
   - `['000001', '000002', '600000']` → `['000001.SZ', '000002.SZ', '600000.SH']`
   - 使用条件列表推导式，为以“0”开头的代码添加`.SZ`，为以“6”开头的代码添加`.SH`

2. **dict.get() 安全取值** - 安全的字典访问：
   - 演示`dict[key]`（会引发KeyError）和`dict.get(key, default)`（返回默认值）之间的区别
   - 展示如何安全访问可能不存在的股票持仓

3. **异常处理（Exception Handling）** - `safe_get_data()`函数：
   - 使用try-except-finally结构
   - 处理无效股票代码的ValueError
   - 在finally块中始终执行清理操作

4. **装饰器（Decorator）** - `@timer`装饰器：
   - 测量函数执行时间
   - 应用于模拟数据处理函数
   - 演示函数包装和计时逻辑

### 验证结果：
所有练习均成功通过，输出正确，表现为：
- ✓ 列表推导式工作正常
- ✓ dict.get() 安全处理缺失的键
- ✓ 异常处理正确捕获错误
- ✓ 装饰器测量执行时间（0.1152秒）

代码符合设计文档的要求，并包含全面的验证检查。




## Task Completed! ✓

I've successfully implemented **Day 2: Python核心语法特训** with all four subtasks:

### What was implemented:

**Created `exercises/week1/day2_python_basics.py`** with:

1. **列表推导式 (List Comprehension)** - Converts stock codes to proper format:
   - `['000001', '000002', '600000']` → `['000001.SZ', '000002.SZ', '600000.SH']`
   - Uses conditional list comprehension to add `.SZ` for codes starting with '0' and `.SH` for codes starting with '6'

2. **dict.get() 安全取值** - Safe dictionary access:
   - Demonstrates the difference between `dict[key]` (raises KeyError) and `dict.get(key, default)` (returns default value)
   - Shows how to safely access stock positions that may not exist

3. **异常处理 (Exception Handling)** - `safe_get_data()` function:
   - Uses try-except-finally structure
   - Handles ValueError for invalid stock codes
   - Always executes cleanup in finally block

4. **装饰器 (Decorator)** - `@timer` decorator:
   - Measures function execution time
   - Applied to a mock data processing function
   - Demonstrates function wrapping and timing logic

### Verification Results:
All exercises passed successfully with proper output showing:
- ✓ List comprehension working correctly
- ✓ dict.get() safely handling missing keys
- ✓ Exception handling catching errors properly
- ✓ Decorator measuring execution time (0.1152 seconds)

The code follows the requirements from the design document and includes comprehensive verification checks.

"""