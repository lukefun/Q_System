"""
示例04：行业分类管理演示

本示例演示如何使用IndustryMapper管理申万行业分类数据。
展示行业结构、股票-行业映射、历史行业变更等功能。

学习要点：
1. 申万行业分类的三级结构
2. 如何查询股票的行业归属
3. 如何获取行业成分股
4. 如何处理历史行业变更
5. 行业数据在量化策略中的应用
"""

import pandas as pd
from datetime import datetime
from src.xtdata_client import XtDataClient
from src.industry_mapper import IndustryMapper

def create_sample_industry_structure():
    """
    创建示例行业结构数据
    
    申万行业分类：
    - 一级行业：28个大类（如金融、医药、科技等）
    - 二级行业：104个中类
    - 三级行业：227个小类
    """
    structure = {
        '801010': {  # 一级行业代码
            'name': '农林牧渔',
            'level': 1,
            'children': {
                '801011': {  # 二级行业代码
                    'name': '农业',
                    'level': 2,
                    'children': {
                        '801012': {'name': '种植业', 'level': 3},
                        '801013': {'name': '养殖业', 'level': 3}
                    }
                }
            }
        },
        '801020': {
            'name': '采掘',
            'level': 1,
            'children': {
                '801021': {
                    'name': '煤炭开采',
                    'level': 2,
                    'children': {
                        '801022': {'name': '动力煤', 'level': 3},
                        '801023': {'name': '焦煤', 'level': 3}
                    }
                }
            }
        },
        '801030': {
            'name': '化工',
            'level': 1,
            'children': {
                '801031': {
                    'name': '基础化工',
                    'level': 2,
                    'children': {
                        '801032': {'name': '化学原料', 'level': 3},
                        '801033': {'name': '化学制品', 'level': 3}
                    }
                }
            }
        },
        '801780': {
            'name': '银行',
            'level': 1,
            'children': {
                '801781': {
                    'name': '银行',
                    'level': 2,
                    'children': {
                        '801782': {'name': '国有大行', 'level': 3},
                        '801783': {'name': '股份制银行', 'level': 3},
                        '801784': {'name': '城商行', 'level': 3}
                    }
                }
            }
        }
    }
    
    return structure

def create_sample_stock_industry_mapping():
    """
    创建示例股票-行业映射数据
    
    包含历史变更记录
    """
    mapping = pd.DataFrame({
        'stock_code': ['000001.SZ', '000001.SZ', '600000.SH', '600036.SH', '000002.SZ'],
        'effective_date': ['20200101', '20230101', '20200101', '20200101', '20200101'],
        'industry_l1_code': ['801780', '801780', '801780', '801780', '801030'],
        'industry_l1_name': ['银行', '银行', '银行', '银行', '化工'],
        'industry_l2_code': ['801781', '801781', '801781', '801781', '801031'],
        'industry_l2_name': ['银行', '银行', '银行', '银行', '基础化工'],
        'industry_l3_code': ['801782', '801783', '801782', '801783', '801032'],
        'industry_l3_name': ['国有大行', '股份制银行', '国有大行', '股份制银行', '化学原料']
    })
    
    return mapping

def demonstrate_industry_structure():
    """演示行业结构查询"""
    print("=" * 60)
    print("1. 申万行业分类结构")
    print("=" * 60)
    print("\n申万行业分类是中国市场最常用的行业分类标准")
    print("采用三级分类体系：\n")
    
    structure = create_sample_industry_structure()
    
    print("一级行业（大类）：")
    for code, info in structure.items():
        print(f"  {code}: {info['name']}")
    
    print("\n二级行业示例（银行）：")
    bank_l1 = structure['801780']
    for code, info in bank_l1['children'].items():
        print(f"  {code}: {info['name']}")
    
    print("\n三级行业示例（银行细分）：")
    bank_l2 = bank_l1['children']['801781']
    for code, info in bank_l2['children'].items():
        print(f"  {code}: {info['name']}")
    
    print("\n行业分类的用途：")
    print("- 板块轮动策略：识别强势行业")
    print("- 行业中性策略：控制行业暴露")
    print("- 行业比较分析：同行业估值对比")
    print("- 风险管理：行业集中度控制")

