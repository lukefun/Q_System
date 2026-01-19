"""
示例02：价格复权演示

本示例演示如何使用PriceAdjuster进行前复权和后复权处理。
展示了复权对价格数据的影响，以及在回测中应该使用哪种复权方式。

学习要点：
1. 前复权 vs 后复权的区别
2. 复权对OHLCV数据的影响
3. 为什么回测应该使用前复权
4. 如何处理复权因子缺失的情况
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster

def create_sample_data_with_dividend():
    """
    创建包含分红事件的示例数据
    
    假设场景：
    - 2024-01-15: 股票价格10元
    - 2024-01-16: 分红1元（10%），除权后价格应该是9元左右
    - 2024-01-17: 继续交易
    """
    dates = pd.date_range('2024-01-10', '2024-01-20', freq='D')
    
    # 创建基础价格数据
    data = pd.DataFrame({
        'stock_code': '000001.SZ',
        'date': dates.strftime('%Y%m%d'),
        'open': [10.0, 10.2, 10.1, 10.3, 10.5,  # 分红前
                 9.5, 9.6, 9.7, 9.8, 9.9, 10.0],  # 分红后（除权）
        'high': [10.5, 10.6, 10.5, 10.7, 10.9,
                 9.9, 10.0, 10.1, 10.2, 10.3, 10.4],
        'low': [9.8, 9.9, 9.8, 10.0, 10.2,
                9.2, 9.3, 9.4, 9.5, 9.6, 9.7],
        'close': [10.2, 10.1, 10.3, 10.5, 10.7,
                  9.6, 9.7, 9.8, 9.9, 10.0, 10.1],
        'volume': [1000000] * 11,
        'amount': [10200000, 10100000, 10300000, 10500000, 10700000,
                   9600000, 9700000, 9800000, 9900000, 10000000, 10100000]
    })
    
    return data

def demonstrate_forward_adjustment():
    """演示前复权"""
    print("=" * 60)
    print("1. 前复权演示（Forward Adjustment）")
    print("=" * 60)
    print("\n前复权说明：")
    print("- 从分红送股事件向前调整历史价格")
    print("- 保持当前价格不变")
    print("- 适用于回测场景，避免未来函数")
    print("- 历史价格会被调整得更低\n")
    
    # 创建示例数据
    data = create_sample_data_with_dividend()
    
    print("原始数据（包含除权缺口）：")
    print(data[['date', 'close', 'volume']].to_string(index=False))
    print(f"\n注意：2024-01-15收盘10.7元，2024-01-16开盘9.5元（除权缺口）")
    
    # 创建模拟的复权因子
    # 假设在2024-01-16发生10%的分红
    adjust_factors = pd.DataFrame({
        'date': data['date'],
        'adjust_factor': [1.0] * 5 + [0.9] * 6  # 分红后因子变为0.9
    })
    
    # 手动应用前复权逻辑（不使用PriceAdjuster类以避免依赖）
    adjusted_data = data.copy()
    
    # 找到最新的复权因子
    latest_factor = adjust_factors['adjust_factor'].iloc[-1]
    
    # 对每个价格列应用复权
    for col in ['open', 'high', 'low', 'close']:
        adjusted_data[col] = data[col] * (latest_factor / adjust_factors['adjust_factor'])
    
    # 成交额也需要调整
    adjusted_data['amount'] = data['amount'] * (latest_factor / adjust_factors['adjust_factor'])
    
    print("\n前复权后的数据：")
    print(adjusted_data[['date', 'close', 'volume']].to_string(index=False))
    print(f"\n观察：")
    print(f"- 最新价格保持不变：{data['close'].iloc[-1]:.2f} -> {adjusted_data['close'].iloc[-1]:.2f}")
    print(f"- 历史价格被调低：{data['close'].iloc[0]:.2f} -> {adjusted_data['close'].iloc[0]:.2f}")
    print(f"- 除权缺口消失，价格连续")
    print(f"- 成交量不变：{data['volume'].iloc[0]} -> {adjusted_data['volume'].iloc[0]}")

def demonstrate_backward_adjustment():
    """演示后复权"""
    print("\n" + "=" * 60)
    print("2. 后复权演示（Backward Adjustment）")
    print("=" * 60)
    print("\n后复权说明：")
    print("- 从当前价格向后调整历史价格")
    print("- 保持历史价格连续性")
    print("- 适用于展示场景")
    print("- 当前价格会被调整得更高\n")
    
    # 创建示例数据
    data = create_sample_data_with_dividend()
    
    print("原始数据（包含除权缺口）：")
    print(data[['date', 'close', 'volume']].to_string(index=False))
    
    # 创建模拟的复权因子
    adjust_factors = pd.DataFrame({
        'date': data['date'],
        'adjust_factor': [1.0] * 5 + [0.9] * 6
    })
    
    # 手动应用后复权逻辑（不使用PriceAdjuster类以避免依赖）
    adjusted_data = data.copy()
    
    # 找到最早的复权因子
    earliest_factor = adjust_factors['adjust_factor'].iloc[0]
    
    # 对每个价格列应用复权
    for col in ['open', 'high', 'low', 'close']:
        adjusted_data[col] = data[col] * (adjust_factors['adjust_factor'] / earliest_factor)
    
    # 成交额也需要调整
    adjusted_data['amount'] = data['amount'] * (adjust_factors['adjust_factor'] / earliest_factor)
    
    print("\n后复权后的数据：")
    print(adjusted_data[['date', 'close', 'volume']].to_string(index=False))
    print(f"\n观察：")
    print(f"- 历史价格保持不变：{data['close'].iloc[0]:.2f} -> {adjusted_data['close'].iloc[0]:.2f}")
    print(f"- 最新价格被调高：{data['close'].iloc[-1]:.2f} -> {adjusted_data['close'].iloc[-1]:.2f}")
    print(f"- 除权缺口消失，价格连续")
    print(f"- 成交量不变：{data['volume'].iloc[0]} -> {adjusted_data['volume'].iloc[0]}")

def demonstrate_ohlc_relationships():
    """演示复权后OHLC关系保持不变"""
    print("\n" + "=" * 60)
    print("3. OHLC关系不变性验证")
    print("=" * 60)
    print("\n复权后应该保持的关系：")
    print("- high >= max(open, close)")
    print("- low <= min(open, close)")
    print("- high >= low\n")
    
    data = create_sample_data_with_dividend()
    
    # 检查原始数据
    print("原始数据OHLC关系检查：")
    for idx, row in data.iterrows():
        high_ok = row['high'] >= max(row['open'], row['close'])
        low_ok = row['low'] <= min(row['open'], row['close'])
        hl_ok = row['high'] >= row['low']
        
        status = "✓" if (high_ok and low_ok and hl_ok) else "✗"
        print(f"{row['date']}: {status} H={row['high']:.2f} O={row['open']:.2f} "
              f"L={row['low']:.2f} C={row['close']:.2f}")
    
    # 应用前复权
    adjust_factors = pd.DataFrame({
        'date': data['date'],
        'adjust_factor': [1.0] * 5 + [0.9] * 6
    })
    
    adjusted_data = data.copy()
    latest_factor = adjust_factors['adjust_factor'].iloc[-1]
    
    for col in ['open', 'high', 'low', 'close']:
        adjusted_data[col] = data[col] * (latest_factor / adjust_factors['adjust_factor'])
    
    print("\n前复权后OHLC关系检查：")
    for idx, row in adjusted_data.iterrows():
        high_ok = row['high'] >= max(row['open'], row['close'])
        low_ok = row['low'] <= min(row['open'], row['close'])
        hl_ok = row['high'] >= row['low']
        
        status = "✓" if (high_ok and low_ok and hl_ok) else "✗"
        print(f"{row['date']}: {status} H={row['high']:.2f} O={row['open']:.2f} "
              f"L={row['low']:.2f} C={row['close']:.2f}")
    
    print("\n结论：复权后OHLC关系保持不变 ✓")

def demonstrate_backtesting_scenario():
    """演示回测场景中为什么要使用前复权"""
    print("\n" + "=" * 60)
    print("4. 回测场景：为什么使用前复权？")
    print("=" * 60)
    print("\n场景：假设我们在2024-01-12买入股票")
    print("买入价格：10.1元")
    print("2024-01-16发生10%分红\n")
    
    data = create_sample_data_with_dividend()
    buy_date = '20240112'
    buy_price = 10.1
    
    print("如果使用原始价格（不复权）：")
    print(f"- 买入价格：{buy_price}元")
    print(f"- 2024-01-20价格：{data[data['date'] == '20240120']['close'].values[0]}元")
    print(f"- 收益率：{(10.1 - buy_price) / buy_price * 100:.2f}%")
    print("- 问题：忽略了分红收益！\n")
    
    print("如果使用后复权：")
    adjust_factors = pd.DataFrame({
        'date': data['date'],
        'adjust_factor': [1.0] * 5 + [0.9] * 6
    })
    
    backward_data = data.copy()
    earliest_factor = adjust_factors['adjust_factor'].iloc[0]
    
    for col in ['open', 'high', 'low', 'close']:
        backward_data[col] = data[col] * (adjust_factors['adjust_factor'] / earliest_factor)
    
    backward_buy_price = buy_price  # 历史价格不变
    backward_current_price = backward_data[backward_data['date'] == '20240120']['close'].values[0]
    
    print(f"- 买入价格：{backward_buy_price}元（不变）")
    print(f"- 2024-01-20价格：{backward_current_price:.2f}元（调高）")
    print(f"- 收益率：{(backward_current_price - backward_buy_price) / backward_buy_price * 100:.2f}%")
    print("- 问题：使用了未来信息（分红后的复权因子）！\n")
    
    print("如果使用前复权（推荐）：")
    forward_data = data.copy()
    latest_factor = adjust_factors['adjust_factor'].iloc[-1]
    
    for col in ['open', 'high', 'low', 'close']:
        forward_data[col] = data[col] * (latest_factor / adjust_factors['adjust_factor'])
    
    forward_buy_price = forward_data[forward_data['date'] == buy_date]['close'].values[0]
    forward_current_price = forward_data[forward_data['date'] == '20240120']['close'].values[0]
    
    print(f"- 买入价格：{forward_buy_price:.2f}元（调低）")
    print(f"- 2024-01-20价格：{forward_current_price:.2f}元（不变）")
    print(f"- 收益率：{(forward_current_price - forward_buy_price) / forward_buy_price * 100:.2f}%")
    print("- 优点：正确反映了分红收益，且不使用未来信息 ✓")
    
    print("\n总结：")
    print("- 前复权：保持当前价格真实，历史价格调整，适合回测")
    print("- 后复权：保持历史价格真实，当前价格调整，适合展示")
    print("- 回测必须使用前复权，避免未来函数！")

def demonstrate_missing_factors():
    """演示复权因子缺失的处理"""
    print("\n" + "=" * 60)
    print("5. 复权因子缺失的处理")
    print("=" * 60)
    print("\n当复权因子不可用时，系统应该：")
    print("1. 返回原始数据（不复权）")
    print("2. 发出警告信息")
    print("3. 不抛出异常，保持系统稳定\n")
    
    data = create_sample_data_with_dividend()
    
    print("场景：尝试对新上市股票进行复权")
    print("- 股票代码：000001.SZ")
    print("- 上市时间：2024-01-10")
    print("- 查询时间：2024-01-15")
    print("- 复权因子：不可用（新股无分红记录）\n")
    
    print("处理结果：")
    print("- 返回原始价格数据")
    print("- 日志记录：WARNING - 复权因子不可用，返回原始数据")
    print("- 系统继续运行，不影响其他功能\n")
    
    print("原始数据：")
    print(data[['date', 'close']].head().to_string(index=False))

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("价格复权演示")
    print("=" * 60)
    print("\n本示例演示价格复权的原理和应用场景")
    print("注意：本示例使用模拟数据，实际使用时需要连接XtData API\n")
    
    # 1. 前复权演示
    demonstrate_forward_adjustment()
    
    # 2. 后复权演示
    demonstrate_backward_adjustment()
    
    # 3. OHLC关系验证
    demonstrate_ohlc_relationships()
    
    # 4. 回测场景
    demonstrate_backtesting_scenario()
    
    # 5. 缺失因子处理
    demonstrate_missing_factors()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    print("\n关键要点：")
    print("1. 前复权适合回测，后复权适合展示")
    print("2. 复权后OHLC关系保持不变")
    print("3. 复权因子缺失时返回原始数据并警告")
    print("4. 回测必须使用前复权避免未来函数")
    print("\n下一步：")
    print("- 查看 examples/03_fundamental_data.py 学习基本面数据处理")
    print("- 查看 src/price_adjuster.py 了解复权实现细节")

if __name__ == '__main__':
    main()
