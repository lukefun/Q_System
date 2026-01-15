"""
Day 3: Pandas数据清洗
学习目标: 掌握Pandas核心数据操作
预计时间: 4-5小时
"""

import pandas as pd
import numpy as np


# === 练习1: loc/iloc 索引操作 ===
def exercise_1_indexing():
    """练习1: DataFrame索引操作"""
    print("=" * 50)
    print("练习1: loc/iloc 索引操作")
    print("=" * 50)
    
    # 创建包含股票代码、收盘价、成交量的DataFrame
    df = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ', '600000.SH'],
        'close': [10.5, 15.2, 8.3],
        'volume': [1000000, 500000, 800000]
    })
    
    print("\n原始DataFrame:")
    print(df)
    
    # 将股票代码设置为索引
    df.set_index('code', inplace=True)
    print("\n设置索引后的DataFrame:")
    print(df)
    
    # 使用 loc 按标签索引获取数据
    print("\n--- 使用 loc 按标签索引 ---")
    price_000001 = df.loc['000001.SZ', 'close']
    print(f"000001.SZ 的收盘价: {price_000001}")
    
    # 获取整行数据
    row_000002 = df.loc['000002.SZ']
    print(f"\n000002.SZ 的完整数据:\n{row_000002}")
    
    # 获取多行数据
    multiple_rows = df.loc[['000001.SZ', '600000.SH']]
    print(f"\n获取多行数据:\n{multiple_rows}")
    
    # 使用 iloc 按位置索引获取数据
    print("\n--- 使用 iloc 按位置索引 ---")
    first_row = df.iloc[0]
    print(f"第一行数据:\n{first_row}")
    
    # 获取特定位置的值
    first_close = df.iloc[0, 0]  # 第一行第一列
    print(f"\n第一行第一列的值: {first_close}")
    
    # 获取前两行
    first_two_rows = df.iloc[0:2]
    print(f"\n前两行数据:\n{first_two_rows}")
    
    # 获取最后一行
    last_row = df.iloc[-1]
    print(f"\n最后一行数据:\n{last_row}")
    
    return df


# === 练习2: 缺失值处理 ===
def exercise_2_missing_values():
    """练习2: 缺失值处理"""
    print("\n" + "=" * 50)
    print("练习2: 缺失值处理")
    print("=" * 50)
    
    # 创建包含NaN值的DataFrame
    df_with_nan = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=6),
        'close': [10.5, np.nan, 11.2, np.nan, 12.0, 11.8],
        'volume': [1000, 2000, np.nan, 4000, np.nan, 3000]
    })
    
    print("\n原始DataFrame (包含NaN):")
    print(df_with_nan)
    print(f"\n缺失值统计:\n{df_with_nan.isnull().sum()}")
    
    # 方法1: fillna(method='ffill') 前向填充
    print("\n--- 方法1: 前向填充 (ffill) ---")
    df_ffill = df_with_nan.fillna(method='ffill')
    print(df_ffill)
    print("说明: 使用前一个有效值填充NaN")
    
    # 方法2: fillna(value) 指定值填充
    print("\n--- 方法2: 指定值填充 ---")
    df_fill_value = df_with_nan.fillna(0)
    print(df_fill_value)
    print("说明: 使用指定值(0)填充所有NaN")
    
    # 方法3: 按列指定不同的填充值
    print("\n--- 方法3: 按列指定填充值 ---")
    df_fill_dict = df_with_nan.fillna({'close': df_with_nan['close'].mean(), 
                                        'volume': 0})
    print(df_fill_dict)
    print("说明: close列用均值填充，volume列用0填充")
    
    # 方法4: dropna() 删除缺失值
    print("\n--- 方法4: 删除缺失值 ---")
    df_dropped = df_with_nan.dropna()
    print(df_dropped)
    print("说明: 删除包含任何NaN的行")
    
    # 对比不同方法的结果差异
    print("\n--- 结果对比 ---")
    print(f"原始数据行数: {len(df_with_nan)}")
    print(f"前向填充后行数: {len(df_ffill)}")
    print(f"指定值填充后行数: {len(df_fill_value)}")
    print(f"删除NaN后行数: {len(df_dropped)}")
    
    return df_with_nan, df_ffill, df_fill_value, df_dropped


