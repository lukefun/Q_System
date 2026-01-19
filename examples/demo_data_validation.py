"""
数据验证和质量检查演示

演示如何使用DataManager的数据验证和质量检查功能：
1. 数据类型和范围验证
2. 异常值检测（负价格、极端值）
3. 数据缺口检测
4. 生成数据质量报告

作者：量化交易培训计划
日期：2024-01
"""

import pandas as pd
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_manager import DataManager
from config import logger


def demo_basic_validation():
    """演示基本数据验证"""
    print("\n" + "="*80)
    print("演示1：基本数据验证")
    print("="*80)
    
    # 创建数据管理器
    manager = DataManager(storage_path="./data/demo_validation")
    
    # 创建有效数据
    print("\n1.1 验证有效数据")
    valid_data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 5,
        'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
        'open': [10.0, 10.5, 10.3, 10.8, 10.6],
        'high': [10.8, 10.9, 10.7, 11.0, 10.9],
        'low': [9.8, 10.2, 10.0, 10.5, 10.3],
        'close': [10.5, 10.3, 10.6, 10.7, 10.8],
        'volume': [1000000, 1200000, 900000, 1100000, 1050000]
    })
    
    report = manager.validate_data(valid_data, 'daily')
    
    print(f"数据有效性: {report['is_valid']}")
    print(f"错误数量: {len(report['errors'])}")
    print(f"警告数量: {len(report['warnings'])}")
    print(f"异常值数量: {len(report['anomalies'])}")
    print(f"记录数: {report['statistics']['record_count']}")
    
    # 创建有问题的数据
    print("\n1.2 验证有问题的数据")
    invalid_data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 5,
        'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
        'open': [10.0, -5.0, 10.3, 10.8, 10.6],  # 包含负价格
        'high': [10.8, 10.9, 10.7, 11.0, 10.9],
        'low': [9.8, 10.2, 10.0, 10.5, 10.3],
        'close': [10.5, 10.3, 10.6, 10.7, 10.8],
        'volume': [1000000, -500000, 900000, 1100000, 1050000]  # 包含负成交量
    })
    
    report = manager.validate_data(invalid_data, 'daily')
    
    print(f"数据有效性: {report['is_valid']}")
    print(f"错误数量: {len(report['errors'])}")
    
    if report['errors']:
        print("\n发现的错误:")
        for i, error in enumerate(report['errors'], 1):
            print(f"  {i}. {error}")


def demo_anomaly_detection():
    """演示异常值检测"""
    print("\n" + "="*80)
    print("演示2：异常值检测")
    print("="*80)
    
    manager = DataManager(storage_path="./data/demo_validation")
    
    # 创建包含异常值的数据
    print("\n2.1 检测价格异常")
    data_with_anomalies = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 10,
        'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
        'open': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 50.0],  # 最后一个异常
        'high': [10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 55.0],
        'low': [9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 45.0],
        'close': [10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 52.0],
        'volume': [1000000, 1100000, 1200000, 1300000, 1400000, 
                   1500000, 1600000, 1700000, 1800000, 50000000]  # 最后一个极端
    })
    
    report = manager.validate_data(data_with_anomalies, 'daily')
    
    print(f"检测到 {len(report['anomalies'])} 个异常值")
    
    if report['anomalies']:
        print("\n异常值详情:")
        for i, anomaly in enumerate(report['anomalies'][:5], 1):  # 只显示前5个
            print(f"\n  异常 {i}:")
            print(f"    类型: {anomaly['type']}")
            print(f"    列: {anomaly['column']}")
            print(f"    值: {anomaly['value']}")
            print(f"    日期: {anomaly['date']}")
            print(f"    原因: {anomaly['reason']}")
    
    # 检测零成交量
    print("\n2.2 检测零成交量")
    data_with_zero_volume = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 5,
        'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
        'open': [10.0, 10.5, 10.3, 10.8, 10.6],
        'high': [10.8, 10.9, 10.7, 11.0, 10.9],
        'low': [9.8, 10.2, 10.0, 10.5, 10.3],
        'close': [10.5, 10.3, 10.6, 10.7, 10.8],
        'volume': [1000000, 0, 900000, 0, 1050000]  # 包含零成交量
    })
    
    report = manager.validate_data(data_with_zero_volume, 'daily')
    
    zero_volume_anomalies = [
        a for a in report['anomalies'] 
        if a['type'] == '成交量异常' and a['value'] == 0
    ]
    
    print(f"检测到 {len(zero_volume_anomalies)} 个零成交量异常")
    
    for anomaly in zero_volume_anomalies:
        print(f"  日期 {anomaly['date']}: 成交量为零")