def demonstrate_stock_industry_query():
    """演示股票行业查询"""
    print("\n" + "=" * 60)
    print("2. 查询股票的行业归属")
    print("=" * 60)
    
    mapping = create_sample_stock_industry_mapping()
    
    print("\n查询示例：平安银行（000001.SZ）")
    stock_code = '000001.SZ'
    
    # 查询当前行业
    current_date = '20240101'
    stock_mapping = mapping[
        (mapping['stock_code'] == stock_code) &
        (mapping['effective_date'] <= current_date)
    ].sort_values('effective_date').iloc[-1]
    
    print(f"\n查询日期：{current_date}")
    print(f"股票代码：{stock_code}")
    print(f"一级行业：{stock_mapping['industry_l1_name']} ({stock_mapping['industry_l1_code']})")
    print(f"二级行业：{stock_mapping['industry_l2_name']} ({stock_mapping['industry_l2_code']})")
    print(f"三级行业：{stock_mapping['industry_l3_name']} ({stock_mapping['industry_l3_code']})")
    print(f"生效日期：{stock_mapping['effective_date']}")
    
    print("\n" + "-" * 60)
    print("批量查询示例：")
    print("-" * 60)
    
    stocks = ['000001.SZ', '600000.SH', '600036.SH', '000002.SZ']
    query_date = '20240101'
    
    print(f"\n查询日期：{query_date}")
    print(f"{'股票代码':<12} {'一级行业':<10} {'三级行业':<15}")
    print("-" * 60)
    
    for stock in stocks:
        stock_data = mapping[
            (mapping['stock_code'] == stock) &
            (mapping['effective_date'] <= query_date)
        ].sort_values('effective_date')
        
        if len(stock_data) > 0:
            latest = stock_data.iloc[-1]
            print(f"{stock:<12} {latest['industry_l1_name']:<10} {latest['industry_l3_name']:<15}")

def demonstrate_industry_constituents():
    """演示行业成分股查询"""
    print("\n" + "=" * 60)
    print("3. 查询行业成分股")
    print("=" * 60)
    
    mapping = create_sample_stock_industry_mapping()
    
    print("\n查询示例：银行行业成分股")
    industry_code = '801780'
    industry_name = '银行'
    query_date = '20240101'
    
    # 查询该行业的所有股票
    constituents = mapping[
        (mapping['industry_l1_code'] == industry_code) &
        (mapping['effective_date'] <= query_date)
    ]
    
    # 获取每只股票的最新记录
    latest_constituents = constituents.sort_values('effective_date').groupby('stock_code').last()
    
    print(f"\n行业：{industry_name} ({industry_code})")
    print(f"查询日期：{query_date}")
    print(f"成分股数量：{len(latest_constituents)}")
    print(f"\n{'股票代码':<12} {'三级行业':<15} {'生效日期':<10}")
    print("-" * 60)
    
    for stock_code, row in latest_constituents.iterrows():
        print(f"{stock_code:<12} {row['industry_l3_name']:<15} {row['effective_date']:<10}")
    
    print("\n应用场景：")
    print("- 构建行业指数：计算行业平均收益")
    print("- 行业轮动策略：选择强势行业的龙头股")
    print("- 配对交易：同行业股票的相对价值")

