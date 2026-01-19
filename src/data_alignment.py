"""
数据对齐工具模块

本模块提供跨数据源的数据对齐功能，确保时间点正确性，防止未来函数（前瞻偏差）。

核心原则：
1. 保守日期匹配：当存在日期不确定性时，使用较早的日期
2. 时间点正确性：确保在任何历史时点，只使用该时点之前公开的信息
3. 防止信息泄露：避免在回测中使用未来数据

未来函数防范原则：
- 价格数据：使用交易日期作为时间戳
- 基本面数据：使用公告日期（announce_date）而非报告期（report_date）
- 行业分类：使用生效日期（effective_date）进行时间点过滤
- 数据对齐：当多个数据源的日期不完全匹配时，使用保守策略（较早日期）

示例场景：
假设我们要在2024-01-15这一天进行交易决策，需要结合价格数据和基本面数据：
- 价格数据：可以使用2024-01-15当天的收盘价
- 基本面数据：只能使用announce_date <= 2024-01-15的财报数据
- 如果最新财报的announce_date是2024-01-10，则使用该财报
- 即使该财报的report_date是2023-12-31，我们也只能在2024-01-10之后使用它

作者：XtData金融数据工程系统
日期：2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def align_data_sources(
    price_data: pd.DataFrame,
    fundamental_data: Optional[pd.DataFrame] = None,
    industry_data: Optional[pd.DataFrame] = None,
    alignment_date: Optional[str] = None,
    method: str = 'conservative',
    validate: bool = True
) -> pd.DataFrame:
    """
    对齐多个数据源，确保时间点正确性，防止未来函数
    
    本函数实现保守的数据对齐策略，确保在任何历史时点，只使用该时点之前
    公开可用的信息。这是防止回测中出现前瞻偏差的关键步骤。
    
    对齐策略：
    1. 以价格数据的交易日期为基准
    2. 对于每个交易日，查找该日期之前最新的基本面数据（基于announce_date）
    3. 对于每个交易日，查找该日期之前有效的行业分类（基于effective_date）
    4. 当存在日期不确定性时，使用较早的日期以避免信息泄露
    
    Args:
        price_data: 价格数据DataFrame，必须包含'date'列和'stock_code'列
                   date格式：'YYYYMMDD'字符串
        fundamental_data: 基本面数据DataFrame（可选），必须包含'announce_date'列
                         如果提供，将与价格数据对齐
        industry_data: 行业分类数据DataFrame（可选），必须包含'effective_date'列
                      如果提供，将与价格数据对齐
        alignment_date: 对齐截止日期（可选），格式'YYYYMMDD'
                       如果提供，只使用该日期之前的数据
        method: 对齐方法，目前支持：
               - 'conservative': 保守策略，使用较早日期（默认）
               - 'forward_fill': 前向填充，使用最近的历史数据
        validate: 是否验证时间点正确性（默认True）
    
    Returns:
        对齐后的DataFrame，包含所有数据源的信息
        
    Raises:
        ValueError: 如果输入数据格式不正确或缺少必需列
        
    示例：
        >>> # 场景1：对齐价格和基本面数据
        >>> price_df = pd.DataFrame({
        ...     'stock_code': ['000001.SZ', '000001.SZ'],
        ...     'date': ['20240115', '20240116'],
        ...     'close': [10.5, 10.8]
        ... })
        >>> fundamental_df = pd.DataFrame({
        ...     'stock_code': ['000001.SZ'],
        ...     'report_date': ['20231231'],
        ...     'announce_date': ['20240110'],  # 关键：使用公告日期
        ...     'pe_ratio': [15.5]
        ... })
        >>> aligned = align_data_sources(price_df, fundamental_df)
        >>> # 结果：两个交易日都会使用2024-01-10公告的财报数据
        
        >>> # 场景2：指定截止日期
        >>> aligned = align_data_sources(
        ...     price_df, 
        ...     fundamental_df,
        ...     alignment_date='20240115'
        ... )
        >>> # 结果：只包含2024-01-15及之前的数据
    """
    # 验证输入数据
    if price_data is None or price_data.empty:
        raise ValueError("价格数据不能为空")
    
    if 'date' not in price_data.columns:
        raise ValueError("价格数据必须包含'date'列")
    
    if 'stock_code' not in price_data.columns:
        raise ValueError("价格数据必须包含'stock_code'列")
    
    # 复制数据以避免修改原始数据
    result = price_data.copy()
    
    # 如果指定了对齐截止日期，过滤价格数据
    if alignment_date is not None:
        result = result[result['date'] <= alignment_date].copy()
        logger.info(f"应用对齐截止日期过滤: {alignment_date}, 剩余记录数: {len(result)}")
    
    # 对齐基本面数据
    if fundamental_data is not None and not fundamental_data.empty:
        result = _align_fundamental_data(
            result, 
            fundamental_data, 
            alignment_date,
            method,
            validate
        )
    
    # 对齐行业数据
    if industry_data is not None and not industry_data.empty:
        result = _align_industry_data(
            result,
            industry_data,
            alignment_date,
            method,
            validate
        )
    
    # 验证时间点正确性
    if validate:
        _validate_time_point_correctness(result, alignment_date)
    
    return result


def _align_fundamental_data(
    price_data: pd.DataFrame,
    fundamental_data: pd.DataFrame,
    alignment_date: Optional[str],
    method: str,
    validate: bool
) -> pd.DataFrame:
    """
    对齐基本面数据到价格数据
    
    使用保守策略：对于每个交易日，使用该日期之前最新公告的财报数据
    
    Args:
        price_data: 价格数据
        fundamental_data: 基本面数据，必须包含'announce_date'列
        alignment_date: 对齐截止日期
        method: 对齐方法
        validate: 是否验证
        
    Returns:
        对齐后的数据
    """
    if 'announce_date' not in fundamental_data.columns:
        raise ValueError("基本面数据必须包含'announce_date'列（公告日期）")
    
    # 复制基本面数据
    fund_data = fundamental_data.copy()
    
    # 如果指定了对齐截止日期，过滤基本面数据
    if alignment_date is not None:
        fund_data = fund_data[fund_data['announce_date'] <= alignment_date].copy()
        logger.info(f"基本面数据应用截止日期过滤: {alignment_date}, 剩余记录数: {len(fund_data)}")
    
    # 按股票代码分组对齐
    result_list = []
    
    for stock_code in price_data['stock_code'].unique():
        # 获取该股票的价格数据
        stock_price = price_data[price_data['stock_code'] == stock_code].copy()
        
        # 获取该股票的基本面数据
        stock_fund = fund_data[fund_data['stock_code'] == stock_code].copy()
        
        if stock_fund.empty:
            logger.warning(f"股票 {stock_code} 没有基本面数据")
            result_list.append(stock_price)
            continue
        
        # 按公告日期排序
        stock_fund = stock_fund.sort_values('announce_date')
        
        # 对于每个交易日，找到该日期之前最新的基本面数据
        aligned_rows = []
        for _, price_row in stock_price.iterrows():
            trade_date = price_row['date']
            
            # 保守策略：只使用公告日期 <= 交易日期的数据
            available_fund = stock_fund[stock_fund['announce_date'] <= trade_date]
            
            if not available_fund.empty:
                # 使用最新的可用数据
                latest_fund = available_fund.iloc[-1]
                
                # 合并数据
                merged_row = price_row.copy()
                for col in stock_fund.columns:
                    if col not in ['stock_code', 'announce_date']:
                        merged_row[col] = latest_fund[col]
                    elif col == 'announce_date':
                        # 保留公告日期信息，用于验证
                        merged_row['fundamental_announce_date'] = latest_fund[col]
                
                aligned_rows.append(merged_row)
            else:
                # 该交易日之前没有可用的基本面数据
                logger.debug(f"股票 {stock_code} 在 {trade_date} 之前没有可用的基本面数据")
                aligned_rows.append(price_row)
        
        if aligned_rows:
            result_list.append(pd.DataFrame(aligned_rows))
    
    if result_list:
        result = pd.concat(result_list, ignore_index=True)
    else:
        result = price_data.copy()
    
    return result


def _align_industry_data(
    price_data: pd.DataFrame,
    industry_data: pd.DataFrame,
    alignment_date: Optional[str],
    method: str,
    validate: bool
) -> pd.DataFrame:
    """
    对齐行业分类数据到价格数据
    
    使用保守策略：对于每个交易日，使用该日期之前有效的行业分类
    
    Args:
        price_data: 价格数据
        industry_data: 行业数据，必须包含'effective_date'列
        alignment_date: 对齐截止日期
        method: 对齐方法
        validate: 是否验证
        
    Returns:
        对齐后的数据
    """
    if 'effective_date' not in industry_data.columns:
        raise ValueError("行业数据必须包含'effective_date'列（生效日期）")
    
    # 复制行业数据
    ind_data = industry_data.copy()
    
    # 如果指定了对齐截止日期，过滤行业数据
    if alignment_date is not None:
        ind_data = ind_data[ind_data['effective_date'] <= alignment_date].copy()
        logger.info(f"行业数据应用截止日期过滤: {alignment_date}, 剩余记录数: {len(ind_data)}")
    
    # 按股票代码分组对齐
    result_list = []
    
    for stock_code in price_data['stock_code'].unique():
        # 获取该股票的价格数据
        stock_price = price_data[price_data['stock_code'] == stock_code].copy()
        
        # 获取该股票的行业数据
        stock_ind = ind_data[ind_data['stock_code'] == stock_code].copy()
        
        if stock_ind.empty:
            logger.warning(f"股票 {stock_code} 没有行业分类数据")
            result_list.append(stock_price)
            continue
        
        # 按生效日期排序
        stock_ind = stock_ind.sort_values('effective_date')
        
        # 对于每个交易日，找到该日期之前有效的行业分类
        aligned_rows = []
        for _, price_row in stock_price.iterrows():
            trade_date = price_row['date']
            
            # 保守策略：只使用生效日期 <= 交易日期的数据
            available_ind = stock_ind[stock_ind['effective_date'] <= trade_date]
            
            if not available_ind.empty:
                # 使用最新的有效分类
                latest_ind = available_ind.iloc[-1]
                
                # 合并数据
                merged_row = price_row.copy()
                for col in stock_ind.columns:
                    if col not in ['stock_code', 'effective_date']:
                        merged_row[col] = latest_ind[col]
                    elif col == 'effective_date':
                        # 保留生效日期信息，用于验证
                        merged_row['industry_effective_date'] = latest_ind[col]
                
                aligned_rows.append(merged_row)
            else:
                # 该交易日之前没有有效的行业分类
                logger.debug(f"股票 {stock_code} 在 {trade_date} 之前没有有效的行业分类")
                aligned_rows.append(price_row)
        
        if aligned_rows:
            result_list.append(pd.DataFrame(aligned_rows))
    
    if result_list:
        result = pd.concat(result_list, ignore_index=True)
    else:
        result = price_data.copy()
    
    return result


def _validate_time_point_correctness(
    data: pd.DataFrame,
    alignment_date: Optional[str]
) -> None:
    """
    验证时间点正确性，确保没有使用未来数据
    
    检查项：
    1. 如果存在fundamental_announce_date列，验证 announce_date <= trade_date
    2. 如果存在industry_effective_date列，验证 effective_date <= trade_date
    3. 如果指定了alignment_date，验证所有日期 <= alignment_date
    
    Args:
        data: 对齐后的数据
        alignment_date: 对齐截止日期
        
    Raises:
        ValueError: 如果检测到时间点错误（使用了未来数据）
    """
    violations = []
    
    # 检查基本面数据的时间点正确性
    if 'fundamental_announce_date' in data.columns:
        invalid_rows = data[data['fundamental_announce_date'] > data['date']]
        if not invalid_rows.empty:
            violations.append(
                f"检测到 {len(invalid_rows)} 条记录使用了未来的基本面数据 "
                f"(announce_date > trade_date)"
            )
    
    # 检查行业数据的时间点正确性
    if 'industry_effective_date' in data.columns:
        invalid_rows = data[data['industry_effective_date'] > data['date']]
        if not invalid_rows.empty:
            violations.append(
                f"检测到 {len(invalid_rows)} 条记录使用了未来的行业分类 "
                f"(effective_date > trade_date)"
            )
    
    # 检查对齐截止日期
    if alignment_date is not None:
        invalid_rows = data[data['date'] > alignment_date]
        if not invalid_rows.empty:
            violations.append(
                f"检测到 {len(invalid_rows)} 条记录超出对齐截止日期 "
                f"(trade_date > alignment_date)"
            )
    
    if violations:
        error_msg = "时间点正确性验证失败:\n" + "\n".join(violations)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("时间点正确性验证通过")


def conservative_date_match(
    date1: str,
    date2: str,
    strategy: str = 'earlier'
) -> str:
    """
    保守日期匹配：当存在日期不确定性时，选择较早的日期
    
    这是防止未来函数的关键策略。当需要在两个日期之间做选择时，
    选择较早的日期可以确保不会使用未来信息。
    
    Args:
        date1: 第一个日期，格式'YYYYMMDD'
        date2: 第二个日期，格式'YYYYMMDD'
        strategy: 匹配策略
                 - 'earlier': 返回较早的日期（默认）
                 - 'later': 返回较晚的日期
                 
    Returns:
        选择的日期
        
    示例：
        >>> conservative_date_match('20240115', '20240110')
        '20240110'  # 返回较早的日期
    """
    if strategy == 'earlier':
        return min(date1, date2)
    elif strategy == 'later':
        return max(date1, date2)
    else:
        raise ValueError(f"不支持的策略: {strategy}")


def get_point_in_time_data(
    data: pd.DataFrame,
    as_of_date: str,
    date_column: str = 'date',
    time_reference_column: Optional[str] = None
) -> pd.DataFrame:
    """
    获取指定时点的数据，确保时间点正确性
    
    本函数实现时间点查询，确保只返回在指定日期之前公开可用的数据。
    这是防止未来函数的基础操作。
    
    Args:
        data: 数据DataFrame
        as_of_date: 查询时点，格式'YYYYMMDD'
        date_column: 日期列名（默认'date'）
        time_reference_column: 时间参考列名（可选）
                              如果提供，使用该列而非date_column进行过滤
                              例如：'announce_date'用于基本面数据
                                   'effective_date'用于行业数据
                                   
    Returns:
        指定时点之前的数据
        
    示例：
        >>> # 获取2024-01-15之前的价格数据
        >>> price_data = get_point_in_time_data(
        ...     all_price_data,
        ...     as_of_date='20240115',
        ...     date_column='date'
        ... )
        
        >>> # 获取2024-01-15之前公告的基本面数据
        >>> fundamental_data = get_point_in_time_data(
        ...     all_fundamental_data,
        ...     as_of_date='20240115',
        ...     time_reference_column='announce_date'
        ... )
    """
    if data is None or data.empty:
        return data
    
    # 确定使用哪个列进行过滤
    filter_column = time_reference_column if time_reference_column else date_column
    
    if filter_column not in data.columns:
        raise ValueError(f"数据中不存在列: {filter_column}")
    
    # 过滤数据
    result = data[data[filter_column] <= as_of_date].copy()
    
    logger.info(
        f"时间点查询: as_of_date={as_of_date}, "
        f"filter_column={filter_column}, "
        f"原始记录数={len(data)}, "
        f"过滤后记录数={len(result)}"
    )
    
    return result


def detect_lookahead_bias(
    data: pd.DataFrame,
    trade_date_column: str = 'date',
    reference_date_columns: Optional[List[str]] = None
) -> Dict[str, List[int]]:
    """
    检测数据中的前瞻偏差（未来函数）
    
    本函数扫描数据，查找可能存在的前瞻偏差，即在某个交易日使用了
    该日期之后才公开的信息。
    
    Args:
        data: 要检测的数据
        trade_date_column: 交易日期列名
        reference_date_columns: 参考日期列名列表（可选）
                               例如：['announce_date', 'effective_date']
                               如果不提供，自动检测常见的日期列
                               
    Returns:
        检测结果字典，键为列名，值为违规行索引列表
        
    示例：
        >>> violations = detect_lookahead_bias(
        ...     aligned_data,
        ...     trade_date_column='date',
        ...     reference_date_columns=['announce_date']
        ... )
        >>> if violations:
        ...     print(f"检测到前瞻偏差: {violations}")
    """
    if data is None or data.empty:
        return {}
    
    if trade_date_column not in data.columns:
        raise ValueError(f"数据中不存在交易日期列: {trade_date_column}")
    
    # 如果未指定参考日期列，自动检测
    if reference_date_columns is None:
        reference_date_columns = []
        common_date_columns = [
            'announce_date', 'effective_date', 'report_date',
            'fundamental_announce_date', 'industry_effective_date'
        ]
        for col in common_date_columns:
            if col in data.columns:
                reference_date_columns.append(col)
    
    violations = {}
    
    # 检查每个参考日期列
    for ref_col in reference_date_columns:
        if ref_col not in data.columns:
            logger.warning(f"参考日期列不存在: {ref_col}")
            continue
        
        # 查找违规行：参考日期 > 交易日期
        invalid_mask = data[ref_col] > data[trade_date_column]
        invalid_indices = data[invalid_mask].index.tolist()
        
        if invalid_indices:
            violations[ref_col] = invalid_indices
            logger.warning(
                f"检测到前瞻偏差: 列 {ref_col} 有 {len(invalid_indices)} 条违规记录"
            )
    
    if not violations:
        logger.info("未检测到前瞻偏差")
    
    return violations
