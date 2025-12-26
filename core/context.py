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

# class Context:
#     def __init__(self):

#         # === 资产账户信息 ===
#         self.cash = 100000.0                # 默认初始资金 10万
#         self.total_asset = 100000.0         # 总资产
#         self.positions = {}                 # 持仓字典 {stock_code: volume} 

#         # === 运行状态 ===
#         self.current_dt = None
#         self.period = '1d'                  # 运行周期，如 '1m', '5m', '1d'

#         # === 策略自定义变量 ===
#         # 策略里可以把 target_list, score 等变量存在这里    
#         self.user_data = {}

#     def log(self, msg):
#         """简易日志打印"""
#         print(f"[{self.current_dt}] {msg}")

#     def order(self, stock_code, volume):
#         """
#         [模拟下单接口]
#         正数代表买入，负数代表卖出
#         """
#         # 1. 简单的撮合逻辑 (仅用于演示架构，暂不考虑滑点/费用)
#         # 注意：这里我们还没传价格进来，简化为“信号发出即成交”
        
#         self.log(f"--- 收到订单: {stock_code}, 数量: {volume} ---")
        
#         # 更新持仓
#         curr_vol = self.positions.get(stock_code, 0)
#         new_vol = curr_vol + volume
#         self.positions[stock_code] = new_vol
        
#         # 实际开发中，这里还需要扣减 cash (资金)，计算市值
#         # 今天重点是跑通流程，资金计算暂略


"""
Week 1 Day 3 原子任务清单
T1: 升级 Context (注入实盘灵魂)
目标：现在的 Context.order 只能打印日志。我们要让它具备“人格分裂”的能力：如果没有 xt_trader 对象，它就模拟；如果有，它就真下单。
行动：修改 core/context.py。

紧急补丁：添加“安全锁”
T4: 修改 core/context.py
目标：区分 实盘(REAL) 和 模拟(SIM) 模式。
逻辑：只有当模式明确设置为 REAL 时，才允许调用 xt_trader 下单。

核心逻辑：
Level 1: 检查 run_mode 是否为 'real'。
Level 2: 检查 manual_confirm 是否为 True。如果是，强制阻塞程序，等待用户输入 y。

"""
# core/context.py
from xtquant import xtconstant  # 导入 xtconstant 模块，包含交易常量
import sys                      # 导入 sys 模块，用于系统相关操作

