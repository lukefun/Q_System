# strategies/double_ma.py

"""
T4: 
    移植双均线策略
目标：
    验证架构是否合理。将 Day 3 的逻辑“填空”到新的架构中。
行动：
    编辑 strategies/double_ma.py。
注意：
    这里我们只写逻辑，不写具体的 xtdata 或 xttrader 代码，那些是引擎该做的事。
"""

# from core.strategy import BaseStrategy

# class DoubleMAStrategy(BaseStrategy):
    
#     def initialize(self, context):
#         # 在这里定义策略参数
#         print(">> 策略初始化...")
#         context.user_data['stock_code'] = '601288.SH'
#         context.user_data['fast_window'] = 5
#         context.user_data['slow_window'] = 20
        
#     def handle_bar(self, context, bar_dict):
#         # 获取上下文中的参数
#         stock = context.user_data['stock_code']
        
#         # 模拟获取数据 (Week 1 后几天我们会实现真实的数据传入)
#         # bar_dict[stock] 理论上包含 'close', 'MA5', 'MA20' 等数据
#         if stock not in bar_dict:
#             return
            
#         data = bar_dict[stock]
#         price = data['close']
#         ma5 = data['ma5']                                 # 假设引擎已经算好了传进来，或者在这里算
#         ma20 = data['ma20']
        
#         curr_pos = context.positions.get(stock, 0)        # 获取当前持仓量，默认0
        
#         # 纯逻辑判断，不涉及具体下单API
#         if ma5 > ma20 and curr_pos == 0:
#             context.log(f"金叉触发: {price}, 发送买入信号")
#             # TODO: 调用 context.order(...) -> 这个方法我们明天实现
            
#         elif ma5 < ma20 and curr_pos > 0:
#             context.log(f"死叉触发: {price}, 发送卖出信号")
#             # TODO: 调用 context.order(...)


"""
Day_T3: 
    更新策略逻辑 (适配真实数据)
目标：
    昨天的 DoubleMAStrategy 里还有 TODO，今天把它补全，让它调用 context.order。
行动：
    修改 strategies/double_ma.py。
"""

# strategies/double_ma.py

from core.strategy import BaseStrategy      # 从核心策略模块导入基础策略类
import pandas as pd                         # 导入pandas库，用于数据处理

# 双均线策略，默认参数为5日均线和20日均线，当5日均线大于20日均线时，买入；当5日均线小于20日均线时，卖出。
class DoubleMAStrategy(BaseStrategy):   
    
    def initialize(self, context):
        """
        策略初始化方法
        在策略开始运行前执行，用于设置策略的基本参数和初始状态
        """
        print(">> 策略初始化: 设置目标标的以比亚迪为例，代码为 002594.SZ")
        
        # 这里的 key 要和 Engine 里传入的一致
        context.user_data['stock_code'] = '002594.SZ'   # 以比亚迪为例
        
    def handle_bar(self, context, bar_dict):
        """
        处理K线数据的方法
        在每个交易周期（如每日）被调用，用于执行策略逻辑
        参数:
            context: 包含策略上下文信息的对象
            bar_dict: 包含股票K线数据的字典
        """

        # 获取上下文中的参数
        stock = context.user_data['stock_code']
        
        # 容错：如果当天没数据（比如停牌），直接返回
        if stock not in bar_dict:
            return
            
        # 获取切片数据
        bar = bar_dict[stock]

        # 提取值 (处理可能的重复索引导致返回Series的情况)
        price = bar['close'].iloc[0] if hasattr(bar['close'], 'iloc') else bar['close']
        ma5 = bar['ma5'].iloc[0] if hasattr(bar['ma5'], 'iloc') else bar['ma5']
        ma20 = bar['ma20'].iloc[0] if hasattr(bar['ma20'], 'iloc') else bar['ma20']

        # 检查 NaN (比如刚上市前几天MA算不出来)
        if pd.isna(ma5) or pd.isna(ma20):
            return
        
        # 获取当前持仓量，默认0
        curr_pos = context.positions.get(stock, 0)
        
        # 策略逻辑
        if ma5 > ma20 and curr_pos == 0:
            context.log(f"金叉 (Price:{price}, MA5:{ma5:.2f}, MA20:{ma20:.2f}) -> 买入")
            context.order(stock, 1000) # 模拟买入1000股
            
        elif ma5 < ma20 and curr_pos > 0:
            context.log(f"死叉 (Price:{price}, MA5:{ma5:.2f}, MA20:{ma20:.2f}) -> 卖出")
            context.order(stock, -curr_pos) # 卖出所有持仓