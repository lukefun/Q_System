"""
Day 7: 周复盘与代码重构 - 验证脚本
学习目标: 验证整理后的函数库可正确导入和使用
"""

import pandas as pd
import numpy as np
from utils.data_utils import (
    safe_loc_indexing,
    fill_missing_forward,
    fill_missing_value,
    identify_missing_values,
    merge_dataframes,
    concat_dataframes,
    resample_ohlcv,
    calculate_moving_average,
    safe_rolling_mean,
    calculate_price_change,
    calculate_pct_change,
    safe_pct_change,
    add_technical_indicators,
    handle_kline_suspension
)


def test_indexing_functions():
    """测试索引相关函数"""
    print("=" * 60)
    print("测试1: 索引操作函数")
    print("=" * 60)
    
    df = pd.DataFrame({
        'price': [10.5, 15.2, 8.3],
        'volume': [1000, 500, 800]
    }, index=['000001.SZ', '000002.SZ', '600000.SH'])
    
    price = safe_loc_indexing(df, '000001.SZ', 'price')
    print(f"000001.SZ的价格: {price}")
    assert price == 10.5, "索引函数测试失败"
    
    none_result = safe_loc_indexing(df, 'INVALID', 'price')
    print(f"无效索引返回: {none_result}")
    assert none_result is None, "无效索引应返回None"
    
    print("✓ 索引操作函数测试通过\n")


def test_missing_value_functions():
    """测试缺失值处理函数"""
    print("=" * 60)
    print("测试2: 缺失值处理函数")
    print("=" * 60)
    
    df = pd.DataFrame({
        'price': [10.0, np.nan, 12.0, np.nan, 14.0],
        'volume': [1000, 2000, np.nan, 4000, 5000]
    })
    
    print("原始数据:")
    print(df)
    
    df_ffill = fill_missing_forward(df)
    print("\n前向填充后:")
    print(df_ffill)
    assert df_ffill['price'].iloc[1] == 10.0, "前向填充失败"
    
    df_filled = fill_missing_value(df, fill_value=0)
    print("\n用0填充后:")
    print(df_filled)
    assert df_filled['price'].iloc[1] == 0, "指定值填充失败"
    
    nan_info = identify_missing_values(df)
    print(f"\nNaN统计: 总计{nan_info['total_nan']}个, 占比{nan_info['nan_percentage']:.1f}%")
    assert nan_info['total_nan'] == 3, "NaN统计错误"
    
    print("✓ 缺失值处理函数测试通过\n")


def test_merge_functions():
    """测试数据合并函数"""
    print("=" * 60)
    print("测试3: 数据合并函数")
    print("=" * 60)
    
    df1 = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ'],
        'price': [10.5, 15.2]
    })
    
    df2 = pd.DataFrame({
        'code': ['000001.SZ', '000002.SZ'],
        'volume': [1000, 500]
    })
    
    merged = merge_dataframes(df1, df2, on='code')
    print("合并后的数据:")
    print(merged)
    assert len(merged) == 2, "合并失败"
    assert 'price' in merged.columns and 'volume' in merged.columns, "列缺失"
    
    df3 = pd.DataFrame({'price': [20.0, 25.0]})
    concatenated = concat_dataframes([df1[['price']], df3])
    print("\n拼接后的数据:")
    print(concatenated)
    assert len(concatenated) == 4, "拼接失败"
    
    print("✓ 数据合并函数测试通过\n")