class Context:
    def __init__(self, xt_trader=None, account=None, run_mode='sim', manual_confirm=True):
        """
        :param xt_trader: 真实的交易接口对象
        :param account: 真实的资金账号对象
        :param run_mode: 运行模式 'sim'(模拟/回测) 或 'real'(实盘)
        :param manual_confirm: 是否开启人工二次确认？(教学阶段必须为 True)
        """
        # === 资产账户信息 ===
        self.cash = 100000.0           # 默认初始资金 10万   
        self.total_asset = 100000.0    # 总资产
        self.positions = {}            # 持仓字典 {stock_code: volume}
        
        # === 运行状态 ===
        self.current_dt = None         # 当前时间 (datetime对象)
        self.period = '1d'             # 运行周期，如 '1m', '5m', '1d'
        self.user_data = {}            # 策略自定义变量
        
        # === 实盘与安全配置 ===
        self.trader = xt_trader        # 真实交易接口对象
        self.account = account         # 真实资金账号对象
        self.run_mode = run_mode       # 运行模式 'sim' 或 'real'
        self.manual_confirm = manual_confirm  # <--- [安全锁] 是否开启人工二次确认

    def log(self, msg):
        """带模式标记的日志"""
        print(f"[{self.current_dt}] [{self.run_mode.upper()}] {msg}")   # 日志中加入运行模式标记,如 [SIM], [REAL], [1d]

    def order(self, stock_code, volume):
        """
        统一对应下单接口
        :param stock_code: 股票代码
        :param volume: 买入数量(正数)或卖出数量(负数)
        逻辑:
        1. 检查运行模式是否为实盘('real')，且是否注入了真实交易接口和资金账号。
        2. 如果是实盘模式，且开启了人工二次确认(manual_confirm=True)，则阻塞程序，等待用户输入确认。
        3. 如果确认无误，或未开启人工二次确认，发送真实下单指令。
        4. 如果不是实盘模式，直接打印日志模拟下单。
        """
        # 记录日志,显示收到的订单,包括股票代码和数量,方便调试,跟踪订单状态,是否为实盘订单/模拟订单,等信息
        self.log(f"--- 信号触发: {stock_code}, 数量: {volume} ---")
        
        # [分支 A] 实盘模式
        # 只有在实盘模式下，且注入了交易接口和账号，才执行真实下单逻辑,
        # 否则,打印日志模拟下单,避免误操作
        # 注意: 这里的 run_mode 是字符串 'real' 或 'sim'
        # 检查是否为实盘模式
        if self.run_mode == 'real' and self.trader and self.account:

            # 1. 准备参数,确定订单类型和数量,价格等信息
            # 确定订单类型(买/卖)和数量(绝对值)
            order_type = xtconstant.STOCK_BUY if volume > 0 else xtconstant.STOCK_SELL
            vol = abs(volume)
            price = 0                   # 实盘策略通常需要传入价格，演示暂设为0(配合市价单或最新价逻辑),
            # 实盘下单时,价格可以设为0,表示使用市价单,也可以设为具体价格,表示使用限价单,
            # 注意: 0 表示使用市价单,其他具体价格表示使用限价单,
            
            # 2. [新增] 人工确认防火墙 (教学阶段强制开启)
            # 只有开启了人工二次确认(manual_confirm=True)，才会阻塞程序,等待用户输入确认
            if self.manual_confirm:
                print("\n" + "!"*60)
                print(f"!!! [教学实盘拦截] 正准备发送交易指令 !!!")
                print(f"!!! 标的: {stock_code}")
                print(f"!!! 方向: {'买入' if volume > 0 else '卖出'}")
                print(f"!!! 数量: {vol}")
                print("!"*60)
                
                # 阻塞等待用户输入确认
                sys.stdout.flush()  # 确保提示信息立即输出
                confirm = input(f">>> 请输入 'y' 确认下单，输入其他任意键取消: ")
                
                # 用户未确认，取消下单
                if confirm.lower() != 'y':
                    self.log("[安全拦截] 用户取消了操作，指令未发送。")
                    return # 直接结束，不发送
            
            # 3. 通过防火墙，发送指令
            # 记录日志，显示真实下单指令已发送,包括股票代码、数量、方向(买/卖)、价格(0表示市价单)等信息
            self.log(f">>> [实盘指令] 发送至 MiniQMT... Code: {stock_code}, Vol: {vol}, Type: {'买' if volume > 0 else '卖'}, Price: {price}")
            
            # 真正的下单动作
            # 调用 xt_trader 的下单方法，发送订单到交易系统,
            # 注意: 这里的 order_type 是 xtconstant.STOCK_BUY 或 xtconstant.STOCK_SELL,
            # 表示买/卖,vol 是订单数量,xtconstant.FIX_PRICE 表示使用限价单,
            # price 是具体价格(0表示市价单),'Live_Strategy' 是策略名称,'Signal' 是订单来源,
            self.trader.order_stock_async(
                self.account,               # 资金账号
                stock_code,                 # 股票代码
                order_type,                 # 订单类型 (买/卖)
                vol,                        # 订单数量
                xtconstant.FIX_PRICE,       # 价格类型 (限价单)
                price,                      # 价格 (0表示市价单)
                'Live_Strategy',            # 策略名称
                'Signal'                    # 订单来源
            )
            
        # [分支 B] 模拟/回测模式
        else:
            self.log(f">>> [虚拟成交] (模式: {self.run_mode}) {stock_code} {volume} 股")    # 模拟下单日志,显示当前运行模式,如 SIM 或 REAL,
            # 记录日志,显示当前持仓,包括股票代码、持仓数量,方便调试,跟踪持仓状态,是否为实盘持仓/模拟持仓,等信息
            curr_vol = self.positions.get(stock_code, 0)    # 获取当前持仓量,默认0
            self.positions[stock_code] = curr_vol + volume  # 更新持仓量