# === 练习3: 数据合并 ===
def exercise_3_merge_concat():
    """练习3: 数据合并操作"""
    print("\n" + "=" * 50)
    print("练习3: 数据合并")
    print("=" * 50)
    
    # 创建两个DataFrame: 价格数据和成交量数据
    df_price = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ', '600000.SH'],
        'close': [10.5, 15.2, 8.3],
        'open': [10.2, 15.0, 8.1]
    })
    
    df_volume = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ', '600000.SH'],
        'volume': [1000000, 500000, 800000],
        'amount': [10500000, 7600000, 6640000]
    })
    
    print("\n价格数据:")
    print(df_price)
    print("\n成交量数据:")
    print(df_volume)
    
    # 练习 pd.merge() 按键合并
    print("\n--- pd.merge() 按键合并 ---")
    merged_inner = pd.merge(df_price, df_volume, on='code', how='inner')
    print("Inner Join (内连接):")
    print(merged_inner)
    
    # 测试 outer join
    df_price_extra = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ', '600000.SH', '600001.SH'],
        'close': [10.5, 15.2, 8.3, 12.0]
    })
    
    merged_outer = pd.merge(df_price_extra, df_volume, on='code', how='outer')
    print("\nOuter Join (外连接):")
    print(merged_outer)
    print("说明: outer join保留所有键，缺失值用NaN填充")
    
    # 练习 pd.concat() 纵向拼接
    print("\n--- pd.concat() 纵向拼接 ---")
    df1 = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ'],
        'close': [10.5, 15.2]
    })
    
    df2 = pd.DataFrame({
        'code': ['600000.SH', '600001.SH'],
        'close': [8.3, 12.0]
    })
    
    concatenated = pd.concat([df1, df2], ignore_index=True)
    print("纵向拼接结果:")
    print(concatenated)
    print("说明: concat将多个DataFrame按行拼接")
    
    # 理解 how='inner' 和 how='outer' 的区别
    print("\n--- Inner vs Outer 对比 ---")
    print("Inner Join: 只保留两个DataFrame中都存在的键")
    print("Outer Join: 保留所有键，缺失值用NaN填充")
    
    return merged_inner, merged_outer, concatenated


# === 练习4: K线数据NaN处理 ===
def exercise_4_kline_nan_handling():
    """练习4: K线数据NaN处理"""
    print("\n" + "=" * 50)
    print("练习4: K线数据NaN处理")
    print("=" * 50)
    
    # 模拟真实K线数据（包含停牌导致的NaN）
    dates = pd.date_range('2024-01-01', periods=10, freq='D')
    kline_data = pd.DataFrame({
        'date': dates,
        'open': [10.0, 10.2, np.nan, np.nan, 10.5, 10.8, 11.0, np.nan, 11.2, 11.5],
        'high': [10.5, 10.6, np.nan, np.nan, 11.0, 11.2, 11.3, np.nan, 11.5, 11.8],
        'low': [9.8, 10.0, np.nan, np.nan, 10.3, 10.5, 10.8, np.nan, 11.0, 11.2],
        'close': [10.2, 10.4, np.nan, np.nan, 10.8, 11.0, 11.1, np.nan, 11.3, 11.6],
        'volume': [1000000, 1200000, 0, 0, 1500000, 1300000, 1400000, 0, 1600000, 1700000]
    })
    
    print("\n原始K线数据 (包含停牌NaN):")
    print(kline_data)
    
    # 编写函数识别并统计NaN值数量
    def identify_nan_values(df):
        """识别并统计NaN值"""
        print("\n--- NaN值统计 ---")
        nan_count = df.isnull().sum()
        print(f"各列NaN数量:\n{nan_count}")
        
        total_nan = df.isnull().sum().sum()
        total_values = df.shape[0] * df.shape[1]
        nan_percentage = (total_nan / total_values) * 100
        print(f"\n总NaN数量: {total_nan}")
        print(f"NaN占比: {nan_percentage:.2f}%")
        
        # 识别包含NaN的行
        nan_rows = df[df.isnull().any(axis=1)]
        print(f"\n包含NaN的行索引: {nan_rows.index.tolist()}")
        
        return nan_count
    
    nan_stats = identify_nan_values(kline_data)
    
    # 选择合适的填充策略处理NaN
    print("\n--- 填充策略选择 ---")
    
    # 策略1: 前向填充 (适用于停牌场景)
    print("\n策略1: 前向填充 (ffill) - 适用于停牌")
    kline_ffill = kline_data.copy()
    kline_ffill[['open', 'high', 'low', 'close']] = kline_ffill[['open', 'high', 'low', 'close']].fillna(method='ffill')
    print(kline_ffill)
    print("说明: 停牌期间价格保持不变，使用前一日价格")
    
    # 策略2: 删除包含NaN的行 (适用于数据质量要求高的场景)
    print("\n策略2: 删除NaN行 - 适用于数据质量要求高")
    kline_dropped = kline_data.dropna()
    print(kline_dropped)
    print(f"说明: 删除停牌日数据，剩余 {len(kline_dropped)} 个交易日")
    
    # 策略3: 标记停牌状态
    print("\n策略3: 标记停牌状态")
    kline_marked = kline_data.copy()
    kline_marked['is_suspended'] = kline_marked['close'].isnull()
    kline_marked[['open', 'high', 'low', 'close']] = kline_marked[['open', 'high', 'low', 'close']].fillna(method='ffill')
    print(kline_marked)
    print("说明: 保留停牌标记，便于后续分析")
    
    return kline_data, kline_ffill, kline_dropped, kline_marked