def test_timeseries_functions():
    """测试时间序列函数"""
    print("=" * 60)
    print("测试4: 时间序列处理函数")
    print("=" * 60)
    
    dates = pd.date_range('2024-01-15 09:30', periods=50, freq='1min')
    df = pd.DataFrame({
        'open': np.random.randn(50).cumsum() + 100,
        'high': np.random.randn(50).cumsum() + 101,
        'low': np.random.randn(50).cumsum() + 99,
        'close': np.random.randn(50).cumsum() + 100,
        'volume': np.random.randint(1000, 5000, 50)
    }, index=dates)
    
    df_5min = resample_ohlcv(df, '5min')
    print(f"1分钟K线数量: {len(df)}")
    print(f"5分钟K线数量: {len(df_5min)}")
    assert len(df_5min) == 10, "重采样失败"
    
    ma5 = calculate_moving_average(df['close'], window=5)
    print(f"\nMA5前10个值:")
    print(ma5.head(10))
    assert ma5.iloc[:4].isna().all(), "MA5前4个值应为NaN"
    assert not ma5.iloc[4:].isna().any(), "MA5第5个值后不应有NaN"
    
    safe_ma = safe_rolling_mean(pd.Series([1, 2, 3]), window=5)
    print(f"\n数据不足时的安全MA: {safe_ma}")
    assert safe_ma is None, "数据不足应返回None"
    
    change = calculate_price_change(df['close'])
    pct = calculate_pct_change(df['close'])
    print(f"\n价格变动前5个值:")
    print(change.head())
    print(f"\n百分比变动前5个值:")
    print(pct.head())
    assert change.iloc[0] is np.nan or pd.isna(change.iloc[0]), "第一个变动值应为NaN"
    
    print("✓ 时间序列处理函数测试通过\n")


def test_technical_indicators():
    """测试技术指标函数"""
    print("=" * 60)
    print("测试5: 技术指标函数")
    print("=" * 60)
    
    df = pd.DataFrame({
        'close': np.random.randn(30).cumsum() + 100
    })
    
    df_with_indicators = add_technical_indicators(df, ma_windows=[5, 10])
    print("添加技术指标后的列:")
    print(df_with_indicators.columns.tolist())
    
    assert 'ma5' in df_with_indicators.columns, "缺少MA5"
    assert 'ma10' in df_with_indicators.columns, "缺少MA10"
    assert 'prev_close' in df_with_indicators.columns, "缺少prev_close"
    assert 'change' in df_with_indicators.columns, "缺少change"
    assert 'pct_change' in df_with_indicators.columns, "缺少pct_change"
    
    print("✓ 技术指标函数测试通过\n")


def test_suspension_handling():
    """测试停牌处理函数"""
    print("=" * 60)
    print("测试6: 停牌处理函数")
    print("=" * 60)
    
    df = pd.DataFrame({
        'open': [10.0, np.nan, np.nan, 10.5],
        'high': [10.5, np.nan, np.nan, 11.0],
        'low': [9.8, np.nan, np.nan, 10.0],
        'close': [10.2, np.nan, np.nan, 10.8]
    })
    
    print("原始数据（包含停牌）:")
    print(df)
    
    df_handled = handle_kline_suspension(df, mark_suspension=True)
    print("\n处理后的数据:")
    print(df_handled)
    
    assert 'is_suspended' in df_handled.columns, "缺少停牌标记"
    assert df_handled['is_suspended'].iloc[1] == True, "停牌标记错误"
    assert df_handled['close'].iloc[1] == 10.2, "停牌期价格填充错误"
    
    print("✓ 停牌处理函数测试通过\n")


def verify_all():
    """运行所有验证测试"""
    print("\n" + "=" * 60)
    print("Day 7: 周复盘与代码重构 - 完整验证")
    print("=" * 60 + "\n")
    
    try:
        test_indexing_functions()
        test_missing_value_functions()
        test_merge_functions()
        test_timeseries_functions()
        test_technical_indicators()
        test_suspension_handling()
        
        print("=" * 60)
        print("所有测试通过！函数库验证成功！✓")
        print("=" * 60)
        print("\n总结:")
        print("✓ 数据索引函数正常工作")
        print("✓ 缺失值处理函数正常工作")
        print("✓ 数据合并函数正常工作")
        print("✓ 时间序列处理函数正常工作")
        print("✓ 技术指标计算函数正常工作")
        print("✓ 停牌处理函数正常工作")
        print("\n函数库已准备就绪，可用于后续量化开发！")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = verify_all()
    exit(0 if success else 1)
