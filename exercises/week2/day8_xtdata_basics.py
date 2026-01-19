"""
Day 8 练习：XtData基础接口

学习目标：
1. 理解XtData API的基本概念
2. 掌握客户端连接和认证
3. 学会获取市场数据
4. 理解错误处理机制

金融概念：
- 股票代码格式：6位数字 + 市场代码（.SZ深圳/.SH上海）
- OHLCV数据：开盘价、最高价、最低价、收盘价、成交量
- Tick数据：逐笔成交数据，包含精确时间戳
- 日线数据：按日聚合的OHLCV数据

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# ============================================================================
# 练习1：连接XtData服务
# ============================================================================

def exercise_1_connect_xtdata():
    """
    练习1：连接XtData服务
    
    任务：
    1. 创建XtDataClient实例
    2. 连接到XtData服务
    3. 检查连接状态
    4. 断开连接
    
    提示：
    - 使用config.py中配置的账户信息
    - 注意处理连接失败的情况
    - 使用try-except捕获异常
    """
    print_section("练习1：连接XtData服务")
    
    # TODO: 在这里实现你的代码
    # 1. 创建XtDataClient实例
    # client = XtDataClient(...)
    
    # 2. 连接到XtData服务
    # if client.connect():
    #     print("✅ 连接成功")
    # else:
    #     print("❌ 连接失败")
    
    # 3. 检查连接状态
    # print(f"连接状态: {client.is_connected()}")
    
    # 4. 断开连接
    # client.disconnect()
    
    print("提示：参考 src/xtdata_client.py 中的XtDataClient类")
    print("提示：使用 XTDATA_ACCOUNT_ID 和 XTDATA_ACCOUNT_KEY")


# ============================================================================
# 练习2：获取股票列表
# ============================================================================

def exercise_2_get_stock_list():
    """
    练习2：获取股票列表
    
    任务：
    1. 创建DataRetriever实例
    2. 获取所有可用的股票代码
    3. 打印股票数量和前10个股票代码
    
    提示：
    - 需要先连接XtData客户端
    - 使用DataRetriever.get_all_stock_codes()方法
    - 股票代码格式：000001.SZ（深圳）或600000.SH（上海）
    """
    print_section("练习2：获取股票列表")
    
    # TODO: 在这里实现你的代码
    # 1. 创建并连接客户端
    # client = XtDataClient(...)
    # client.connect()
    
    # 2. 创建DataRetriever
    # retriever = DataRetriever(client)
    
    # 3. 获取股票列表
    # stock_codes = retriever.get_all_stock_codes()
    
    # 4. 打印结果
    # print(f"共有 {len(stock_codes)} 只股票")
    # print(f"前10个股票代码: {stock_codes[:10]}")
    
    # 5. 断开连接
    # client.disconnect()
    
    print("提示：参考 src/data_retriever.py 中的DataRetriever类")


# ============================================================================
# 练习3：获取历史日线数据
# ============================================================================

def exercise_3_get_daily_data():
    """
    练习3：获取历史日线数据
    
    任务：
    1. 获取平安银行（000001.SZ）最近10天的日线数据
    2. 打印数据的形状（行数和列数）
    3. 打印数据的前5行
    4. 打印数据的列名
    
    提示：
    - 使用DataRetriever.download_history_data()方法
    - 日期格式：'YYYYMMDD'，如'20240101'
    - period参数使用'1d'表示日线
    - 返回的是pandas DataFrame
    """
    print_section("练习3：获取历史日线数据")
    
    # TODO: 在这里实现你的代码
    # 1. 创建并连接客户端
    # client = XtDataClient(...)
    # client.connect()
    
    # 2. 创建DataRetriever
    # retriever = DataRetriever(client)
    
    # 3. 定义参数
    # stock_codes = ['000001.SZ']  # 平安银行
    # from datetime import datetime, timedelta
    # end_date = datetime.now()
    # start_date = end_date - timedelta(days=10)
    # start_date_str = start_date.strftime('%Y%m%d')
    # end_date_str = end_date.strftime('%Y%m%d')
    
    # 4. 获取数据
    # data = retriever.download_history_data(
    #     stock_codes=stock_codes,
    #     start_date=start_date_str,
    #     end_date=end_date_str,
    #     period='1d'
    # )
    
    # 5. 打印结果
    # print(f"数据形状: {data.shape}")
    # print(f"\n列名: {list(data.columns)}")
    # print(f"\n前5行数据:")
    # print(data.head())
    
    # 6. 断开连接
    # client.disconnect()
    
    print("提示：使用datetime模块计算日期")
    print("提示：DataFrame的shape属性返回(行数, 列数)")


# ============================================================================
# 练习4：获取多只股票数据
# ============================================================================

def exercise_4_get_multiple_stocks():
    """
    练习4：获取多只股票数据
    
    任务：
    1. 获取3只银行股的最近5天日线数据：
       - 平安银行（000001.SZ）
       - 招商银行（600036.SH）
       - 浦发银行（600000.SH）
    2. 统计每只股票的数据条数
    3. 计算每只股票的平均收盘价
    
    提示：
    - stock_codes参数传入列表
    - 使用pandas的groupby进行分组统计
    - 使用mean()计算平均值
    """
    print_section("练习4：获取多只股票数据")
    
    # TODO: 在这里实现你的代码
    # 1. 创建并连接客户端
    # client = XtDataClient(...)
    # client.connect()
    
    # 2. 创建DataRetriever
    # retriever = DataRetriever(client)
    
    # 3. 定义参数
    # stock_codes = ['000001.SZ', '600036.SH', '600000.SH']
    # ... 计算日期 ...
    
    # 4. 获取数据
    # data = retriever.download_history_data(...)
    
    # 5. 统计每只股票的数据条数
    # counts = data.groupby('stock_code').size()
    # print("每只股票的数据条数:")
    # print(counts)
    
    # 6. 计算每只股票的平均收盘价
    # avg_close = data.groupby('stock_code')['close'].mean()
    # print("\n每只股票的平均收盘价:")
    # print(avg_close)
    
    # 7. 断开连接
    # client.disconnect()
    
    print("提示：使用pandas的groupby和agg方法")


# ============================================================================
# 练习5：错误处理
# ============================================================================

def exercise_5_error_handling():
    """
    练习5：错误处理
    
    任务：
    1. 尝试获取无效股票代码的数据（如'INVALID'）
    2. 捕获并处理异常
    3. 打印友好的错误消息
    
    提示：
    - 使用try-except捕获异常
    - 不同的错误类型有不同的处理方式
    - 参考config.py中定义的异常类
    """
    print_section("练习5：错误处理")
    
    # TODO: 在这里实现你的代码
    # 1. 创建并连接客户端
    # client = XtDataClient(...)
    # client.connect()
    
    # 2. 创建DataRetriever
    # retriever = DataRetriever(client)
    
    # 3. 尝试获取无效股票代码的数据
    # try:
    #     data = retriever.download_history_data(
    #         stock_codes=['INVALID'],  # 无效的股票代码
    #         start_date='20240101',
    #         end_date='20240110'
    #     )
    # except ValueError as e:
    #     print(f"参数错误: {str(e)}")
    # except Exception as e:
    #     print(f"其他错误: {str(e)}")
    
    # 4. 断开连接
    # client.disconnect()
    
    print("提示：查看错误消息，理解参数验证的重要性")


# ============================================================================
# 扩展挑战
# ============================================================================

def challenge_get_market_snapshot():
    """
    扩展挑战：获取市场快照
    
    任务：
    1. 获取5只股票的实时市场快照
    2. 打印每只股票的最新价格、涨跌幅
    3. 找出涨幅最大的股票
    
    提示：
    - 使用DataRetriever.get_market_data()方法
    - 计算涨跌幅：(close - open) / open * 100
    - 使用idxmax()找出最大值的索引
    """
    print_section("扩展挑战：获取市场快照")
    
    # TODO: 在这里实现你的代码
    
    print("提示：这是一个进阶任务，完成基础练习后再尝试")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("  Day 8 练习：XtData基础接口")
    print("=" * 60)
    print()
    print("本练习包含5个基础练习和1个扩展挑战")
    print("请按顺序完成每个练习")
    print()
    
    # 运行练习
    exercise_1_connect_xtdata()
    exercise_2_get_stock_list()
    exercise_3_get_daily_data()
    exercise_4_get_multiple_stocks()
    exercise_5_error_handling()
    
    # 扩展挑战（可选）
    print("\n" + "=" * 60)
    print("  扩展挑战（可选）")
    print("=" * 60)
    challenge_get_market_snapshot()
    
    print("\n" + "=" * 60)
    print("  练习完成！")
    print("=" * 60)
    print()
    print("下一步：")
    print("- 完成所有TODO标记的代码")
    print("- 运行程序验证结果")
    print("- 理解每个API的用法和参数")
    print("- 继续Day 9练习：价格复权")


if __name__ == '__main__':
    main()
