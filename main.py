"""
Day2_T4: 
    编写启动脚本
目标：
    把引擎和策略组装起来运行。
行动：
    编辑根目录下的 main.py。
"""
# main.py
from strategies.double_ma import DoubleMAStrategy
from core.engine import BacktestEngine

def run():
    # 1. 实例化策略
    strategy = DoubleMAStrategy()       # 实例化双均线策略，默认参数为5日均线和20日均线
    
    # 2. 配置回测参数
    # 选取过去一年的数据
    start_date = '20250101'             # 回测开始日期
    end_date = '20251225'               # 回测结束日期
    stock_list = ['002594.SZ']          # 以比亚迪为例
    
    # 3. 实例化引擎
    engine = BacktestEngine(strategy, start_date, end_date, stock_list)     # 实例化回测引擎
    
    # 4. 加载数据
    engine.load_data()                  # 加载数据
    
    # 5. 运行回测
    engine.run()                        # 运行回测

if __name__ == "__main__":
    run()