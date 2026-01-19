"""
Day 12 练习：数据持久化

学习目标：
1. 掌握HDF5数据存储
2. 学会数据的保存和加载
3. 理解增量更新机制
4. 掌握数据查询方法

金融概念：
- 数据持久化：将数据保存到磁盘，避免重复下载
- HDF5格式：高效的二进制存储格式，适合大规模数据
- 增量更新：只下载新增数据，提高效率
- 数据完整性：确保数据的准确性和一致性

前置知识：Day 8-11

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
from config import XTDATA_ACCOUNT_ID, XTDATA_ACCOUNT_KEY, DATA_STORAGE_PATH


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# 练习1：保存数据到HDF5
def exercise_1_save_data():
    """保存市场数据到HDF5"""
    print_section("练习1：保存数据到HDF5")
    print("TODO: 获取数据并保存到HDF5文件")
    print("提示：使用DataManager.save_market_data()")


# 练习2：从HDF5加载数据
def exercise_2_load_data():
    """从HDF5加载数据"""
    print_section("练习2：从HDF5加载数据")
    print("TODO: 从HDF5文件加载数据")
    print("提示：使用DataManager.load_market_data()")


# 练习3：数据查询
def exercise_3_query_data():
    """按条件查询数据"""
    print_section("练习3：数据查询")
    print("TODO: 按股票代码和日期范围查询数据")
    print("提示：传入start_date和end_date参数")


# 练习4：增量更新
def exercise_4_incremental_update():
    """执行增量更新"""
    print_section("练习4：增量更新")
    print("TODO: 执行增量更新，只下载新数据")
    print("提示：使用DataManager.incremental_update()")


# 练习5：数据导出
def exercise_5_export_data():
    """导出数据到CSV"""
    print_section("练习5：数据导出")
    print("TODO: 将HDF5数据导出为CSV文件")
    print("提示：使用DataManager.export_to_csv()")


def main():
    print("=" * 60)
    print("  Day 12 练习：数据持久化")
    print("=" * 60)
    print()
    print("重要概念：")
    print("• HDF5提供高效的数据存储")
    print("• 增量更新减少API调用")
    print("• 数据查询支持多种过滤条件")
    print()
    
    exercise_1_save_data()
    exercise_2_load_data()
    exercise_3_query_data()
    exercise_4_incremental_update()
    exercise_5_export_data()
    
    print("\n下一步：Day 13 - 数据可视化")


if __name__ == '__main__':
    main()
