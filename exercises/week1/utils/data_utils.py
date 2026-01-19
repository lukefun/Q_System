"""
Data Utilities for Quantitative Trading
数据处理工具库

This module provides utility functions for data cleaning, time series processing,
and technical indicator calculations commonly used in quantitative trading.
"""

import pandas as pd
import numpy as np


def safe_loc_indexing(df, label, column=None):
    """
    Safely retrieve data using label-based indexing.
    
    Args:
        df (pd.DataFrame): The DataFrame to index
        label: The row label to retrieve
        column (str, optional): The column name to retrieve. If None, returns entire row.
    
    Returns:
        The requested data, or None if label doesn't exist
    
    Example:
        >>> df = pd.DataFrame({'price': [10, 20]}, index=['A', 'B'])
        >>> safe_loc_indexing(df, 'A', 'price')
        10
    """
    try:
        if column:
            return df.loc[label, column]
        return df.loc[label]
    except KeyError:
        return None


def fill_missing_forward(df, columns=None):
    """
    Forward fill missing values in DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with potential missing values
        columns (list, optional): Specific columns to fill. If None, fills all columns.
    
    Returns:
        pd.DataFrame: DataFrame with forward-filled values
    
    Example:
        >>> df = pd.DataFrame({'price': [10, np.nan, 12]})
        >>> fill_missing_forward(df)
           price
        0   10.0
        1   10.0
        2   12.0
    """
    df_filled = df.copy()
    if columns:
        df_filled[columns] = df_filled[columns].fillna(method='ffill')
    else:
        df_filled = df_filled.fillna(method='ffill')
    return df_filled


def fill_missing_value(df, fill_value=0, columns=None):
    """
    Fill missing values with a specified value.
    
    Args:
        df (pd.DataFrame): DataFrame with potential missing values
        fill_value: Value to use for filling (default: 0)
        columns (list, optional): Specific columns to fill. If None, fills all columns.
    
    Returns:
        pd.DataFrame: DataFrame with filled values
    
    Example:
        >>> df = pd.DataFrame({'price': [10, np.nan, 12]})
        >>> fill_missing_value(df, fill_value=0)
           price
        0   10.0
        1    0.0
        2   12.0
    """
    df_filled = df.copy()
    if columns:
        df_filled[columns] = df_filled[columns].fillna(fill_value)
    else:
        df_filled = df_filled.fillna(fill_value)
    return df_filled


def identify_missing_values(df):
    """
    Identify and count missing values in DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
    
    Returns:
        dict: Dictionary containing:
            - 'nan_count': Series with NaN count per column
            - 'total_nan': Total number of NaN values
            - 'nan_percentage': Percentage of NaN values
            - 'nan_rows': List of row indices containing NaN
    
    Example:
        >>> df = pd.DataFrame({'a': [1, np.nan, 3], 'b': [4, 5, np.nan]})
        >>> result = identify_missing_values(df)
        >>> result['total_nan']
        2
    """
    nan_count = df.isnull().sum()
    total_nan = df.isnull().sum().sum()
    total_values = df.shape[0] * df.shape[1]
    nan_percentage = (total_nan / total_values) * 100 if total_values > 0 else 0
    
    nan_rows = df[df.isnull().any(axis=1)].index.tolist()
    
    return {
        'nan_count': nan_count,
        'total_nan': total_nan,
        'nan_percentage': nan_percentage,
        'nan_rows': nan_rows
    }


def merge_dataframes(df1, df2, on, how='inner'):
    """
    Merge two DataFrames on a common key.
    
    Args:
        df1 (pd.DataFrame): First DataFrame
        df2 (pd.DataFrame): Second DataFrame
        on (str or list): Column name(s) to merge on
        how (str): Type of merge ('inner', 'outer', 'left', 'right'). Default: 'inner'
    
    Returns:
        pd.DataFrame: Merged DataFrame
    
    Example:
        >>> df1 = pd.DataFrame({'code': ['A', 'B'], 'price': [10, 20]})
        >>> df2 = pd.DataFrame({'code': ['A', 'B'], 'volume': [100, 200]})
        >>> merge_dataframes(df1, df2, on='code')
          code  price  volume
        0    A     10     100
        1    B     20     200
    """
    return pd.merge(df1, df2, on=on, how=how)


def concat_dataframes(dfs, axis=0, ignore_index=True):
    """
    Concatenate multiple DataFrames.
    
    Args:
        dfs (list): List of DataFrames to concatenate
        axis (int): Axis to concatenate along (0=rows, 1=columns). Default: 0
        ignore_index (bool): Whether to reset index. Default: True
    
    Returns:
        pd.DataFrame: Concatenated DataFrame
    
    Example:
        >>> df1 = pd.DataFrame({'price': [10, 20]})
        >>> df2 = pd.DataFrame({'price': [30, 40]})
        >>> concat_dataframes([df1, df2])
           price
        0     10
        1     20
        2     30
        3     40
    """
    return pd.concat(dfs, axis=axis, ignore_index=ignore_index)


