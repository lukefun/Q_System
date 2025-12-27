"""
文件 2：core/live_runner.py (实盘引擎)
核心逻辑：
    负责连接 MiniQMT。
    负责将安全配置 (run_mode, manual_confirm) 传递给 Context。
    负责下载实时数据并驱动策略。
"""

# core/live_runner.py

from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount
from core.context import Context
import time
import datetime
import pandas as pd

class LiveRunner:
    def __init__(self, strategy, stock_list, account_id, mini_qmt_path, session_id, run_mode='sim', manual_confirm=True):
        self.strategy = strategy
        self.stock_list = stock_list
        self.mini_qmt_path = mini_qmt_path
        self.session_id = session_id
        
        # 初始化交易对象
        self.trader = XtQuantTrader(mini_qmt_path, session_id)
        self.acc = StockAccount(account_id, 'STOCK')
        
        # 初始化上下文 (注入 trader 和 安全配置)
        self.context = Context(
            xt_trader=self.trader, 
            account=self.acc, 
            run_mode=run_mode,
            manual_confirm=manual_confirm
        )

    def start(self):
        print(">> [LiveRunner] 正在启动实盘引擎...")
        
        # 1. 启动交易接口
        self.trader.start()
        res = self.trader.connect()
        if res == 0:
            print(">> [LiveRunner] 交易接口连接成功")
            self.trader.subscribe(self.acc) # 订阅账户资金持仓
        else:
            print(f">> [LiveRunner] 连接失败: {res}")
            return

        # 2. 策略初始化
        self.strategy.initialize(self.context)
        
        # 3. 订阅行情 (保持活跃)
        for stock in self.stock_list:
            xtdata.subscribe_quote(stock, period='tick', callback=self.on_market_data)

    def on_market_data(self, data):
        """
        Tick行情回调 (本日线策略暂不使用，仅作心跳)
        """
        pass
            
    def run_daily_check(self):
        """
        日线策略专用执行函数
        模拟每天收盘前的定点检查
        """
        print(f"\n>> [Daily Check] 开始执行定点检查 ({datetime.datetime.now()})...")
        
        # 1. 主动下载最新的日线数据
        for stock in self.stock_list:
            xtdata.download_history_data(stock, period='1d', count=30)
            
        # 2. 读取数据
        raw_data = xtdata.get_market_data(field_list=[], stock_list=self.stock_list, period='1d', count=30)
        
        # 3. 组装数据并计算指标
        bar_dict = {}
        for stock in self.stock_list:
            if stock not in raw_data['close'].index:
                continue
                
            df = pd.DataFrame()
            df['close'] = raw_data['close'].loc[stock]
            
            # 实时计算 MA
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 取最新一行 (即今天的状态)
            latest = df.iloc[-1]
            bar_dict[stock] = latest
            
        # 4. 调用策略
        self.context.current_dt = datetime.datetime.now()
        self.strategy.handle_bar(self.context, bar_dict)
        print(">> [Daily Check] 检查完成。")