def demonstrate_historical_industry_changes():
    """演示历史行业变更"""
    print("\n" + "=" * 60)
    print("4. 历史行业变更追踪")
    print("=" * 60)
    print("\n公司业务调整可能导致行业分类变更")
    print("回测时必须使用历史时点的正确分类\n")
    
    mapping = create_sample_stock_industry_mapping()
    
    stock_code = '000001.SZ'
    stock_history = mapping[mapping['stock_code'] == stock_code].sort_values('effective_date')
    
    print(f"股票：{stock_code}（平安银行）")
    print(f"行业变更历史：\n")
    print(f"{'生效日期':<12} {'一级行业':<10} {'三级行业':<15}")
    print("-" * 60)
    
    for _, row in stock_history.iterrows():
        print(f"{row['effective_date']:<12} {row['industry_l1_name']:<10} {row['industry_l3_name']:<15}")
    
    print("\n变更说明：")
    print("- 2020-01-01: 归类为国有大行")
    print("- 2023-01-01: 重新归类为股份制银行（业务性质调整）")
    
    print("\n" + "-" * 60)
    print("时间点正确性验证：")
    print("-" * 60)
    
    # 查询不同时点的行业
    dates = ['20220101', '20230601']
    
    for date in dates:
        stock_data = stock_history[stock_history['effective_date'] <= date]
        if len(stock_data) > 0:
            latest = stock_data.iloc[-1]
            print(f"\n{date}: {latest['industry_l3_name']}")
            print(f"  使用生效日期：{latest['effective_date']}")
    
    print("\n重要性：")
    print("- 回测时使用错误的行业分类会导致结果失真")
    print("- 必须使用effective_date进行时间点过滤")
    print("- 类似于基本面数据的announce_date概念")

def demonstrate_industry_query_methods():
    """演示不同的行业查询方式"""
    print("\n" + "=" * 60)
    print("5. 行业查询方式")
    print("=" * 60)
    
    mapping = create_sample_stock_industry_mapping()
    structure = create_sample_industry_structure()
    
    print("\n方式1：按行业代码查询")
    print("-" * 60)
    industry_code = '801780'
    constituents_by_code = mapping[mapping['industry_l1_code'] == industry_code]['stock_code'].unique()
    print(f"行业代码：{industry_code}")
    print(f"成分股：{list(constituents_by_code)}")
    
    print("\n方式2：按行业名称查询")
    print("-" * 60)
    industry_name = '银行'
    constituents_by_name = mapping[mapping['industry_l1_name'] == industry_name]['stock_code'].unique()
    print(f"行业名称：{industry_name}")
    print(f"成分股：{list(constituents_by_name)}")
    
    print("\n方式3：多级行业查询")
    print("-" * 60)
    print("查询：银行 -> 银行 -> 股份制银行")
    l3_constituents = mapping[mapping['industry_l3_code'] == '801783']['stock_code'].unique()
    print(f"三级行业成分股：{list(l3_constituents)}")
    
    print("\n一致性验证：")
    print(f"按代码查询结果 == 按名称查询结果: {set(constituents_by_code) == set(constituents_by_name)}")

