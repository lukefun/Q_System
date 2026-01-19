"""
Day 14 练习：全市场数据库构建

学习目标：
1. 掌握全市场数据下载
2. 理解断点续传机制
3. 学会数据质量检查
4. 掌握数据库维护方法

金融概念：
- 全市场数据库：包含所有股票的历史数据
- 断点续传：下载中断后可以继续，不需要重新开始
- 数据质量：数据的准确性、完整性和一致性
- 数据维护：定期更新和清理数据

前置知识：Day 8-13

作者：Q_System
日期：2026-01-19
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.data_manager import DataManager
from src.full_market_downloader import FullMarketDownloader
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY, DATA_STORAGE_PATH


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：下载全市场数据
def exercise_1_download_full_market():
    """下载全市场日线数据"""
    print_section("练习1：下载全市场数据")
    print("TODO: 下载所有股票的日线数据")
    print("提示：使用FullMarketDownloader.download_full_market()")
    print("注意：全市场下载需要较长时间，建议先用少量股票测试")


# 练习2：断点续传
def exercise_2_resume_download():
    """使用断点续传功能"""
    print_section("练习2：断点续传")
    print("TODO: 模拟下载中断，然后使用断点续传继续")
    print("提示：传入resume=True参数")


# 练习3：进度报告
def exercise_3_progress_callback():
    """实现进度回调函数"""
    print_section("练习3：进度报告")
    print("TODO: 实现进度回调函数，显示下载进度")
    print("提示：定义progress_callback函数")


# 练习4：数据质量检查
def exercise_4_quality_check():
    """检查数据质量"""
    print_section("练习4：数据质量检查")
    print("TODO: 对下载的数据进行质量检查")
    print("提示：使用DataManager.generate_quality_report()")


# 练习5：数据库维护
def exercise_5_database_maintenance():
    """数据库维护操作"""
    print_section("练习5：数据库维护")
    print("TODO: 执行数据库维护操作")
    print("提示：包括增量更新、数据清理、统计信息等")


def main():
    print("=" * 60)
    print("  Day 14 练习：全市场数据库构建")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• 全市场数据库是量化交易的基础")
    print("• 断点续传提高下载可靠性")
    print("• 数据质量检查确保数据准确性")
    print("• 定期维护保持数据最新")
    print()
    
    exercise_1_download_full_market()
    exercise_2_resume_download()
    exercise_3_progress_callback()
    exercise_4_quality_check()
    exercise_5_database_maintenance()
    
    print("\n" + "=" * 60)
    print("  Week 2 练习全部完成！")
    print("=" * 60)
    print()
    print("恭喜你完成了Week 2的所有练习！")
    print()
    print("你已经掌握：")
    print("✓ XtData API的使用")
    print("✓ 价格复权的原理和应用")
    print("✓ 基本面数据的处理")
    print("✓ 行业分类的查询")
    print("✓ 数据的持久化和查询")
    print("✓ 数据的可视化")
    print("✓ 全市场数据库的构建")
    print()
    print("下一步：")
    print("• 复习本周的核心概念")
    print("• 完善自己的数据库")
    print("• 准备进入Week 3：策略开发")


if __name__ == '__main__':
    main()
