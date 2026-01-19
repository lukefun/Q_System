"""
未来函数（前瞻偏差）演示

本示例通过对比演示，展示未来函数的危害以及如何正确避免。
未来函数是量化回测中最常见也最危险的错误之一。

什么是未来函数？
未来函数（Look-ahead Bias）是指在历史分析中使用了未来信息的错误。
这会导致回测结果过于乐观，实盘交易时无法复现。

常见的未来函数陷阱：
1. 使用后复权进行回测
2. 使用报告期而非公告日期
3. 数据对齐时使用未来信息
4. 技术指标计算时使用未来数据

作者：Q_System
日期：2026-01-19
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from src.fundamental_handler import FundamentalHandler
from src.industry_mapper import IndustryMapper
from config import (
    logger,
    XTDATA_ACCOUNT_ID,
    XTDATA_ACCOUNT_KEY
)


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_warning(message):
    """打印警告信息"""
    print(f"⚠️  {message}")


def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")


def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")


def demo_1_price_adjustment_lookahead():
    """
    演示1：价格复权中的未来函数
    
    对比前复权和后复权在回测中的差异
    """
    print_section("演示1：价格复权中的未来函数")
    
    print("场景：")
    print("假设某股票在2024-06-01发生10%的分红除权")
    print("我们在2024-01-01进行回测，应该使用哪种复权方法？")
    print()
    
    # 模拟数据
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    
    # 原始价格（2024-06-01除权）
    prices_before = [10.0] * 151  # 2024-01-01 到 2024-05-31
    prices_after = [9.0] * (len(dates) - 151)  # 2024-06-01 到 2024-12-31
    original_prices = prices_before + prices_after
    
    data = pd.DataFrame({
        'date': [d.strftime('%Y%m%d') for d in dates],
        'close': original_prices
    })
    
    print("原始价格数据（部分）：")
    print("2024-05-30: 10.00")
    print("2024-05-31: 10.00")
    print("2024-06-01: 9.00  ← 除权日，价格下跌10%")
    print("2024-06-02: 9.00")
    print()
    
    # 前复权
    print("【方法1：前复权（正确）】")
    print("保持当前价格不变，向前调整历史价格")
    print()
    
    # 模拟前复权：2024-06-01之前的价格 × 0.9
    forward_adjusted = data.copy()
    forward_adjusted.loc[forward_adjusted['date'] < '20240601', 'close'] *= 0.9
    
    print("前复权后的价格：")
    print("2024-05-30: 9.00  ← 向前调整")
    print("2024-05-31: 9.00  ← 向前调整")
    print("2024-06-01: 9.00  ← 当前价格不变")
    print("2024-06-02: 9.00")
    print()
    
    print_success("前复权的优点：")
    print("• 在2024-01-01回测时，只使用2024-01-01之前的复权因子")
    print("• 不会使用2024-06-01的除权信息（未来信息）")
    print("• 当前价格真实，与市场报价一致")
    print("• 适合回测和策略开发")
    print()
    
    # 后复权
    print("【方法2：后复权（错误）】")
    print("保持历史价格不变，向后调整当前价格")
    print()
    
    # 模拟后复权：2024-06-01之后的价格 × (1/0.9)
    backward_adjusted = data.copy()
    backward_adjusted.loc[backward_adjusted['date'] >= '20240601', 'close'] /= 0.9
    
    print("后复权后的价格：")
    print("2024-05-30: 10.00  ← 历史价格不变")
    print("2024-05-31: 10.00  ← 历史价格不变")
    print("2024-06-01: 10.00  ← 向后调整")
    print("2024-06-02: 10.00  ← 向后调整")
    print()
    
    print_error("后复权的问题：")
    print("• 在2024-01-01回测时，使用了2024-06-01的除权信息（未来信息）")
    print("• 历史价格看起来连续，但这是用未来信息'修正'的结果")
    print("• 当前价格失真，与市场报价不一致")
    print("• 不适合回测，会导致回测结果过于乐观")
    print()
    
    # 回测对比
    print("【回测对比】")
    print("假设策略：在价格跌破10.0时买入")
    print()
    
    print("使用前复权：")
    print("• 2024-01-01时，价格为9.00（已调整）")
    print("• 策略触发买入信号 ✓")
    print("• 这是正确的，因为考虑了除权后的价格")
    print()
    
    print("使用后复权：")
    print("• 2024-01-01时，价格为10.00（未调整）")
    print("• 策略不触发买入信号 ✗")
    print("• 这是错误的，因为使用了未来的除权信息")
    print()
    
    print_warning("结论：回测必须使用前复权，避免未来函数！")


def demo_2_fundamental_data_lookahead():
    """
    演示2：基本面数据中的未来函数
    
    对比使用报告期和公告日期的差异
    """
    print_section("演示2：基本面数据中的未来函数")
    
    print("场景：")
    print("某公司2023年年报在2024-04-30公布")
    print("报告期：2023-12-31")
    print("公告日期：2024-04-30")
    print()
    print("问题：在2024-01-01回测时，能否使用这份年报数据？")
    print()
    
    # 模拟财务数据
    financial_data = pd.DataFrame({
        'stock_code': ['000001.SZ'],
        'report_date': ['20231231'],      # 报告期
        'announce_date': ['20240430'],    # 公告日期
        'net_profit': [1000000],
        'pe_ratio': [15.5],
        'pb_ratio': [1.2]
    })
    
    print("财务数据：")
    print(financial_data)
    print()
    
    # 错误做法
    print("【错误做法：使用报告期】")
    print()
    
    query_date = '20240101'
    print(f"查询日期：{query_date}")
    print()
    
    # 使用报告期过滤
    wrong_data = financial_data[financial_data['report_date'] <= query_date]
    
    if not wrong_data.empty:
        print_error("使用报告期过滤，返回了数据：")
        print(wrong_data)
        print()
        print("问题：")
        print("• 2023年年报在2024-04-30才公布")
        print("• 在2024-01-01时，这份年报还不存在")
        print("• 使用这个数据就是未来函数！")
        print("• 回测结果会过于乐观，实盘无法复现")
    print()
    
    # 正确做法
    print("【正确做法：使用公告日期】")
    print()
    
    # 使用公告日期过滤
    correct_data = financial_data[financial_data['announce_date'] <= query_date]
    
    if correct_data.empty:
        print_success("使用公告日期过滤，没有返回数据 ✓")
        print()
        print("原因：")
        print("• 公告日期（2024-04-30）晚于查询日期（2024-01-01）")
        print("• 在2024-01-01时，这份年报确实还未公布")
        print("• 不返回数据是正确的，避免了未来函数")
    print()
    
    # 正确的查询
    print("【正确的查询时点】")
    print()
    
    query_date_2 = '20240501'
    print(f"查询日期：{query_date_2}")
    print()
    
    correct_data_2 = financial_data[financial_data['announce_date'] <= query_date_2]
    
    if not correct_data_2.empty:
        print_success("使用公告日期过滤，返回了数据 ✓")
        print(correct_data_2)
        print()
        print("原因：")
        print("• 公告日期（2024-04-30）早于查询日期（2024-05-01）")
        print("• 在2024-05-01时，这份年报已经公布")
        print("• 可以安全使用这个数据")
    print()
    
    print_warning("结论：必须使用公告日期（announce_date）而非报告期（report_date）！")


def demo_3_data_alignment_lookahead():
    """
    演示3：数据对齐中的未来函数
    
    演示如何正确对齐不同数据源
    """
    print_section("演示3：数据对齐中的未来函数")
    
    print("场景：")
    print("将价格数据和财务数据对齐，用于计算PE比率")
    print()
    
    # 模拟价格数据
    price_data = pd.DataFrame({
        'date': ['20240101', '20240102', '20240103'],
        'stock_code': ['000001.SZ'] * 3,
        'close': [10.0, 10.5, 10.3]
    })
    
    # 模拟财务数据
    financial_data = pd.DataFrame({
        'stock_code': ['000001.SZ', '000001.SZ'],
        'report_date': ['20231231', '20240331'],
        'announce_date': ['20240430', '20240530'],  # 注意：都在未来
        'eps': [1.0, 1.2]
    })
    
    print("价格数据：")
    print(price_data)
    print()
    
    print("财务数据：")
    print(financial_data)
    print()
    
    # 错误做法
    print("【错误做法：使用报告期对齐】")
    print()
    
    # 对于每个交易日，使用最新的报告期数据
    wrong_aligned = []
    for _, row in price_data.iterrows():
        trade_date = row['date']
        
        # 错误：使用report_date <= trade_date
        available = financial_data[
            financial_data['report_date'] <= trade_date
        ].sort_values('report_date')
        
        if not available.empty:
            latest = available.iloc[-1]
            pe = row['close'] / latest['eps']
            
            wrong_aligned.append({
                'date': trade_date,
                'close': row['close'],
                'eps': latest['eps'],
                'pe': pe,
                'report_date': latest['report_date'],
                'announce_date': latest['announce_date']
            })
    
    if wrong_aligned:
        wrong_df = pd.DataFrame(wrong_aligned)
        print_error("错误的对齐结果：")
        print(wrong_df)
        print()
        print("问题：")
        print("• 在2024-01-01使用了2023年报数据")
        print("• 但2023年报在2024-04-30才公布")
        print("• 这是未来函数！")
    print()
    
    # 正确做法
    print("【正确做法：使用公告日期对齐】")
    print()
    
    # 对于每个交易日，使用已公告的最新数据
    correct_aligned = []
    for _, row in price_data.iterrows():
        trade_date = row['date']
        
        # 正确：使用announce_date <= trade_date
        available = financial_data[
            financial_data['announce_date'] <= trade_date
        ].sort_values('announce_date')
        
        if not available.empty:
            latest = available.iloc[-1]
            pe = row['close'] / latest['eps']
            
            correct_aligned.append({
                'date': trade_date,
                'close': row['close'],
                'eps': latest['eps'],
                'pe': pe,
                'report_date': latest['report_date'],
                'announce_date': latest['announce_date']
            })
        else:
            correct_aligned.append({
                'date': trade_date,
                'close': row['close'],
                'eps': None,
                'pe': None,
                'report_date': None,
                'announce_date': None
            })
    
    correct_df = pd.DataFrame(correct_aligned)
    print_success("正确的对齐结果：")
    print(correct_df)
    print()
    print("说明：")
    print("• 在2024-01-01、2024-01-02、2024-01-03时")
    print("• 没有已公告的财务数据可用")
    print("• 返回None是正确的，避免了未来函数")
    print()
    
    print_warning("结论：数据对齐必须使用公告日期，采用保守策略！")


def demo_4_industry_classification_lookahead():
    """
    演示4：行业分类中的未来函数
    
    演示如何正确查询历史行业分类
    """
    print_section("演示4：行业分类中的未来函数")
    
    print("场景：")
    print("某股票在2024-06-01从银行业调整到保险业")
    print("在2024-01-01回测时，应该使用哪个行业分类？")
    print()
    
    # 模拟行业变更数据
    industry_history = pd.DataFrame({
        'stock_code': ['000001.SZ', '000001.SZ'],
        'effective_date': ['20200101', '20240601'],
        'industry_name': ['银行', '保险']
    })
    
    print("行业变更历史：")
    print(industry_history)
    print()
    
    # 错误做法
    print("【错误做法：使用当前行业分类】")
    print()
    
    query_date = '20240101'
    print(f"查询日期：{query_date}")
    print()
    
    # 错误：使用最新的行业分类
    wrong_industry = industry_history.iloc[-1]['industry_name']
    
    print_error(f"使用当前行业分类：{wrong_industry}")
    print()
    print("问题：")
    print("• 在2024-01-01时，股票还属于银行业")
    print("• 保险业分类在2024-06-01才生效")
    print("• 使用保险业分类是未来函数！")
    print()
    
    # 正确做法
    print("【正确做法：使用历史时点的行业分类】")
    print()
    
    # 正确：使用effective_date <= query_date的最新记录
    correct_records = industry_history[
        industry_history['effective_date'] <= query_date
    ].sort_values('effective_date')
    
    if not correct_records.empty:
        correct_industry = correct_records.iloc[-1]['industry_name']
        print_success(f"使用历史时点的行业分类：{correct_industry} ✓")
        print()
        print("原因：")
        print("• 在2024-01-01时，最新的有效分类是银行业")
        print("• 生效日期（2020-01-01）早于查询日期（2024-01-01）")
        print("• 这是正确的历史分类")
    print()
    
    print_warning("结论：必须使用历史时点的行业分类，不能使用当前分类！")


def demo_5_technical_indicator_lookahead():
    """
    演示5：技术指标中的未来函数
    
    演示如何正确计算技术指标
    """
    print_section("演示5：技术指标中的未来函数")
    
    print("场景：")
    print("计算5日移动平均线（MA5）")
    print()
    
    # 模拟价格数据
    dates = pd.date_range('2024-01-01', '2024-01-10', freq='D')
    prices = [10.0, 10.5, 10.3, 10.8, 10.6, 10.9, 11.0, 10.7, 10.8, 11.1]
    
    data = pd.DataFrame({
        'date': [d.strftime('%Y%m%d') for d in dates],
        'close': prices
    })
    
    print("价格数据：")
    print(data)
    print()
    
    # 错误做法
    print("【错误做法：使用未来数据计算MA】")
    print()
    
    # 错误：使用中心对齐的移动平均
    wrong_ma = data['close'].rolling(window=5, center=True).mean()
    
    print_error("使用center=True的移动平均：")
    print(pd.DataFrame({
        'date': data['date'],
        'close': data['close'],
        'ma5': wrong_ma
    }))
    print()
    print("问题：")
    print("• center=True会使用前后各2天的数据")
    print("• 在2024-01-03计算MA5时，使用了2024-01-04和2024-01-05的数据")
    print("• 这是未来函数！")
    print()
    
    # 正确做法
    print("【正确做法：只使用历史数据计算MA】")
    print()
    
    # 正确：使用右对齐的移动平均
    correct_ma = data['close'].rolling(window=5, center=False).mean()
    
    print_success("使用center=False的移动平均：")
    print(pd.DataFrame({
        'date': data['date'],
        'close': data['close'],
        'ma5': correct_ma
    }))
    print()
    print("说明：")
    print("• center=False（默认）只使用当前及之前的数据")
    print("• 在2024-01-05计算MA5时，使用2024-01-01到2024-01-05的数据")
    print("• 前4天的MA5为NaN是正确的，因为数据不足5天")
    print()
    
    print_warning("结论：技术指标计算必须只使用历史数据，不能使用未来数据！")


def main():
    """主函数"""
    print_section("未来函数（前瞻偏差）演示")
    
    print("本示例通过5个对比演示，展示未来函数的危害以及如何正确避免。")
    print()
    print("未来函数是量化回测中最常见也最危险的错误之一。")
    print("它会导致回测结果过于乐观，实盘交易时无法复现。")
    print()
    
    input("按Enter键开始演示...")
    
    # 演示1：价格复权
    demo_1_price_adjustment_lookahead()
    input("\n按Enter键继续下一个演示...")
    
    # 演示2：基本面数据
    demo_2_fundamental_data_lookahead()
    input("\n按Enter键继续下一个演示...")
    
    # 演示3：数据对齐
    demo_3_data_alignment_lookahead()
    input("\n按Enter键继续下一个演示...")
    
    # 演示4：行业分类
    demo_4_industry_classification_lookahead()
    input("\n按Enter键继续下一个演示...")
    
    # 演示5：技术指标
    demo_5_technical_indicator_lookahead()
    
    # 总结
    print_section("总结：如何避免未来函数")
    
    print("1. 价格复权")
    print("   ✅ 回测使用前复权")
    print("   ❌ 不要使用后复权")
    print()
    
    print("2. 基本面数据")
    print("   ✅ 使用公告日期（announce_date）")
    print("   ❌ 不要使用报告期（report_date）")
    print()
    
    print("3. 数据对齐")
    print("   ✅ 使用保守策略，只使用已公告的数据")
    print("   ❌ 不要假设数据立即可用")
    print()
    
    print("4. 行业分类")
    print("   ✅ 使用历史时点的分类")
    print("   ❌ 不要使用当前分类")
    print()
    
    print("5. 技术指标")
    print("   ✅ 只使用历史数据计算")
    print("   ❌ 不要使用未来数据（如center=True）")
    print()
    
    print("系统的未来函数防范机制：")
    print("• PriceAdjuster默认使用前复权")
    print("• FundamentalHandler强制使用公告日期")
    print("• IndustryMapper支持历史时点查询")
    print("• DataAlignment采用保守对齐策略")
    print()
    
    print("记住：")
    print("在任何历史时点，只能使用该时点之前的信息！")
    print()
    
    print_section("演示完成")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}", exc_info=True)
        print(f"\n❌ 程序执行失败: {str(e)}")
