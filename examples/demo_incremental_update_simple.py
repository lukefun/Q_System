"""
增量更新功能简单演示

使用模拟数据演示DataManager的incremental_update方法。
展示如何自动识别最后更新日期、处理重复数据和进度报告。
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_manager import DataManager
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock


def create_mock_retriever():
    """创建模拟的数据获取器"""
    mock_retriever = Mock()
    
    # 模拟download_history_data方法
    def mock_download(stock_codes, start_date, end_date, period, adjust_type):
        """模拟下载历史数据"""
        stock_code = stock_codes[0]
        
        # 生成日期范围
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        # 生成5天的数据
        dates = []
        current = start_dt
        while current <= end_dt and len(dates) < 5:
            dates.append(current.strftime('%Y%m%d'))
            current += timedelta(days=1)
        
        if not dates:
            return pd.DataFrame()
        
        # 创建模拟数据
        data = pd.DataFrame({
            'stock_code': [stock_code] * len(dates),
            'date': dates,
            'open': [10.0 + i * 0.1 for i in range(len(dates))],
            'high': [11.0 + i * 0.1 for i in range(len(dates))],
            'low': [9.0 + i * 0.1 for i in range(len(dates))],
            'close': [10.5 + i * 0.1 for i in range(len(dates))],
            'volume': [1000000 + i * 10000 for i in range(len(dates))],
            'amount': [10500000 + i * 100000 for i in range(len(dates))]
        })
        
        return data
    
    mock_retriever.download_history_data = mock_download
    return mock_retriever


def progress_callback(current, total, stock_code):
    """进度回调函数"""
    percentage = (current / total) * 100
    print(f"  进度: [{current}/{total}] {percentage:.1f}% - {stock_code}")


def main():
    """主演示函数"""
    
    print("=" * 70)
    print("DataManager 增量更新功能演示")
    print("=" * 70)
    print()
    
    # 1. 初始化
    print("步骤 1: 初始化数据管理器")
    print("-" * 70)
    
    import tempfile
    temp_dir = tempfile.mkdtemp()
    print(f"临时存储路径: {temp_dir}")
    
    manager = DataManager(storage_path=temp_dir)
    retriever = create_mock_retriever()
    
    print("✓ 初始化完成\n")
    
    # 2. 第一次增量更新
    print("步骤 2: 第一次增量更新（无历史数据）")
    print("-" * 70)
    
    stock_codes = ['000001.SZ', '000002.SZ', '600000.SH']
    print(f"股票列表: {', '.join(stock_codes)}")
    print()
    
    updated = manager.incremental_update(
        retriever,
        stock_codes,
        'daily',
        progress_callback=progress_callback
    )
    
    print(f"\n✓ 第一次更新完成，新增 {updated} 条记录\n")
    
    # 3. 查看数据
    print("步骤 3: 查看各股票数据")
    print("-" * 70)
    
    for stock_code in stock_codes:
        data = manager.load_market_data('daily', stock_code)
        last_date = manager.get_last_update_date('daily', stock_code)
        print(f"{stock_code:12} | 记录数: {len(data):3} | 最后更新: {last_date}")
    
    print()
    
    # 4. 第二次增量更新
    print("步骤 4: 第二次增量更新（有历史数据）")
    print("-" * 70)
    print("系统会自动从最后更新日期之后开始获取数据")
    print()
    
    updated = manager.incremental_update(
        retriever,
        stock_codes,
        'daily',
        progress_callback=progress_callback
    )
    
    print(f"\n✓ 第二次更新完成，新增 {updated} 条记录\n")
    
    # 5. 再次查看数据
    print("步骤 5: 更新后的数据统计")
    print("-" * 70)
    
    for stock_code in stock_codes:
        data = manager.load_market_data('daily', stock_code)
        last_date = manager.get_last_update_date('daily', stock_code)
        print(f"{stock_code:12} | 记录数: {len(data):3} | 最后更新: {last_date}")
    
    print()
    
    # 6. 演示重复数据处理
    print("步骤 6: 演示重复数据处理")
    print("-" * 70)
    
    # 手动添加重复数据
    existing_data = manager.load_market_data('daily', '000001.SZ')
    duplicate_data = existing_data.head(2).copy()
    duplicate_data['close'] = duplicate_data['close'] + 1.0
    
    print(f"添加 {len(duplicate_data)} 条重复日期的数据...")
    print(f"重复日期: {', '.join(duplicate_data['date'].tolist())}")
    
    # 保存（会自动去重）
    manager.save_market_data(duplicate_data, 'daily', '000001.SZ')
    
    # 检查结果
    final_data = manager.load_market_data('daily', '000001.SZ')
    print(f"✓ 去重后总记录数: {len(final_data)} 条（重复数据已自动跳过）\n")
    
    # 7. 存储信息
    print("步骤 7: 存储信息统计")
    print("-" * 70)
    
    info = manager.get_storage_info()
    print(f"文件大小: {info['file_size_mb']:.3f} MB")
    print(f"数据类型: {', '.join(info['data_types'])}")
    print(f"总记录数: {info['total_records']}")
    print()
    
    # 8. 导出示例
    print("步骤 8: 导出数据到CSV")
    print("-" * 70)
    
    csv_path = os.path.join(temp_dir, "000001_SZ_daily.csv")
    manager.export_to_csv('daily', csv_path, '000001.SZ')
    
    # 读取并显示前几行
    exported = pd.read_csv(csv_path)
    print(f"✓ 已导出到: {csv_path}")
    print(f"  导出记录数: {len(exported)}")
    print(f"  数据列: {', '.join(exported.columns.tolist())}")
    print()
    
    # 总结
    print("=" * 70)
    print("演示完成！")
    print("=" * 70)
    print()
    print("增量更新功能特性：")
    print("  ✓ 自动识别最后更新日期")
    print("  ✓ 仅获取新数据，避免重复下载")
    print("  ✓ 自动检测和去除重复数据")
    print("  ✓ 支持进度回调，实时监控")
    print("  ✓ 单只股票失败不影响其他股票")
    print("  ✓ 支持多种数据类型（daily, tick, fundamental）")
    print()
    
    # 清理
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"✓ 临时目录已清理")
    except Exception as e:
        print(f"⚠ 清理临时目录失败: {e}")


if __name__ == '__main__':
    main()
