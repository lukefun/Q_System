"""
数据对齐属性测试

使用基于属性的测试验证数据对齐功能的通用正确性属性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st, assume
from src.data_alignment import (
    align_data_sources,
    conservative_date_match,
    get_point_in_time_data,
    detect_lookahead_bias
)
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 股票代码生成策略
@st.composite
def stock_code_strategy(draw):
    """生成有效的股票代码"""
    stock_num = draw(st.integers(min_value=0, max_value=999999))
    stock_num_str = f"{stock_num:06d}"
    market = draw(st.sampled_from(['SZ', 'SH']))
    return f"{stock_num_str}.{market}"


# 日期生成策略
@st.composite
def date_strategy(draw, min_days_ago=365, max_days_ago=30):
    """生成日期字符串，格式YYYYMMDD"""
    days_ago = draw(st.integers(min_value=max_days_ago, max_value=min_days_ago))
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y%m%d')


# 价格数据生成策略
@st.composite
def price_data_strategy(draw, num_stocks=None, num_days=None):
    """生成价格数据DataFrame"""
    if num_stocks is None:
        num_stocks = draw(st.integers(min_value=1, max_value=3))
    if num_days is None:
        num_days = draw(st.integers(min_value=5, max_value=20))
    
    stock_codes = [draw(stock_code_strategy()) for _ in range(num_stocks)]
    
    # 生成日期序列
    start_date = datetime.now() - timedelta(days=num_days + 10)
    dates = [
        (start_date + timedelta(days=i)).strftime('%Y%m%d')
        for i in range(num_days)
    ]
    
    data = []
    for stock_code in stock_codes:
        base_price = draw(st.floats(min_value=5.0, max_value=50.0))
        for date in dates:
            # 生成符合OHLC关系的价格
            low = base_price * draw(st.floats(min_value=0.95, max_value=0.99))
            high = base_price * draw(st.floats(min_value=1.01, max_value=1.05))
            open_price = draw(st.floats(min_value=low, max_value=high))
            close = draw(st.floats(min_value=low, max_value=high))
            volume = draw(st.integers(min_value=100000, max_value=5000000))
            
            data.append({
                'stock_code': stock_code,
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
            
            base_price = close
    
    return pd.DataFrame(data)


# 基本面数据生成策略
@st.composite
def fundamental_data_strategy(draw, stock_codes, date_range):
    """
    生成基本面数据DataFrame
    
    Args:
        stock_codes: 股票代码列表
        date_range: 日期范围元组 (start_date, end_date)
    """
    start_date_str, end_date_str = date_range
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    
    data = []
    for stock_code in stock_codes:
        # 为每个股票生成1-3条财报记录
        num_reports = draw(st.integers(min_value=1, max_value=3))
        
        for i in range(num_reports):
            # 报告期：在日期范围内随机选择
            report_days = (end_date - start_date).days
            report_offset = draw(st.integers(min_value=0, max_value=max(1, report_days - 30)))
            report_date = start_date + timedelta(days=report_offset)
            
            # 公告日期：在报告期之后10-60天
            announce_offset = draw(st.integers(min_value=10, max_value=60))
            announce_date = report_date + timedelta(days=announce_offset)
            
            # 确保公告日期不超过结束日期
            if announce_date > end_date:
                announce_date = end_date
            
            data.append({
                'stock_code': stock_code,
                'report_date': report_date.strftime('%Y%m%d'),
                'announce_date': announce_date.strftime('%Y%m%d'),
                'pe_ratio': round(draw(st.floats(min_value=5.0, max_value=50.0)), 2),
                'pb_ratio': round(draw(st.floats(min_value=0.5, max_value=10.0)), 2),
                'roe': round(draw(st.floats(min_value=0.01, max_value=0.30)), 4)
            })
    
    return pd.DataFrame(data) if data else pd.DataFrame()


# 行业数据生成策略
@st.composite
def industry_data_strategy(draw, stock_codes, date_range):
    """
    生成行业分类数据DataFrame
    
    Args:
        stock_codes: 股票代码列表
        date_range: 日期范围元组 (start_date, end_date)
    """
    start_date_str, end_date_str = date_range
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    
    industries = [
        ('801010', '农林牧渔'),
        ('801020', '采掘'),
        ('801030', '化工'),
        ('801040', '钢铁'),
        ('801050', '电子')
    ]
    
    data = []
    for stock_code in stock_codes:
        # 为每个股票生成1-2条行业分类记录（可能有行业变更）
        num_classifications = draw(st.integers(min_value=1, max_value=2))
        
        for i in range(num_classifications):
            # 生效日期：在日期范围内随机选择
            effective_days = (end_date - start_date).days
            effective_offset = draw(st.integers(min_value=0, max_value=max(1, effective_days)))
            effective_date = start_date + timedelta(days=effective_offset)
            
            industry_code, industry_name = draw(st.sampled_from(industries))
            
            data.append({
                'stock_code': stock_code,
                'effective_date': effective_date.strftime('%Y%m%d'),
                'industry_l1_code': industry_code,
                'industry_l1_name': industry_name
            })
    
    return pd.DataFrame(data) if data else pd.DataFrame()


# ============================================================================
# 属性21：保守日期对齐
# ============================================================================

class TestProperty21ConservativeDateAlignment:
    """属性21：保守日期对齐"""
    
    @given(
        price_data=price_data_strategy(num_stocks=2, num_days=15),
        data=st.data()
    )
    @settings(max_examples=5, deadline=None)
    def test_property_21_conservative_alignment_with_fundamental(self, price_data, data):
        """
        Feature: week2-xtdata-engineering, Property 21: 保守日期对齐
        
        对于任何跨数据源的数据对齐操作，当存在日期不确定性时，
        系统应该使用较早的日期以避免使用未来信息。
        
        验证需求：7.5
        """
        # 获取价格数据的日期范围
        min_date = price_data['date'].min()
        max_date = price_data['date'].max()
        stock_codes = price_data['stock_code'].unique().tolist()
        
        # 生成基本面数据
        fundamental_data = data.draw(fundamental_data_strategy(
            stock_codes=stock_codes,
            date_range=(min_date, max_date)
        ))
        
        # 如果没有生成基本面数据，跳过此测试
        assume(not fundamental_data.empty)
        
        # 执行数据对齐
        aligned_data = align_data_sources(
            price_data=price_data,
            fundamental_data=fundamental_data,
            method='conservative',
            validate=True
        )
        
        # 属性验证1：对齐后的数据不应为空
        assert not aligned_data.empty, "对齐后的数据不应为空"
        
        # 属性验证2：对齐后的数据应包含价格数据的所有记录
        assert len(aligned_data) >= len(price_data), \
            "对齐后的数据应至少包含所有价格数据记录"
        
        # 属性验证3：如果存在基本面数据，验证时间点正确性
        if 'fundamental_announce_date' in aligned_data.columns:
            # 所有基本面数据的公告日期应该 <= 交易日期（保守策略）
            has_fundamental = aligned_data['fundamental_announce_date'].notna()
            if has_fundamental.any():
                fundamental_rows = aligned_data[has_fundamental]
                violations = fundamental_rows[
                    fundamental_rows['fundamental_announce_date'] > fundamental_rows['date']
                ]
                
                assert violations.empty, \
                    f"检测到 {len(violations)} 条记录违反保守日期对齐原则：" \
                    f"announce_date > trade_date"
        
        # 属性验证4：对于每个交易日，使用的应该是该日期之前最新的基本面数据
        for stock_code in stock_codes:
            stock_aligned = aligned_data[aligned_data['stock_code'] == stock_code]
            stock_fundamental = fundamental_data[fundamental_data['stock_code'] == stock_code]
            
            if stock_fundamental.empty:
                continue
            
            for _, row in stock_aligned.iterrows():
                trade_date = row['date']
                
                # 找到该交易日之前可用的所有基本面数据
                available_fundamental = stock_fundamental[
                    stock_fundamental['announce_date'] <= trade_date
                ]
                
                if not available_fundamental.empty and 'fundamental_announce_date' in row:
                    # 如果该行有基本面数据，应该是最新的可用数据
                    if pd.notna(row.get('fundamental_announce_date')):
                        latest_announce_date = available_fundamental['announce_date'].max()
                        assert row['fundamental_announce_date'] == latest_announce_date, \
                            f"交易日 {trade_date} 应使用最新的基本面数据 " \
                            f"(expected: {latest_announce_date}, got: {row['fundamental_announce_date']})"
    
    @given(
        price_data=price_data_strategy(num_stocks=2, num_days=15),
        data=st.data()
    )
    @settings(max_examples=5, deadline=None)
    def test_property_21_conservative_alignment_with_industry(self, price_data, data):
        """
        Feature: week2-xtdata-engineering, Property 21: 保守日期对齐（行业数据）
        
        验证行业数据对齐时的保守策略
        
        验证需求：7.5
        """
        # 获取价格数据的日期范围
        min_date = price_data['date'].min()
        max_date = price_data['date'].max()
        stock_codes = price_data['stock_code'].unique().tolist()
        
        # 生成行业数据
        industry_data = data.draw(industry_data_strategy(
            stock_codes=stock_codes,
            date_range=(min_date, max_date)
        ))
        
        # 如果没有生成行业数据，跳过此测试
        assume(not industry_data.empty)
        
        # 执行数据对齐
        aligned_data = align_data_sources(
            price_data=price_data,
            industry_data=industry_data,
            method='conservative',
            validate=True
        )
        
        # 属性验证1：对齐后的数据不应为空
        assert not aligned_data.empty, "对齐后的数据不应为空"
        
        # 属性验证2：如果存在行业数据，验证时间点正确性
        if 'industry_effective_date' in aligned_data.columns:
            # 所有行业数据的生效日期应该 <= 交易日期（保守策略）
            has_industry = aligned_data['industry_effective_date'].notna()
            if has_industry.any():
                industry_rows = aligned_data[has_industry]
                violations = industry_rows[
                    industry_rows['industry_effective_date'] > industry_rows['date']
                ]
                
                assert violations.empty, \
                    f"检测到 {len(violations)} 条记录违反保守日期对齐原则：" \
                    f"effective_date > trade_date"
    
    @given(
        date1=date_strategy(),
        date2=date_strategy()
    )
    @settings(max_examples=10, deadline=None)
    def test_property_21_conservative_date_match_returns_earlier(self, date1, date2):
        """
        Feature: week2-xtdata-engineering, Property 21: 保守日期匹配返回较早日期
        
        验证conservative_date_match函数在使用'earlier'策略时返回较早的日期
        
        验证需求：7.5
        """
        result = conservative_date_match(date1, date2, strategy='earlier')
        
        # 属性验证：结果应该是两个日期中较早的一个
        expected = min(date1, date2)
        assert result == expected, \
            f"保守日期匹配应返回较早的日期 (expected: {expected}, got: {result})"
    
    @given(
        price_data=price_data_strategy(num_stocks=1, num_days=10),
        data=st.data()
    )
    @settings(max_examples=5, deadline=None)
    def test_property_21_alignment_date_filter(self, price_data, data):
        """
        Feature: week2-xtdata-engineering, Property 21: 对齐截止日期过滤
        
        验证指定alignment_date时，只使用该日期之前的数据
        
        验证需求：7.5
        """
        # 选择一个中间日期作为对齐截止日期
        all_dates = sorted(price_data['date'].unique())
        if len(all_dates) < 3:
            assume(False)  # 需要至少3个日期
        
        alignment_date = all_dates[len(all_dates) // 2]
        
        # 生成基本面数据
        min_date = price_data['date'].min()
        max_date = price_data['date'].max()
        stock_codes = price_data['stock_code'].unique().tolist()
        
        fundamental_data = data.draw(fundamental_data_strategy(
            stock_codes=stock_codes,
            date_range=(min_date, max_date)
        ))
        
        # 执行数据对齐，指定截止日期
        aligned_data = align_data_sources(
            price_data=price_data,
            fundamental_data=fundamental_data,
            alignment_date=alignment_date,
            method='conservative',
            validate=True
        )
        
        # 属性验证1：所有交易日期应该 <= alignment_date
        assert all(aligned_data['date'] <= alignment_date), \
            f"所有交易日期应该 <= alignment_date ({alignment_date})"
        
        # 属性验证2：如果有基本面数据，所有公告日期应该 <= alignment_date
        if 'fundamental_announce_date' in aligned_data.columns:
            has_fundamental = aligned_data['fundamental_announce_date'].notna()
            if has_fundamental.any():
                assert all(
                    aligned_data.loc[has_fundamental, 'fundamental_announce_date'] <= alignment_date
                ), f"所有基本面公告日期应该 <= alignment_date ({alignment_date})"


# ============================================================================
# 辅助功能测试
# ============================================================================

class TestDataAlignmentHelpers:
    """测试数据对齐辅助函数"""
    
    @given(
        price_data=price_data_strategy(num_stocks=1, num_days=10)
    )
    @settings(max_examples=5, deadline=None)
    def test_get_point_in_time_data(self, price_data):
        """测试时间点数据查询功能"""
        # 选择一个中间日期
        all_dates = sorted(price_data['date'].unique())
        if len(all_dates) < 3:
            assume(False)
        
        as_of_date = all_dates[len(all_dates) // 2]
        
        # 获取时间点数据
        result = get_point_in_time_data(
            price_data,
            as_of_date=as_of_date,
            date_column='date'
        )
        
        # 验证：所有返回的数据日期应该 <= as_of_date
        assert all(result['date'] <= as_of_date), \
            f"所有数据日期应该 <= as_of_date ({as_of_date})"
        
        # 验证：应该包含as_of_date之前的所有数据
        expected_count = len(price_data[price_data['date'] <= as_of_date])
        assert len(result) == expected_count, \
            f"应该包含所有 <= as_of_date 的数据 (expected: {expected_count}, got: {len(result)})"
    
    @given(
        price_data=price_data_strategy(num_stocks=1, num_days=10)
    )
    @settings(max_examples=5, deadline=None)
    def test_detect_lookahead_bias_clean_data(self, price_data):
        """测试前瞻偏差检测功能 - 干净数据"""
        # 对于干净的价格数据，不应检测到前瞻偏差
        violations = detect_lookahead_bias(
            price_data,
            trade_date_column='date'
        )
        
        # 验证：不应有违规
        assert not violations, \
            f"干净的价格数据不应检测到前瞻偏差，但发现: {violations}"
    
    def test_detect_lookahead_bias_with_violations(self):
        """测试前瞻偏差检测功能 - 包含违规的数据"""
        # 创建包含前瞻偏差的测试数据
        data = pd.DataFrame({
            'stock_code': ['000001.SZ', '000001.SZ', '000001.SZ'],
            'date': ['20240110', '20240115', '20240120'],
            'close': [10.0, 10.5, 11.0],
            'announce_date': ['20240105', '20240120', '20240125']  # 第2、3条有问题
        })
        
        # 检测前瞻偏差
        violations = detect_lookahead_bias(
            data,
            trade_date_column='date',
            reference_date_columns=['announce_date']
        )
        
        # 验证：应该检测到违规
        assert 'announce_date' in violations, \
            "应该检测到announce_date列的前瞻偏差"
        
        # 验证：应该有2条违规记录（索引1和2）
        assert len(violations['announce_date']) == 2, \
            f"应该检测到2条违规记录，实际: {len(violations['announce_date'])}"
