"""
Day 4: Pandas时间序列处理
学习目标: 掌握K线数据处理和技术指标计算
预计时间: 5-6小时
"""

import pandas as pd
import numpy as np
from datetime import datetime

# === 理论部分 ===
# 时间序列是量化交易的核心数据结构
# resample: K线周期转换（1分钟->5分钟->小时->日线）
# rolling: 移动窗口计算（均线、标准差等）
# shift/diff: 时间偏移和差分计算（涨跌幅）

# === 练习1: resample周期转换 ===
def exercise_1_resample():
    """练习1: 使用resample将1分钟K线转换为5分钟和小时K线"""
    print("=" * 60)
    print("练习1: resample周期转换")
    print("=" * 60)
    
    # 生成模拟的1分钟K线数据（240根，代表一个交易日 9:30-15:00）
    # 注意：实际交易时间是4小时（240分钟），中午休市
    dates = pd.date_range('2024-01-15 09:30', periods=240, freq='1min')
    
    # 生成OHLCV数据
    np.random.seed(42)  # 固定随机种子，保证结果可复现
    base_price = 100.0
    
    # 模拟价格随机游走
    price_changes = np.random.randn(240) * 0.5
    close_prices = base_price + np.cumsum(price_changes)
    
    # 生成OHLC数据
    df_1min = pd.DataFrame({
        'open': close_prices + np.random.randn(240) * 0.1,
        'high': close_prices + np.abs(np.random.randn(240)) * 0.3,
        'low': close_prices - np.abs(np.random.randn(240)) * 0.3,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 240)
    }, index=dates)
    
    # 确保 high >= close >= low 和 high >= open >= low
    df_1min['high'] = df_1min[['open', 'high', 'close']].max(axis=1)
    df_1min['low'] = df_1min[['open', 'low', 'close']].min(axis=1)
    
    print("\n1分钟K线数据（前5行）:")
    print(df_1min.head())
    print(f"\n总共 {len(df_1min)} 根1分钟K线")
    
    # 转换为5分钟K线
    # resample的聚合规则：
    # - open: 取第一个值（'first'）
    # - high: 取最大值（'max'）
    # - low: 取最小值（'min'）
    # - close: 取最后一个值（'last'）
    # - volume: 求和（'sum'）
    df_5min = df_1min.resample('5min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    
    print("\n5分钟K线数据（前5行）:")
    print(df_5min.head())
    print(f"\n总共 {len(df_5min)} 根5分钟K线")
    
    # 转换为1小时K线
    df_1h = df_1min.resample('1h').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    
    print("\n1小时K线数据:")
    print(df_1h)
    print(f"\n总共 {len(df_1h)} 根1小时K线")
    
    # 验证OHLCV聚合逻辑
    print("\n" + "=" * 60)
    print("验证聚合逻辑:")
    print("=" * 60)
    
    # 验证第一根5分钟K线
    first_5min_period = df_1min.iloc[:5]  # 前5根1分钟K线
    print("\n前5根1分钟K线（应该聚合成第一根5分钟K线）:")
    print(first_5min_period)
    
    print("\n第一根5分钟K线:")
    print(df_5min.iloc[0])
    
    # 手动验证
    expected_open = first_5min_period['open'].iloc[0]
    expected_high = first_5min_period['high'].max()
    expected_low = first_5min_period['low'].min()
    expected_close = first_5min_period['close'].iloc[-1]
    expected_volume = first_5min_period['volume'].sum()
    
    print("\n手动计算的预期值:")
    print(f"Open: {expected_open:.2f}")
    print(f"High: {expected_high:.2f}")
    print(f"Low: {expected_low:.2f}")
    print(f"Close: {expected_close:.2f}")
    print(f"Volume: {expected_volume}")
    
    # 验证是否匹配
    actual = df_5min.iloc[0]
    tolerance = 0.01
    assert abs(actual['open'] - expected_open) < tolerance, "Open价格不匹配"
    assert abs(actual['high'] - expected_high) < tolerance, "High价格不匹配"
    assert abs(actual['low'] - expected_low) < tolerance, "Low价格不匹配"
    assert abs(actual['close'] - expected_close) < tolerance, "Close价格不匹配"
    assert actual['volume'] == expected_volume, "Volume不匹配"
    
    print("\n✓ OHLCV聚合逻辑验证通过！")
    
    return df_1min, df_5min, df_1h


# === 练习2: rolling移动平均 ===
def exercise_2_rolling(df):
    """练习2: 使用rolling计算移动平均线"""
    print("\n" + "=" * 60)
    print("练习2: rolling移动平均")
    print("=" * 60)
    
    # 计算MA5和MA20
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    
    print("\n前25行数据（观察NaN值）:")
    print(df[['close', 'ma5', 'ma20']].head(25))
    
    print("\n观察要点:")
    print("1. MA5的前4行为NaN（因为窗口大小为5，需要至少5个数据点）")
    print("2. MA20的前19行为NaN（因为窗口大小为20，需要至少20个数据点）")
    print("3. 这是时间序列计算的边界情况，需要特别注意")
    
    # 统计NaN值
    ma5_nan_count = df['ma5'].isna().sum()
    ma20_nan_count = df['ma20'].isna().sum()
    
    print(f"\nMA5的NaN值数量: {ma5_nan_count} (预期: 4)")
    print(f"MA20的NaN值数量: {ma20_nan_count} (预期: 19)")
    
    assert ma5_nan_count == 4, "MA5的NaN值数量不正确"
    assert ma20_nan_count == 19, "MA20的NaN值数量不正确"
    
    print("\n✓ rolling移动平均计算正确！")
    
    # 可选：绘制图表（需要matplotlib）
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['close'], label='Close', linewidth=1)
        plt.plot(df.index, df['ma5'], label='MA5', linewidth=1.5)
        plt.plot(df.index, df['ma20'], label='MA20', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Close Price with MA5 and MA20')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig('data/day4_ma_chart.png', dpi=100)
        print("\n图表已保存到: data/day4_ma_chart.png")
        plt.close()
    except ImportError:
        print("\n提示: 安装matplotlib可以绘制图表 (pip install matplotlib)")
    
    return df


# === 练习3: shift/diff涨跌计算 ===
def exercise_3_shift_diff(df):
    """练习3: 使用shift/diff计算涨跌幅"""
    print("\n" + "=" * 60)
    print("练习3: shift/diff涨跌计算")
    print("=" * 60)
    
    # 使用shift获取前一根K线的收盘价
    df['prev_close'] = df['close'].shift(1)
    
    # 使用diff计算涨跌额
    df['change'] = df['close'].diff()
    
    # 使用pct_change计算涨跌幅（百分比）
    df['pct_change'] = df['close'].pct_change() * 100
    
    print("\n前10行数据:")
    print(df[['close', 'prev_close', 'change', 'pct_change']].head(10))
    
    print("\n观察要点:")
    print("1. 第一行的prev_close、change、pct_change都是NaN（因为没有前一根K线）")
    print("2. change = close - prev_close")
    print("3. pct_change = (close - prev_close) / prev_close * 100")
    
    # 验证计算正确性（从第二行开始）
    for i in range(1, min(10, len(df))):
        expected_prev = df['close'].iloc[i-1]
        expected_change = df['close'].iloc[i] - df['close'].iloc[i-1]
        expected_pct = (df['close'].iloc[i] - df['close'].iloc[i-1]) / df['close'].iloc[i-1] * 100
        
        actual_prev = df['prev_close'].iloc[i]
        actual_change = df['change'].iloc[i]
        actual_pct = df['pct_change'].iloc[i]
        
        tolerance = 0.01
        assert abs(actual_prev - expected_prev) < tolerance, f"第{i}行prev_close不正确"
        assert abs(actual_change - expected_change) < tolerance, f"第{i}行change不正确"
        assert abs(actual_pct - expected_pct) < tolerance, f"第{i}行pct_change不正确"
    
    print("\n✓ shift/diff涨跌计算验证通过！")
    
    # 统计涨跌情况
    up_count = (df['change'] > 0).sum()
    down_count = (df['change'] < 0).sum()
    flat_count = (df['change'] == 0).sum()
    
    print(f"\n涨跌统计:")
    print(f"上涨: {up_count} 根K线")
    print(f"下跌: {down_count} 根K线")
    print(f"平盘: {flat_count} 根K线")
    print(f"最大涨幅: {df['pct_change'].max():.2f}%")
    print(f"最大跌幅: {df['pct_change'].min():.2f}%")
    
    return df


# === 练习4: 边界情况处理 ===
def exercise_4_boundary_cases():
    """练习4: 测试并安全处理边界情况"""
    print("\n" + "=" * 60)
    print("练习4: 边界情况处理")
    print("=" * 60)
    
    # 测试1: rolling在数据不足时的行为
    print("\n测试1: rolling在数据不足时的行为")
    print("-" * 60)
    
    small_df = pd.DataFrame({
        'close': [100, 101, 102]
    })
    
    print("原始数据（只有3行）:")
    print(small_df)
    
    small_df['ma5'] = small_df['close'].rolling(window=5).mean()
    
    print("\n计算MA5后:")
    print(small_df)
    print("结论: 当数据不足5行时，所有MA5值都是NaN")
    
    # 测试2: shift在第一行的行为
    print("\n测试2: shift在第一行的行为")
    print("-" * 60)
    
    small_df['prev_close'] = small_df['close'].shift(1)
    
    print("使用shift(1)后:")
    print(small_df)
    print("结论: 第一行的prev_close是NaN（因为没有前一行）")
    
    # 测试3: 编写安全处理函数
    print("\n测试3: 编写安全处理函数")
    print("-" * 60)
    
    def safe_rolling_mean(series, window):
        """安全计算移动平均，处理数据不足的情况"""
        if len(series) < window:
            print(f"警告: 数据长度({len(series)})小于窗口大小({window})，返回None")
            return None
        return series.rolling(window=window).mean()
    
    def safe_pct_change(series):
        """安全计算涨跌幅，处理第一行NaN的情况"""
        pct = series.pct_change() * 100
        # 可以选择填充第一行为0，或者保持NaN
        # pct.fillna(0, inplace=True)  # 如果需要填充
        return pct
    
    # 测试安全函数
    test_data = pd.Series([100, 102, 101, 103, 105])
    
    print("\n测试数据:")
    print(test_data)
    
    # 测试数据不足的情况
    result = safe_rolling_mean(test_data[:3], window=5)
    print(f"\n数据不足时的MA5: {result}")
    
    # 测试数据充足的情况
    result = safe_rolling_mean(test_data, window=3)
    print(f"\n数据充足时的MA3:")
    print(result)
    
    # 测试涨跌幅计算
    pct = safe_pct_change(test_data)
    print(f"\n涨跌幅计算:")
    print(pct)
    
    print("\n✓ 边界情况处理函数编写完成！")
    
    # 返回安全处理函数供后续使用
    return safe_rolling_mean, safe_pct_change


# === 验收检查 ===
def verify():
    """运行所有练习并验收"""
    print("\n" + "=" * 60)
    print("Day 4: Pandas时间序列处理 - 验收检查")
    print("=" * 60)
    
    try:
        # 练习1: resample
        df_1min, df_5min, df_1h = exercise_1_resample()
        print("\n✓ 练习1完成: resample周期转换")
        
        # 练习2: rolling
        df_with_ma = exercise_2_rolling(df_1min.copy())
        print("\n✓ 练习2完成: rolling移动平均")
        
        # 练习3: shift/diff
        df_with_change = exercise_3_shift_diff(df_1min.copy())
        print("\n✓ 练习3完成: shift/diff涨跌计算")
        
        # 练习4: 边界情况
        safe_rolling_mean, safe_pct_change = exercise_4_boundary_cases()
        print("\n✓ 练习4完成: 边界情况处理")
        
        print("\n" + "=" * 60)
        print("所有练习完成！Day 4验收通过！")
        print("=" * 60)
        
        print("\n学习总结:")
        print("1. resample: K线周期转换的核心方法")
        print("2. rolling: 计算移动平均等技术指标")
        print("3. shift/diff: 计算涨跌幅的标准方法")
        print("4. 边界情况: 时间序列计算中必须注意的NaN处理")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 验收失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    verify()


"""
摘要：创建了练习文件exercises/week1/day4_timeseries.py，其中包含全面的Pandas时间序列练习，涵盖以下内容：
✓ 子任务4.1 - 重采样练习
• 生成了240个1分钟K线柱（模拟一个交易日）
• 使用resample('5min')转换为5分钟K线
• 使用resample('1h')转换为1小时K线
• 验证OHLCV聚合逻辑正确
✓ 子任务4.2 - 滚动移动平均
• 计算了MA5（5周期移动平均线）
• 计算了MA20（20周期移动平均线）
• 观察到前4行（MA5）和前19行（MA20）存在NaN值
• 包含可选的图表绘制功能
✓ 子任务4.3 - 位移/差值价格变动计算
• 使用shift(1)获取前一根K线数据
• 使用diff()计算价格变动量
• 使用pct_change()计算百分比变动
• 通过断言验证计算正确性
✓ 子任务4.4 - 边界情况处理
• 测试了数据不足时的滚动行为
• 测试了首行的位移行为
• 创建了安全处理函数：safe_rolling_mean()和safe_pct_change()

所有练习都包含详细注释和验证检查，执行时均能成功运行。该代码验证了需求文档中规定的4.1、4.2、4.3和4.4项要求。


## Summary

Created `exercises/week1/day4_timeseries.py` with comprehensive Pandas time series exercises covering:

**✓ Subtask 4.1 - Resample Practice**

-   Generated 240 1-minute K-line bars (simulating a trading day)
-   Converted to 5-minute K-lines using `resample('5min')`
-   Converted to 1-hour K-lines using `resample('1h')`
-   Verified OHLCV aggregation logic is correct

**✓ Subtask 4.2 - Rolling Moving Average**

-   Calculated MA5 (5-period moving average)
-   Calculated MA20 (20-period moving average)
-   Observed NaN values in the first 4 rows (MA5) and first 19 rows (MA20)
-   Included optional chart plotting functionality

**✓ Subtask 4.3 - Shift/Diff Price Change Calculation**

-   Used `shift(1)` to get previous K-line data
-   Used `diff()` to calculate price change amount
-   Used `pct_change()` to calculate percentage change
-   Verified calculation correctness with assertions

**✓ Subtask 4.4 - Boundary Case Handling**

-   Tested rolling behavior with insufficient data
-   Tested shift behavior on the first row
-   Created safe handling functions: `safe_rolling_mean()` and `safe_pct_change()`

All exercises include detailed comments, verification checks, and pass successfully when executed. The code validates Requirements 4.1, 4.2, 4.3, and 4.4 as specified in the requirements document.
"""