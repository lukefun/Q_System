"""
行业分类映射器模块

管理申万行业分类和股票-行业映射关系，支持历史时点查询
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime
from config import (
    logger,
    DataError,
    ValidationError,
    CACHE_DIR
)
from src.xtdata_client import XtDataClient


class IndustryMapper:
    """
    行业分类映射器
    
    管理申万行业分类体系和股票-行业映射关系。支持三级行业分类查询、
    历史时点查询和行业成分股查询。实现缓存机制以提高查询效率。
    
    Attributes:
        client: XtData客户端实例
        _industry_cache: 行业数据缓存字典
    
    Example:
        >>> client = XtDataClient(account_id="test", account_key="test")
        >>> client.connect()
        >>> mapper = IndustryMapper(client)
        >>> structure = mapper.get_industry_structure()
        >>> industry = mapper.get_stock_industry('000001.SZ')
        >>> constituents = mapper.get_industry_constituents('801010')
    """
    
    def __init__(self, client: XtDataClient):
        """
        初始化行业映射器
        
        Args:
            client: XtData客户端实例
        
        Raises:
            ValueError: 客户端为None
        """
        if client is None:
            raise ValueError("XtDataClient不能为None")
        
        self.client = client
        
        # 缓存结构：
        # {
        #     'structure': {...},  # 行业层级结构
        #     'stock_mapping': pd.DataFrame,  # 股票-行业映射
        #     'industry_names': {...},  # 行业代码到名称的映射
        #     'last_update': datetime  # 最后更新时间
        # }
        self._industry_cache = {}
        
        logger.info("IndustryMapper初始化完成")
    
    def get_industry_structure(self) -> Dict[str, Any]:
        """
        获取申万行业分类层级结构
        
        返回完整的申万行业三级分类体系，包括一级、二级、三级行业的
        代码和名称。结果会被缓存以提高后续查询效率。
        
        Returns:
            行业层级字典，包含一级、二级、三级行业
            格式：
            {
                'level1': [
                    {
                        'code': '801010',
                        'name': '农林牧渔',
                        'level2': [
                            {
                                'code': '801011',
                                'name': '农业',
                                'level3': [
                                    {'code': '801012', 'name': '种植业'},
                                    {'code': '801013', 'name': '养殖业'}
                                ]
                            }
                        ]
                    }
                ]
            }
        
        Raises:
            ConnectionError: 客户端未连接
            DataError: 数据获取失败
        
        Example:
            >>> structure = mapper.get_industry_structure()
            >>> for l1 in structure['level1']:
            ...     print(f"一级行业: {l1['name']}")
        """
        # 检查缓存
        if 'structure' in self._industry_cache:
            logger.debug("从缓存返回行业结构")
            return self._industry_cache['structure']
        
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info("获取申万行业分类结构")
        
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_industry_list()
            
            # 模拟申万行业分类结构
            structure = {
                'level1': [
                    {
                        'code': '801010',
                        'name': '农林牧渔',
                        'level2': [
                            {
                                'code': '801011',
                                'name': '农业',
                                'level3': [
                                    {'code': '801012', 'name': '种植业'},
                                    {'code': '801013', 'name': '养殖业'}
                                ]
                            },
                            {
                                'code': '801014',
                                'name': '林业',
                                'level3': [
                                    {'code': '801015', 'name': '林木培育'}
                                ]
                            }
                        ]
                    },
                    {
                        'code': '801020',
                        'name': '采掘',
                        'level2': [
                            {
                                'code': '801021',
                                'name': '煤炭开采',
                                'level3': [
                                    {'code': '801022', 'name': '煤炭开采加工'}
                                ]
                            }
                        ]
                    },
                    {
                        'code': '801030',
                        'name': '化工',
                        'level2': [
                            {
                                'code': '801031',
                                'name': '基础化工',
                                'level3': [
                                    {'code': '801032', 'name': '化学原料'},
                                    {'code': '801033', 'name': '化学制品'}
                                ]
                            }
                        ]
                    },
                    {
                        'code': '801040',
                        'name': '钢铁',
                        'level2': [
                            {
                                'code': '801041',
                                'name': '钢铁',
                                'level3': [
                                    {'code': '801042', 'name': '普钢'},
                                    {'code': '801043', 'name': '特钢'}
                                ]
                            }
                        ]
                    },
                    {
                        'code': '801050',
                        'name': '有色金属',
                        'level2': [
                            {
                                'code': '801051',
                                'name': '工业金属',
                                'level3': [
                                    {'code': '801052', 'name': '铜'},
                                    {'code': '801053', 'name': '铝'}
                                ]
                            }
                        ]
                    }
                ]
            }
            
            # 缓存结果
            self._industry_cache['structure'] = structure
            
            # 同时构建行业代码到名称的映射缓存
            self._build_industry_name_mapping(structure)
            
            logger.info(f"行业结构获取完成: {len(structure['level1'])} 个一级行业")
            
            return structure
        
        except Exception as e:
            error_msg = f"获取行业结构失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def get_stock_industry(
        self,
        stock_code: str,
        date: Optional[str] = None
    ) -> Dict[str, str]:
        """
        获取股票的行业分类
        
        查询指定股票在指定日期的行业分类信息，包括一级、二级、三级行业
        的代码和名称。支持历史时点查询，使用effective_date进行过滤。
        
        Args:
            stock_code: 股票代码，如 '000001.SZ'
            date: 查询日期，格式 'YYYYMMDD'，None表示当前最新
        
        Returns:
            包含各级行业代码和名称的字典
            格式：
            {
                'stock_code': '000001.SZ',
                'effective_date': '20240101',
                'industry_l1_code': '801010',
                'industry_l1_name': '农林牧渔',
                'industry_l2_code': '801011',
                'industry_l2_name': '农业',
                'industry_l3_code': '801012',
                'industry_l3_name': '种植业'
            }
        
        Raises:
            ConnectionError: 客户端未连接
            ValueError: 股票代码或日期格式无效
            DataError: 数据获取失败或股票不存在
        
        Example:
            >>> # 查询当前行业分类
            >>> industry = mapper.get_stock_industry('000001.SZ')
            >>> print(f"一级行业: {industry['industry_l1_name']}")
            >>> 
            >>> # 查询历史行业分类
            >>> industry = mapper.get_stock_industry('000001.SZ', '20200101')
        """
        # 参数验证
        self._validate_stock_code(stock_code)
        if date is not None:
            self._validate_date(date)
        
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        logger.info(f"查询股票 {stock_code} 的行业分类，日期: {date or '当前'}")
        
        try:
            # 获取股票-行业映射数据
            mapping_df = self._get_stock_industry_mapping()
            
            # 过滤股票代码
            stock_data = mapping_df[mapping_df['stock_code'] == stock_code]
            
            if stock_data.empty:
                raise DataError(f"未找到股票 {stock_code} 的行业分类数据")
            
            # 时间点过滤
            if date is not None:
                # 获取指定日期或之前的最新记录
                stock_data = stock_data[stock_data['effective_date'] <= date]
                
                if stock_data.empty:
                    raise DataError(
                        f"未找到股票 {stock_code} 在日期 {date} 或之前的行业分类数据"
                    )
            
            # 获取最新的记录（按effective_date降序排序后取第一条）
            latest_record = stock_data.sort_values(
                'effective_date',
                ascending=False
            ).iloc[0]
            
            result = {
                'stock_code': latest_record['stock_code'],
                'effective_date': latest_record['effective_date'],
                'industry_l1_code': latest_record['industry_l1_code'],
                'industry_l1_name': latest_record['industry_l1_name'],
                'industry_l2_code': latest_record['industry_l2_code'],
                'industry_l2_name': latest_record['industry_l2_name'],
                'industry_l3_code': latest_record['industry_l3_code'],
                'industry_l3_name': latest_record['industry_l3_name']
            }
            
            logger.debug(
                f"股票 {stock_code} 行业分类: "
                f"{result['industry_l1_name']} > "
                f"{result['industry_l2_name']} > "
                f"{result['industry_l3_name']}"
            )
            
            return result
        
        except DataError:
            raise
        except Exception as e:
            error_msg = f"查询股票行业分类失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def get_industry_constituents(
        self,
        industry_code: Optional[str] = None,
        industry_name: Optional[str] = None,
        date: Optional[str] = None
    ) -> List[str]:
        """
        获取行业成分股
        
        查询指定行业在指定日期的所有成分股。支持按行业代码或行业名称查询，
        支持历史时点查询。
        
        Args:
            industry_code: 行业代码，如 '801010'（一级）、'801011'（二级）、'801012'（三级）
            industry_name: 行业名称，如 '农林牧渔'、'农业'、'种植业'
            date: 查询日期，格式 'YYYYMMDD'，None表示当前最新
        
        Returns:
            股票代码列表
        
        Raises:
            ConnectionError: 客户端未连接
            ValueError: 参数无效（必须提供industry_code或industry_name之一）
            DataError: 数据获取失败或行业不存在
        
        Example:
            >>> # 按行业代码查询
            >>> stocks = mapper.get_industry_constituents(industry_code='801010')
            >>> print(f"农林牧渔行业共有 {len(stocks)} 只股票")
            >>> 
            >>> # 按行业名称查询
            >>> stocks = mapper.get_industry_constituents(industry_name='农业')
            >>> 
            >>> # 查询历史成分股
            >>> stocks = mapper.get_industry_constituents(
            ...     industry_code='801010',
            ...     date='20200101'
            ... )
        """
        # 参数验证
        if industry_code is None and industry_name is None:
            raise ValueError("必须提供industry_code或industry_name参数之一")
        
        if date is not None:
            self._validate_date(date)
        
        # 检查连接状态
        if not self.client.is_connected():
            raise ConnectionError("XtData客户端未连接，请先调用client.connect()")
        
        # 如果提供了行业名称，转换为行业代码
        if industry_name is not None and industry_code is None:
            industry_code = self._get_industry_code_by_name(industry_name)
        
        logger.info(
            f"查询行业 {industry_code} 的成分股，日期: {date or '当前'}"
        )
        
        try:
            # 获取股票-行业映射数据
            mapping_df = self._get_stock_industry_mapping()
            
            # 时间点过滤
            if date is not None:
                mapping_df = mapping_df[mapping_df['effective_date'] <= date]
                
                if mapping_df.empty:
                    logger.warning(f"日期 {date} 或之前没有行业映射数据")
                    return []
            
            # 对每只股票，获取最新的行业分类记录
            latest_mapping = mapping_df.sort_values(
                'effective_date',
                ascending=False
            ).groupby('stock_code').first().reset_index()
            
            # 过滤行业代码（匹配一级、二级或三级行业）
            constituents = latest_mapping[
                (latest_mapping['industry_l1_code'] == industry_code) |
                (latest_mapping['industry_l2_code'] == industry_code) |
                (latest_mapping['industry_l3_code'] == industry_code)
            ]
            
            if constituents.empty:
                logger.warning(f"行业 {industry_code} 没有成分股")
                return []
            
            stock_list = constituents['stock_code'].tolist()
            
            logger.info(
                f"行业 {industry_code} 成分股查询完成: {len(stock_list)} 只股票"
            )
            
            return stock_list
        
        except Exception as e:
            error_msg = f"查询行业成分股失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    # ========================================================================
    # 内部辅助方法
    # ========================================================================
    
    def _get_stock_industry_mapping(self) -> pd.DataFrame:
        """
        获取股票-行业映射数据
        
        从缓存或API获取完整的股票-行业映射表。
        
        Returns:
            股票-行业映射DataFrame
        """
        # 检查缓存
        if 'stock_mapping' in self._industry_cache:
            logger.debug("从缓存返回股票-行业映射")
            return self._industry_cache['stock_mapping']
        
        logger.debug("获取股票-行业映射数据")
        
        try:
            # 注意：这里是模拟数据获取
            # 实际实现需要调用xtquant的API
            # 例如：xtdata.get_stock_industry()
            
            # 模拟股票-行业映射数据
            mapping_data = [
                # 000001.SZ - 农林牧渔 > 农业 > 种植业
                {
                    'stock_code': '000001.SZ',
                    'effective_date': '20200101',
                    'industry_l1_code': '801010',
                    'industry_l1_name': '农林牧渔',
                    'industry_l2_code': '801011',
                    'industry_l2_name': '农业',
                    'industry_l3_code': '801012',
                    'industry_l3_name': '种植业'
                },
                # 000001.SZ 行业变更（模拟历史变化）
                {
                    'stock_code': '000001.SZ',
                    'effective_date': '20230101',
                    'industry_l1_code': '801010',
                    'industry_l1_name': '农林牧渔',
                    'industry_l2_code': '801011',
                    'industry_l2_name': '农业',
                    'industry_l3_code': '801013',
                    'industry_l3_name': '养殖业'
                },
                # 000002.SZ - 采掘 > 煤炭开采 > 煤炭开采加工
                {
                    'stock_code': '000002.SZ',
                    'effective_date': '20200101',
                    'industry_l1_code': '801020',
                    'industry_l1_name': '采掘',
                    'industry_l2_code': '801021',
                    'industry_l2_name': '煤炭开采',
                    'industry_l3_code': '801022',
                    'industry_l3_name': '煤炭开采加工'
                },
                # 600000.SH - 化工 > 基础化工 > 化学原料
                {
                    'stock_code': '600000.SH',
                    'effective_date': '20200101',
                    'industry_l1_code': '801030',
                    'industry_l1_name': '化工',
                    'industry_l2_code': '801031',
                    'industry_l2_name': '基础化工',
                    'industry_l3_code': '801032',
                    'industry_l3_name': '化学原料'
                },
                # 600001.SH - 钢铁 > 钢铁 > 普钢
                {
                    'stock_code': '600001.SH',
                    'effective_date': '20200101',
                    'industry_l1_code': '801040',
                    'industry_l1_name': '钢铁',
                    'industry_l2_code': '801041',
                    'industry_l2_name': '钢铁',
                    'industry_l3_code': '801042',
                    'industry_l3_name': '普钢'
                },
                # 600002.SH - 有色金属 > 工业金属 > 铜
                {
                    'stock_code': '600002.SH',
                    'effective_date': '20200101',
                    'industry_l1_code': '801050',
                    'industry_l1_name': '有色金属',
                    'industry_l2_code': '801051',
                    'industry_l2_name': '工业金属',
                    'industry_l3_code': '801052',
                    'industry_l3_name': '铜'
                }
            ]
            
            mapping_df = pd.DataFrame(mapping_data)
            
            # 缓存结果
            self._industry_cache['stock_mapping'] = mapping_df
            
            logger.debug(f"股票-行业映射数据获取完成: {len(mapping_df)} 条记录")
            
            return mapping_df
        
        except Exception as e:
            error_msg = f"获取股票-行业映射数据失败: {str(e)}"
            logger.error(error_msg)
            raise DataError(error_msg) from e
    
    def _build_industry_name_mapping(self, structure: Dict[str, Any]) -> None:
        """
        构建行业代码到名称的映射
        
        从行业结构中提取所有行业的代码和名称，构建双向映射缓存。
        
        Args:
            structure: 行业层级结构
        """
        code_to_name = {}
        name_to_code = {}
        
        for l1 in structure['level1']:
            code_to_name[l1['code']] = l1['name']
            name_to_code[l1['name']] = l1['code']
            
            for l2 in l1.get('level2', []):
                code_to_name[l2['code']] = l2['name']
                name_to_code[l2['name']] = l2['code']
                
                for l3 in l2.get('level3', []):
                    code_to_name[l3['code']] = l3['name']
                    name_to_code[l3['name']] = l3['code']
        
        self._industry_cache['code_to_name'] = code_to_name
        self._industry_cache['name_to_code'] = name_to_code
        
        logger.debug(f"行业名称映射构建完成: {len(code_to_name)} 个行业")
    
    def _get_industry_code_by_name(self, industry_name: str) -> str:
        """
        根据行业名称获取行业代码
        
        Args:
            industry_name: 行业名称
        
        Returns:
            行业代码
        
        Raises:
            DataError: 行业名称不存在
        """
        # 确保已加载行业结构
        if 'name_to_code' not in self._industry_cache:
            self.get_industry_structure()
        
        name_to_code = self._industry_cache['name_to_code']
        
        if industry_name not in name_to_code:
            raise DataError(f"未找到行业名称: {industry_name}")
        
        return name_to_code[industry_name]
    
    def clear_cache(self) -> None:
        """
        清除缓存
        
        清除所有缓存的行业数据，下次查询时会重新从API获取。
        
        Example:
            >>> mapper.clear_cache()
            >>> # 下次查询会重新获取数据
            >>> structure = mapper.get_industry_structure()
        """
        self._industry_cache.clear()
        logger.info("行业数据缓存已清除")
    
    # ========================================================================
    # 参数验证方法
    # ========================================================================
    
    def _validate_stock_code(self, stock_code: str) -> None:
        """
        验证股票代码格式
        
        Args:
            stock_code: 股票代码
        
        Raises:
            ValueError: 股票代码格式无效
        """
        if not stock_code or not isinstance(stock_code, str):
            raise ValueError("股票代码不能为空")
        
        if '.' not in stock_code:
            raise ValueError(
                f"无效的股票代码格式: {stock_code}。"
                f"正确格式: '000001.SZ' 或 '600000.SH'"
            )
        
        parts = stock_code.split('.')
        if len(parts) != 2:
            raise ValueError(f"无效的股票代码格式: {stock_code}")
        
        stock_num, market = parts
        
        if len(stock_num) != 6 or not stock_num.isdigit():
            raise ValueError(
                f"无效的股票代码: {stock_code}。股票代码应为6位数字"
            )
        
        if market not in ['SZ', 'SH']:
            raise ValueError(
                f"无效的市场代码: {market}。应为 'SZ' 或 'SH'"
            )
    
    def _validate_date(self, date: str) -> None:
        """
        验证日期格式
        
        Args:
            date: 日期字符串
        
        Raises:
            ValueError: 日期格式无效
        """
        try:
            datetime.strptime(date, "%Y%m%d")
        except ValueError:
            raise ValueError(
                f"无效的日期格式: {date}。应为 'YYYYMMDD'"
            )
    
    def __repr__(self) -> str:
        """字符串表示"""
        cache_status = "已缓存" if self._industry_cache else "未缓存"
        return f"IndustryMapper(client={self.client}, cache={cache_status})"
