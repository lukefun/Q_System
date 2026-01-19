"""
示例05：数据持久化和加载

本示例演示如何使用DataManager进行数据的持久化存储和加载：
1. 保存市场数据到HDF5格式
2. 从HDF5加载数据
3. 查询最后更新日期
4. 导出数据到CSV格式

学习目标：
- 理解HDF5存储格式的优势
- 掌握数据的保存和加载方法
- 学习如何管理本地数据库
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from src.data_manager import DataManager
from src.data_retriever import DataRetriever
from src.xtdata_client import XtDataClient
import config

def main():
    print("=" * 60)
    print("示例05：数据持久化和加载")
    print("=" * 60)
    print()
    
    # 1. 初始化数据管理器
    print("1. 初始化数据管理器")
    print("-" * 60)
    
    storage_path = config.DATA_STORAGE_PATH
    manager = DataManager(storage_path=storage_path)
    
    print(f"存储路径: {storage_path}")
    print(f"HDF5文件: {manager.hdf5_path}")
    print()
    
    # 2. 准备示例数据（模拟从API获取的数据）
    print("2. 准备示例数据")
    print("-" * 60)
    
    # 生成示例日线数据
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    sample_data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * len(dates),
        'date': dates.strftime('%Y%m%d'),
        'open': [10.0 + i * 0.1 for i in range(len(dates))],
        'high': [10.5 + i * 0.1 for i in range(len(dates))],
        'low': [9.8 + i * 0.1 for i in range(len(dates))],
        'close': [10.2 + i * 0.1 for i in range(len(dates))],
        'volume': [1000000 + i * 10000 for i in range(len(dates))],
        'amount': [10000000 + i * 100000 for i in range(len(dates))]
    })
    
    print(f"生成示例数据: {len(sample_data)} 条记录")
    print(sample_data.head())
    print()
    
    # 3. 保存数据到HDF5
    print("3. 保存数据到HDF5")
    print("-" * 60)
    
    try:
        manager.save_market_data(
            data=sample_data,
            data_type='daily',
            stock_code='000001.SZ'
        )
        print("✓ 数据保存成功")
        
        # 检查文件大小
        if os.path.exists(manager.hdf5_path):
            file_size = os.path.getsize(manager.hdf5_path) / 1024  # KB
            print(f"  文件大小: {file_size:.2f} KB")
    except Exception as e:
        print(f"✗ 保存失败: {e}")
    print()
    
    # 4. 从HDF5加载数据
    print("4. 从HDF5加载数据")
    print("-" * 60)
    
    try:
        loaded_data = manager.load_market_data(
            data_type='daily',
            stock_code='000001.SZ'
        )
        print(f"✓ 加载成功: {len(loaded_data)} 条记录")
        print(loaded_data.head())
        
        # 验证数据一致性
        if len(loaded_data) == len(sample_data):
            print("✓ 数据完整性验证通过")
        else:
            print(f"✗ 数据不完整: 期望 {len(sample_data)} 条，实际 {len(loaded_data)} 条")
    except Exception as e:
        print(f"✗ 加载失败: {e}")
    print()
    
    # 5. 查询最后更新日期
    print("5. 查询最后更新日期")
    print("-" * 60)
    
    try:
        last_date = manager.get_last_update_date(
            data_type='daily',
            stock_code='000001.SZ'
        )
        if last_date:
            print(f"✓ 最后更新日期: {last_date}")
            
            # 转换为可读格式
            date_obj = datetime.strptime(last_date, '%Y%m%d')
            print(f"  格式化日期: {date_obj.strftime('%Y年%m月%d日')}")
        else:
            print("✗ 未找到更新记录")
    except Exception as e:
        print(f"✗ 查询失败: {e}")
    print()
    
    # 6. 按日期范围加载数据
    print("6. 按日期范围加载数据")
    print("-" * 60)
    
    try:
        filtered_data = manager.load_market_data(
            data_type='daily',
            stock_code='000001.SZ',
            start_date='20240103',
            end_date='20240107'
        )
        print(f"✓ 加载指定日期范围数据: {len(filtered_data)} 条记录")
        print(filtered_data)
    except Exception as e:
        print(f"✗ 加载失败: {e}")
    print()
    
    # 7. 导出数据到CSV
    print("7. 导出数据到CSV")
    print("-" * 60)
    
    csv_output_path = os.path.join(config.DATA_STORAGE_PATH, 'csv_exports', '000001_example.csv')
    
    try:
        # 确保导出目录存在
        os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
        
        manager.export_to_csv(
            data_type='daily',
            output_path=csv_output_path,
            stock_code='000001.SZ'
        )
        print(f"✓ 数据导出成功")
        print(f"  导出路径: {csv_output_path}")
        
        # 检查文件大小
        if os.path.exists(csv_output_path):
            file_size = os.path.getsize(csv_output_path) / 1024  # KB
            print(f"  文件大小: {file_size:.2f} KB")
    except Exception as e:
        print(f"✗ 导出失败: {e}")
    print()
    
    # 8. 保存多只股票数据
    print("8. 保存多只股票数据")
    print("-" * 60)
    
    # 生成第二只股票的数据
    sample_data_2 = sample_data.copy()
    sample_data_2['stock_code'] = '600000.SH'
    sample_data_2['open'] = sample_data_2['open'] * 2
    sample_data_2['high'] = sample_data_2['high'] * 2
    sample_data_2['low'] = sample_data_2['low'] * 2
    sample_data_2['close'] = sample_data_2['close'] * 2
    
    try:
        manager.save_market_data(
            data=sample_data_2,
            data_type='daily',
            stock_code='600000.SH'
        )
        print("✓ 第二只股票数据保存成功")
        
        # 验证两只股票的数据都存在
        data_1 = manager.load_market_data('daily', '000001.SZ')
        data_2 = manager.load_market_data('daily', '600000.SH')
        
        print(f"  000001.SZ: {len(data_1)} 条记录")
        print(f"  600000.SH: {len(data_2)} 条记录")
    except Exception as e:
        print(f"✗ 保存失败: {e}")
    print()
    
    # 9. 数据持久化的优势总结
    print("9. 数据持久化的优势")
    print("-" * 60)
    print("""
    HDF5格式的优势：
    1. 高效存储：二进制格式，压缩率高
    2. 快速读取：支持部分读取，无需加载全部数据
    3. 结构化：支持分层存储，便于组织管理
    4. 跨平台：Python、R、MATLAB等都支持
    
    使用场景：
    - 本地数据库构建
    - 历史数据缓存
    - 回测数据准备
    - 数据分析研究
    
    注意事项：
    - 定期备份数据文件
    - 使用增量更新避免重复下载
    - 合理设置数据压缩级别
    - 注意磁盘空间管理
    """)
    
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
