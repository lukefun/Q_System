"""
示例9：构建本地全市场数据库

演示如何使用FullMarketDownloader批量下载全市场股票数据，
构建本地数据库。支持断点续传、进度报告和汇总统计。

学习要点：
1. 全市场数据下载流程
2. 断点续传机制
3. 进度报告和统计
4. 数据完整性验证
5. API速率限制处理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.data_manager import DataManager
from src.full_market_downloader import FullMarketDownloader, download_full_market
from config import logger


def progress_callback(current: int, total: int, stock_code: str):
    """
    进度回调函数
    
    在下载过程中显示进度信息。
    
    Args:
        current: 当前进度
        total: 总数
        stock_code: 当前处理的股票代码
    """
    percentage = (current / total) * 100
    print(f"\r进度: {current}/{total} ({percentage:.1f}%) - {stock_code}", end='', flush=True)


def main():
    """主函数"""
    print("=" * 80)
    print("示例9：构建本地全市场数据库")
    print("=" * 80)
    print()
    
    # ========================================================================
    # 1. 初始化组件
    # ========================================================================
    print("1. 初始化XtData客户端和数据管理器...")
    
    # 创建XtData客户端
    client = XtDataClient(
        account_id="test_account",
        account_key="test_key"
    )
    
    # 连接到XtData服务
    if not client.connect():
        print("错误: 无法连接到XtData服务")
        return
    
    print("   ✓ XtData客户端连接成功")
    
    # 创建数据获取器
    retriever = DataRetriever(client)
    print("   ✓ 数据获取器创建成功")
    
    # 创建数据管理器
    manager = DataManager()
    print("   ✓ 数据管理器创建成功")
    
    print()
    
    # ========================================================================
    # 2. 方法1：使用FullMarketDownloader类
    # ========================================================================
    print("2. 方法1：使用FullMarketDownloader类下载全市场数据...")
    print()
    
    # 创建全市场下载器
    downloader = FullMarketDownloader(
        retriever=retriever,
        data_manager=manager
    )
    
    # 设置日期范围（下载最近10天的数据）
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    print(f"   日期范围: {start_date_str} - {end_date_str}")
    print()
    
    # 检查是否有未完成的下载
    progress = downloader.get_download_progress()
    if progress['is_downloading']:
        print(f"   检测到未完成的下载:")
        print(f"   - 已完成: {progress['completed_count']} 只股票")
        print(f"   - 失败: {progress['failed_count']} 只股票")
        print(f"   - 日期范围: {progress['start_date']} - {progress['end_date']}")
        print()
        
        user_input = input("   是否继续上次的下载？(y/n): ")
        resume = user_input.lower() == 'y'
    else:
        resume = True
    
    print()
    print("   开始下载...")
    print()
    
    try:
        # 下载全市场数据
        stats = downloader.download_full_market(
            start_date=start_date_str,
            end_date=end_date_str,
            data_type='daily',
            resume=resume,
            progress_callback=progress_callback
        )
        
        print()  # 换行
        print()
        
        # 显示统计信息
        print("   下载完成！统计信息:")
        print(f"   - 总股票数: {stats['total_stocks']}")
        print(f"   - 成功下载: {stats['success_count']}")
        print(f"   - 下载失败: {stats['failed_count']}")
        print(f"   - 跳过股票: {stats['skipped_count']}")
        print(f"   - 总记录数: {stats['total_records']}")
        print(f"   - 开始时间: {stats['start_time']}")
        print(f"   - 结束时间: {stats['end_time']}")
        print(f"   - 总耗时: {stats['duration_seconds']:.2f} 秒")
        
        if stats['failed_stocks']:
            print()
            print(f"   失败股票列表（前5个）:")
            for failed in stats['failed_stocks'][:5]:
                print(f"   - {failed['stock_code']}: {failed['error']}")
        
        if 'validation' in stats:
            print()
            print("   数据完整性验证:")
            print(f"   - 有数据: {stats['validation']['stocks_with_data']}")
            print(f"   - 无数据: {stats['validation']['stocks_without_data']}")
        
        print()
    
    except Exception as e:
        print()
        print(f"   错误: 下载失败 - {str(e)}")
        print()
    
    # ========================================================================
    # 3. 方法2：使用便捷函数
    # ========================================================================
    print()
    print("3. 方法2：使用便捷函数下载全市场数据...")
    print()
    print("   （演示用法，实际不执行以避免重复下载）")
    print()
    
    # 演示代码（注释掉以避免实际执行）
    print("   示例代码:")
    print("   ```python")
    print("   from src.full_market_downloader import download_full_market")
    print()
    print("   stats = download_full_market(")
    print("       retriever=retriever,")
    print("       data_manager=manager,")
    print("       start_date='20240101',")
    print("       end_date='20240110',")
    print("       data_type='daily',")
    print("       resume=True,")
    print("       progress_callback=lambda c, t, s: print(f'{c}/{t}: {s}')")
    print("   )")
    print("   ```")
    print()
    
    # ========================================================================
    # 4. 查看存储信息
    # ========================================================================
    print("4. 查看本地数据库存储信息...")
    print()
    
    storage_info = manager.get_storage_info()
    
    print(f"   HDF5文件路径: {storage_info['hdf5_path']}")
    print(f"   文件是否存在: {storage_info['file_exists']}")
    
    if storage_info['file_exists']:
        print(f"   文件大小: {storage_info['file_size_mb']:.2f} MB")
        print(f"   数据类型: {', '.join(storage_info['data_types'])}")
        print(f"   总记录数: {storage_info['total_records']}")
    
    print()
    
    # ========================================================================
    # 5. 验证数据质量
    # ========================================================================
    print("5. 验证部分股票的数据质量...")
    print()
    
    # 获取所有股票代码
    all_codes = retriever.get_all_stock_codes()
    
    if all_codes:
        # 验证前3只股票的数据质量
        for stock_code in all_codes[:3]:
            print(f"   验证股票 {stock_code}...")
            
            try:
                # 加载数据
                data = manager.load_market_data('daily', stock_code)
                
                if data.empty:
                    print(f"   - 无数据")
                    continue
                
                # 生成质量报告
                report = manager.generate_quality_report('daily', stock_code)
                
                print(f"   - 记录数: {report['data_info']['record_count']}")
                print(f"   - 日期范围: {report['data_info']['date_range']['start']} - "
                      f"{report['data_info']['date_range']['end']}")
                print(f"   - 质量评分: {report['summary']['quality_score']}")
                print(f"   - 状态: {report['summary']['status']}")
                print(f"   - 错误数: {report['summary']['error_count']}")
                print(f"   - 警告数: {report['summary']['warning_count']}")
                print(f"   - 异常数: {report['summary']['anomaly_count']}")
                print(f"   - 缺口数: {report['summary']['gap_count']}")
                print()
            
            except Exception as e:
                print(f"   - 验证失败: {str(e)}")
                print()
    
    # ========================================================================
    # 6. 断开连接
    # ========================================================================
    print("6. 断开XtData连接...")
    client.disconnect()
    print("   ✓ 连接已断开")
    print()
    
    print("=" * 80)
    print("示例完成！")
    print("=" * 80)
    print()
    print("学习要点总结:")
    print("1. 使用FullMarketDownloader批量下载全市场数据")
    print("2. 支持断点续传，可以从中断点恢复下载")
    print("3. 提供进度回调，实时显示下载进度")
    print("4. 自动处理API速率限制，避免请求过快")
    print("5. 生成详细的汇总统计和数据完整性验证")
    print("6. 使用状态文件记录下载进度")
    print()
    print("提示:")
    print("- 全市场下载可能需要较长时间，请耐心等待")
    print("- 如果下载中断，可以使用resume=True继续下载")
    print("- 建议在非交易时间进行全市场下载")
    print("- 定期使用增量更新保持数据最新")
    print()


if __name__ == "__main__":
    main()
