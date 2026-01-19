"""
Day 9 练习：价格复权

学习目标：
1. 理解前复权和后复权的区别
2. 掌握复权算法的实现
3. 学会在回测中正确使用复权
4. 理解未来函数的概念

金融概念：
- 除权除息：分红送股导致的价格调整
- 前复权：保持当前价格不变，向前调整历史价格（用于回测）
- 后复权：保持历史价格不变，向后调整当前价格（用于展示）
- 复权因子：反映分红送股对价格影响的系数

前置知识：Day 8 - XtData基础接口

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：获取并应用前复权
def exercise_1_forward_adjust():
    """
    练习1：获取并应用前复权
    
    任务：
    1. 获取某只股票的原始日线数据
    2. 应用前复权
    3. 对比复权前后的价格差异
    4. 打印最近5天的复权前后价格
    
    提示：
    - 使用PriceAdjuster.forward_adjust()方法
    - 对比原始数据和复权后数据的close列
    """
    print_section("练习1：获取并应用前复权")
    print("TODO: 实现前复权处理")
    print("提示：参考 examples/02_price_adjustment.py")


# 练习2：对比前复权和后复权
def exercise_2_compare_adjustments():
    """
    练习2：对比前复权和后复权
    
    任务：
    1. 对同一只股票分别应用前复权和后复权
    2. 对比两种复权方法的结果
    3. 验证前复权保持当前价格不变
    4. 验证后复权保持历史价格连续
    
    提示：
    - 使用forward_adjust()和backward_adjust()
    - 比较最新日期和最早日期的价格
    """
    print_section("练习2：对比前复权和后复权")
    print("TODO: 对比两种复权方法")


# 练习3：验证OHLCV一致性
def exercise_3_verify_ohlcv_consistency():
    """
    练习3：验证OHLCV一致性
    
    任务：
    1. 对数据应用复权
    2. 验证复权后OHLC关系仍然成立：
       - high >= max(open, close)
       - low <= min(open, close)
    3. 统计违反关系的记录数
    
    提示：
    - 使用pandas的布尔索引
    - 检查每一行的OHLC关系
    """
    print_section("练习3：验证OHLCV一致性")
    print("TODO: 验证OHLCV关系")


# 练习4：计算复权收益率
def exercise_4_calculate_adjusted_returns():
    """
    练习4：计算复权收益率
    
    任务：
    1. 获取股票数据并应用前复权
    2. 计算日收益率：(今日收盘价 - 昨日收盘价) / 昨日收盘价
    3. 计算累计收益率
    4. 打印最大单日涨幅和跌幅
    
    提示：
    - 使用pct_change()计算收益率
    - 使用cumprod()计算累计收益率
    """
    print_section("练习4：计算复权收益率")
    print("TODO: 计算收益率")


# 练习5：未来函数演示
def exercise_5_lookahead_bias_demo():
    """
    练习5：未来函数演示
    
    任务：
    1. 模拟一个简单的回测场景
    2. 分别使用前复权和后复权
    3. 对比两种方法的回测结果
    4. 理解为什么后复权会导致未来函数
    
    提示：
    - 假设策略：价格低于某个阈值时买入
    - 使用前复权和后复权分别回测
    - 观察信号触发的差异
    """
    print_section("练习5：未来函数演示")
    print("TODO: 演示未来函数问题")
    print("提示：参考 examples/10_lookahead_bias_demo.py")


# 扩展挑战：批量复权处理
def challenge_batch_adjustment():
    """
    扩展挑战：批量复权处理
    
    任务：
    1. 获取多只股票的数据
    2. 对每只股票应用前复权
    3. 计算每只股票的累计收益率
    4. 找出收益率最高的股票
    
    提示：
    - 使用循环处理每只股票
    - 将结果存储在字典中
    - 使用max()找出最大值
    """
    print_section("扩展挑战：批量复权处理")
    print("TODO: 批量处理多只股票")


def main():
    """主函数"""
    print("=" * 60)
    print("  Day 9 练习：价格复权")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• 前复权：保持当前价格不变，用于回测")
    print("• 后复权：保持历史价格不变，用于展示")
    print("• 回测必须使用前复权，避免未来函数")
    print()
    
    exercise_1_forward_adjust()
    exercise_2_compare_adjustments()
    exercise_3_verify_ohlcv_consistency()
    exercise_4_calculate_adjusted_returns()
    exercise_5_lookahead_bias_demo()
    
    print("\n" + "=" * 60)
    print("  扩展挑战（可选）")
    print("=" * 60)
    challenge_batch_adjustment()
    
    print("\n" + "=" * 60)
    print("  练习完成！")
    print("=" * 60)
    print()
    print("关键要点：")
    print("✓ 前复权适合回测，后复权适合展示")
    print("✓ 复权保持OHLCV数据的相对关系")
    print("✓ 使用后复权回测会导致未来函数")
    print()
    print("下一步：Day 10 - 基本面数据ETL")


if __name__ == '__main__':
    main()