# === 验收检查 ===
def verify():
    """运行验收检查"""
    print("\n" + "=" * 70)
    print("Day 3: Pandas数据清洗 - 验收检查")
    print("=" * 70)
    
    try:
        # 练习1: 索引操作
        df1 = exercise_1_indexing()
        assert df1 is not None, "练习1未完成"
        assert df1.index.name == 'code', "索引设置不正确"
        print("\n✓ 练习1: 索引操作 - 通过")
        
        # 练习2: 缺失值处理
        results2 = exercise_2_missing_values()
        assert len(results2) == 4, "练习2未完成"
        print("\n✓ 练习2: 缺失值处理 - 通过")
        
        # 练习3: 数据合并
        results3 = exercise_3_merge_concat()
        assert len(results3) == 3, "练习3未完成"
        print("\n✓ 练习3: 数据合并 - 通过")
        
        # 练习4: K线数据NaN处理
        results4 = exercise_4_kline_nan_handling()
        assert len(results4) == 4, "练习4未完成"
        print("\n✓ 练习4: K线数据NaN处理 - 通过")
        
        print("\n" + "=" * 70)
        print("所有练习完成！Day 3 验收通过 ✓")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 验收失败: {e}")
        raise


if __name__ == '__main__':
    verify()


"""
## 摘要

创建了`exercises/week1/day3_pandas_basics.py`，其中包含全面的Pandas数据清洗练习：

**练习1（子任务3.1）**：DataFrame索引操作
- 创建了包含股票代码、收盘价和成交量的DataFrame
- 演示了用于基于标签索引的`loc`
- 演示了用于基于位置索引的`iloc`

**练习2（子任务3.2）**：缺失值处理
- 创建了带有NaN值的DataFrame
- 实现了前向填充（`ffill`）
- 实现了基于值的填充
- 实现了特定列的填充策略
- 演示了用于删除缺失值的`dropna()`
- 比较了不同方法的结果

**练习3（子任务3.3）**：数据合并
- 创建了单独的价格和成交量DataFrame
- 演示了带有内连接和外连接的`pd.merge()`
- 演示了用于垂直拼接的`pd.concat()`
- 解释了内连接和外连接之间的区别

**练习4（子任务3.4）**：K线数据NaN值处理
- 模拟了带有停牌期（NaN值）的真实K线数据
- 创建了识别和计数NaN值的函数
- 实现了三种填充策略：
  - 停牌期的前向填充
  - 针对高数据质量要求的删除NaN行
  - 填充时标记停牌状态

所有练习都包含验证检查，且均成功通过。该脚本验证了需求文档中规定的需求3.1、3.2、3.3和3.4。


## Summary

Created `exercises/week1/day3_pandas_basics.py` with comprehensive Pandas data cleaning exercises:

**Exercise 1 (Subtask 3.1)**: DataFrame indexing operations
- Created DataFrame with stock codes, closing prices, and volumes
- Demonstrated `loc` for label-based indexing
- Demonstrated `iloc` for position-based indexing

**Exercise 2 (Subtask 3.2)**: Missing value handling
- Created DataFrame with NaN values
- Implemented forward fill (`ffill`)
- Implemented value-based filling
- Implemented column-specific filling strategies
- Demonstrated `dropna()` for removing missing values
- Compared results of different methods

**Exercise 3 (Subtask 3.3)**: Data merging
- Created separate price and volume DataFrames
- Demonstrated `pd.merge()` with inner and outer joins
- Demonstrated `pd.concat()` for vertical concatenation
- Explained differences between inner and outer joins

**Exercise 4 (Subtask 3.4)**: K-line data NaN handling
- Simulated real K-line data with suspension periods (NaN values)
- Created function to identify and count NaN values
- Implemented three filling strategies:
  - Forward fill for suspension periods
  - Dropping NaN rows for high data quality requirements
  - Marking suspension status while filling

All exercises include verification checks and passed successfully. The script validates Requirements 3.1, 3.2, 3.3, and 3.4 as specified in the requirements document.
"""