"""
行业映射器单元测试

测试IndustryMapper类的基本功能和错误处理
"""

import pytest
import pandas as pd
from unittest.mock import Mock
from src.industry_mapper import IndustryMapper
from config import DataError, ValidationError, ConnectionError


class TestIndustryMapperInit:
    """测试IndustryMapper初始化"""
    
    def test_init_with_valid_client(self, mock_xtdata_client):
        """测试使用有效客户端初始化"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        assert mapper.client == mock_xtdata_client
        assert mapper._industry_cache == {}
    
    def test_init_with_none_client(self):
        """测试使用None客户端初始化应该失败"""
        with pytest.raises(ValueError, match="XtDataClient不能为None"):
            IndustryMapper(None)


class TestGetIndustryStructure:
    """测试获取行业结构"""
    
    def test_get_industry_structure_success(self, mock_xtdata_client):
        """测试成功获取行业结构"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        structure = mapper.get_industry_structure()
        
        # 验证结构
        assert 'level1' in structure
        assert isinstance(structure['level1'], list)
        assert len(structure['level1']) > 0
        
        # 验证一级行业
        l1 = structure['level1'][0]
        assert 'code' in l1
        assert 'name' in l1
        assert 'level2' in l1
        
        # 验证二级行业
        if l1['level2']:
            l2 = l1['level2'][0]
            assert 'code' in l2
            assert 'name' in l2
            assert 'level3' in l2
    
    def test_get_industry_structure_caching(self, mock_xtdata_client):
        """测试行业结构缓存机制"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 第一次调用
        structure1 = mapper.get_industry_structure()
        
        # 第二次调用应该从缓存返回
        structure2 = mapper.get_industry_structure()
        
        # 应该是同一个对象（从缓存返回）
        assert structure1 is structure2
    
    def test_get_industry_structure_not_connected(self, mock_xtdata_client):
        """测试客户端未连接时获取行业结构"""
        mock_xtdata_client.is_connected.return_value = False
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(Exception) as exc_info:
            mapper.get_industry_structure()
        
        assert "XtData客户端未连接" in str(exc_info.value)


class TestGetStockIndustry:
    """测试获取股票行业分类"""
    
    def test_get_stock_industry_current(self, mock_xtdata_client):
        """测试获取股票当前行业分类"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        industry = mapper.get_stock_industry('000001.SZ')
        
        # 验证返回结构
        assert 'stock_code' in industry
        assert 'effective_date' in industry
        assert 'industry_l1_code' in industry
        assert 'industry_l1_name' in industry
        assert 'industry_l2_code' in industry
        assert 'industry_l2_name' in industry
        assert 'industry_l3_code' in industry
        assert 'industry_l3_name' in industry
        
        assert industry['stock_code'] == '000001.SZ'
    
    def test_get_stock_industry_historical(self, mock_xtdata_client):
        """测试获取股票历史行业分类"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询历史日期
        industry_old = mapper.get_stock_industry('000001.SZ', '20210101')
        industry_new = mapper.get_stock_industry('000001.SZ', '20240101')
        
        # 验证时间点正确性
        assert industry_old['effective_date'] <= '20210101'
        assert industry_new['effective_date'] <= '20240101'
        
        # 由于模拟数据中000001.SZ在2023年有行业变更
        # 2021年应该是种植业，2024年应该是养殖业
        assert industry_old['industry_l3_name'] == '种植业'
        assert industry_new['industry_l3_name'] == '养殖业'
    
    def test_get_stock_industry_invalid_code(self, mock_xtdata_client):
        """测试无效股票代码"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的股票代码格式"):
            mapper.get_stock_industry('000001')
        
        with pytest.raises(ValueError, match="无效的股票代码"):
            mapper.get_stock_industry('00001.SZ')
        
        with pytest.raises(ValueError, match="无效的市场代码"):
            mapper.get_stock_industry('000001.XX')
    
    def test_get_stock_industry_not_found(self, mock_xtdata_client):
        """测试股票不存在"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(DataError, match="未找到股票.*的行业分类数据"):
            mapper.get_stock_industry('999999.SZ')
    
    def test_get_stock_industry_invalid_date(self, mock_xtdata_client):
        """测试无效日期格式"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的日期格式"):
            mapper.get_stock_industry('000001.SZ', '2024-01-01')
    
    def test_get_stock_industry_not_connected(self, mock_xtdata_client):
        """测试客户端未连接"""
        mock_xtdata_client.is_connected.return_value = False
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(Exception) as exc_info:
            mapper.get_stock_industry('000001.SZ')
        
        assert "XtData客户端未连接" in str(exc_info.value)