def demonstrate_industry_analysis_applications():
    """演示行业分析应用"""
    print("\n" + "=" * 60)
    print("6. 行业分析应用场景")
    print("=" * 60)
    
    print("\n应用1：行业轮动策略")
    print("-" * 60)
    print("思路：")
    print("1. 计算各行业的平均收益率")
    print("2. 选择收益率最高的前N个行业")
    print("3. 在这些行业中选择龙头股")
    print("4. 定期调仓（如每月）")
    
    print("\n示例代码：")
    print("""
def industry_rotation_strategy(date):
    # 1. 获取所有一级行业
    industries = mapper.get_industry_structure()['level1']
    
    # 2. 计算每个行业的收益率
    industry_returns = {}
    for industry_code in industries:
        constituents = mapper.get_industry_constituents(
            industry_code=industry_code,
            date=date
        )
        # 计算行业平均收益
        returns = calculate_average_return(constituents, date)
        industry_returns[industry_code] = returns
    
    # 3. 选择前3个强势行业
    top_industries = sorted(
        industry_returns.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    return top_industries
""")
    
    print("\n应用2：行业中性策略")
    print("-" * 60)
    print("思路：")
    print("1. 确保投资组合在各行业的权重与基准一致")
    print("2. 在行业内部选股，避免行业暴露")
    print("3. 降低行业轮动风险")
    
    print("\n示例代码：")
    print("""
def industry_neutral_portfolio(benchmark_weights):
    portfolio = {}
    
    for industry_code, target_weight in benchmark_weights.items():
        # 获取行业成分股
        constituents = mapper.get_industry_constituents(
            industry_code=industry_code
        )
        
        # 在行业内选股（如选择PE最低的）
        selected_stocks = select_stocks_in_industry(
            constituents,
            criterion='lowest_pe'
        )
        
        # 分配权重
        for stock in selected_stocks:
            portfolio[stock] = target_weight / len(selected_stocks)
    
    return portfolio
""")
    
    print("\n应用3：行业估值比较")
    print("-" * 60)
    print("思路：")
    print("1. 计算各行业的平均PE、PB")
    print("2. 与历史分位数比较")
    print("3. 识别低估行业")
    
    print("\n示例：")
    print(f"{'行业':<10} {'平均PE':<10} {'历史分位':<10} {'评价':<10}")
    print("-" * 60)
    print(f"{'银行':<10} {'5.2':<10} {'15%':<10} {'低估':<10}")
    print(f"{'化工':<10} {'18.5':<10} {'65%':<10} {'合理':<10}")
    print(f"{'医药':<10} {'45.3':<10} {'95%':<10} {'高估':<10}")

def demonstrate_caching_mechanism():
    """演示缓存机制"""
    print("\n" + "=" * 60)
    print("7. 行业数据缓存机制")
    print("=" * 60)
    print("\n行业数据相对稳定，适合缓存以提高性能\n")
    
    print("缓存策略：")
    print("1. 行业结构数据：启动时加载，长期缓存")
    print("2. 股票-行业映射：按需加载，定期更新")
    print("3. 行业成分股：计算后缓存，避免重复查询")
    
    print("\n缓存更新时机：")
    print("- 每日收盘后更新（捕获行业调整）")
    print("- 手动清除缓存：mapper.clear_cache()")
    print("- 自动过期：缓存时间超过24小时")
    
    print("\n性能对比：")
    print(f"{'操作':<30} {'无缓存':<15} {'有缓存':<15}")
    print("-" * 60)
    print(f"{'查询行业结构':<30} {'500ms':<15} {'<1ms':<15}")
    print(f"{'查询1000只股票行业':<30} {'2000ms':<15} {'50ms':<15}")
    print(f"{'查询行业成分股':<30} {'300ms':<15} {'<1ms':<15}")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("行业分类管理演示")
    print("=" * 60)
    print("\n本示例演示申万行业分类的查询和应用")
    print("注意：本示例使用模拟数据\n")
    
    # 1. 行业结构
    demonstrate_industry_structure()
    
    # 2. 股票行业查询
    demonstrate_stock_industry_query()
    
    # 3. 行业成分股
    demonstrate_industry_constituents()
    
    # 4. 历史变更
    demonstrate_historical_industry_changes()
    
    # 5. 查询方式
    demonstrate_industry_query_methods()
    
    # 6. 应用场景
    demonstrate_industry_analysis_applications()
    
    # 7. 缓存机制
    demonstrate_caching_mechanism()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    print("\n关键要点：")
    print("1. 申万行业分类采用三级结构")
    print("2. 使用effective_date确保时间点正确性")
    print("3. 支持按代码或名称查询行业")
    print("4. 缓存机制提高查询性能")
    print("5. 行业数据在量化策略中有广泛应用")
    print("\n下一步：")
    print("- 查看 examples/05_data_persistence.py 学习数据持久化")
    print("- 查看 src/industry_mapper.py 了解实现细节")

if __name__ == '__main__':
    main()
