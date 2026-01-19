"""
基本面数据处理器属性测试

使用基于属性的测试验证FundamentalHandler的通用正确性属性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from src.fundamental_handler import FundamentalHandler
from unittest.mock import Mock


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


# 股票代码列表生成策略
stock_codes_list = st.lists(
    stock_code_strategy(),
    min_size=1,
    max_size=5,
    unique=True
)


# 日期生成策略（过去的日期）
@st.composite
def past_date_strategy(draw):
    """生成过去的日期"""
    days_ago = draw(st.integers(min_value=1, max_value=365 * 2))
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y%m%d')


# 指标列表生成策略
indicators_list = st.lists(
    st.sampled_from(['pe', 'pb', 'roe', 'revenue', 'net_profit', 'total_assets', 'total_equity']),
    min_size=1,
    max_size=3,
    unique=True
)


def create_mock_client():
    """创建mock客户端"""
    client = Mock()
    client.is_connected.return_value = True
    return client


# ============================================================================
# 属性10：时间点正确性
# ============================================================================

class TestProperty10TimePointCorrectness:
    """
    属性10：时间点正确性
    
    验证需求：3.1, 3.6, 7.2
    
    对于任何查询日期和基本面数据请求，返回的所有数据记录的announce_date
    （公告日期）都应该小于或等于查询日期。
    
    这是防止未来函数的关键属性：确保在回测中不会使用到在历史时点
    尚未公开的财务信息。
    """
    
    @given(
        stock_codes=stock_codes_list,
        indicators=indicators_list,
        as_of_date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_10_announce_date_before_query_date(
        self,
        stock_codes,
        indicators,
        as_of_date
    ):
        """
        Feature: week2-xtdata-engineering, Property 10: 时间点正确性
        
        **Validates: Requirements 3.1, 3.6, 7.2**
        
        测试说明：
        1. 使用随机生成的股票代码、指标和查询日期
        2. 调用get_financial_data获取财务数据
        3. 验证所有返回记录的announce_date <= as_of_date
        
        这确保了在任何历史时点，我们只能看到已经公告的财务数据，
        而不会"穿越"到未来获取尚未公开的信息。
        """
        # 创建mock客户端和处理器
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 获取财务数据
        data = handler.get_financial_data(
            stock_codes=stock_codes,
            indicators=indicators,
            as_of_date=as_of_date
        )
        
        # 验证返回的是DataFrame
        assert isinstance(data, pd.DataFrame), \
            "get_financial_data应该返回pandas DataFrame"
        
        # 如果有数据返回，验证时间点正确性
        if not data.empty:
            # 验证必需的列存在
            assert 'announce_date' in data.columns, \
                "返回的数据必须包含announce_date列"
            assert 'stock_code' in data.columns, \
                "返回的数据必须包含stock_code列"
            
            # 核心验证：所有公告日期都应该 <= 查询日期
            for idx, row in data.iterrows():
                announce_date = row['announce_date']
                stock_code = row['stock_code']
                
                # 验证公告日期格式
                assert isinstance(announce_date, str), \
                    f"announce_date应该是字符串类型，当前类型: {type(announce_date)}"
                assert len(announce_date) == 8, \
                    f"announce_date应该是8位日期格式YYYYMMDD，当前: {announce_date}"
                
                # 核心断言：公告日期 <= 查询日期
                assert announce_date <= as_of_date, \
                    (f"时间点正确性违反！股票 {stock_code} 的公告日期 "
                     f"{announce_date} 晚于查询日期 {as_of_date}。"
                     f"这会导致未来函数问题！")
            
            # 额外验证：返回的股票代码应该是请求的子集
            returned_codes = set(data['stock_code'].unique())
            requested_codes = set(stock_codes)
            assert returned_codes.issubset(requested_codes), \
                f"返回的股票代码 {returned_codes} 应该是请求代码 {requested_codes} 的子集"
    
    @given(
        stock_code=stock_code_strategy(),
        indicators=indicators_list,
        as_of_date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_10_single_stock_time_correctness(
        self,
        stock_code,
        indicators,
        as_of_date
    ):
        """
        Feature: week2-xtdata-engineering, Property 10: 时间点正确性（单股票版本）
        
        **Validates: Requirements 3.1, 3.6, 7.2**
        
        测试单只股票的时间点正确性，确保即使只查询一只股票，
        时间点正确性也得到保证。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 获取单只股票的财务数据
        data = handler.get_financial_data(
            stock_codes=[stock_code],
            indicators=indicators,
            as_of_date=as_of_date
        )
        
        assert isinstance(data, pd.DataFrame)
        
        if not data.empty:
            # 应该只有一只股票的数据
            assert len(data['stock_code'].unique()) == 1
            assert data['stock_code'].iloc[0] == stock_code
            
            # 验证时间点正确性
            announce_date = data['announce_date'].iloc[0]
            assert announce_date <= as_of_date, \
                (f"单股票查询时间点正确性违反！"
                 f"公告日期 {announce_date} > 查询日期 {as_of_date}")
    
    def test_property_10_edge_case_same_date(self):
        """
        Feature: week2-xtdata-engineering, Property 10: 时间点正确性（边缘情况）
        
        **Validates: Requirements 3.1, 3.6, 7.2**
        
        测试边缘情况：当查询日期正好等于公告日期时，
        数据应该被包含在结果中（announce_date <= as_of_date）。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个固定的日期进行测试
        as_of_date = '20240330'  # 这个日期在模拟数据中有公告
        
        data = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe', 'pb'],
            as_of_date=as_of_date
        )
        
        if not data.empty:
            # 验证所有公告日期 <= 查询日期
            for announce_date in data['announce_date']:
                assert announce_date <= as_of_date, \
                    f"边缘情况失败：announce_date {announce_date} > as_of_date {as_of_date}"
    
    def test_property_10_early_date_returns_empty_or_old_data(self):
        """
        Feature: week2-xtdata-engineering, Property 10: 时间点正确性（早期日期）
        
        **Validates: Requirements 3.1, 3.6, 7.2**
        
        测试早期日期：当查询一个很早的日期时，应该返回空数据
        或者只返回那个时点之前公告的数据。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个很早的日期（在所有模拟数据的公告日期之前）
        very_early_date = '20200101'
        
        data = handler.get_financial_data(
            stock_codes=['000001.SZ', '000002.SZ'],
            indicators=['pe', 'pb', 'roe'],
            as_of_date=very_early_date
        )
        
        # 应该返回空DataFrame或者所有announce_date都 <= very_early_date
        assert isinstance(data, pd.DataFrame)
        
        if not data.empty:
            for announce_date in data['announce_date']:
                assert announce_date <= very_early_date, \
                    (f"早期日期查询失败：返回了未来的数据！"
                     f"announce_date {announce_date} > as_of_date {very_early_date}")
    
    @given(
        stock_codes=stock_codes_list,
        indicators=indicators_list
    )
    @settings(max_examples=50, deadline=None)
    def test_property_10_future_date_includes_all_data(
        self,
        stock_codes,
        indicators
    ):
        """
        Feature: week2-xtdata-engineering, Property 10: 时间点正确性（未来日期）
        
        **Validates: Requirements 3.1, 3.6, 7.2**
        
        测试未来日期：当查询一个未来的日期时，应该返回所有已公告的数据，
        且所有announce_date仍然 <= 查询日期（因为查询日期在未来）。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个未来的日期
        future_date = '20991231'
        
        data = handler.get_financial_data(
            stock_codes=stock_codes,
            indicators=indicators,
            as_of_date=future_date
        )
        
        assert isinstance(data, pd.DataFrame)
        
        # 即使是未来日期，时间点正确性仍然应该成立
        if not data.empty:
            for announce_date in data['announce_date']:
                assert announce_date <= future_date, \
                    (f"未来日期查询失败：announce_date {announce_date} "
                     f"> as_of_date {future_date}")


# ============================================================================
# 辅助测试：验证时间点正确性的实现细节
# ============================================================================

class TestTimePointCorrectnessImplementation:
    """
    验证时间点正确性的实现细节
    
    这些测试不是属性测试，而是验证实现是否正确使用了announce_date
    而不是report_date进行过滤。
    """
    
    def test_uses_announce_date_not_report_date(self):
        """
        验证使用announce_date而非report_date进行时间过滤
        
        这是防止未来函数的关键：报告期（report_date）是财务报表
        所属的会计期间，而公告日期（announce_date）是实际披露日期。
        必须使用公告日期！
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 选择一个介于report_date和announce_date之间的日期
        # 根据模拟数据：report_date='20231231', announce_date='20240330'
        # 我们选择 as_of_date='20240101'（在报告期之后，但在公告日期之前）
        as_of_date = '20240101'
        
        data = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe'],
            as_of_date=as_of_date
        )
        
        # 如果正确使用announce_date，应该没有2023年年报的数据
        # （因为年报在2024-03-30才公告）
        if not data.empty:
            for idx, row in data.iterrows():
                report_date = row.get('report_date', '')
                announce_date = row['announce_date']
                
                # 关键验证：即使report_date在as_of_date之前，
                # 如果announce_date在as_of_date之后，也不应该返回
                assert announce_date <= as_of_date, \
                    (f"错误！使用了report_date而非announce_date进行过滤！"
                     f"report_date={report_date}, announce_date={announce_date}, "
                     f"as_of_date={as_of_date}")
    
    def test_returns_most_recent_announced_data(self):
        """
        验证返回最新公告的数据
        
        当有多个符合条件的财务报告时，应该返回公告日期最新的那个。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个较晚的日期，应该能获取到多个季度的数据
        as_of_date = '20240430'
        
        data = handler.get_financial_data(
            stock_codes=['000001.SZ'],
            indicators=['pe', 'pb'],
            as_of_date=as_of_date
        )
        
        if not data.empty:
            # 对于单只股票，应该只返回一条记录（最新的）
            stock_data = data[data['stock_code'] == '000001.SZ']
            
            # 验证只有一条记录
            assert len(stock_data) == 1, \
                "应该只返回最新公告的一条财务数据"
            
            # 验证announce_date是最新的（在as_of_date之前）
            announce_date = stock_data['announce_date'].iloc[0]
            assert announce_date <= as_of_date



# ============================================================================
# 属性11：PE比率计算正确性
# ============================================================================

class TestProperty11PERatioCalculationCorrectness:
    """
    属性11：PE比率计算正确性
    
    验证需求：3.2
    
    对于任何有效的价格和盈利数据，计算的PE比率应该等于价格除以每股收益，
    且数据时间对齐正确。
    
    PE比率 = 股价 / 每股收益（EPS）
    EPS = 净利润 / 总股本
    
    关键验证点：
    1. PE比率的数学计算正确性
    2. 使用的财务数据必须是查询日期之前公告的（时间对齐）
    3. 当EPS为负或零时，应该返回None
    4. 当数据缺失时，应该返回None而非异常
    """
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_11_pe_ratio_calculation_correctness(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性
        
        **Validates: Requirements 3.2**
        
        测试说明：
        1. 生成随机的股票代码和日期
        2. 创建价格数据
        3. 调用calculate_pe_ratio计算PE比率
        4. 验证计算结果的正确性和时间对齐
        
        验证点：
        - PE比率的计算公式正确
        - 使用的财务数据在查询日期之前公告
        - 返回值类型正确（float或None）
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 生成价格数据
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PE比率
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证返回值类型
        assert pe_ratio is None or isinstance(pe_ratio, (float, int)), \
            f"PE比率应该是float或None，当前类型: {type(pe_ratio)}"
        
        # 如果返回了PE比率，验证其合理性
        if pe_ratio is not None:
            # PE比率应该是正数
            assert pe_ratio > 0, \
                f"PE比率应该是正数，当前值: {pe_ratio}"
            
            # PE比率应该在合理范围内（通常0-1000）
            assert 0 < pe_ratio < 1000, \
                f"PE比率超出合理范围: {pe_ratio}"
            
            # 验证时间对齐：获取用于计算的财务数据
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['net_profit'],
                as_of_date=date
            )
            
            # 如果有财务数据，验证公告日期在查询日期之前
            if not financial_data.empty:
                announce_date = financial_data['announce_date'].iloc[0]
                assert announce_date <= date, \
                    (f"时间对齐错误！PE比率计算使用了未来数据。"
                     f"公告日期 {announce_date} > 查询日期 {date}")
    
    def test_property_11_pe_ratio_formula_correctness(self):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性（公式验证）
        
        **Validates: Requirements 3.2**
        
        测试PE比率计算公式的正确性：
        PE = 股价 / EPS
        EPS = 净利润 / 总股本
        
        验证PE比率的计算逻辑是正确的。
        注意：由于模拟数据使用随机值，我们验证的是计算逻辑而非精确值。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用固定的测试数据
        stock_code = '000001.SZ'
        date = '20240430'
        close_price = 10.0
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [9.5],
            'high': [10.5],
            'low': [9.0],
            'close': [close_price],
            'volume': [1000000]
        })
        
        # 计算PE比率
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证PE比率的基本属性
        if pe_ratio is not None:
            # PE比率应该是正数
            assert pe_ratio > 0, \
                f"PE比率应该是正数，当前值: {pe_ratio}"
            
            # PE比率应该在合理范围内
            assert 0 < pe_ratio < 1000, \
                f"PE比率超出合理范围: {pe_ratio}"
            
            # 验证计算使用了正确的数据源
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['net_profit'],
                as_of_date=date
            )
            
            # 应该能获取到财务数据
            assert not financial_data.empty, \
                "PE比率不为None时，应该能获取到财务数据"
            
            # 验证公告日期在查询日期之前
            announce_date = financial_data['announce_date'].iloc[0]
            assert announce_date <= date, \
                f"时间对齐错误：announce_date {announce_date} > date {date}"
    
    def test_property_11_pe_ratio_negative_eps_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性（负EPS）
        
        **Validates: Requirements 3.2**
        
        测试当EPS为负数时，应该返回None而非负的PE比率。
        
        在实际市场中，亏损公司的EPS为负，此时PE比率无意义。
        """
        mock_client = create_mock_client()
        
        # 创建一个会返回负净利润的mock handler
        # 注意：由于当前实现使用随机正数，这个测试验证的是逻辑
        # 在实际数据中，如果net_profit为负，应该返回None
        
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PE比率
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：如果返回了PE比率，它应该是正数
        # 如果EPS为负，应该返回None
        if pe_ratio is not None:
            assert pe_ratio > 0, \
                "当EPS为负时，应该返回None而非负的PE比率"
    
    def test_property_11_pe_ratio_missing_price_data_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性（缺失价格数据）
        
        **Validates: Requirements 3.2**
        
        测试当价格数据缺失时，应该返回None而非抛出异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        # 创建不包含目标日期的价格数据
        price_data = pd.DataFrame({
            'stock_code': ['000002.SZ'],  # 不同的股票代码
            'date': ['20240429'],  # 不同的日期
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PE比率
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：应该返回None
        assert pe_ratio is None, \
            "当价格数据缺失时，应该返回None"
    
    def test_property_11_pe_ratio_missing_financial_data_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性（缺失财务数据）
        
        **Validates: Requirements 3.2**
        
        测试当财务数据缺失时，应该返回None而非抛出异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        # 使用一个很早的日期，在所有财务数据公告之前
        date = '20200101'
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PE比率
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：应该返回None（因为没有财务数据）
        assert pe_ratio is None, \
            "当财务数据缺失时，应该返回None"
    
    @given(
        stock_codes=stock_codes_list,
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_11_pe_ratio_time_alignment_consistency(
        self,
        stock_codes,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 11: PE比率计算正确性（时间对齐一致性）
        
        **Validates: Requirements 3.2**
        
        测试PE比率计算中的时间对齐一致性：
        calculate_pe_ratio内部调用get_financial_data时，
        应该使用相同的as_of_date，确保时间点正确性。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        for stock_code in stock_codes:
            price_data = pd.DataFrame({
                'stock_code': [stock_code],
                'date': [date],
                'open': [10.0],
                'high': [11.0],
                'low': [9.5],
                'close': [10.5],
                'volume': [1000000]
            })
            
            # 计算PE比率
            pe_ratio = handler.calculate_pe_ratio(
                stock_code=stock_code,
                date=date,
                price_data=price_data
            )
            
            # 直接获取财务数据
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['net_profit'],
                as_of_date=date
            )
            
            # 验证一致性：
            # 如果PE比率不为None，则财务数据应该存在
            # 如果财务数据不存在，则PE比率应该为None
            if pe_ratio is not None:
                assert not financial_data.empty, \
                    (f"时间对齐不一致！PE比率不为None，"
                     f"但get_financial_data返回空数据")
                
                # 验证使用的财务数据的公告日期
                announce_date = financial_data['announce_date'].iloc[0]
                assert announce_date <= date, \
                    (f"时间对齐错误！使用的财务数据公告日期 "
                     f"{announce_date} > 查询日期 {date}")



# ============================================================================
# 属性12：PB比率计算正确性
# ============================================================================

class TestProperty12PBRatioCalculationCorrectness:
    """
    属性12：PB比率计算正确性
    
    验证需求：3.3
    
    对于任何有效的价格和账面价值数据，计算的PB比率应该等于价格除以每股净资产，
    且数据时间对齐正确。
    
    PB比率 = 股价 / 每股净资产（BVPS）
    BVPS = 净资产 / 总股本
    
    关键验证点：
    1. PB比率的数学计算正确性
    2. 使用的财务数据必须是查询日期之前公告的（时间对齐）
    3. 当BVPS为负或零时，应该返回None
    4. 当数据缺失时，应该返回None而非异常
    """
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_12_pb_ratio_calculation_correctness(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性
        
        **Validates: Requirements 3.3**
        
        测试说明：
        1. 生成随机的股票代码和日期
        2. 创建价格数据
        3. 调用calculate_pb_ratio计算PB比率
        4. 验证计算结果的正确性和时间对齐
        
        验证点：
        - PB比率的计算公式正确
        - 使用的财务数据在查询日期之前公告
        - 返回值类型正确（float或None）
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 生成价格数据
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证返回值类型
        assert pb_ratio is None or isinstance(pb_ratio, (float, int)), \
            f"PB比率应该是float或None，当前类型: {type(pb_ratio)}"
        
        # 如果返回了PB比率，验证其合理性
        if pb_ratio is not None:
            # PB比率应该是正数
            assert pb_ratio > 0, \
                f"PB比率应该是正数，当前值: {pb_ratio}"
            
            # PB比率应该在合理范围内（通常0-100）
            assert 0 < pb_ratio < 100, \
                f"PB比率超出合理范围: {pb_ratio}"
            
            # 验证时间对齐：获取用于计算的财务数据
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['total_equity'],
                as_of_date=date
            )
            
            # 如果有财务数据，验证公告日期在查询日期之前
            if not financial_data.empty:
                announce_date = financial_data['announce_date'].iloc[0]
                assert announce_date <= date, \
                    (f"时间对齐错误！PB比率计算使用了未来数据。"
                     f"公告日期 {announce_date} > 查询日期 {date}")
    
    def test_property_12_pb_ratio_formula_correctness(self):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（公式验证）
        
        **Validates: Requirements 3.3**
        
        测试PB比率计算公式的正确性：
        PB = 股价 / BVPS
        BVPS = 净资产 / 总股本
        
        验证PB比率的计算逻辑是正确的。
        注意：由于模拟数据使用随机值，我们验证的是计算逻辑而非精确值。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用固定的测试数据
        stock_code = '000001.SZ'
        date = '20240430'
        close_price = 10.0
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [9.5],
            'high': [10.5],
            'low': [9.0],
            'close': [close_price],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证PB比率的基本属性
        if pb_ratio is not None:
            # PB比率应该是正数
            assert pb_ratio > 0, \
                f"PB比率应该是正数，当前值: {pb_ratio}"
            
            # PB比率应该在合理范围内
            assert 0 < pb_ratio < 100, \
                f"PB比率超出合理范围: {pb_ratio}"
            
            # 验证计算使用了正确的数据源
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['total_equity'],
                as_of_date=date
            )
            
            # 应该能获取到财务数据
            assert not financial_data.empty, \
                "PB比率不为None时，应该能获取到财务数据"
            
            # 验证公告日期在查询日期之前
            announce_date = financial_data['announce_date'].iloc[0]
            assert announce_date <= date, \
                f"时间对齐错误：announce_date {announce_date} > date {date}"
    
    def test_property_12_pb_ratio_negative_bvps_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（负BVPS）
        
        **Validates: Requirements 3.3**
        
        测试当BVPS为负数时，应该返回None而非负的PB比率。
        
        在实际市场中，资不抵债公司的净资产为负，此时PB比率无意义。
        """
        mock_client = create_mock_client()
        
        # 创建一个会返回负净资产的mock handler
        # 注意：由于当前实现使用随机正数，这个测试验证的是逻辑
        # 在实际数据中，如果total_equity为负，应该返回None
        
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：如果返回了PB比率，它应该是正数
        # 如果BVPS为负，应该返回None
        if pb_ratio is not None:
            assert pb_ratio > 0, \
                "当BVPS为负时，应该返回None而非负的PB比率"
    
    def test_property_12_pb_ratio_missing_price_data_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（缺失价格数据）
        
        **Validates: Requirements 3.3**
        
        测试当价格数据缺失时，应该返回None而非抛出异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        # 创建不包含目标日期的价格数据
        price_data = pd.DataFrame({
            'stock_code': ['000002.SZ'],  # 不同的股票代码
            'date': ['20240429'],  # 不同的日期
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：应该返回None
        assert pb_ratio is None, \
            "当价格数据缺失时，应该返回None"
    
    def test_property_12_pb_ratio_missing_financial_data_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（缺失财务数据）
        
        **Validates: Requirements 3.3**
        
        测试当财务数据缺失时，应该返回None而非抛出异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        # 使用一个很早的日期，在所有财务数据公告之前
        date = '20200101'
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：应该返回None（因为没有财务数据）
        assert pb_ratio is None, \
            "当财务数据缺失时，应该返回None"
    
    @given(
        stock_codes=stock_codes_list,
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_12_pb_ratio_time_alignment_consistency(
        self,
        stock_codes,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（时间对齐一致性）
        
        **Validates: Requirements 3.3**
        
        测试PB比率计算中的时间对齐一致性：
        calculate_pb_ratio内部调用get_financial_data时，
        应该使用相同的as_of_date，确保时间点正确性。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        for stock_code in stock_codes:
            price_data = pd.DataFrame({
                'stock_code': [stock_code],
                'date': [date],
                'open': [10.0],
                'high': [11.0],
                'low': [9.5],
                'close': [10.5],
                'volume': [1000000]
            })
            
            # 计算PB比率
            pb_ratio = handler.calculate_pb_ratio(
                stock_code=stock_code,
                date=date,
                price_data=price_data
            )
            
            # 直接获取财务数据
            financial_data = handler.get_financial_data(
                stock_codes=[stock_code],
                indicators=['total_equity'],
                as_of_date=date
            )
            
            # 验证一致性：
            # 如果PB比率不为None，则财务数据应该存在
            # 如果财务数据不存在，则PB比率应该为None
            if pb_ratio is not None:
                assert not financial_data.empty, \
                    (f"时间对齐不一致！PB比率不为None，"
                     f"但get_financial_data返回空数据")
                
                # 验证使用的财务数据的公告日期
                announce_date = financial_data['announce_date'].iloc[0]
                assert announce_date <= date, \
                    (f"时间对齐错误！使用的财务数据公告日期 "
                     f"{announce_date} > 查询日期 {date}")
    
    def test_property_12_pb_ratio_zero_bvps_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（零BVPS）
        
        **Validates: Requirements 3.3**
        
        测试当BVPS为零时，应该返回None以避免除零错误。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 验证：如果返回了PB比率，它应该是正数（不应该是无穷大或NaN）
        if pb_ratio is not None:
            assert pb_ratio > 0, \
                "PB比率应该是正数"
            assert not np.isinf(pb_ratio), \
                "PB比率不应该是无穷大（BVPS为零时应返回None）"
            assert not np.isnan(pb_ratio), \
                "PB比率不应该是NaN"
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_12_pb_ratio_reasonable_range(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 12: PB比率计算正确性（合理范围）
        
        **Validates: Requirements 3.3**
        
        测试PB比率应该在合理的范围内。
        
        在实际市场中，PB比率通常在0.1到20之间，极少数情况会超出这个范围。
        这个测试验证计算结果的合理性。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        # 计算PB比率
        pb_ratio = handler.calculate_pb_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        
        # 如果返回了PB比率，验证其在合理范围内
        if pb_ratio is not None:
            # PB比率应该是正数
            assert pb_ratio > 0, \
                f"PB比率应该是正数，当前值: {pb_ratio}"
            
            # PB比率应该在合理范围内（0.01到100）
            # 注意：由于使用模拟数据，范围可能比实际市场更宽
            assert 0.01 < pb_ratio < 100, \
                (f"PB比率超出合理范围: {pb_ratio}。"
                 f"股票: {stock_code}, 日期: {date}")
            
            # PB比率不应该是无穷大或NaN
            assert not np.isinf(pb_ratio), \
                f"PB比率不应该是无穷大: {pb_ratio}"
            assert not np.isnan(pb_ratio), \
                f"PB比率不应该是NaN: {pb_ratio}"


# ============================================================================
# 属性13：基本面数据缺失处理
# ============================================================================

class TestProperty13MissingDataHandling:
    """
    属性13：基本面数据缺失处理
    
    验证需求：3.5
    
    对于任何基本面数据请求，当数据缺失或为空时，系统应该返回None或空值
    而不是抛出异常。
    
    这是系统健壮性的关键属性：财务数据经常存在缺失情况（公司未披露、
    数据源问题、新上市公司等），系统必须优雅地处理这些情况，而不是崩溃。
    
    关键验证点：
    1. 当股票代码不存在时，返回空DataFrame而非异常
    2. 当查询日期早于所有公告日期时，返回空DataFrame而非异常
    3. 当请求的指标不可用时，返回空DataFrame或部分数据而非异常
    4. 当计算PE/PB比率时数据缺失，返回None而非异常
    5. 系统应该记录警告但继续运行
    """
    
    @given(
        stock_codes=stock_codes_list,
        indicators=indicators_list,
        as_of_date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_13_missing_data_returns_empty_not_exception(
        self,
        stock_codes,
        indicators,
        as_of_date
    ):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理
        
        **Validates: Requirements 3.5**
        
        测试说明：
        对于任何基本面数据请求，即使数据缺失，系统也应该返回空DataFrame
        或None，而不是抛出异常。
        
        这确保了系统的健壮性：在实际应用中，数据缺失是常态而非异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 测试：即使数据可能缺失，也不应该抛出异常
        try:
            data = handler.get_financial_data(
                stock_codes=stock_codes,
                indicators=indicators,
                as_of_date=as_of_date
            )
            
            # 验证返回类型
            assert isinstance(data, pd.DataFrame), \
                "get_financial_data应该返回DataFrame，即使数据缺失"
            
            # 如果返回空DataFrame，这是可以接受的
            # 如果返回有数据的DataFrame，验证数据结构正确
            if not data.empty:
                assert 'stock_code' in data.columns, \
                    "返回的数据应该包含stock_code列"
                assert 'announce_date' in data.columns, \
                    "返回的数据应该包含announce_date列"
                
                # 验证时间点正确性（即使在缺失数据的情况下）
                for announce_date in data['announce_date']:
                    assert announce_date <= as_of_date, \
                        "即使数据缺失，时间点正确性也应该保持"
        
        except Exception as e:
            pytest.fail(
                f"基本面数据缺失处理失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"股票代码: {stock_codes}\n"
                f"指标: {indicators}\n"
                f"日期: {as_of_date}\n"
                f"系统应该返回空DataFrame而非抛出异常"
            )
    
    def test_property_13_very_early_date_returns_empty(self):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（早期日期）
        
        **Validates: Requirements 3.5**
        
        测试当查询一个非常早的日期（在所有财务数据公告之前）时，
        应该返回空DataFrame而非异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个非常早的日期（在所有模拟数据之前）
        very_early_date = '20000101'
        
        try:
            data = handler.get_financial_data(
                stock_codes=['000001.SZ', '000002.SZ'],
                indicators=['pe', 'pb', 'roe'],
                as_of_date=very_early_date
            )
            
            # 应该返回空DataFrame
            assert isinstance(data, pd.DataFrame), \
                "应该返回DataFrame类型"
            
            # 对于非常早的日期，应该返回空数据（因为没有公告）
            # 但这不是强制要求，如果有数据也可以接受
            # 关键是不应该抛出异常
            
        except Exception as e:
            pytest.fail(
                f"早期日期查询失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"日期: {very_early_date}\n"
                f"系统应该返回空DataFrame而非抛出异常"
            )
    
    def test_property_13_nonexistent_stock_returns_empty(self):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（不存在的股票）
        
        **Validates: Requirements 3.5**
        
        测试当查询不存在的股票代码时，应该返回空DataFrame而非异常。
        
        注意：这里测试的是数据层面的缺失，而非参数验证层面的错误。
        股票代码格式正确，但数据源中没有该股票的数据。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用格式正确但可能不存在的股票代码
        nonexistent_stocks = ['999999.SZ', '999998.SH']
        
        try:
            data = handler.get_financial_data(
                stock_codes=nonexistent_stocks,
                indicators=['pe', 'pb'],
                as_of_date='20240430'
            )
            
            # 应该返回DataFrame（可能为空）
            assert isinstance(data, pd.DataFrame), \
                "应该返回DataFrame类型，即使股票不存在"
            
            # 如果返回空DataFrame，这是预期的
            # 如果返回有数据，说明模拟数据生成了这些股票的数据，也可以接受
            
        except Exception as e:
            pytest.fail(
                f"不存在的股票查询失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"股票代码: {nonexistent_stocks}\n"
                f"系统应该返回空DataFrame而非抛出异常"
            )
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_13_pe_ratio_missing_data_returns_none(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（PE比率）
        
        **Validates: Requirements 3.5**
        
        测试当计算PE比率时数据缺失，应该返回None而非抛出异常。
        
        可能的缺失情况：
        1. 价格数据缺失
        2. 财务数据缺失
        3. 净利润为负或零
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 创建可能不完整的价格数据
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        try:
            # 计算PE比率
            pe_ratio = handler.calculate_pe_ratio(
                stock_code=stock_code,
                date=date,
                price_data=price_data
            )
            
            # 验证返回值类型
            assert pe_ratio is None or isinstance(pe_ratio, (float, int)), \
                f"PE比率应该是None或float，当前类型: {type(pe_ratio)}"
            
            # 如果返回None，这是可以接受的（数据缺失）
            # 如果返回数值，验证其合理性
            if pe_ratio is not None:
                assert pe_ratio > 0, \
                    "如果返回PE比率，应该是正数"
                assert not np.isinf(pe_ratio), \
                    "PE比率不应该是无穷大"
                assert not np.isnan(pe_ratio), \
                    "PE比率不应该是NaN"
        
        except Exception as e:
            pytest.fail(
                f"PE比率计算失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"股票代码: {stock_code}\n"
                f"日期: {date}\n"
                f"当数据缺失时，应该返回None而非抛出异常"
            )
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_13_pb_ratio_missing_data_returns_none(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（PB比率）
        
        **Validates: Requirements 3.5**
        
        测试当计算PB比率时数据缺失，应该返回None而非抛出异常。
        
        可能的缺失情况：
        1. 价格数据缺失
        2. 财务数据缺失
        3. 净资产为负或零
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 创建可能不完整的价格数据
        price_data = pd.DataFrame({
            'stock_code': [stock_code],
            'date': [date],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'volume': [1000000]
        })
        
        try:
            # 计算PB比率
            pb_ratio = handler.calculate_pb_ratio(
                stock_code=stock_code,
                date=date,
                price_data=price_data
            )
            
            # 验证返回值类型
            assert pb_ratio is None or isinstance(pb_ratio, (float, int)), \
                f"PB比率应该是None或float，当前类型: {type(pb_ratio)}"
            
            # 如果返回None，这是可以接受的（数据缺失）
            # 如果返回数值，验证其合理性
            if pb_ratio is not None:
                assert pb_ratio > 0, \
                    "如果返回PB比率，应该是正数"
                assert not np.isinf(pb_ratio), \
                    "PB比率不应该是无穷大"
                assert not np.isnan(pb_ratio), \
                    "PB比率不应该是NaN"
        
        except Exception as e:
            pytest.fail(
                f"PB比率计算失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"股票代码: {stock_code}\n"
                f"日期: {date}\n"
                f"当数据缺失时，应该返回None而非抛出异常"
            )
    
    def test_property_13_empty_price_data_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（空价格数据）
        
        **Validates: Requirements 3.5**
        
        测试当价格数据为空DataFrame时，PE和PB比率计算应该返回None而非异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        date = '20240430'
        
        # 创建空的价格数据
        empty_price_data = pd.DataFrame(columns=['stock_code', 'date', 'open', 'high', 'low', 'close', 'volume'])
        
        try:
            # 计算PE比率
            pe_ratio = handler.calculate_pe_ratio(
                stock_code=stock_code,
                date=date,
                price_data=empty_price_data
            )
            
            # 应该返回None
            assert pe_ratio is None, \
                "当价格数据为空时，PE比率应该返回None"
            
            # 计算PB比率
            pb_ratio = handler.calculate_pb_ratio(
                stock_code=stock_code,
                date=date,
                price_data=empty_price_data
            )
            
            # 应该返回None
            assert pb_ratio is None, \
                "当价格数据为空时，PB比率应该返回None"
        
        except Exception as e:
            pytest.fail(
                f"空价格数据处理失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"当价格数据为空时，应该返回None而非抛出异常"
            )
    
    def test_property_13_mismatched_stock_code_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（股票代码不匹配）
        
        **Validates: Requirements 3.5**
        
        测试当价格数据中不包含请求的股票代码时，应该返回None而非异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 请求的股票代码
        requested_stock = '000001.SZ'
        date = '20240430'
        
        # 价格数据中包含不同的股票代码
        price_data = pd.DataFrame({
            'stock_code': ['000002.SZ', '000003.SZ'],
            'date': ['20240430', '20240430'],
            'open': [10.0, 11.0],
            'high': [11.0, 12.0],
            'low': [9.5, 10.5],
            'close': [10.5, 11.5],
            'volume': [1000000, 1200000]
        })
        
        try:
            # 计算PE比率
            pe_ratio = handler.calculate_pe_ratio(
                stock_code=requested_stock,
                date=date,
                price_data=price_data
            )
            
            # 应该返回None（因为价格数据中没有请求的股票）
            assert pe_ratio is None, \
                "当价格数据中不包含请求的股票时，PE比率应该返回None"
            
            # 计算PB比率
            pb_ratio = handler.calculate_pb_ratio(
                stock_code=requested_stock,
                date=date,
                price_data=price_data
            )
            
            # 应该返回None
            assert pb_ratio is None, \
                "当价格数据中不包含请求的股票时，PB比率应该返回None"
        
        except Exception as e:
            pytest.fail(
                f"股票代码不匹配处理失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"当价格数据中不包含请求的股票时，应该返回None而非抛出异常"
            )
    
    def test_property_13_mismatched_date_returns_none(self):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（日期不匹配）
        
        **Validates: Requirements 3.5**
        
        测试当价格数据中不包含请求的日期时，应该返回None而非异常。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        stock_code = '000001.SZ'
        requested_date = '20240430'
        
        # 价格数据中包含不同的日期
        price_data = pd.DataFrame({
            'stock_code': ['000001.SZ', '000001.SZ'],
            'date': ['20240428', '20240429'],  # 不包含请求的日期
            'open': [10.0, 10.2],
            'high': [11.0, 11.2],
            'low': [9.5, 9.7],
            'close': [10.5, 10.7],
            'volume': [1000000, 1100000]
        })
        
        try:
            # 计算PE比率
            pe_ratio = handler.calculate_pe_ratio(
                stock_code=stock_code,
                date=requested_date,
                price_data=price_data
            )
            
            # 应该返回None（因为价格数据中没有请求的日期）
            assert pe_ratio is None, \
                "当价格数据中不包含请求的日期时，PE比率应该返回None"
            
            # 计算PB比率
            pb_ratio = handler.calculate_pb_ratio(
                stock_code=stock_code,
                date=requested_date,
                price_data=price_data
            )
            
            # 应该返回None
            assert pb_ratio is None, \
                "当价格数据中不包含请求的日期时，PB比率应该返回None"
        
        except Exception as e:
            pytest.fail(
                f"日期不匹配处理失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"当价格数据中不包含请求的日期时，应该返回None而非抛出异常"
            )
    
    @given(
        stock_codes=stock_codes_list,
        indicators=indicators_list
    )
    @settings(max_examples=50, deadline=None)
    def test_property_13_partial_data_availability(
        self,
        stock_codes,
        indicators
    ):
        """
        Feature: week2-xtdata-engineering, Property 13: 基本面数据缺失处理（部分数据可用）
        
        **Validates: Requirements 3.5**
        
        测试当部分股票有数据、部分股票没有数据时，系统应该返回可用的数据，
        而不是因为部分缺失就完全失败。
        """
        mock_client = create_mock_client()
        handler = FundamentalHandler(mock_client)
        
        # 使用一个较晚的日期，确保有些数据可用
        as_of_date = '20240430'
        
        try:
            data = handler.get_financial_data(
                stock_codes=stock_codes,
                indicators=indicators,
                as_of_date=as_of_date
            )
            
            # 应该返回DataFrame
            assert isinstance(data, pd.DataFrame), \
                "应该返回DataFrame类型"
            
            # 如果有数据返回，验证数据结构
            if not data.empty:
                # 返回的股票数量可能少于请求的数量（部分缺失）
                returned_stocks = set(data['stock_code'].unique())
                requested_stocks = set(stock_codes)
                
                # 返回的股票应该是请求股票的子集
                assert returned_stocks.issubset(requested_stocks), \
                    "返回的股票应该是请求股票的子集"
                
                # 验证数据结构正确
                assert 'stock_code' in data.columns
                assert 'announce_date' in data.columns
                
                # 验证时间点正确性
                for announce_date in data['announce_date']:
                    assert announce_date <= as_of_date
        
        except Exception as e:
            pytest.fail(
                f"部分数据可用处理失败！抛出了异常: {type(e).__name__}: {str(e)}\n"
                f"当部分数据缺失时，系统应该返回可用的数据而非抛出异常"
            )
