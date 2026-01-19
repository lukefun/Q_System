"""
示例07：增量更新演示

本示例演示如何使用DataManager进行增量更新：
1. 初始化本地数据库
2. 识别最后更新日期
3. 仅下载新数据
4. 避免重复数据
5. 进度报告和统计

学习目标：
- 理解增量更新的原理和优势
- 掌握如何最小化API调用
- 学习如何维护本地数据库的时效性
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from src.data_manager import DataManager
from src.data_retriever import DataRetriever
from src.xtdata_client import XtDataClient
import config
import time

def generate_historical_data(stock_code, start_date, end_date):
    """
    生成历史数据（模拟API返回）
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期字符串 'YYYYMMDD'
        end_date: 结束日期字符串 'YYYYMMDD'
    
    Returns:
        DataFrame: 历史数据
    """
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    
    dates = pd.date_range(start=start, end=end, freq='D')
    
    data = []
    base_price = 10.0 if stock_code.startswith('000') else 8.0
    
    for i, date in enumerate(dates):
        data.append({
            'stock_code': stock_code,
            'date': date.strftime('%Y%m%d'),
            'open': base_price + i * 0.1,
            'high': base_price + i * 0.1 + 0.5,
            'low': base_price + i * 0.1 - 0.3,
            'close': base_price + i * 0.1 + 0.2,
            'volume': 1000000 + i * 10000,
            'amount': (base_price + i * 0.1) * (1000000 + i * 10000)
        })
    
    return pd.DataFrame(data)

def progress_callback(current, total, stock_code):
    """
    进度回调函数
    
    Args:
        current: 当前进度
        total: 总数
        stock_code: 当前处理的股票代码
    """
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"  进度: [{current}/{total}] {percentage:.1f}% - 正在处理: {stock_code}")

def main():
    print("=" * 60)
    print("示例07：增量更新演示")
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
    
    # 2. 场景1：首次下载（无历史数据）
    print("2. 场景1：首次下载（无历史数据）")
    print("-" * 60)
    
    stock_code = '000001.SZ'
    
    # 检查是否有历史数据
    last_date = manager.get_last_update_date('daily', stock_code)
    
    if last_date:
        print(f"发现历史数据，最后更新日期: {last_date}")
    else:
        print("未发现历史数据，将进行首次下载")
        
        # 模拟首次下载
        initial_data = generate_historical_data(
            stock_code=stock_code,
            start_date='20240101',
            end_date='20240110'
        )
        
        print(f"下载历史数据: {len(initial_data)} 条记录")
        print(f"日期范围: {initial_data['date'].iloc[0]} - {initial_data['date'].iloc[-1]}")
        
        # 保存到本地
        manager.save_market_data(
            data=initial_data,
            data_type='daily',
            stock_code=stock_code
        )
        print("✓ 首次下载完成并保存")
    print()
    
    # 3. 场景2：增量更新（有新数据）
    print("3. 场景2：增量更新（有新数据）")
    print("-" * 60)
    
    # 获取最后更新日期
    last_date = manager.get_last_update_date('daily', stock_code)
    print(f"当前最后更新日期: {last_date}")
    
    # 计算需要更新的日期范围
    last_date_obj = datetime.strptime(last_date, '%Y%m%d')
    next_date = last_date_obj + timedelta(days=1)
    end_date = last_date_obj + timedelta(days=5)
    
    print(f"需要更新的日期范围: {next_date.strftime('%Y%m%d')} - {end_date.strftime('%Y%m%d')}")
    
    # 模拟下载新数据
    new_data = generate_historical_data(
        stock_code=stock_code,
        start_date=next_date.strftime('%Y%m%d'),
        end_date=end_date.strftime('%Y%m%d')
    )
    
    print(f"下载新数据: {len(new_data)} 条记录")
    
    # 保存新数据（增量更新）
    manager.save_market_data(
        data=new_data,
        data_type='daily',
        stock_code=stock_code
    )
    
    # 验证更新后的数据
    updated_data = manager.load_market_data('daily', stock_code)
    new_last_date = manager.get_last_update_date('daily', stock_code)
    
    print(f"✓ 增量更新完成")
    print(f"  更新后总记录数: {len(updated_data)}")
    print(f"  新的最后更新日期: {new_last_date}")
    print()
    
    # 4. 场景3：重复数据处理
    print("4. 场景3：重复数据处理")
    print("-" * 60)
    
    # 尝试保存重复数据
    duplicate_data = generate_historical_data(
        stock_code=stock_code,
        start_date='20240110',
        end_date='20240112'
    )
    
    print(f"尝试保存部分重复数据: {len(duplicate_data)} 条记录")
    print(f"日期范围: {duplicate_data['date'].iloc[0]} - {duplicate_data['date'].iloc[-1]}")
    
    before_count = len(manager.load_market_data('daily', stock_code))
    
    manager.save_market_data(
        data=duplicate_data,
        data_type='daily',
        stock_code=stock_code
    )
    
    after_count = len(manager.load_market_data('daily', stock_code))
    
    print(f"✓ 重复数据处理完成")
    print(f"  保存前记录数: {before_count}")
    print(f"  保存后记录数: {after_count}")
    print(f"  新增记录数: {after_count - before_count}")
    print()
    
    # 5. 场景4：批量增量更新
    print("5. 场景4：批量增量更新")
    print("-" * 60)
    
    stock_list = ['000001.SZ', '600000.SH', '600036.SH']
    
    print(f"准备更新 {len(stock_list)} 只股票")
    print(f"股票列表: {', '.join(stock_list)}")
    print()
    
    update_summary = []
    
    for i, stock in enumerate(stock_list, 1):
        print(f"[{i}/{len(stock_list)}] 处理 {stock}")
        
        # 获取最后更新日期
        last_date = manager.get_last_update_date('daily', stock)
        
        if last_date:
            # 增量更新
            last_date_obj = datetime.strptime(last_date, '%Y%m%d')
            next_date = last_date_obj + timedelta(days=1)
            end_date = datetime.now()
            
            if next_date.date() < end_date.date():
                new_data = generate_historical_data(
                    stock_code=stock,
                    start_date=next_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )
                
                manager.save_market_data(
                    data=new_data,
                    data_type='daily',
                    stock_code=stock
                )
                
                update_summary.append({
                    'stock_code': stock,
                    'last_date': last_date,
                    'new_records': len(new_data),
                    'status': '更新成功'
                })
                print(f"  ✓ 新增 {len(new_data)} 条记录")
            else:
                update_summary.append({
                    'stock_code': stock,
                    'last_date': last_date,
                    'new_records': 0,
                    'status': '已是最新'
                })
                print(f"  ✓ 数据已是最新")
        else:
            # 首次下载
            initial_data = generate_historical_data(
                stock_code=stock,
                start_date='20240101',
                end_date=datetime.now().strftime('%Y%m%d')
            )
            
            manager.save_market_data(
                data=initial_data,
                data_type='daily',
                stock_code=stock
            )
            
            update_summary.append({
                'stock_code': stock,
                'last_date': None,
                'new_records': len(initial_data),
                'status': '首次下载'
            })
            print(f"  ✓ 首次下载 {len(initial_data)} 条记录")
        
        # 模拟API调用延迟
        time.sleep(0.1)
        print()
    
    # 6. 更新汇总报告
    print("6. 更新汇总报告")
    print("-" * 60)
    
    summary_df = pd.DataFrame(update_summary)
    print(summary_df.to_string(index=False))
    print()
    
    total_new_records = summary_df['new_records'].sum()
    print(f"总计新增记录: {total_new_records} 条")
    print(f"更新成功: {len(summary_df[summary_df['status'] == '更新成功'])} 只")
    print(f"首次下载: {len(summary_df[summary_df['status'] == '首次下载'])} 只")
    print(f"已是最新: {len(summary_df[summary_df['status'] == '已是最新'])} 只")
    print()
    
    # 7. 增量更新的优势
    print("7. 增量更新的优势")
    print("-" * 60)
    print("""
    增量更新 vs 全量更新：
    
    增量更新优势：
    1. 节省时间：只下载新数据，速度快
    2. 减少API调用：降低被限流的风险
    3. 节省带宽：数据传输量小
    4. 降低服务器负载：对API服务器友好
    
    实现要点：
    1. 准确记录最后更新日期
    2. 正确处理重复数据
    3. 考虑交易日历（跳过非交易日）
    4. 处理数据修正（历史数据可能被修正）
    
    最佳实践：
    1. 每日定时更新（如收盘后）
    2. 添加重试机制处理网络错误
    3. 记录更新日志便于追踪
    4. 定期验证数据完整性
    5. 备份重要数据
    
    注意事项：
    - 首次下载需要较长时间
    - 注意API调用频率限制
    - 处理节假日和停牌情况
    - 考虑数据修正和复权调整
    """)
    
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
