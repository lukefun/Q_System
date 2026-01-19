"""
示例03：基本面数据处理演示

本示例演示如何使用FundamentalHandler获取和处理基本面财务数据。
重点展示时间点正确性（Point-in-Time Correctness）的重要性。

学习要点：
1. 如何获取财务指标数据（PE、PB、ROE等）
2. 时间点正确性：使用公告日期而非报告期
3. 如何计算PE和PB比率
4. 如何处理缺失的财务数据
5. 避免未来函数的最佳实践
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.xtdata_client import XtDataClient
from src.fundamental_handler import FundamentalHandler

def create_sample_financial_data():
    """
    创建示例财务数据
    
    关键概念：
    - report_date: 报告期结束日期（如2023Q4 = 20231231）
    - announce_date: 财报公告日期（如20240430）
    - 时间点正确性：只能使用announce_date之前的数据
    """
    data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 4,
        'report_date': ['20230331', '20230630', '20230930', '20231231'],
        'announce_date': ['20230430', '20230831', '20231031', '20240430'],  # 注意：年报通常延迟公告
        'eps': [0.25, 0.52, 0.78, 1.05],  # 每股收益（累计）
        'bvps': [8.5, 8.7, 8.9, 9.2],  # 每股净资产
        'roe': [0.03, 0.06, 0.09, 0.11],  # 净资产收益率（累计）
        'revenue': [1000000000, 2100000000, 3200000000, 4500000000],  # 营业收入（累计）
        'net_profit': [50000000, 104000000, 156000000, 210000000],  # 净利润（累计）
        'total_assets': [5000000000, 5200000000, 5400000000, 5600000000],
        'total_equity': [1700000000, 1740000000, 1780000000, 1840000000]
    })
    
    return data

def demonstrate_time_point_correctness():
    """演示时间点正确性的重要性"""
    print("=" * 60)
    print("1. 时间点正确性（Point-in-Time Correctness）")
    print("=" * 60)
    print("\n核心概念：")
    print("- 报告期（report_date）：财报覆盖的时间段")
    print("- 公告日期（announce_date）：财报对外公布的日期")
    print("- 时间点正确性：只能使用公告日期之前的数据\n")
    
    financial_data = create_sample_financial_data()
    
    print("示例财务数据：")
    print(financial_data[['report_date', 'announce_date', 'eps', 'roe']].to_string(index=False))
    
    print("\n" + "-" * 60)
    print("场景1：2023年11月1日查询财务数据")
    print("-" * 60)
    query_date = '20231101'
    
    # 错误做法：使用report_date过滤
    wrong_data = financial_data[financial_data['report_date'] <= query_date]
    print("\n❌ 错误做法：使用report_date过滤")
    print(f"查询日期：{query_date}")
    print(f"返回数据：{len(wrong_data)}条")
    if len(wrong_data) > 0:
        print(wrong_data[['report_date', 'announce_date', 'eps']].to_string(index=False))
    print("问题：包含了2023Q3数据，但该数据在10月31日才公告！")
    print("      这是未来函数，会导致回测结果失真！")
    
    # 正确做法：使用announce_date过滤
    correct_data = financial_data[financial_data['announce_date'] <= query_date]
    print("\n✓ 正确做法：使用announce_date过滤")
    print(f"查询日期：{query_date}")
    print(f"返回数据：{len(correct_data)}条")
    if len(correct_data) > 0:
        print(correct_data[['report_date', 'announce_date', 'eps']].to_string(index=False))
    print("正确：只包含10月31日之前公告的数据")
    
    print("\n" + "-" * 60)
    print("场景2：2024年5月1日查询财务数据")
    print("-" * 60)
    query_date = '20240501'
    
    correct_data = financial_data[financial_data['announce_date'] <= query_date]
    print(f"\n查询日期：{query_date}")
    print(f"返回数据：{len(correct_data)}条")
    print(correct_data[['report_date', 'announce_date', 'eps']].to_string(index=False))
    print("\n注意：现在可以看到2023年报数据了（4月30日公告）")

def demonstrate_pe_ratio_calculation():
    """演示PE比率计算"""
    print("\n" + "=" * 60)
    print("2. PE比率（市盈率）计算")
    print("=" * 60)
    print("\nPE比率 = 股价 / 每股收益（EPS）")
    print("- 反映市场对公司盈利能力的估值")
    print("- PE越高，市场预期越高（或估值越贵）")
    print("- 需要确保价格和EPS的时间对齐\n")
    
    financial_data = create_sample_financial_data()
    
    # 创建价格数据
    price_data = pd.DataFrame({
        'date': ['20231101', '20240501'],
        'close': [10.5, 12.0]
    })
    
    print("价格数据：")
    print(price_data.to_string(index=False))
    
    print("\n" + "-" * 60)
    print("计算2023年11月1日的PE比率")
    print("-" * 60)
    query_date = '20231101'
    price = price_data[price_data['date'] == query_date]['close'].values[0]
    
    # 获取该日期可用的最新财务数据
    available_data = financial_data[financial_data['announce_date'] <= query_date]
    if len(available_data) > 0:
        latest_data = available_data.iloc[-1]
        eps = latest_data['eps']
        pe_ratio = price / eps if eps > 0 else None
        
        print(f"股价：{price}元")
        print(f"最新可用EPS：{eps}元（{latest_data['report_date']}报告期，{latest_data['announce_date']}公告）")
        print(f"PE比率：{pe_ratio:.2f}" if pe_ratio else "PE比率：无法计算（EPS<=0）")
    
    print("\n" + "-" * 60)
    print("计算2024年5月1日的PE比率")
    print("-" * 60)
    query_date = '20240501'
    price = price_data[price_data['date'] == query_date]['close'].values[0]
    
    available_data = financial_data[financial_data['announce_date'] <= query_date]
    if len(available_data) > 0:
        latest_data = available_data.iloc[-1]
        eps = latest_data['eps']
        pe_ratio = price / eps if eps > 0 else None
        
        print(f"股价：{price}元")
        print(f"最新可用EPS：{eps}元（{latest_data['report_date']}报告期，{latest_data['announce_date']}公告）")
        print(f"PE比率：{pe_ratio:.2f}" if pe_ratio else "PE比率：无法计算（EPS<=0）")
        print(f"\n注意：现在使用的是2023年报数据，PE比率更准确")

def demonstrate_pb_ratio_calculation():
    """演示PB比率计算"""
    print("\n" + "=" * 60)
    print("3. PB比率（市净率）计算")
    print("=" * 60)
    print("\nPB比率 = 股价 / 每股净资产（BVPS）")
    print("- 反映市场对公司净资产的估值")
    print("- PB越高，市场对资产质量评价越高")
    print("- 通常用于资产密集型行业（银行、地产等）\n")
    
    financial_data = create_sample_financial_data()
    
    query_date = '20240501'
    price = 12.0
    
    available_data = financial_data[financial_data['announce_date'] <= query_date]
    if len(available_data) > 0:
        latest_data = available_data.iloc[-1]
        bvps = latest_data['bvps']
        pb_ratio = price / bvps if bvps > 0 else None
        
        print(f"查询日期：{query_date}")
        print(f"股价：{price}元")
        print(f"每股净资产：{bvps}元（{latest_data['report_date']}报告期）")
        print(f"PB比率：{pb_ratio:.2f}" if pb_ratio else "PB比率：无法计算（BVPS<=0）")
        
        print(f"\n解读：")
        if pb_ratio:
            if pb_ratio < 1:
                print(f"PB < 1：股价低于净资产，可能被低估或资产质量存疑")
            elif pb_ratio < 3:
                print(f"1 < PB < 3：合理估值范围")
            else:
                print(f"PB > 3：市场给予较高溢价，可能是成长性或品牌价值")

def demonstrate_missing_data_handling():
    """演示缺失数据的处理"""
    print("\n" + "=" * 60)
    print("4. 缺失数据的优雅处理")
    print("=" * 60)
    print("\n系统应该优雅处理以下情况：")
    print("1. 财务数据不可用（新上市公司）")
    print("2. 价格数据缺失")
    print("3. 负值或零值（EPS、BVPS）")
    print("4. 数据不匹配\n")
    
    print("-" * 60)
    print("场景1：新上市公司，无财务数据")
    print("-" * 60)
    print("股票代码：000002.SZ")
    print("上市日期：2024-01-01")
    print("查询日期：2024-02-01")
    print("财务数据：无（尚未公告首份财报）")
    print("\n处理结果：")
    print("- get_financial_data() 返回空DataFrame")
    print("- calculate_pe_ratio() 返回None")
    print("- calculate_pb_ratio() 返回None")
    print("- 不抛出异常，系统继续运行 ✓")
    
    print("\n" + "-" * 60)
    print("场景2：亏损公司，EPS为负")
    print("-" * 60)
    print("股票代码：000003.SZ")
    print("EPS：-0.50元（亏损）")
    print("股价：5.0元")
    print("\n处理结果：")
    print("- PE比率：None（负EPS无意义）")
    print("- 日志记录：INFO - EPS为负，PE比率不适用")
    print("- 不抛出异常 ✓")
    
    print("\n" + "-" * 60)
    print("场景3：价格数据缺失")
    print("-" * 60)
    print("股票代码：000001.SZ")
    print("查询日期：2024-01-01（非交易日）")
    print("价格数据：无")
    print("\n处理结果：")
    print("- calculate_pe_ratio() 返回None")
    print("- 日志记录：WARNING - 价格数据不可用")
    print("- 不抛出异常 ✓")

def demonstrate_quarterly_vs_ttm():
    """演示季度数据 vs TTM（滚动12个月）数据"""
    print("\n" + "=" * 60)
    print("5. 季度数据 vs TTM数据")
    print("=" * 60)
    print("\n财务指标的两种计算方式：")
    print("1. 季度数据：单季度的财务数据")
    print("2. TTM（Trailing Twelve Months）：最近12个月累计数据\n")
    
    financial_data = create_sample_financial_data()
    
    print("累计数据（报表原始数据）：")
    print(financial_data[['report_date', 'eps', 'revenue']].to_string(index=False))
    
    # 计算单季度数据
    quarterly_data = financial_data.copy()
    quarterly_data['eps_q'] = quarterly_data['eps'].diff().fillna(quarterly_data['eps'])
    quarterly_data['revenue_q'] = quarterly_data['revenue'].diff().fillna(quarterly_data['revenue'])
    
    print("\n单季度数据（差分计算）：")
    print(quarterly_data[['report_date', 'eps_q', 'revenue_q']].to_string(index=False))
    
    print("\nTTM数据（滚动12个月）：")
    print("- 2023Q1 TTM = 2023Q1（只有一个季度）")
    print("- 2023Q2 TTM = 2023Q1 + 2023Q2")
    print("- 2023Q3 TTM = 2023Q1 + 2023Q2 + 2023Q3")
    print("- 2023Q4 TTM = 2023全年")
    print("\n注意：TTM更能反映公司的持续盈利能力")
    print("      PE(TTM) = 股价 / EPS(TTM)")

def demonstrate_best_practices():
    """演示最佳实践"""
    print("\n" + "=" * 60)
    print("6. 基本面数据使用最佳实践")
    print("=" * 60)
    
    print("\n✓ 正确做法：")
    print("1. 始终使用announce_date进行时间过滤")
    print("2. 使用TTM数据计算PE比率")
    print("3. 优雅处理缺失数据，返回None而非异常")
    print("4. 记录详细日志便于调试")
    print("5. 在回测中严格遵守时间点正确性")
    
    print("\n❌ 错误做法：")
    print("1. 使用report_date过滤（未来函数！）")
    print("2. 忽略公告延迟（年报通常延迟4个月）")
    print("3. 不处理缺失数据导致程序崩溃")
    print("4. 混用不同时间点的数据")
    print("5. 使用单季度数据计算PE（波动大）")
    
    print("\n代码示例：")
    print("""
