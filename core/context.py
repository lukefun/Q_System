# core/context.py

"""
Day1 T2: 
    定义上帝视角 —— Context 对象
概念：
    在回测或实盘中，策略需要随时知道：“我有多少钱？”“现在几点了？”“我持仓多少？”。我们将这些信息打包成一个对象，叫 Context。
行动：
    编辑 core/context.py。

"""


# class Context:
#     """
#     上下文对象：存储全局状态
#     在策略运行过程中，context 会被不断更新，并在函数间传递
#     """
#     def __init__(self):
#         # === 资产账户信息 ===
#         self.cash = 0.0           # 可用资金
#         self.total_asset = 0.0    # 总资产
#         self.positions = {}       # 持仓字典 {stock_code: volume}
        
#         # === 运行状态 ===
#         self.current_dt = None    # 当前时间 (datetime对象)
#         self.period = '1d'        # 运行周期，如 '1m', '5m', '1d'
        
#         # === 策略自定义变量 ===
#         # 策略里可以把 target_list, score 等变量存在这里
#         self.user_data = {} 
        
#     def log(self, msg):
#         """简易日志打印"""
#         print(f"[{self.current_dt}] {msg}")


"""
Day2 T1: 
    升级 Context (赋予交易能力)
目标：
    昨天的 Context 只是个数据容器，今天我们要给它加上 order 方法。
说明：
    在回测模式下，order 只是打印日志（模拟）；
    在未来实盘模式下，我们将把这个方法替换为真实的 xttrader 调用。
行动：
    修改 core/context.py，增加 order 方法。
"""

class Context:
    def __init__(self):

        # === 资产账户信息 ===
        self.cash = 100000.0                # 默认初始资金 10万
        self.total_asset = 100000.0         # 总资产
        self.positions = {}                 # 持仓字典 {stock_code: volume} 

        # === 运行状态 ===
        self.current_dt = None
        self.period = '1d'                  # 运行周期，如 '1m', '5m', '1d'

        # === 策略自定义变量 ===
        # 策略里可以把 target_list, score 等变量存在这里    
        self.user_data = {}

    def log(self, msg):
        """简易日志打印"""
        print(f"[{self.current_dt}] {msg}")

    def order(self, stock_code, volume):
        """
        [模拟下单接口]
        正数代表买入，负数代表卖出
        """
        # 1. 简单的撮合逻辑 (仅用于演示架构，暂不考虑滑点/费用)
        # 注意：这里我们还没传价格进来，简化为“信号发出即成交”
        
        self.log(f"--- 收到订单: {stock_code}, 数量: {volume} ---")
        
        # 更新持仓
        curr_vol = self.positions.get(stock_code, 0)
        new_vol = curr_vol + volume
        self.positions[stock_code] = new_vol
        
        # 实际开发中，这里还需要扣减 cash (资金)，计算市值
        # 今天重点是跑通流程，资金计算暂略