class TestGetIndustryConstituents:
    """测试获取行业成分股"""
    
    def test_get_constituents_by_code_l1(self, mock_xtdata_client):
        """测试按一级行业代码查询成分股"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询农林牧渔行业（801010）
        constituents = mapper.get_industry_constituents(industry_code='801010')
        
        assert isinstance(constituents, list)
        assert len(constituents) > 0
        # 000001.SZ应该在农林牧渔行业中
        assert '000001.SZ' in constituents
    
    def test_get_constituents_by_code_l2(self, mock_xtdata_client):
        """测试按二级行业代码查询成分股"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询农业行业（801011）
        constituents = mapper.get_industry_constituents(industry_code='801011')
        
        assert isinstance(constituents, list)
        assert '000001.SZ' in constituents
    
    def test_get_constituents_by_code_l3(self, mock_xtdata_client):
        """测试按三级行业代码查询成分股"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询养殖业行业（801013）- 000001.SZ在2023年后属于此行业
        constituents = mapper.get_industry_constituents(industry_code='801013')
        
        assert isinstance(constituents, list)
        assert '000001.SZ' in constituents
    
    def test_get_constituents_by_name(self, mock_xtdata_client):
        """测试按行业名称查询成分股"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询农林牧渔行业
        constituents = mapper.get_industry_constituents(industry_name='农林牧渔')
        
        assert isinstance(constituents, list)
        assert len(constituents) > 0
        assert '000001.SZ' in constituents
    
    def test_get_constituents_historical(self, mock_xtdata_client):
        """测试查询历史成分股"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询2021年的养殖业成分股
        constituents_old = mapper.get_industry_constituents(
            industry_code='801013',
            date='20210101'
        )
        
        # 查询2024年的养殖业成分股
        constituents_new = mapper.get_industry_constituents(
            industry_code='801013',
            date='20240101'
        )
        
        # 2021年000001.SZ还是种植业，不在养殖业中
        assert '000001.SZ' not in constituents_old
        
        # 2024年000001.SZ已经是养殖业
        assert '000001.SZ' in constituents_new
    
    def test_get_constituents_no_params(self, mock_xtdata_client):
        """测试不提供任何参数"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="必须提供industry_code或industry_name"):
            mapper.get_industry_constituents()
    
    def test_get_constituents_invalid_industry_name(self, mock_xtdata_client):
        """测试无效的行业名称"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(DataError, match="未找到行业名称"):
            mapper.get_industry_constituents(industry_name='不存在的行业')
    
    def test_get_constituents_empty_result(self, mock_xtdata_client):
        """测试查询结果为空"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 查询一个不存在的行业代码
        constituents = mapper.get_industry_constituents(industry_code='999999')
        
        assert constituents == []
    
    def test_get_constituents_not_connected(self, mock_xtdata_client):
        """测试客户端未连接"""
        mock_xtdata_client.is_connected.return_value = False
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(Exception) as exc_info:
            mapper.get_industry_constituents(industry_code='801010')
        
        assert "XtData客户端未连接" in str(exc_info.value)


class TestIndustryQueryConsistency:
    """测试行业查询方式一致性"""
    
    def test_query_by_code_and_name_consistency(self, mock_xtdata_client):
        """测试按代码和名称查询结果一致"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 按代码查询
        constituents_by_code = mapper.get_industry_constituents(
            industry_code='801010'
        )
        
        # 按名称查询
        constituents_by_name = mapper.get_industry_constituents(
            industry_name='农林牧渔'
        )
        
        # 结果应该一致
        assert set(constituents_by_code) == set(constituents_by_name)


class TestCacheManagement:
    """测试缓存管理"""
    
    def test_clear_cache(self, mock_xtdata_client):
        """测试清除缓存"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 获取数据（会缓存）
        structure1 = mapper.get_industry_structure()
        assert mapper._industry_cache  # 缓存不为空
        
        # 清除缓存
        mapper.clear_cache()
        assert not mapper._industry_cache  # 缓存为空
        
        # 再次获取数据
        structure2 = mapper.get_industry_structure()
        
        # 应该是不同的对象（重新获取）
        assert structure1 is not structure2