def demo_gap_detection():
    """演示数据缺口检测"""
    print("\n" + "="*80)
    print("演示3：数据缺口检测")
    print("="*80)
    
    manager = DataManager(storage_path="./data/demo_validation")
    
    # 创建有缺口的数据
    print("\n3.1 检测日线数据缺口")
    data_with_gaps = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 6,
        'date': [
            '20240101', '20240102', '20240103',  # 连续
            '20240110',  # 缺口：20240104-20240109
            '20240111', '20240112'
        ],
        'close': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
    })
    
    gaps = manager.detect_data_gaps(data_with_gaps, 'daily', '000001.SZ')
    
    print(f"检测到 {len(gaps)} 个数据缺口")
    
    if gaps:
        print("\n缺口详情:")
        for i, gap in enumerate(gaps, 1):
            print(f"\n  缺口 {i}:")
            print(f"    开始日期: {gap['start_date']}")
            print(f"    结束日期: {gap['end_date']}")
            print(f"    缺失天数: {gap['gap_days']}")
    
    # 创建连续数据（无缺口）
    print("\n3.2 检测连续数据（无缺口）")
    continuous_data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 5,
        'date': ['20240101', '20240102', '20240103', '20240104', '20240105'],
        'close': [10.0, 10.1, 10.2, 10.3, 10.4]
    })
    
    gaps = manager.detect_data_gaps(continuous_data, 'daily', '000001.SZ')
    
    print(f"检测到 {len(gaps)} 个数据缺口")
    if len(gaps) == 0:
        print("数据连续，没有缺口！")


def demo_quality_report():
    """演示生成数据质量报告"""
    print("\n" + "="*80)
    print("演示4：生成数据质量报告")
    print("="*80)
    
    manager = DataManager(storage_path="./data/demo_validation")
    
    # 保存一些测试数据
    print("\n4.1 保存测试数据")
    
    # 高质量数据
    good_data = pd.DataFrame({
        'stock_code': ['000001.SZ'] * 10,
        'date': [f'2024010{i}' for i in range(1, 10)] + ['20240110'],
        'open': [10.0 + i * 0.1 for i in range(10)],
        'high': [10.5 + i * 0.1 for i in range(10)],
        'low': [9.5 + i * 0.1 for i in range(10)],
        'close': [10.2 + i * 0.1 for i in range(10)],
        'volume': [1000000 + i * 100000 for i in range(10)]
    })
    manager.save_market_data(good_data, 'daily', '000001.SZ')
    
    # 有问题的数据
    bad_data = pd.DataFrame({
        'stock_code': ['000002.SZ'] * 10,
        'date': ['20240101', '20240102', '20240103', '20240110',  # 有缺口
                 '20240111', '20240112', '20240113', '20240114', 
                 '20240115', '20240116'],
        'open': [20.0, -5.0, 20.3, 20.8, 20.6, 20.7, 20.8, 20.9, 21.0, 21.1],  # 有负价格
        'high': [20.8, 20.9, 20.7, 21.0, 20.9, 21.0, 21.1, 21.2, 21.3, 21.4],
        'low': [19.8, 20.2, 20.0, 20.5, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8],
        'close': [20.5, 20.3, 20.6, 20.7, 20.8, 20.9, 21.0, 21.1, 21.2, 21.3],
        'volume': [2000000, 0, 1900000, 2100000, 0, 2200000,  # 有零成交量
                   2300000, 2400000, 2500000, 2600000]
    })
    manager.save_market_data(bad_data, 'daily', '000002.SZ')
    
    # 生成高质量数据的报告
    print("\n4.2 高质量数据报告")
    report = manager.generate_quality_report('daily', '000001.SZ')
    
    print(f"\n数据信息:")
    print(f"  股票代码: {report['data_info']['stock_code']}")
    print(f"  记录数: {report['data_info']['record_count']}")
    print(f"  日期范围: {report['data_info']['date_range']['start']} - "
          f"{report['data_info']['date_range']['end']}")
    
    print(f"\n质量摘要:")
    print(f"  质量评分: {report['summary']['quality_score']:.1f}/100")
    print(f"  完整性: {report['summary']['completeness']:.1f}%")
    print(f"  状态: {report['summary']['status']}")
    print(f"  错误数: {report['summary']['error_count']}")
    print(f"  警告数: {report['summary']['warning_count']}")
    print(f"  异常值数: {report['summary']['anomaly_count']}")
    print(f"  缺口数: {report['summary']['gap_count']}")
    
    # 生成低质量数据的报告
    print("\n4.3 低质量数据报告")
    report = manager.generate_quality_report('daily', '000002.SZ')
    
    print(f"\n数据信息:")
    print(f"  股票代码: {report['data_info']['stock_code']}")
    print(f"  记录数: {report['data_info']['record_count']}")
    print(f"  日期范围: {report['data_info']['date_range']['start']} - "
          f"{report['data_info']['date_range']['end']}")
    
    print(f"\n质量摘要:")
    print(f"  质量评分: {report['summary']['quality_score']:.1f}/100")
    print(f"  完整性: {report['summary']['completeness']:.1f}%")
    print(f"  状态: {report['summary']['status']}")
    print(f"  错误数: {report['summary']['error_count']}")
    print(f"  警告数: {report['summary']['warning_count']}")
    print(f"  异常值数: {report['summary']['anomaly_count']}")
    print(f"  缺口数: {report['summary']['gap_count']}")
    
    if report['validation_result']['errors']:
        print(f"\n发现的错误:")
        for i, error in enumerate(report['validation_result']['errors'][:3], 1):
            print(f"  {i}. {error}")
    
    if report['gaps']:
        print(f"\n发现的缺口:")
        for i, gap in enumerate(report['gaps'][:3], 1):
            print(f"  {i}. {gap['start_date']} - {gap['end_date']} "
                  f"(缺失 {gap['gap_days']} 天)")