# 正确的查询方式
def get_pe_ratio_at_date(stock_code, date, handler):
    # 1. 获取该日期可用的财务数据
    financial_data = handler.get_financial_data(
        stock_codes=[stock_code],
        indicators=['eps'],
        as_of_date=date  # 使用as_of_date确保时间点正确
    )
    
    # 2. 获取价格数据
    price_data = get_price_at_date(stock_code, date)
    
    # 3. 计算PE比率
    if not financial_data.empty and price_data is not None:
        pe_ratio = handler.calculate_pe_ratio(
            stock_code=stock_code,
            date=date,
            price_data=price_data
        )
        return pe_ratio
    else:
        return None  # 优雅处理缺失数据
""")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("基本面数据处理演示")
    print("=" * 60)
    print("\n本示例演示基本面数据的获取和处理")
    print("重点：时间点正确性（避免未来函数）\n")
    
    # 1. 时间点正确性
    demonstrate_time_point_correctness()
    
    # 2. PE比率计算
    demonstrate_pe_ratio_calculation()
    
    # 3. PB比率计算
    demonstrate_pb_ratio_calculation()
    
    # 4. 缺失数据处理
    demonstrate_missing_data_handling()
    
    # 5. 季度 vs TTM
    demonstrate_quarterly_vs_ttm()
    
    # 6. 最佳实践
    demonstrate_best_practices()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    print("\n关键要点：")
    print("1. 使用announce_date而非report_date（避免未来函数）")
    print("2. 优雅处理缺失数据（返回None而非异常）")
    print("3. 使用TTM数据计算PE比率更准确")
    print("4. 严格遵守时间点正确性原则")
    print("\n下一步：")
    print("- 查看 examples/04_industry_classification.py 学习行业分类")
    print("- 查看 src/fundamental_handler.py 了解实现细节")

if __name__ == '__main__':
    main()
