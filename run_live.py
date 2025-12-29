"""
T3: 编写实盘启动入口
目标：创建一个单独的 run_live.py，用于启动实盘模式。
行动：在根目录创建 run_live.py。
注意：请填入您真实的 MiniQMT 路径和账号。

run_live.py (启动脚本)
核心逻辑：
    用户配置区。
    默认开启 MANUAL_CONFIRM = True。
"""


# run_live.py

from strategies.double_ma import DoubleMAStrategy
from core.live_runner import LiveRunner
import random
import time

def run():
    # ==========================================
    # [配置区域] 请仔细检查
    # ==========================================
    # 1. MiniQMT 路径 (请替换)
    MINI_QMT_PATH = r'D:\迅投极速交易终端\userdata_mini' 
    
    # 2. 资金账号 (请替换)
    ACCOUNT_ID = '您的账号'                             
    
    # 3. 会话ID
    SESSION_ID = int(random.randint(100000, 999999))
    
    # 4. 【安全锁】运行模式
    # 'sim'  = 模拟模式 (只打印日志，不下单) -> 推荐调试用
    # 'real' = 实盘模式 (触发人工确认) -> 需谨慎
    RUN_MODE = 'sim'
    
    # 5. 【人工确认防火墙】
    # True  = 下单前必须手动输入 'y' 确认 (教学阶段请保持 True)
    # False = 全自动下单 (实盘严禁在测试期开启)
    MANUAL_CONFIRM = True
    # ==========================================

    print(f"启动模式: [{RUN_MODE.upper()}]")
    print(f"人工确认: [{'开启' if MANUAL_CONFIRM else '关闭'}]")

    # 1. 实例化策略
    strategy = DoubleMAStrategy()
    
    # 2. 标的池 (比亚迪)
    stock_list = ['002594.SZ'] 
    
    # 3. 实例化实盘引擎
    runner = LiveRunner(
        strategy, stock_list, ACCOUNT_ID, MINI_QMT_PATH, SESSION_ID, 
        run_mode=RUN_MODE,
        manual_confirm=MANUAL_CONFIRM
    )
    
    # 4. 启动连接
    runner.start()
    
    # 5. 执行一次检查 (模拟盘中定时触发)
    runner.run_daily_check()

    # 保持程序不退出
    input(">> 按回车键退出程序...")

if __name__ == "__main__":
    run()