def resample_ohlcv(df, freq):
    """
    Resample OHLCV data to a different frequency.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV columns and datetime index
        freq (str): Target frequency ('5min', '1h', '1D', etc.)
    
    Returns:
        pd.DataFrame: Resampled DataFrame
    
    Example:
        >>> dates = pd.date_range('2024-01-01 09:30', periods=10, freq='1min')
        >>> df = pd.DataFrame({
        ...     'open': range(10), 'high': range(10), 
        ...     'low': range(10), 'close': range(10), 'volume': range(10)
        ... }, index=dates)
        >>> resample_ohlcv(df, '5min')
    """
    resampled = df.resample(freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    return resampled


def calculate_moving_average(series, window):
    """
    Calculate moving average for a series.
    
    Args:
        series (pd.Series): Price series
        window (int): Window size for moving average
    
    Returns:
        pd.Series: Moving average series
    
    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105])
        >>> calculate_moving_average(prices, window=3)
        0         NaN
        1         NaN
        2    101.000
        3    102.000
        4    103.000
        dtype: float64
    """
    return series.rolling(window=window).mean()


def safe_rolling_mean(series, window):
    """
    Safely calculate moving average with data validation.
    
    Args:
        series (pd.Series): Price series
        window (int): Window size for moving average
    
    Returns:
        pd.Series or None: Moving average series, or None if insufficient data
    
    Example:
        >>> prices = pd.Series([100, 102])
        >>> safe_rolling_mean(prices, window=5)
        None
    """
    if len(series) < window:
        return None
    return series.rolling(window=window).mean()


def calculate_price_change(series):
    """
    Calculate price change (difference from previous value).
    
    Args:
        series (pd.Series): Price series
    
    Returns:
        pd.Series: Price change series
    
    Example:
        >>> prices = pd.Series([100, 102, 101])
        >>> calculate_price_change(prices)
        0    NaN
        1    2.0
        2   -1.0
        dtype: float64
    """
    return series.diff()


def calculate_pct_change(series):
    """
    Calculate percentage change from previous value.
    
    Args:
        series (pd.Series): Price series
    
    Returns:
        pd.Series: Percentage change series (in percentage, not decimal)
    
    Example:
        >>> prices = pd.Series([100, 102, 101])
        >>> calculate_pct_change(prices)
        0    NaN
        1    2.0
        2   -0.98...
        dtype: float64
    """
    return series.pct_change() * 100


def safe_pct_change(series):
    """
    Safely calculate percentage change.
    
    Args:
        series (pd.Series): Price series
    
    Returns:
        pd.Series: Percentage change series
    
    Example:
        >>> prices = pd.Series([100, 102, 101])
        >>> safe_pct_change(prices)
        0    NaN
        1    2.0
        2   -0.98...
        dtype: float64
    """
    return series.pct_change() * 100


def add_technical_indicators(df, ma_windows=None):
    """
    Add common technical indicators to OHLCV DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with at least 'close' column
        ma_windows (list, optional): List of moving average windows. Default: [5, 20]
    
    Returns:
        pd.DataFrame: DataFrame with added technical indicators
    
    Example:
        >>> df = pd.DataFrame({'close': range(100, 125)})
        >>> df_with_indicators = add_technical_indicators(df, ma_windows=[5, 10])
        >>> 'ma5' in df_with_indicators.columns
        True
    """
    if ma_windows is None:
        ma_windows = [5, 20]
    
    df_result = df.copy()
    
    for window in ma_windows:
        df_result[f'ma{window}'] = calculate_moving_average(df_result['close'], window)
    
    df_result['prev_close'] = df_result['close'].shift(1)
    df_result['change'] = calculate_price_change(df_result['close'])
    df_result['pct_change'] = calculate_pct_change(df_result['close'])
    
    return df_result


def handle_kline_suspension(df, price_columns=None, mark_suspension=True):
    """
    Handle stock suspension periods in K-line data.
    
    Args:
        df (pd.DataFrame): K-line DataFrame with potential NaN values
        price_columns (list, optional): Price columns to fill. Default: ['open', 'high', 'low', 'close']
        mark_suspension (bool): Whether to add suspension flag column. Default: True
    
    Returns:
        pd.DataFrame: DataFrame with handled suspension periods
    
    Example:
        >>> df = pd.DataFrame({
        ...     'open': [10, np.nan, 12],
        ...     'close': [10.5, np.nan, 12.5]
        ... })
        >>> handle_kline_suspension(df, price_columns=['open', 'close'])
    """
    if price_columns is None:
        price_columns = ['open', 'high', 'low', 'close']
    
    df_result = df.copy()
    
    if mark_suspension:
        df_result['is_suspended'] = df_result[price_columns[0]].isnull()
    
    df_result[price_columns] = df_result[price_columns].fillna(method='ffill')
    
    return df_result
