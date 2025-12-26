
"""
T3: 
    定义策略的法律 —— BaseStrategy 基类
概念：
    所有的策略（均线、多因子、网格）都必须遵守同一套规则：初始化一次，然后每个K线运行一次。
行动：
    编辑 core/strategy.py。我们将使用 Python 的 abc 模块强制执行这些规则。

    ################################################################################################
    **  使用 Python 的 abc 模块强制执行这些规则  **

    这句话核心是借助 Python 的 `abc` 模块（全称 Abstract Base Classes，抽象基类），
    为策略代码设定“强制遵守的规则”，避免随意编写导致的逻辑混乱或兼容性问题，具体解析如下：

    1. **abc 模块的核心作用**：  
    它提供了“抽象基类”的功能 —— 即定义一个“模板类”（如代码中的 `BaseStrategy`），
    这个模板里可以声明**必须实现的“抽象方法”**
    （用 `@abstractmethod` 装饰的方法，如 `initialize` 和 `handle_bar`），但不写具体实现。

    2. **“强制执行规则”的体现**：  
    - 所有自定义策略（如 `DoubleMAStrategy`）必须**继承**这个抽象基类 `BaseStrategy`；  
    - 若自定义策略没有完整实现基类中所有的抽象方法 （比如只写了 `initialize`，没写 `handle_bar`），Python 会直接报错，
    **不允许创建该策略的实例**（比如运行 `DoubleMAStrategy()` 会触发 `TypeError`）；  
    - 最终确保所有策略都遵循“初始化（`initialize`）+ 逐K线处理（`handle_bar`）”的统一逻辑框架，
    方便后续对接 回测引擎 或 实盘系统（引擎只需按基类标准调用方法，无需适配不同策略的自定义逻辑）。
    ################################################################################################

"""

# core/strategy.py
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    策略抽象基类
    所有具体的策略（如双均线策略）都必须继承此类
    """
    
    @abstractmethod
    def initialize(self, context):
        """
        [必须实现] 初始化函数
        只在策略启动刚开始执行一次
        用于设置参数、股票池等初始化操作
        """
        pass

    @abstractmethod
    def handle_bar(self, context, bar_dict):
        """
        [必须实现] K线切片函数
        每根K线结束时调用一次
        用于计算指标、判断信号、下单等操作
        
        :param bar_dict: 包含当根K线数据的字典 {stock_code: dataframe_row}
        """
        pass