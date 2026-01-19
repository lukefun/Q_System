"""
示例1：基础数据获取

本示例演示如何使用XtData API获取市场数据，包括：
1. 连接到XtData服务
2. 获取历史日线数据
3. 获取实时市场快照
4. 获取Tick级别数据
5. 获取所有股票代码列表

学习目标：
- 理解XtData客户端的连接和认证流程
- 掌握不同类型市场数据的获取方法
- 了解数据返回格式和字段含义
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def example_1_connect_to_xtdata():
    """示例1：连接到XtData服务"""
    print("=" * 60)
    print("示例1：连接到XtData服务")
    print("=" * 60)
    
    # 创建客户端实例
    client = XtDataClient(
        account_id=XTDATA_ACCOUNT_ID,
        account_key=XTDATA_ACCOUNT_KEY
    )
    
    # 连接到服务
    print(f"正在连接到XtData服务...")
    success = client.connect()
    
    if success:
        print(f"✓ 连接成功！")
        print(f"  连接状态: {client.is_connected()}")
    else:
        print(f"✗ 连接失败")
        return None
    
    print()
    return client


def example_2_download_daily_data(client):
    """示例2：下载历史日线数据"""
    print("=" * 60)
    print("示例2：下载历史日线数据")
    print("=" * 60)
    
    # 创建数据获取器
    retriever = DataRetriever(client)
    
    # 设置参数
    stock_codes = ['000001.SZ', '600000.SH']  # 平安银行、浦发银行
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    print(f"股票代码: {stock_codes}")
    print(f"日期范围: {start_date} 至 {end_date}")
    print(f"正在下载数据...")
    
    try:
        # 下载日线数据
        data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period='1d',
            adjust_type='none'  # 不复权
        )
        
        print(f"✓ 下载成功！")
        print(f"\n数据概览:")
        print(f"  总记录数: {len(data)}")
        print(f"  股票数量: {data['stock_code'].nunique()}")
        print(f"  日期范围: {data['date'].min()} 至 {data['date'].max()}")
        print(f"\n数据列: {list(data.columns)}")
        print(f"\n前5条记录:")
        print(data.head())
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
    
    print()


def example_3_get_market_snapshot(client):
    """示例3：获取实时市场快照"""
    print("=" * 60)
    print("示例3：获取实时市场快照")
    print("=" * 60)
    
    retriever = DataRetriever(client)
    
    # 设置参数
    stock_codes = ['000001.SZ', '600000.SH', '000002.SZ']
    
    print(f"股票代码: {stock_codes}")
    print(f"正在获取市场快照...")
    
    try:
        # 获取市场快照
        snapshot = retriever.get_market_data(stock_codes=stock_codes)
        
        print(f"✓ 获取成功！")
        print(f"\n快照数据:")
        print(snapshot)
        
        print(f"\n数据说明:")
        print(f"  - 包含当前最新的市场数据")
        print(f"  - 包括最新价、涨跌幅、成交量等信息")
        print(f"  - 适用于实时监控和交易决策")
        
    except Exception as e:
        print(f"✗ 获取失败: {e}")
    
    print()


def example_4_download_tick_data(client):
    """示例4：下载Tick级别数据"""
    print("=" * 60)
    print("示例4：下载Tick级别数据")
    print("=" * 60)
    
    retriever = DataRetriever(client)
    
    # 设置参数（Tick数据量大，只获取最近1天）
    stock_codes = ['000001.SZ']
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = end_date  # 只获取当天
    
    print(f"股票代码: {stock_codes}")
    print(f"日期: {start_date}")
    print(f"正在下载Tick数据...")
    print(f"注意: Tick数据量较大，下载可能需要较长时间")
    
    try:
        # 下载Tick数据
        tick_data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period='tick',
            adjust_type='none'
        )
        
        print(f"✓ 下载成功！")
        print(f"\nTick数据概览:")
        print(f"  总记录数: {len(tick_data)}")
        print(f"  时间范围: {tick_data['time'].min()} 至 {tick_data['time'].max()}")
        print(f"\n数据列: {list(tick_data.columns)}")
        print(f"\n前10条记录:")
        print(tick_data.head(10))
        
        print(f"\nTick数据特点:")
        print(f"  - 逐笔成交数据，时间精度到秒或毫秒")
        print(f"  - 包含每笔交易的价格、数量、买卖盘信息")
        print(f"  - 适用于高频交易和微观结构分析")
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
    
    print()


def example_5_get_all_stock_codes(client):
    """示例5：获取所有股票代码"""
    print("=" * 60)
    print("示例5：获取所有股票代码")
    print("=" * 60)
    
    retriever = DataRetriever(client)
    
    print(f"正在获取所有股票代码...")
    
    try:
        # 获取所有股票代码
        all_codes = retriever.get_all_stock_codes()
        
        print(f"✓ 获取成功！")
        print(f"\n股票代码统计:")
        print(f"  总数量: {len(all_codes)}")
        
        # 统计不同市场的股票数量
        sz_count = sum(1 for code in all_codes if code.endswith('.SZ'))
        sh_count = sum(1 for code in all_codes if code.endswith('.SH'))
        
        print(f"  深圳市场 (SZ): {sz_count}")
        print(f"  上海市场 (SH): {sh_count}")
        
        print(f"\n前20个股票代码:")
        for i, code in enumerate(all_codes[:20], 1):
            print(f"  {i:2d}. {code}")
        
        print(f"\n用途说明:")
        print(f"  - 用于构建全市场数据库")
        print(f"  - 用于股票池筛选和组合构建")
        print(f"  - 用于批量数据下载")
        
    except Exception as e:
        print(f"✗ 获取失败: {e}")
    
    print()


def main():
    """主函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  XtData基础数据获取示例".center(56) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()
    
    # 示例1：连接到XtData
    client = example_1_connect_to_xtdata()
    
    if client is None:
        print("无法连接到XtData服务，请检查:")
        print("  1. XtQuant是否已安装")
        print("  2. 账户ID和密钥是否正确")
        print("  3. 网络连接是否正常")
        return
    
    try:
        # 示例2：下载日线数据
        example_2_download_daily_data(client)
        
        # 示例3：获取市场快照
        example_3_get_market_snapshot(client)
        
        # 示例4：下载Tick数据（可选，数据量大）
        # 取消注释以运行此示例
        # example_4_download_tick_data(client)
        
        # 示例5：获取所有股票代码
        example_5_get_all_stock_codes(client)
        
    finally:
        # 断开连接
        print("=" * 60)
        print("清理资源")
        print("=" * 60)
        client.disconnect()
        print("✓ 已断开连接")
        print()
    
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  示例运行完成！".center(56) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()
    
    print("下一步学习:")
    print("  - examples/02_price_adjustment.py - 学习价格复权")
    print("  - examples/03_fundamental_data.py - 学习基本面数据处理")
    print("  - examples/04_industry_classification.py - 学习行业分类")
    print()


if __name__ == '__main__':
    main()
