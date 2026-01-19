"""
Day 11 练习：行业分类管理

学习目标：
1. 理解申万行业分类体系
2. 掌握行业分类查询方法
3. 学会处理行业变更
4. 理解历史时点的行业分类

金融概念：
- 申万行业分类：中国市场标准的行业分类体系
- 三级行业：一级（大类）、二级（中类）、三级（小类）
- 行业轮动：不同行业在不同时期的表现差异
- 板块分析：基于行业分类的投资分析方法

前置知识：Day 8 - XtData基础接口

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.industry_mapper import IndustryMapper
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：查询股票行业
def exercise_1_get_stock_industry():
    """查询股票的行业分类"""
    print_section("练习1：查询股票行业")
    print("TODO: 查询股票的一级、二级、三级行业")
    print("提示：使用IndustryMapper.get_stock_industry()")


# 练习2：获取行业成分股
def exercise_2_get_industry_constituents():
    """获取行业的成分股"""
    print_section("练习2：获取行业成分股")
    print("TODO: 获取某个行业的所有成分股")
    print("提示：使用IndustryMapper.get_industry_constituents()")


# 练习3：历史行业分类
def exercise_3_historical_industry():
    """查询历史时点的行业分类"""
    print_section("练习3：历史行业分类")
    print("TODO: 查询股票在历史某个日期的行业分类")
    print("提示：传入date参数")


# 练习4：行业对比分析
def exercise_4_industry_comparison():
    """对比不同行业的股票"""
    print_section("练习4：行业对比分析")
    print("TODO: 获取多个行业的成分股并对比")
    print("提示：统计每个行业的股票数量")


# 练习5：行业变更追踪
def exercise_5_industry_change_tracking():
    """追踪股票的行业变更"""
    print_section("练习5：行业变更追踪")
    print("TODO: 查询股票在不同时点的行业分类")
    print("提示：对比不同日期的查询结果")


def main():
    print("=" * 60)
    print("  Day 11 练习：行业分类管理")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• 申万行业分类是中国市场标准")
    print("• 行业分类会随时间变化")
    print("• 必须使用历史时点的分类")
    print()
    
    exercise_1_get_stock_industry()
    exercise_2_get_industry_constituents()
    exercise_3_historical_industry()
    exercise_4_industry_comparison()
    exercise_5_industry_change_tracking()
    
    print("\n下一步：Day 12 - 数据持久化")


if __name__ == '__main__':
    main()