class TestStockIndustryMapping:
    """测试股票-行业映射内部方法"""
    
    def test_get_stock_industry_mapping(self, mock_xtdata_client):
        """测试获取股票-行业映射数据"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        mapping_df = mapper._get_stock_industry_mapping()
        
        # 验证DataFrame结构
        assert isinstance(mapping_df, pd.DataFrame)
        assert not mapping_df.empty
        
        # 验证必需的列
        required_columns = [
            'stock_code', 'effective_date',
            'industry_l1_code', 'industry_l1_name',
            'industry_l2_code', 'industry_l2_name',
            'industry_l3_code', 'industry_l3_name'
        ]
        for col in required_columns:
            assert col in mapping_df.columns
    
    def test_mapping_caching(self, mock_xtdata_client):
        """测试映射数据缓存"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 第一次调用
        mapping1 = mapper._get_stock_industry_mapping()
        
        # 第二次调用应该从缓存返回
        mapping2 = mapper._get_stock_industry_mapping()
        
        # 应该是同一个对象
        assert mapping1 is mapping2


class TestIndustryNameMapping:
    """测试行业名称映射"""
    
    def test_build_industry_name_mapping(self, mock_xtdata_client):
        """测试构建行业名称映射"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 获取行业结构（会自动构建名称映射）
        structure = mapper.get_industry_structure()
        
        # 验证映射已构建
        assert 'code_to_name' in mapper._industry_cache
        assert 'name_to_code' in mapper._industry_cache
        
        code_to_name = mapper._industry_cache['code_to_name']
        name_to_code = mapper._industry_cache['name_to_code']
        
        # 验证映射内容
        assert '801010' in code_to_name
        assert code_to_name['801010'] == '农林牧渔'
        assert '农林牧渔' in name_to_code
        assert name_to_code['农林牧渔'] == '801010'
    
    def test_get_industry_code_by_name(self, mock_xtdata_client):
        """测试根据名称获取代码"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 先加载行业结构
        mapper.get_industry_structure()
        
        # 获取行业代码
        code = mapper._get_industry_code_by_name('农林牧渔')
        assert code == '801010'
        
        code = mapper._get_industry_code_by_name('农业')
        assert code == '801011'
    
    def test_get_industry_code_by_invalid_name(self, mock_xtdata_client):
        """测试无效的行业名称"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 先加载行业结构
        mapper.get_industry_structure()
        
        with pytest.raises(DataError, match="未找到行业名称"):
            mapper._get_industry_code_by_name('不存在的行业')


class TestParameterValidation:
    """测试参数验证"""
    
    def test_validate_stock_code_valid(self, mock_xtdata_client):
        """测试有效股票代码验证"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 不应该抛出异常
        mapper._validate_stock_code('000001.SZ')
        mapper._validate_stock_code('600000.SH')
    
    def test_validate_stock_code_invalid(self, mock_xtdata_client):
        """测试无效股票代码验证"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(ValueError):
            mapper._validate_stock_code('')
        
        with pytest.raises(ValueError):
            mapper._validate_stock_code('000001')
        
        with pytest.raises(ValueError):
            mapper._validate_stock_code('00001.SZ')
        
        with pytest.raises(ValueError):
            mapper._validate_stock_code('000001.XX')
    
    def test_validate_date_valid(self, mock_xtdata_client):
        """测试有效日期验证"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        # 不应该抛出异常
        mapper._validate_date('20240101')
        mapper._validate_date('20231231')
    
    def test_validate_date_invalid(self, mock_xtdata_client):
        """测试无效日期验证"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        with pytest.raises(ValueError, match="无效的日期格式"):
            mapper._validate_date('2024-01-01')
        
        with pytest.raises(ValueError, match="无效的日期格式"):
            mapper._validate_date('20240132')  # 无效日期
        
        with pytest.raises(ValueError, match="无效的日期格式"):
            mapper._validate_date('invalid')


class TestRepr:
    """测试字符串表示"""
    
    def test_repr(self, mock_xtdata_client):
        """测试__repr__方法"""
        mapper = IndustryMapper(mock_xtdata_client)
        
        repr_str = repr(mapper)
        assert 'IndustryMapper' in repr_str
        assert 'cache' in repr_str
