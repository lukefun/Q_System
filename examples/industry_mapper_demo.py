"""
行业分类映射器演示脚本

演示IndustryMapper类的主要功能：
1. 获取申万行业分类结构
2. 查询股票的行业分类
3. 查询行业成分股
4. 历史时点查询
5. 按代码和名称查询的一致性
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xtdata_client import XtDataClient
from src.industry_mapper import IndustryMapper
from config import logger


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_industry_structure(mapper):
    """演示获取行业结构"""
    print_section("1. 获取申万行业分类结构")
    
    structure = mapper.get_industry_structure()
    
    print(f"\n共有 {len(structure['level1'])} 个一级行业：\n")
    
    # 显示前3个一级行业及其子行业
    for i, l1 in enumerate(structure['level1'][:3]):
        print(f"一级行业: {l1['code']} - {l1['name']}")
        
        for l2 in l1.get('level2', [])[:2]:
            print(f"  └─ 二级行业: {l2['code']} - {l2['name']}")
            
            for l3 in l2.get('level3', [])[:2]:
                print(f"      └─ 三级行业: {l3['code']} - {l3['name']}")
        
        if i < 2:
            print()


def demo_stock_industry(mapper):
    """演示查询股票行业分类"""
    print_section("2. 查询股票的行业分类")
    
    stock_code = '000001.SZ'
    print(f"\n查询股票 {stock_code} 的当前行业分类：\n")
    
    industry = mapper.get_stock_industry(stock_code)
    
    print(f"股票代码: {industry['stock_code']}")
    print(f"生效日期: {industry['effective_date']}")
    print(f"一级行业: {industry['industry_l1_code']} - {industry['industry_l1_name']}")
    print(f"二级行业: {industry['industry_l2_code']} - {industry['industry_l2_name']}")
    print(f"三级行业: {industry['industry_l3_code']} - {industry['industry_l3_name']}")


def demo_historical_industry(mapper):
    """演示历史时点查询"""
    print_section("3. 历史时点行业分类查询")
    
    stock_code = '000001.SZ'
    
    # 查询2021年的行业分类
    print(f"\n查询股票 {stock_code} 在 2021年1月1日 的行业分类：\n")
    industry_2021 = mapper.get_stock_industry(stock_code, '20210101')
    print(f"三级行业: {industry_2021['industry_l3_name']}")
    print(f"生效日期: {industry_2021['effective_date']}")
    
    # 查询2024年的行业分类
    print(f"\n查询股票 {stock_code} 在 2024年1月1日 的行业分类：\n")
    industry_2024 = mapper.get_stock_industry(stock_code, '20240101')
    print(f"三级行业: {industry_2024['industry_l3_name']}")
    print(f"生效日期: {industry_2024['effective_date']}")
    
    print("\n说明：000001.SZ在2023年发生了行业变更，从种植业变更为养殖业")


def demo_industry_constituents(mapper):
    """演示查询行业成分股"""
    print_section("4. 查询行业成分股")
    
    # 按行业代码查询
    industry_code = '801010'
    print(f"\n按行业代码查询 {industry_code}（农林牧渔）的成分股：\n")
    
    constituents = mapper.get_industry_constituents(industry_code=industry_code)
    print(f"成分股数量: {len(constituents)}")
    print(f"成分股列表: {constituents}")


def demo_query_consistency(mapper):
    """演示按代码和名称查询的一致性"""
    print_section("5. 查询方式一致性验证")
    
    industry_code = '801010'
    industry_name = '农林牧渔'
    
    print(f"\n验证按代码和名称查询的一致性：\n")
    
    # 按代码查询
    constituents_by_code = mapper.get_industry_constituents(
        industry_code=industry_code
    )
    print(f"按代码 {industry_code} 查询: {len(constituents_by_code)} 只股票")
    
    # 按名称查询
    constituents_by_name = mapper.get_industry_constituents(
        industry_name=industry_name
    )
    print(f"按名称 {industry_name} 查询: {len(constituents_by_name)} 只股票")
    
    # 验证一致性
    if set(constituents_by_code) == set(constituents_by_name):
        print("\n✓ 查询结果一致！")
    else:
        print("\n✗ 查询结果不一致！")


def demo_cache_mechanism(mapper):
    """演示缓存机制"""
    print_section("6. 缓存机制演示")
    
    print("\n第一次获取行业结构（从API获取）...")
    import time
    start = time.time()
    structure1 = mapper.get_industry_structure()
    time1 = time.time() - start
    print(f"耗时: {time1*1000:.2f} ms")
    
    print("\n第二次获取行业结构（从缓存获取）...")
    start = time.time()
    structure2 = mapper.get_industry_structure()
    time2 = time.time() - start
    print(f"耗时: {time2*1000:.2f} ms")
    
    print(f"\n缓存加速比: {time1/time2:.1f}x")
    
    # 清除缓存
    print("\n清除缓存...")
    mapper.clear_cache()
    
    print("第三次获取行业结构（缓存已清除，重新从API获取）...")
    start = time.time()
    structure3 = mapper.get_industry_structure()
    time3 = time.time() - start
    print(f"耗时: {time3*1000:.2f} ms")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  行业分类映射器演示")
    print("=" * 60)
    
    # 创建客户端和映射器
    print("\n初始化XtData客户端和行业映射器...")
    client = XtDataClient(account_id="demo", account_key="demo")
    client.connect()
    
    mapper = IndustryMapper(client)
    print("✓ 初始化完成")
    
    try:
        # 演示各项功能
        demo_industry_structure(mapper)
        demo_stock_industry(mapper)
        demo_historical_industry(mapper)
        demo_industry_constituents(mapper)
        demo_query_consistency(mapper)
        demo_cache_mechanism(mapper)
        
        print("\n" + "=" * 60)
        print("  演示完成")
        print("=" * 60 + "\n")
    
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}", exc_info=True)
        print(f"\n错误: {e}")
    
    finally:
        # 断开连接
        client.disconnect()
        print("已断开连接")


if __name__ == "__main__":
    main()
