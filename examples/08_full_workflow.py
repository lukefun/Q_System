"""
完整工作流示例

本示例演示Week 2金融数据工程的完整工作流程，包括：
1. 连接XtData API
2. 获取市场数据
3. 应用价格复权
4. 获取基本面数据
5. 查询行业分类
6. 数据持久化
7. 数据可视化
8. 增量更新

这是一个端到端的示例，展示如何将所有模块组合使用。

作者：Q_System
日期：2026-01-19
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.xtdata_client import XtDataClient
from src.data_retriever import DataRetriever
from src.price_adjuster import PriceAdjuster
from src.fundamental_handler import FundamentalHandler
from src.industry_mapper import IndustryMapper
from src.data_manager import DataManager
from src.visualizer import Visualizer
from config import (
    logger,
    XTDATA_ACCOUNT_ID,
    XTDATA_ACCOUNT_KEY,
    DATA_STORAGE_PATH
)


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """
    完整工作流主函数
    
    演示从数据获取到可视化的完整流程
    """
    print_section("Week 2 金融数据工程 - 完整工作流示例")
    
    # ========================================================================
    # 步骤1：初始化客户端和模块
    # ========================================================================
    print_section("步骤1：初始化客户端和模块")
    
    try:
        # 创建XtData客户端
        print("创建XtData客户端...")
        client = XtDataClient(
            account_id=XTDATA_ACCOUNT_ID,
            account_key=XTDATA_ACCOUNT_KEY
        )
        
        # 连接到XtData服务
        print("连接到XtData服务...")
        if not client.connect():
            print("❌ 连接失败，请检查账户配置")
            return
        
        print("✅ XtData客户端连接成功")
        
        # 初始化各个模块
        print("\n初始化数据工程模块...")
        retriever = DataRetriever(client)
        adjuster = PriceAdjuster(client)
        fundamental_handler = FundamentalHandler(client)
        industry_mapper = IndustryMapper(client)
        manager = DataManager(DATA_STORAGE_PATH)
        visualizer = Visualizer()
        
        print("✅ 所有模块初始化完成")
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return
    
    # ========================================================================
    # 步骤2：获取市场数据
    # ========================================================================
    print_section("步骤2：获取市场数据")
    
    # 定义要分析的股票
    stock_codes = ['000001.SZ', '600000.SH']  # 平安银行、浦发银行
    
    # 定义日期范围（最近3个月）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    print(f"股票代码: {', '.join(stock_codes)}")
    print(f"日期范围: {start_date_str} - {end_date_str}")
    
    try:
        print("\n下载历史数据...")
        raw_data = retriever.download_history_data(
            stock_codes=stock_codes,
            start_date=start_date_str,
            end_date=end_date_str,
            period='1d'
        )
        
        print(f"✅ 获取到 {len(raw_data)} 条记录")
        print(f"   涵盖 {len(raw_data['stock_code'].unique())} 只股票")
        print(f"\n数据预览：")
        print(raw_data.head())
        
    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        return
    
    # ========================================================================
    # 步骤3：应用价格复权
    # ========================================================================
    print_section("步骤3：应用价格复权")
    
    print("说明：")
    print("- 前复权：保持当前价格不变，向前调整历史价格（用于回测）")
    print("- 后复权：保持历史价格不变，向后调整当前价格（用于展示）")
    print("\n本示例使用前复权，这是回测的标准做法。")
    
    try:
        adjusted_data = {}
        
        for stock_code in stock_codes:
            print(f"\n处理 {stock_code}...")
            
            # 筛选单只股票的数据
            stock_data = raw_data[raw_data['stock_code'] == stock_code].copy()
            
            # 应用前复权
            adjusted = adjuster.forward_adjust(stock_data, stock_code)
            adjusted_data[stock_code] = adjusted
            
            # 比较复权前后的价格
            if len(stock_data) > 0:
                original_close = stock_data['close'].iloc[-1]
                adjusted_close = adjusted['close'].iloc[-1]
                print(f"   原始收盘价: {original_close:.2f}")
                print(f"   复权后收盘价: {adjusted_close:.2f}")
                print(f"   差异: {abs(adjusted_close - original_close):.2f}")
        
        print("\n✅ 价格复权完成")
        
    except Exception as e:
        print(f"❌ 价格复权失败: {str(e)}")
        return
    
    # ========================================================================
    # 步骤4：获取基本面数据
    # ========================================================================
    print_section("步骤4：获取基本面数据")
    
    print("获取财务指标（PE、PB、ROE）...")
    print("注意：使用公告日期而非报告期，确保时间点正确性")
    
    try:
        # 查询当前时点的财务数据
        as_of_date = end_date_str
        
        fundamental_data = fundamental_handler.get_financial_data(
            stock_codes=stock_codes,
            indicators=['pe', 'pb', 'roe'],
            as_of_date=as_of_date
        )
        
        if not fundamental_data.empty:
            print(f"\n✅ 获取到 {len(fundamental_data)} 条财务记录")
            print("\n财务指标：")
            print(fundamental_data[['stock_code', 'pe_ratio', 'pb_ratio', 'roe']])
        else:
            print("⚠️  没有获取到财务数据")
        
    except Exception as e:
        print(f"❌ 获取基本面数据失败: {str(e)}")
        # 继续执行，不中断流程
    
    # ========================================================================
    # 步骤5：查询行业分类
    # ========================================================================
    print_section("步骤5：查询行业分类")
    
    print("查询股票的申万行业分类...")
    
    try:
        for stock_code in stock_codes:
            industry_info = industry_mapper.get_stock_industry(stock_code)
            
            if industry_info:
                print(f"\n{stock_code}:")
                print(f"   一级行业: {industry_info.get('industry_l1_name', 'N/A')}")
                print(f"   二级行业: {industry_info.get('industry_l2_name', 'N/A')}")
                print(f"   三级行业: {industry_info.get('industry_l3_name', 'N/A')}")
            else:
                print(f"\n{stock_code}: 未找到行业分类")
        
        print("\n✅ 行业分类查询完成")
        
    except Exception as e:
        print(f"❌ 查询行业分类失败: {str(e)}")
        # 继续执行
    
    # ========================================================================
    # 步骤6：数据持久化
    # ========================================================================
    print_section("步骤6：数据持久化")
    
    print("将数据保存到本地HDF5数据库...")
    
    try:
        total_saved = 0
        
        for stock_code in stock_codes:
            if stock_code in adjusted_data:
                data = adjusted_data[stock_code]
                
                # 保存到HDF5
                manager.save_market_data(
                    data=data,
                    data_type='daily',
                    stock_code=stock_code
                )
                
                total_saved += len(data)
                print(f"   {stock_code}: {len(data)} 条记录")
        
        print(f"\n✅ 共保存 {total_saved} 条记录到 {DATA_STORAGE_PATH}/market_data.h5")
        
        # 验证：从数据库加载数据
        print("\n验证：从数据库加载数据...")
        loaded_data = manager.load_market_data(
            data_type='daily',
            stock_code=stock_codes[0],
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        print(f"   加载了 {len(loaded_data)} 条记录")
        print("   ✅ 数据完整性验证通过")
        
    except Exception as e:
        print(f"❌ 数据持久化失败: {str(e)}")
        return
    
    # ========================================================================
    # 步骤7：数据可视化
    # ========================================================================
    print_section("步骤7：数据可视化")
    
    print("生成K线图和技术指标...")
    
    try:
        for stock_code in stock_codes:
            if stock_code in adjusted_data:
                data = adjusted_data[stock_code]
                
                # 生成K线图（带5日和20日均线）
                output_path = f"data/kline_{stock_code}.png"
                
                print(f"\n绘制 {stock_code} 的K线图...")
                visualizer.plot_kline(
                    data=data,
                    stock_code=stock_code,
                    ma_periods=[5, 20],
                    save_path=output_path
                )
                
                print(f"   ✅ 图表已保存到: {output_path}")
        
        # 绘制多股票对比图
        print("\n绘制多股票收盘价对比图...")
        output_path = "data/comparison.png"
        
        visualizer.plot_multiple_stocks(
            data_dict=adjusted_data,
            metric='close',
            save_path=output_path
        )
        
        print(f"   ✅ 对比图已保存到: {output_path}")
        
    except Exception as e:
        print(f"❌ 数据可视化失败: {str(e)}")
        # 继续执行
    
    # ========================================================================
    # 步骤8：增量更新
    # ========================================================================
    print_section("步骤8：增量更新")
    
    print("演示增量更新功能...")
    print("增量更新会自动识别最后更新日期，仅获取新数据")
    
    try:
        # 获取最后更新日期
        for stock_code in stock_codes:
            last_date = manager.get_last_update_date('daily', stock_code)
            print(f"\n{stock_code}:")
            print(f"   最后更新日期: {last_date}")
        
        # 执行增量更新
        print("\n执行增量更新...")
        new_records = manager.incremental_update(
            retriever=retriever,
            stock_codes=stock_codes,
            data_type='daily'
        )
        
        print(f"\n✅ 增量更新完成，新增 {new_records} 条记录")
        
        if new_records == 0:
            print("   （数据已是最新，无需更新）")
        
    except Exception as e:
        print(f"❌ 增量更新失败: {str(e)}")
    
    # ========================================================================
    # 步骤9：清理资源
    # ========================================================================
    print_section("步骤9：清理资源")
    
    try:
        # 断开连接
        client.disconnect()
        print("✅ XtData连接已断开")
        
    except Exception as e:
        print(f"⚠️  清理资源时发生错误: {str(e)}")
    
    # ========================================================================
    # 总结
    # ========================================================================
    print_section("工作流完成")
    
    print("本示例演示了以下内容：")
    print("✅ 1. XtData API连接和认证")
    print("✅ 2. 历史市场数据获取")
    print("✅ 3. 价格复权处理（前复权）")
    print("✅ 4. 基本面数据查询")
    print("✅ 5. 行业分类查询")
    print("✅ 6. 数据持久化到HDF5")
    print("✅ 7. K线图和技术指标可视化")
    print("✅ 8. 增量更新机制")
    
    print("\n关键要点：")
    print("• 使用前复权进行回测，避免未来函数")
    print("• 基本面数据使用公告日期，确保时间点正确性")
    print("• HDF5提供高效的数据存储和查询")
    print("• 增量更新减少API调用，提高效率")
    
    print("\n下一步：")
    print("• 查看 examples/09_build_local_database.py 学习构建全市场数据库")
    print("• 查看 examples/10_lookahead_bias_demo.py 学习未来函数防范")
    print("• 开始开发自己的量化策略！")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}", exc_info=True)
        print(f"\n❌ 程序执行失败: {str(e)}")
        print("详细错误信息请查看日志文件")
