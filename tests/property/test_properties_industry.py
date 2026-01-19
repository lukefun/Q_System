"""
行业分类映射器属性测试

使用基于属性的测试验证IndustryMapper的通用正确性属性
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from src.industry_mapper import IndustryMapper
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


# 行业代码生成策略（基于模拟数据中的行业代码）
industry_codes = st.sampled_from([
    '801010',  # 农林牧渔
    '801011',  # 农业
    '801012',  # 种植业
    '801013',  # 养殖业
    '801014',  # 林业
    '801015',  # 林木培育
    '801020',  # 采掘
    '801021',  # 煤炭开采
    '801022',  # 煤炭开采加工
    '801030',  # 化工
    '801031',  # 基础化工
    '801032',  # 化学原料
    '801033',  # 化学制品
    '801040',  # 钢铁
    '801041',  # 钢铁
    '801042',  # 普钢
    '801043',  # 特钢
    '801050',  # 有色金属
    '801051',  # 工业金属
    '801052',  # 铜
    '801053',  # 铝
])


# 行业名称生成策略
industry_names = st.sampled_from([
    '农林牧渔', '农业', '种植业', '养殖业', '林业', '林木培育',
    '采掘', '煤炭开采', '煤炭开采加工',
    '化工', '基础化工', '化学原料', '化学制品',
    '钢铁', '普钢', '特钢',
    '有色金属', '工业金属', '铜', '铝'
])


def create_mock_client():
    """创建mock客户端"""
    client = Mock()
    client.is_connected.return_value = True
    return client


# ============================================================================
# 属性14：行业成分股一致性
# ============================================================================

class TestProperty14IndustryConstituentsConsistency:
    """
    属性14：行业成分股一致性
    
    验证需求：4.3
    
    对于任何行业代码，get_industry_constituents返回的所有股票，
    在get_stock_industry查询时都应该返回该行业代码。
    
    这是行业映射的双向一致性：如果股票A属于行业X，那么行业X的
    成分股列表中应该包含股票A。反之亦然。
    """
    
    @given(industry_code=industry_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_14_constituents_match_stock_industry(
        self,
        industry_code
    ):
        """
        Feature: week2-xtdata-engineering, Property 14: 行业成分股一致性
        
        **Validates: Requirements 4.3**
        
        测试说明：
        1. 使用随机生成的行业代码
        2. 调用get_industry_constituents获取成分股列表
        3. 对每只成分股调用get_stock_industry
        4. 验证返回的行业分类包含原始行业代码
        
        这确保了行业映射的双向一致性：
        - 如果股票A在行业X的成分股列表中
        - 那么查询股票A的行业分类时，应该返回行业X
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 获取行业成分股
        constituents = mapper.get_industry_constituents(
            industry_code=industry_code
        )
        
        # 验证返回类型
        assert isinstance(constituents, list), \
            "get_industry_constituents应该返回列表"
        
        # 如果有成分股，验证一致性
        if constituents:
            for stock_code in constituents:
                # 查询该股票的行业分类
                stock_industry = mapper.get_stock_industry(stock_code)
                
                # 验证返回的行业分类包含原始行业代码
                # 行业代码可能在一级、二级或三级行业中
                industry_codes_in_stock = [
                    stock_industry['industry_l1_code'],
                    stock_industry['industry_l2_code'],
                    stock_industry['industry_l3_code']
                ]
                
                assert industry_code in industry_codes_in_stock, \
                    (f"行业成分股一致性违反！"
                     f"股票 {stock_code} 在行业 {industry_code} 的成分股列表中，"
                     f"但查询该股票的行业分类时，返回的行业代码为 "
                     f"{industry_codes_in_stock}，不包含 {industry_code}")
    
    def test_property_14_specific_industry_consistency(self):
        """
        Feature: week2-xtdata-engineering, Property 14: 行业成分股一致性（特定行业）
        
        **Validates: Requirements 4.3**
        
        测试特定行业的成分股一致性，使用模拟数据中已知的行业。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 测试农林牧渔行业（801010）
        constituents = mapper.get_industry_constituents(industry_code='801010')
        
        assert isinstance(constituents, list)
        
        # 验证每只成分股
        for stock_code in constituents:
            stock_industry = mapper.get_stock_industry(stock_code)
            
            # 应该属于农林牧渔行业
            assert stock_industry['industry_l1_code'] == '801010', \
                (f"股票 {stock_code} 在农林牧渔行业的成分股列表中，"
                 f"但其一级行业代码为 {stock_industry['industry_l1_code']}")
    
    @given(
        industry_code=industry_codes,
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_14_historical_consistency(
        self,
        industry_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 14: 行业成分股一致性（历史时点）
        
        **Validates: Requirements 4.3**
        
        测试历史时点的行业成分股一致性。
        
        在指定的历史日期，如果股票A在行业X的成分股列表中，
        那么查询股票A在该日期的行业分类时，应该返回行业X。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 获取历史时点的行业成分股
        constituents = mapper.get_industry_constituents(
            industry_code=industry_code,
            date=date
        )
        
        assert isinstance(constituents, list)
        
        # 验证每只成分股在该历史时点的行业分类
        if constituents:
            for stock_code in constituents:
                stock_industry = mapper.get_stock_industry(
                    stock_code=stock_code,
                    date=date
                )
                
                # 验证行业代码一致性
                industry_codes_in_stock = [
                    stock_industry['industry_l1_code'],
                    stock_industry['industry_l2_code'],
                    stock_industry['industry_l3_code']
                ]
                
                assert industry_code in industry_codes_in_stock, \
                    (f"历史时点行业成分股一致性违反！"
                     f"日期 {date}，股票 {stock_code} 在行业 {industry_code} "
                     f"的成分股列表中，但查询该股票的行业分类时，"
                     f"返回的行业代码为 {industry_codes_in_stock}")


# ============================================================================
# 属性15：历史行业分类时间点正确性
# ============================================================================

class TestProperty15HistoricalIndustryTimePointCorrectness:
    """
    属性15：历史行业分类时间点正确性
    
    验证需求：4.4, 4.5
    
    对于任何股票代码和历史日期，get_stock_industry应该返回在该日期
    有效的行业分类（effective_date <= 查询日期）。
    
    这是防止未来函数的关键属性：在回测中，我们只能使用在历史时点
    已经生效的行业分类，而不能使用未来的行业变更信息。
    """
    
    @given(
        stock_code=stock_code_strategy(),
        date=past_date_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_15_effective_date_before_query_date(
        self,
        stock_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 15: 历史行业分类时间点正确性
        
        **Validates: Requirements 4.4, 4.5**
        
        测试说明：
        1. 使用随机生成的股票代码和日期
        2. 调用get_stock_industry查询该日期的行业分类
        3. 验证返回的effective_date <= 查询日期
        
        这确保了在任何历史时点，我们只能看到已经生效的行业分类，
        而不会"穿越"到未来获取尚未生效的行业变更信息。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        try:
            # 查询历史时点的行业分类
            stock_industry = mapper.get_stock_industry(
                stock_code=stock_code,
                date=date
            )
            
            # 验证返回的是字典
            assert isinstance(stock_industry, dict), \
                "get_stock_industry应该返回字典"
            
            # 验证必需的字段存在
            assert 'effective_date' in stock_industry, \
                "返回的数据必须包含effective_date字段"
            
            effective_date = stock_industry['effective_date']
            
            # 核心验证：生效日期 <= 查询日期
            assert effective_date <= date, \
                (f"时间点正确性违反！股票 {stock_code} 的行业分类"
                 f"生效日期 {effective_date} 晚于查询日期 {date}。"
                 f"这会导致未来函数问题！")
        
        except Exception as e:
            # 如果股票不存在或数据缺失，应该抛出DataError
            # 这是可以接受的，不算违反属性
            from config import DataError
            if not isinstance(e, DataError):
                raise
    
    def test_property_15_industry_change_time_correctness(self):
        """
        Feature: week2-xtdata-engineering, Property 15: 历史行业分类时间点正确性（行业变更）
        
        **Validates: Requirements 4.4, 4.5**
        
        测试行业变更的时间点正确性。
        
        根据模拟数据，000001.SZ在2023年1月1日发生了行业变更：
        - 2023年之前：种植业（801012）
        - 2023年之后：养殖业（801013）
        
        验证在不同时点查询时，返回正确的行业分类。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        stock_code = '000001.SZ'
        
        # 查询2021年的行业分类（应该是种植业）
        industry_2021 = mapper.get_stock_industry(
            stock_code=stock_code,
            date='20210101'
        )
        
        # 验证生效日期在查询日期之前
        assert industry_2021['effective_date'] <= '20210101', \
            f"2021年查询的生效日期 {industry_2021['effective_date']} > 20210101"
        
        # 应该是种植业
        assert industry_2021['industry_l3_name'] == '种植业', \
            f"2021年应该是种植业，实际为 {industry_2021['industry_l3_name']}"
        
        # 查询2024年的行业分类（应该是养殖业）
        industry_2024 = mapper.get_stock_industry(
            stock_code=stock_code,
            date='20240101'
        )
        
        # 验证生效日期在查询日期之前
        assert industry_2024['effective_date'] <= '20240101', \
            f"2024年查询的生效日期 {industry_2024['effective_date']} > 20240101"
        
        # 应该是养殖业
        assert industry_2024['industry_l3_name'] == '养殖业', \
            f"2024年应该是养殖业，实际为 {industry_2024['industry_l3_name']}"
    
    def test_property_15_early_date_returns_earliest_classification(self):
        """
        Feature: week2-xtdata-engineering, Property 15: 历史行业分类时间点正确性（早期日期）
        
        **Validates: Requirements 4.4, 4.5**
        
        测试当查询一个很早的日期时，应该返回最早的行业分类
        （如果该日期在最早的生效日期之后）。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        stock_code = '000001.SZ'
        # 使用一个在最早生效日期之后的日期
        early_date = '20200601'
        
        try:
            industry = mapper.get_stock_industry(
                stock_code=stock_code,
                date=early_date
            )
            
            # 验证生效日期在查询日期之前
            assert industry['effective_date'] <= early_date, \
                (f"早期日期查询失败：生效日期 {industry['effective_date']} "
                 f"> 查询日期 {early_date}")
        
        except Exception as e:
            # 如果日期太早，没有数据，应该抛出DataError
            from config import DataError
            assert isinstance(e, DataError), \
                f"应该抛出DataError，实际抛出 {type(e).__name__}"
    
    @given(date=past_date_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_15_current_date_returns_latest_classification(
        self,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 15: 历史行业分类时间点正确性（最新分类）
        
        **Validates: Requirements 4.4, 4.5**
        
        测试查询任意日期时，应该返回该日期之前最新的行业分类。
        
        如果一只股票有多次行业变更，应该返回查询日期之前
        最近的一次变更后的行业分类。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 使用模拟数据中有行业变更的股票
        stock_code = '000001.SZ'
        
        try:
            industry = mapper.get_stock_industry(
                stock_code=stock_code,
                date=date
            )
            
            # 验证生效日期在查询日期之前
            effective_date = industry['effective_date']
            assert effective_date <= date, \
                (f"时间点正确性违反：生效日期 {effective_date} "
                 f"> 查询日期 {date}")
            
            # 获取所有历史行业分类记录
            mapping_df = mapper._get_stock_industry_mapping()
            stock_records = mapping_df[
                (mapping_df['stock_code'] == stock_code) &
                (mapping_df['effective_date'] <= date)
            ]
            
            # 如果有多条记录，返回的应该是最新的
            if not stock_records.empty:
                latest_effective_date = stock_records['effective_date'].max()
                assert effective_date == latest_effective_date, \
                    (f"应该返回最新的行业分类！"
                     f"返回的生效日期 {effective_date}，"
                     f"但最新的生效日期是 {latest_effective_date}")
        
        except Exception as e:
            from config import DataError
            if not isinstance(e, DataError):
                raise


# ============================================================================
# 属性16：行业查询方式一致性
# ============================================================================

class TestProperty16IndustryQueryMethodConsistency:
    """
    属性16：行业查询方式一致性
    
    验证需求：4.6
    
    对于任何行业，按行业代码查询和按行业名称查询应该返回相同的成分股列表。
    
    这确保了查询接口的一致性：无论用户使用行业代码还是行业名称，
    都应该得到相同的结果。
    """
    
    @given(industry_code=industry_codes)
    @settings(max_examples=100, deadline=None)
    def test_property_16_code_and_name_query_consistency(
        self,
        industry_code
    ):
        """
        Feature: week2-xtdata-engineering, Property 16: 行业查询方式一致性
        
        **Validates: Requirements 4.6**
        
        测试说明：
        1. 使用随机生成的行业代码
        2. 按行业代码查询成分股
        3. 获取该行业代码对应的行业名称
        4. 按行业名称查询成分股
        5. 验证两次查询的结果一致
        
        这确保了查询接口的一致性：代码和名称查询应该返回相同的结果。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 按行业代码查询
        constituents_by_code = mapper.get_industry_constituents(
            industry_code=industry_code
        )
        
        assert isinstance(constituents_by_code, list)
        
        # 获取行业结构，找到对应的行业名称
        structure = mapper.get_industry_structure()
        industry_name = None
        
        # 在行业结构中查找行业名称
        for l1 in structure['level1']:
            if l1['code'] == industry_code:
                industry_name = l1['name']
                break
            for l2 in l1.get('level2', []):
                if l2['code'] == industry_code:
                    industry_name = l2['name']
                    break
                for l3 in l2.get('level3', []):
                    if l3['code'] == industry_code:
                        industry_name = l3['name']
                        break
                if industry_name:
                    break
            if industry_name:
                break
        
        # 如果找到了行业名称，按名称查询并验证一致性
        if industry_name:
            constituents_by_name = mapper.get_industry_constituents(
                industry_name=industry_name
            )
            
            assert isinstance(constituents_by_name, list)
            
            # 验证两次查询的结果一致
            assert set(constituents_by_code) == set(constituents_by_name), \
                (f"行业查询方式一致性违反！"
                 f"按代码 {industry_code} 查询得到 {len(constituents_by_code)} 只股票，"
                 f"按名称 {industry_name} 查询得到 {len(constituents_by_name)} 只股票。"
                 f"两次查询结果不一致！")
    
    def test_property_16_specific_industry_consistency(self):
        """
        Feature: week2-xtdata-engineering, Property 16: 行业查询方式一致性（特定行业）
        
        **Validates: Requirements 4.6**
        
        测试特定行业的查询方式一致性，使用模拟数据中已知的行业。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 测试农林牧渔行业
        constituents_by_code = mapper.get_industry_constituents(
            industry_code='801010'
        )
        
        constituents_by_name = mapper.get_industry_constituents(
            industry_name='农林牧渔'
        )
        
        # 验证结果一致
        assert set(constituents_by_code) == set(constituents_by_name), \
            (f"农林牧渔行业查询不一致！"
             f"按代码查询: {constituents_by_code}，"
             f"按名称查询: {constituents_by_name}")
    
    @given(
        industry_code=industry_codes,
        date=past_date_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_16_historical_query_consistency(
        self,
        industry_code,
        date
    ):
        """
        Feature: week2-xtdata-engineering, Property 16: 行业查询方式一致性（历史时点）
        
        **Validates: Requirements 4.6**
        
        测试历史时点的查询方式一致性。
        
        在指定的历史日期，按代码和按名称查询应该返回相同的成分股列表。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 按行业代码查询历史成分股
        constituents_by_code = mapper.get_industry_constituents(
            industry_code=industry_code,
            date=date
        )
        
        assert isinstance(constituents_by_code, list)
        
        # 获取行业名称
        structure = mapper.get_industry_structure()
        industry_name = None
        
        for l1 in structure['level1']:
            if l1['code'] == industry_code:
                industry_name = l1['name']
                break
            for l2 in l1.get('level2', []):
                if l2['code'] == industry_code:
                    industry_name = l2['name']
                    break
                for l3 in l2.get('level3', []):
                    if l3['code'] == industry_code:
                        industry_name = l3['name']
                        break
                if industry_name:
                    break
            if industry_name:
                break
        
        # 如果找到了行业名称，按名称查询并验证一致性
        if industry_name:
            constituents_by_name = mapper.get_industry_constituents(
                industry_name=industry_name,
                date=date
            )
            
            assert isinstance(constituents_by_name, list)
            
            # 验证两次查询的结果一致
            assert set(constituents_by_code) == set(constituents_by_name), \
                (f"历史时点行业查询方式一致性违反！"
                 f"日期 {date}，行业 {industry_code}/{industry_name}，"
                 f"按代码查询得到 {len(constituents_by_code)} 只股票，"
                 f"按名称查询得到 {len(constituents_by_name)} 只股票。"
                 f"两次查询结果不一致！")
    
    def test_property_16_all_levels_consistency(self):
        """
        Feature: week2-xtdata-engineering, Property 16: 行业查询方式一致性（所有层级）
        
        **Validates: Requirements 4.6**
        
        测试所有层级（一级、二级、三级）的查询方式一致性。
        """
        mock_client = create_mock_client()
        mapper = IndustryMapper(mock_client)
        
        # 测试一级行业
        l1_by_code = mapper.get_industry_constituents(industry_code='801010')
        l1_by_name = mapper.get_industry_constituents(industry_name='农林牧渔')
        assert set(l1_by_code) == set(l1_by_name), \
            "一级行业查询方式不一致"
        
        # 测试二级行业
        l2_by_code = mapper.get_industry_constituents(industry_code='801011')
        l2_by_name = mapper.get_industry_constituents(industry_name='农业')
        assert set(l2_by_code) == set(l2_by_name), \
            "二级行业查询方式不一致"
        
        # 测试三级行业
        l3_by_code = mapper.get_industry_constituents(industry_code='801012')
        l3_by_name = mapper.get_industry_constituents(industry_name='种植业')
        assert set(l3_by_code) == set(l3_by_name), \
            "三级行业查询方式不一致"
