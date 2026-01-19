"""
Day 10 练习：基本面数据ETL

学习目标：
1. 理解基本面数据的时间点正确性
2. 掌握财务指标的提取和计算
3. 学会使用公告日期而非报告期
4. 理解未来函数在基本面数据中的体现

金融概念：
- PE比率（市盈率）：股价/每股收益，衡量估值水平
- PB比率（市净率）：股价/每股净资产，衡量资产价值
- ROE（净资产收益率）：净利润/净资产，衡量盈利能力
- 报告期 vs 公告日期：财报覆盖的时间段 vs 财报发布的日期

前置知识：Day 8 - XtData基础接口

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.fundamental_handler import FundamentalHandler
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：获取财务指标
def exercise_1_get_financial_data():
    """获取指定时点的财务数据"""
    print_section("练习1：获取财务指标")
    print("TODO: 获取PE、PB、ROE等财务指标")
    print("提示：使用FundamentalHandler.get_financial_data()")


# 练习2：时间点正确性验证
def exercise_2_point_in_time_correctness():
    """验证时间点正确性"""
    print_section("练习2：时间点正确性验证")
    print("TODO: 验证返回的数据都在查询日期之前公告")
    print("提示：检查announce_date <= as_of_date")


# 练习3：计算PE比率
def exercise_3_calculate_pe_ratio():
    """计算PE比率"""
    print_section("练习3：计算PE比率")
    print("TODO: 使用价格和盈利数据计算PE比率")
    print("提示：PE = 股价 / 每股收益")


# 练习4：财务数据缺失处理
def exercise_4_handle_missing_data():
    """处理缺失的财务数据"""
    print_section("练习4：财务数据缺失处理")
    print("TODO: 优雅处理缺失的财务数据")
    print("提示：使用try-except或检查None值")


# 练习5：未来函数陷阱
def exercise_5_lookahead_trap():
    """演示基本面数据中的未来函数陷阱"""
    print_section("练习5：未来函数陷阱")
    print("TODO: 对比使用报告期和公告日期的差异")
    print("提示：参考 examples/10_lookahead_bias_demo.py")


def main():
    print("=" * 60)
    print("  Day 10 练习：基本面数据ETL")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• 必须使用公告日期（announce_date）")
    print("• 不能使用报告期（report_date）")
    print("• 确保时间点正确性，避免未来函数")
    print()
    
    exercise_1_get_financial_data()
    exercise_2_point_in_time_correctness()
    exercise_3_calculate_pe_ratio()
    exercise_4_handle_missing_data()
    exercise_5_lookahead_trap()
    
    print("\n下一步：Day 11 - 行业分类管理")


if __name__ == '__main__':
    main()
