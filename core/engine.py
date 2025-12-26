# core/engine.py

"""
Day2_T2: 
    构建时间机器 —— BacktestEngine
目标：
    这是今天的重头戏。引擎负责：下载数据 -> 清洗数据 -> 驱动时间循环 -> 喂给策略。
行动：
    创建 core/engine.py。
"""

from xtquant import xtdata          # 从xtquant库导入xtdata模块，用于下载历史K线数据
import pandas as pd                 # 导入pandas库，用于数据处理
from core.context import Context     # 从核心模块导入上下文类，用于存储策略运行时的状态和参数

class BacktestEngine:
    """
    回测引擎类
    负责加载历史数据、驱动时间循环、将数据喂给策略
    参数:
        strategy: 要运行的策略实例
        start_date: 回测开始日期 (格式: '20230101')
        end_date: 回测结束日期 (格式: '20230101')
        stock_list: 要回测的股票列表 (如 ['601288.SH', '002594.SZ'])
    """
    def __init__(self, strategy, start_date, end_date, stock_list):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.stock_list = stock_list
        self.context = Context()                                        # 创建这一局游戏的上下文

    def load_data(self):
        """
        数据加载与预处理 (ETL)
        """
        print(">> 引擎正在加载历史数据...")
        # 1. 下载
        # 下载所有股票的历史数据，周期为1天，时间范围为start_date到end_date
        for stock in self.stock_list:
            xtdata.download_history_data(stock, period='1d', 
                                         start_time=self.start_date, end_time=self.end_date)
        
        # 2. 读取
        # 从xtdata获取所有股票的历史数据，字段为空表示获取所有字段，时间范围为start_date到end_date
        raw_data = xtdata.get_market_data(field_list=[], stock_list=self.stock_list, 
                                          period='1d', start_time=self.start_date, end_time=self.end_date)
        
        # 3. 结构重组 (参考 Week0 Day2 的知识)
        # 我们把数据处理成一个字典: {stock_code: DataFrame}
        # 每个DataFrame包含 OHLCV 以及预计算的 MA5, MA20
        self.data_map = {}
        
        # 4. 结构重组
        # 遍历所有股票，将数据组织成DataFrame，包含OHLCV和预计算的MA5, MA20，
        # 并将时间索引转换为datetime格式，方便后续时间操作，如切片、比较等，
        # 并将索引设置为时间，方便后续按时间筛选数据，如 df.loc['2023-01-01']
        for stock in self.stock_list:
            # 提取 OHLCV
            df = pd.DataFrame()
            # 必须确保 keys 存在
            if 'close' not in raw_data or stock not in raw_data['close'].index:
                print(f"警告: {stock} 无数据")
                continue

            df['open'] = raw_data['open'].loc[stock]
            df['high'] = raw_data['high'].loc[stock]
            df['low'] = raw_data['low'].loc[stock]
            df['close'] = raw_data['close'].loc[stock]
            df['volume'] = raw_data['volume'].loc[stock]
            
            # 预计算技术指标 (为了提升回测速度，我们利用向量化提前算好)
            # 在实盘中，这些指标是每一刻实时算的；但在回测里，我们可以偷懒先算好
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 处理时间索引 (XtQuant 返回 'YYYYMMDD' 格式字符串)
            df.index = pd.to_datetime(df.index, format='%Y%m%d')
            self.data_map[stock] = df
            
        print(">> 数据加载完成。")

    def run(self):
        """
        启动时间循环
        """
        # 1. 策略初始化
        self.strategy.initialize(self.context)
        
        # 2. 生成统一的时间轴 (取第一只股票的时间索引)
        first_stock = self.stock_list[0]
        if first_stock not in self.data_map:
            return
        
        timeline = self.data_map[first_stock].index
        
        print(f">> 开始回测: {self.start_date} -> {self.end_date}")
        
        # 3. 时间开始流动 (Loop)
        for current_time in timeline:
            # 更新上下文的时间
            self.context.current_dt = current_time
            
            # 构建当根K线的 bar_dict
            # 格式: {stock_code: Series(包含 close, ma5, ma20...)}
            bar_dict = {}
            for stock in self.stock_list:
                df = self.data_map[stock]
                if current_time in df.index:
                    bar_dict[stock] = df.loc[current_time]
            
            # 调用策略的 handle_bar
            self.strategy.handle_bar(self.context, bar_dict)
            
        print(">> 回测结束。")