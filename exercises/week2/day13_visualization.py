"""
Day 13 练习：数据可视化

学习目标：
1. 掌握K线图的绘制
2. 学会添加技术指标
3. 理解成交量的展示
4. 掌握多股票对比图

金融概念：
- K线图（蜡烛图）：展示OHLC数据的图表
- 移动平均线（MA）：平滑价格波动的技术指标
- 成交量：反映市场活跃度的指标
- 技术分析：基于价格和成交量的分析方法

前置知识：Day 8-12

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.visualizer import Visualizer
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：绘制K线图
def exercise_1_plot_kline():
    """绘制基本K线图"""
    print_section("练习1：绘制K线图")
    print("TODO: 绘制股票的K线图")
    print("提示：使用Visualizer.plot_kline()")


# 练习2：添加移动平均线
def exercise_2_add_moving_average():
    """添加移动平均线"""
    print_section("练习2：添加移动平均线")
    print("TODO: 在K线图上叠加5日和20日均线")
    print("提示：传入ma_periods=[5, 20]参数")


# 练习3：绘制成交量
def exercise_3_plot_volume():
    """绘制成交量柱状图"""
    print_section("练习3：绘制成交量")
    print("TODO: 绘制成交量柱状图")
    print("提示：使用Visualizer.plot_volume()")


# 练习4：多股票对比
def exercise_4_compare_stocks():
    """绘制多股票对比图"""
    print_section("练习4：多股票对比")
    print("TODO: 绘制多只股票的收盘价对比图")
    print("提示：使用Visualizer.plot_multiple_stocks()")


# 练习5：保存图表
def exercise_5_save_chart():
    """保存图表到文件"""
    print_section("练习5：保存图表")
    print("TODO: 将图表保存为PNG文件")
    print("提示：传入save_path参数")


def main():
    print("=" * 60)
    print("  Day 13 练习：数据可视化")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• K线图直观展示价格走势")
    print("• 移动平均线帮助识别趋势")
    print("• 成交量反映市场活跃度")
    print()
    
    exercise_1_plot_kline()
    exercise_2_add_moving_average()
    exercise_3_plot_volume()
    exercise_4_compare_stocks()
    exercise_5_save_chart()
    
    print("\n下一步：Day 14 - 全市场数据库构建")


if __name__ == '__main__':
    main()
