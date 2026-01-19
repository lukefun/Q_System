"""
增量更新功能演示

演示如何使用DataManager的incremental_update方法进行增量数据更新。
该功能会自动识别最后更新日期，仅获取新数据，并处理重复数据。
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_manager import DataManager
from src.data_retriever import DataRetriever
from src.xtdata_client import XtDataClient
import pandas as pd
from datetime import datetime


def progress_callback(current, total, stock_code):
    """
    进度回调函数
    
    Args:
        current: 当前处理的股票序号
        total: 总股票数
        stock_code: 当前股票代码
    """
    percentage = (current / total) * 100
    print(f"进度: [{current}/{total}] {percentage:.1f}% - 正在处理: {stock_code}")


def demo_incremental_update():
    """演示增量更新功能"""
    
    print("=" * 60)
    print("增量更新功能演示")
    print("=" * 60)
    print()
    
    # 1. 初始化组件
    print("1. 初始化数据管理器和数据获取器...")
    
    # 使用临时目录存储数据
    import tempfile
    temp_dir = tempfile.mkdtemp()
    print(f"   数据存储路径: {temp_dir}")
    
    manager = DataManager(storage_path=temp_dir)
    
    # 创建模拟的客户端和获取器
    client = XtDataClient(account_id="demo", account_key="demo")
    client.connect()
    retriever = DataRetriever(client)
    
    print("   ✓ 初始化完成")
    print()
    
    # 2. 第一次更新 - 没有历史数据
    print("2. 第一次增量更新（没有历史数据）...")
    
    stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
    
    updated_count = manager.incremental_update(
        retriever,
        stock_codes,
        data_type='daily',
        progress_callback=progress_callback
    )
    
    print(f"   ✓ 第一次更新完成，新增 {updated_count} 条记录")
    print()
    
    # 3. 查看每只股票的数据
    print("3. 查看各股票的数据情况...")
    for stock_code in stock_codes:
        data = manager.load_market_data('daily', stock_code)
        if not data.empty:
            last_date = manager.get_last_update_date('daily', stock_code)
            print(f"   {stock_code}: {len(data)} 条记录, 最后更新: {last_date}")
    print()
    
    # 4. 第二次更新 - 有历史数据
    print("4. 第二次增量更新（有历史数据）...")
    print("   系统会自动识别最后更新日期，仅获取新数据...")
    
    updated_count = manager.incremental_update(
        retriever,
        stock_codes,
        data_type='daily',
        progress_callback=progress_callback
    )
    
    print(f"   ✓ 第二次更新完成，新增 {updated_count} 条记录")
    print()
    
    # 5. 再次查看数据
    print("5. 更新后的数据情况...")
    for stock_code in stock_codes:
        data = manager.load_market_data('daily', stock_code)
        if not data.empty:
            last_date = manager.get_last_update_date('daily', stock_code)
            print(f"   {stock_code}: {len(data)} 条记录, 最后更新: {last_date}")
    print()
    
    # 6. 演示重复数据处理
    print("6. 演示重复数据处理...")
    print("   手动添加一些重复日期的数据...")
    
    # 获取第一只股票的现有数据
    existing_data = manager.load_market_data('daily', '000001.SZ')
    if not existing_data.empty:
        # 创建包含重复日期的数据
        duplicate_data = existing_data.head(2).copy()
        duplicate_data['close'] = duplicate_data['close'] + 1.0  # 修改价格
        
        print(f"   添加 {len(duplicate_data)} 条重复日期的数据...")
        
        # 尝试保存（会自动去重）
        manager.save_market_data(duplicate_data, 'daily', '000001.SZ')
        
        # 检查数据量
        final_data = manager.load_market_data('daily', '000001.SZ')
        print(f"   ✓ 去重后数据量: {len(final_data)} 条（重复数据已被跳过）")
    print()
    
    # 7. 获取存储信息
    print("7. 存储信息统计...")
    info = manager.get_storage_info()
    print(f"   文件路径: {info['hdf5_path']}")
    print(f"   文件大小: {info['file_size_mb']:.2f} MB")
    print(f"   数据类型: {', '.join(info['data_types'])}")
    print(f"   总记录数: {info['total_records']}")
    print()
    
    # 8. 导出数据到CSV
    print("8. 导出数据到CSV...")
    csv_path = os.path.join(temp_dir, "000001_SZ_daily.csv")
    manager.export_to_csv('daily', csv_path, '000001.SZ')
    print(f"   ✓ 数据已导出到: {csv_path}")
    print()
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print()
    print("关键特性总结：")
    print("1. ✓ 自动识别最后更新日期")
    print("2. ✓ 仅获取新数据，避免重复下载")
    print("3. ✓ 自动检测和去除重复数据")
    print("4. ✓ 支持进度回调，实时监控更新进度")
    print("5. ✓ 单只股票失败不影响其他股票")
    print("6. ✓ 支持多种数据类型（daily, tick, fundamental）")
    print()
    
    # 清理临时目录
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"✓ 临时目录已清理: {temp_dir}")
    except:
        print(f"⚠ 无法清理临时目录: {temp_dir}")


def demo_error_handling():
    """演示错误处理"""
    
    print("\n" + "=" * 60)
    print("错误处理演示")
    print("=" * 60)
    print()
    
    import tempfile
    temp_dir = tempfile.mkdtemp()
    manager = DataManager(storage_path=temp_dir)
    
    client = XtDataClient(account_id="demo", account_key="demo")
    client.connect()
    retriever = DataRetriever(client)
    
    # 1. 空股票列表
    print("1. 测试空股票列表...")
    try:
        manager.incremental_update(retriever, [], 'daily')
        print("   ✗ 应该抛出异常")
    except Exception as e:
        print(f"   ✓ 正确捕获异常: {type(e).__name__}")
    print()
    
    # 2. 无效数据类型
    print("2. 测试无效数据类型...")
    try:
        manager.incremental_update(retriever, ['000001.SZ'], 'invalid_type')
        print("   ✗ 应该抛出异常")
    except Exception as e:
        print(f"   ✓ 正确捕获异常: {type(e).__name__}")
    print()
    
    # 3. None retriever
    print("3. 测试None retriever...")
    try:
        manager.incremental_update(None, ['000001.SZ'], 'daily')
        print("   ✗ 应该抛出异常")
    except Exception as e:
        print(f"   ✓ 正确捕获异常: {type(e).__name__}")
    print()
    
    print("=" * 60)
    print("错误处理演示完成！")
    print("=" * 60)
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except:
        pass


if __name__ == '__main__':
    # 运行主演示
    demo_incremental_update()
    
    # 运行错误处理演示
    demo_error_handling()
