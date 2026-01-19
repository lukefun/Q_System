"""
示例06：K线图和技术指标可视化

本示例演示如何使用Visualizer进行金融数据可视化：
1. 绘制K线图（蜡烛图）
2. 添加移动平均线
3. 绘制成交量柱状图
4. 多股票对比图
5. 保存图表到文件

学习目标：
- 理解K线图的构成和意义
- 掌握技术指标的可视化方法
- 学习如何进行多股票对比分析
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from src.visualizer import Visualizer
from src.data_manager import DataManager
import config

def generate_sample_data(stock_code, start_date, num_days=60, base_price=10.0):
    """
    生成示例K线数据
    
    Args:
        stock_code: 股票代码
        start_date: 开始日期
        num_days: 天数
        base_price: 基础价格
    
    Returns:
        DataFrame: 包含OHLCV数据
    """
    dates = pd.date_range(start=start_date, periods=num_days, freq='D')
    
    # 生成随机价格走势
    np.random.seed(hash(stock_code) % 2**32)  # 使用股票代码作为随机种子
    
    # 生成收盘价（随机游走）
    returns = np.random.normal(0.001, 0.02, num_days)
    close_prices = base_price * np.exp(np.cumsum(returns))
    
    # 生成OHLC数据
    data = []
    for i, date in enumerate(dates):
        close = close_prices[i]
        # 开盘价在前一日收盘价附近
        open_price = close_prices[i-1] * (1 + np.random.normal(0, 0.01)) if i > 0 else close
        # 最高价和最低价
        high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.01)))
        low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.01)))
        # 成交量
        volume = np.random.randint(800000, 1500000)
        
        data.append({
            'stock_code': stock_code,
            'date': date.strftime('%Y%m%d'),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'amount': volume * close
        })
    
    return pd.DataFrame(data)

def main():
    print("=" * 60)
    print("示例06：K线图和技术指标可视化")
    print("=" * 60)
    print()
    
    # 1. 初始化可视化器
    print("1. 初始化可视化器")
    print("-" * 60)
    
    visualizer = Visualizer(style='default')
    print("✓ 可视化器初始化完成")
    print()
    
    # 2. 准备示例数据
    print("2. 准备示例数据")
    print("-" * 60)
    
    # 生成平安银行(000001.SZ)的示例数据
    data_pingan = generate_sample_data('000001.SZ', '2024-01-01', num_days=60, base_price=10.0)
    print(f"✓ 生成平安银行数据: {len(data_pingan)} 条记录")
    print(f"  日期范围: {data_pingan['date'].iloc[0]} - {data_pingan['date'].iloc[-1]}")
    print(f"  价格范围: {data_pingan['close'].min():.2f} - {data_pingan['close'].max():.2f}")
    print()
    
    # 3. 绘制基础K线图
    print("3. 绘制基础K线图")
    print("-" * 60)
    
    output_dir = os.path.join(config.DATA_STORAGE_PATH, 'charts')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        save_path = os.path.join(output_dir, 'kline_basic.png')
        visualizer.plot_kline(
            data=data_pingan,
            stock_code='000001.SZ 平安银行',
            save_path=save_path
        )
        print(f"✓ K线图生成成功")
        print(f"  保存路径: {save_path}")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    print()
    
    # 4. 绘制带移动平均线的K线图
    print("4. 绘制带移动平均线的K线图")
    print("-" * 60)
    
    try:
        save_path = os.path.join(output_dir, 'kline_with_ma.png')
        visualizer.plot_kline(
            data=data_pingan,
            stock_code='000001.SZ 平安银行',
            ma_periods=[5, 10, 20],  # 5日、10日、20日均线
            save_path=save_path
        )
        print(f"✓ 带均线的K线图生成成功")
        print(f"  移动平均线: MA5, MA10, MA20")
        print(f"  保存路径: {save_path}")
        print()
        print("  技术分析提示：")
        print("  - MA5: 短期趋势，反应灵敏")
        print("  - MA10: 中短期趋势")
        print("  - MA20: 中期趋势，常用支撑/阻力位")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    print()
    
    # 5. 绘制成交量图
    print("5. 绘制成交量图")
    print("-" * 60)
    
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制K线图（简化版）
        ax1.plot(range(len(data_pingan)), data_pingan['close'], label='收盘价')
        ax1.set_title('000001.SZ 平安银行 - 价格与成交量', fontsize=14)
        ax1.set_ylabel('价格 (元)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 绘制成交量
        visualizer.plot_volume(data=data_pingan, ax=ax2)
        
        save_path = os.path.join(output_dir, 'price_volume.png')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 价格-成交量图生成成功")
        print(f"  保存路径: {save_path}")
        print()
        print("  成交量分析提示：")
        print("  - 价涨量增：上涨趋势健康")
        print("  - 价涨量缩：上涨动能不足")
        print("  - 价跌量增：下跌压力大")
        print("  - 价跌量缩：下跌动能减弱")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    print()
    
    # 6. 多股票对比图
    print("6. 多股票对比图")
    print("-" * 60)
    
    # 生成多只股票的数据
    data_pufa = generate_sample_data('600000.SH', '2024-01-01', num_days=60, base_price=8.0)
    data_cmb = generate_sample_data('600036.SH', '2024-01-01', num_days=60, base_price=35.0)
    
    print(f"✓ 生成浦发银行数据: {len(data_pufa)} 条记录")
    print(f"✓ 生成招商银行数据: {len(data_cmb)} 条记录")
    
    try:
        data_dict = {
            '000001.SZ 平安银行': data_pingan,
            '600000.SH 浦发银行': data_pufa,
            '600036.SH 招商银行': data_cmb
        }
        
        save_path = os.path.join(output_dir, 'multi_stock_comparison.png')
        visualizer.plot_multiple_stocks(
            data_dict=data_dict,
            metric='close',
            save_path=save_path
        )
        print(f"✓ 多股票对比图生成成功")
        print(f"  对比股票: 平安银行、浦发银行、招商银行")
        print(f"  保存路径: {save_path}")
        print()
        print("  对比分析提示：")
        print("  - 观察相对强弱")
        print("  - 识别板块联动")
        print("  - 发现超跌/超涨机会")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    print()
    
    # 7. 归一化对比图
    print("7. 归一化对比图（相对涨跌幅）")
    print("-" * 60)
    
    try:
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 计算归一化价格（以第一天为基准）
        for name, data in data_dict.items():
            normalized = (data['close'] / data['close'].iloc[0] - 1) * 100
            ax.plot(range(len(normalized)), normalized, label=name, linewidth=2)
        
        ax.set_title('银行股相对涨跌幅对比', fontsize=14)
        ax.set_xlabel('交易日', fontsize=12)
        ax.set_ylabel('相对涨跌幅 (%)', fontsize=12)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        save_path = os.path.join(output_dir, 'normalized_comparison.png')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 归一化对比图生成成功")
        print(f"  保存路径: {save_path}")
        print()
        print("  归一化分析优势：")
        print("  - 消除价格绝对值差异")
        print("  - 直观比较涨跌幅")
        print("  - 适合不同价格区间的股票对比")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
    print()
    
    # 8. 可视化最佳实践
    print("8. 可视化最佳实践")
    print("-" * 60)
    print("""
    K线图解读：
    1. 红色（阳线）：收盘价 > 开盘价，表示上涨
    2. 绿色（阴线）：收盘价 < 开盘价，表示下跌
    3. 上影线：最高价与实体上端的距离，表示上方压力
    4. 下影线：最低价与实体下端的距离，表示下方支撑
    
    技术指标使用：
    1. 移动平均线：判断趋势方向
       - 金叉：短期均线上穿长期均线，看涨信号
       - 死叉：短期均线下穿长期均线，看跌信号
    
    2. 成交量：确认价格走势
       - 量价齐升：上涨趋势确认
       - 量价背离：趋势可能反转
    
    注意事项：
    - 技术分析仅供参考，不构成投资建议
    - 结合基本面分析做出决策
    - 注意风险控制和仓位管理
    """)
    
    print("=" * 60)
    print("示例完成！")
    print(f"所有图表已保存到: {output_dir}")
    print("=" * 60)

if __name__ == '__main__':
    main()