def demo_validation_workflow():
    """演示完整的数据验证工作流"""
    print("\n" + "="*80)
    print("演示5：完整的数据验证工作流")
    print("="*80)
    
    manager = DataManager(storage_path="./data/demo_validation")
    
    # 模拟从API获取的数据
    print("\n5.1 模拟获取数据")
    raw_data = pd.DataFrame({
        'stock_code': ['000003.SZ'] * 8,
        'date': ['20240101', '20240102', '20240103', '20240104',
                 '20240105', '20240108', '20240109', '20240110'],
        'open': [30.0, 30.5, 30.3, 30.8, 30.6, 30.7, 30.8, 30.9],
        'high': [30.8, 30.9, 30.7, 31.0, 30.9, 31.0, 31.1, 31.2],
        'low': [29.8, 30.2, 30.0, 30.5, 30.3, 30.4, 30.5, 30.6],
        'close': [30.5, 30.3, 30.6, 30.7, 30.8, 30.9, 31.0, 31.1],
        'volume': [3000000, 3100000, 3200000, 3300000, 
                   3400000, 3500000, 3600000, 3700000]
    })
    
    print(f"获取到 {len(raw_data)} 条记录")
    
    # 步骤1：验证数据
    print("\n5.2 验证数据质量")
    validation_report = manager.validate_data(raw_data, 'daily')
    
    if validation_report['is_valid']:
        print("✓ 数据验证通过")
    else:
        print("✗ 数据验证失败")
        print(f"  错误: {validation_report['errors']}")
        return
    
    # 步骤2：检查异常值
    print("\n5.3 检查异常值")
    if validation_report['anomalies']:
        print(f"⚠ 发现 {len(validation_report['anomalies'])} 个异常值")
        for anomaly in validation_report['anomalies'][:3]:
            print(f"  - {anomaly['type']}: {anomaly['column']} = {anomaly['value']}")
    else:
        print("✓ 未发现异常值")
    
    # 步骤3：检查数据缺口
    print("\n5.4 检查数据缺口")
    gaps = manager.detect_data_gaps(raw_data, 'daily', '000003.SZ')
    
    if gaps:
        print(f"⚠ 发现 {len(gaps)} 个数据缺口")
        for gap in gaps:
            print(f"  - {gap['start_date']} 到 {gap['end_date']}: "
                  f"缺失 {gap['gap_days']} 天")
    else:
        print("✓ 数据连续，无缺口")
    
    # 步骤4：保存数据
    print("\n5.5 保存数据")
    manager.save_market_data(raw_data, 'daily', '000003.SZ')
    print("✓ 数据已保存")
    
    # 步骤5：生成质量报告
    print("\n5.6 生成质量报告")
    quality_report = manager.generate_quality_report('daily', '000003.SZ')
    
    print(f"\n最终质量评分: {quality_report['summary']['quality_score']:.1f}/100")
    print(f"数据状态: {quality_report['summary']['status']}")
    
    print("\n✓ 数据验证工作流完成！")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("数据验证和质量检查演示")
    print("="*80)
    
    try:
        # 运行各个演示
        demo_basic_validation()
        demo_anomaly_detection()
        demo_gap_detection()
        demo_quality_report()
        demo_validation_workflow()
        
        print("\n" + "="*80)
        print("所有演示完成！")
        print("="*80)
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {str(e)}", exc_info=True)
        print(f"\n错误: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
