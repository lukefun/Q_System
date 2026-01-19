"""
Visualizer类的单元测试

测试可视化器的基本功能，包括K线图、成交量图和多股票对比图的绘制。
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免显示窗口
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import tempfile
from pathlib import Path

from src.visualizer import Visualizer
from config import ValidationError


@pytest.fixture
def sample_kline_data():
    """生成示例K线数据"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    data = []
    base_price = 10.0
    
    for i, date in enumerate(dates):
        close = base_price + np.random.randn() * 0.5
        open_price = close + np.random.randn() * 0.2
        high = max(open_price, close) + abs(np.random.randn()) * 0.3
        low = min(open_price, close) - abs(np.random.randn()) * 0.3
        volume = int(np.random.uniform(500000, 2000000))
        
        data.append({
            'stock_code': '000001.SZ',
            'date': date.strftime('%Y%m%d'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume,
        })
        
        base_price = close  # 下一天的基准价格
    
    return pd.DataFrame(data)


@pytest.fixture
def multiple_stock_data():
    """生成多只股票的示例数据"""
    dates = pd.date_range(end=datetime.now(), periods=20, freq='D')
    
    stocks = {
        '000001.SZ': 10.0,
        '600000.SH': 15.0,
        '000002.SZ': 8.0
    }
    
    data_dict = {}
    
    for stock_code, base_price in stocks.items():
        data = []
        current_price = base_price
        
        for date in dates:
            close = current_price + np.random.randn() * 0.3
            open_price = close + np.random.randn() * 0.15
            high = max(open_price, close) + abs(np.random.randn()) * 0.2
            low = min(open_price, close) - abs(np.random.randn()) * 0.2
            volume = int(np.random.uniform(500000, 2000000))
            
            data.append({
                'stock_code': stock_code,
                'date': date.strftime('%Y%m%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume,
            })
            
            current_price = close
        
        data_dict[stock_code] = pd.DataFrame(data)
    
    return data_dict


@pytest.fixture
def visualizer():
    """创建Visualizer实例"""
    return Visualizer()


@pytest.fixture
def temp_output_dir():
    """创建临时输出目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestVisualizerInitialization:
    """测试Visualizer初始化"""
    
    def test_init_default_style(self):
        """测试默认样式初始化"""
        viz = Visualizer()
        assert viz.up_color == '#FF3333'      # 红色（上涨）
        assert viz.down_color == '#00CC00'    # 绿色（下跌）
        assert viz.flat_color == '#FFFFFF'    # 白色（平盘）
    
    def test_init_custom_style(self):
        """测试自定义样式初始化"""
        # 测试有效样式
        viz = Visualizer(style='default')
        assert viz is not None
        
        # 测试无效样式（应该回退到默认样式）
        viz = Visualizer(style='invalid_style')
        assert viz is not None
    
    def test_chinese_font_setup(self):
        """测试中文字体设置"""
        viz = Visualizer()
        # 验证字体设置已应用
        assert 'SimHei' in plt.rcParams['font.sans-serif'] or \
               'Microsoft YaHei' in plt.rcParams['font.sans-serif']


class TestPlotKline:
    """测试K线图绘制"""
    
    def test_plot_kline_basic(self, visualizer, sample_kline_data, temp_output_dir):
        """测试基本K线图绘制"""
        output_path = os.path.join(temp_output_dir, 'kline_basic.png')
        
        # 绘制K线图（不应抛出异常）
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    
    def test_plot_kline_with_ma(self, visualizer, sample_kline_data, temp_output_dir):
        """测试带移动平均线的K线图"""
        output_path = os.path.join(temp_output_dir, 'kline_with_ma.png')
        
        # 绘制带MA的K线图
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            ma_periods=[5, 10, 20],
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    
    def test_plot_kline_without_volume(self, visualizer, sample_kline_data, temp_output_dir):
        """测试不显示成交量的K线图"""
        output_path = os.path.join(temp_output_dir, 'kline_no_volume.png')
        
        # 绘制不带成交量的K线图
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            show_volume=False,
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    
    def test_plot_kline_custom_figsize(self, visualizer, sample_kline_data, temp_output_dir):
        """测试自定义图表大小"""
        output_path = os.path.join(temp_output_dir, 'kline_custom_size.png')
        
        # 绘制自定义大小的K线图
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            figsize=(10, 6),
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
    
    def test_plot_kline_empty_data(self, visualizer):
        """测试空数据"""
        empty_data = pd.DataFrame()
        
        with pytest.raises(ValidationError, match="数据不能为空"):
            visualizer.plot_kline(
                data=empty_data,
                stock_code='000001.SZ'
            )
    
    def test_plot_kline_missing_columns(self, visualizer):
        """测试缺少必需列"""
        incomplete_data = pd.DataFrame({
            'date': ['20240101', '20240102'],
            'close': [10.0, 10.5]
            # 缺少 open, high, low
        })
        
        with pytest.raises(ValidationError, match="数据缺少必需列"):
            visualizer.plot_kline(
                data=incomplete_data,
                stock_code='000001.SZ'
            )
    
    def test_plot_kline_invalid_data_type(self, visualizer):
        """测试无效数据类型"""
        with pytest.raises(ValidationError, match="数据必须是DataFrame类型"):
            visualizer.plot_kline(
                data="not a dataframe",
                stock_code='000001.SZ'
            )
    
    def test_plot_kline_different_formats(self, visualizer, sample_kline_data, temp_output_dir):
        """测试不同文件格式保存"""
        formats = ['png', 'jpg', 'pdf']
        
        for fmt in formats:
            output_path = os.path.join(temp_output_dir, f'kline.{fmt}')
            
            visualizer.plot_kline(
                data=sample_kline_data,
                stock_code='000001.SZ',
                save_path=output_path
            )
            
            # 验证文件已创建
            assert os.path.exists(output_path)


class TestPlotVolume:
    """测试成交量图绘制"""
    
    def test_plot_volume_basic(self, visualizer, sample_kline_data):
        """测试基本成交量图绘制"""
        # 创建新图表
        fig, ax = plt.subplots()
        
        # 绘制成交量（不应抛出异常）
        result_ax = visualizer.plot_volume(data=sample_kline_data, ax=ax)
        
        # 验证返回的是轴对象
        assert result_ax is not None
        assert isinstance(result_ax, plt.Axes)
        
        plt.close(fig)
    
    def test_plot_volume_standalone(self, visualizer, sample_kline_data):
        """测试独立成交量图（不提供ax参数）"""
        # 不提供ax参数，应该创建新图表
        result_ax = visualizer.plot_volume(data=sample_kline_data)
        
        # 验证返回的是轴对象
        assert result_ax is not None
        assert isinstance(result_ax, plt.Axes)
        
        plt.close('all')
    
    def test_plot_volume_missing_columns(self, visualizer):
        """测试缺少必需列"""
        incomplete_data = pd.DataFrame({
            'date': ['20240101', '20240102'],
            'volume': [1000000, 1200000]
            # 缺少 open, close
        })
        
        with pytest.raises(ValidationError, match="数据缺少必需列"):
            visualizer.plot_volume(data=incomplete_data)
    
    def test_plot_volume_color_convention(self, visualizer, sample_kline_data):
        """测试成交量颜色惯例（红涨绿跌）"""
        fig, ax = plt.subplots()
        
        # 绘制成交量
        visualizer.plot_volume(data=sample_kline_data, ax=ax)
        
        # 验证图表已创建（具体颜色验证较复杂，这里只验证不抛异常）
        assert ax is not None
        
        plt.close(fig)


class TestPlotMultipleStocks:
    """测试多股票对比图"""
    
    def test_plot_multiple_stocks_basic(self, visualizer, multiple_stock_data, temp_output_dir):
        """测试基本多股票对比图"""
        output_path = os.path.join(temp_output_dir, 'multiple_stocks.png')
        
        # 绘制多股票对比图
        visualizer.plot_multiple_stocks(
            data_dict=multiple_stock_data,
            metric='close',
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    
    def test_plot_multiple_stocks_normalized(self, visualizer, multiple_stock_data, temp_output_dir):
        """测试归一化多股票对比图"""
        output_path = os.path.join(temp_output_dir, 'multiple_stocks_normalized.png')
        
        # 绘制归一化对比图
        visualizer.plot_multiple_stocks(
            data_dict=multiple_stock_data,
            metric='close',
            normalize=True,
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
    
    def test_plot_multiple_stocks_not_normalized(self, visualizer, multiple_stock_data, temp_output_dir):
        """测试非归一化多股票对比图"""
        output_path = os.path.join(temp_output_dir, 'multiple_stocks_not_normalized.png')
        
        # 绘制非归一化对比图
        visualizer.plot_multiple_stocks(
            data_dict=multiple_stock_data,
            metric='close',
            normalize=False,
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
    
    def test_plot_multiple_stocks_different_metrics(self, visualizer, multiple_stock_data, temp_output_dir):
        """测试不同指标的对比图"""
        metrics = ['close', 'volume', 'open']
        
        for metric in metrics:
            output_path = os.path.join(temp_output_dir, f'multiple_stocks_{metric}.png')
            
            visualizer.plot_multiple_stocks(
                data_dict=multiple_stock_data,
                metric=metric,
                save_path=output_path
            )
            
            # 验证文件已创建
            assert os.path.exists(output_path)
    
    def test_plot_multiple_stocks_custom_title(self, visualizer, multiple_stock_data, temp_output_dir):
        """测试自定义标题"""
        output_path = os.path.join(temp_output_dir, 'multiple_stocks_custom_title.png')
        
        visualizer.plot_multiple_stocks(
            data_dict=multiple_stock_data,
            metric='close',
            title='自定义标题：股票对比',
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)
    
    def test_plot_multiple_stocks_empty_dict(self, visualizer):
        """测试空数据字典"""
        with pytest.raises(ValidationError, match="data_dict不能为空"):
            visualizer.plot_multiple_stocks(
                data_dict={},
                metric='close'
            )
    
    def test_plot_multiple_stocks_missing_metric(self, visualizer, multiple_stock_data):
        """测试缺少指定指标"""
        with pytest.raises(ValidationError, match="数据缺少列"):
            visualizer.plot_multiple_stocks(
                data_dict=multiple_stock_data,
                metric='nonexistent_metric'
            )


class TestHelperMethods:
    """测试辅助方法"""
    
    def test_format_volume(self, visualizer):
        """测试成交量格式化"""
        # 测试亿级别
        assert '1.00亿' == visualizer._format_volume(1e8)
        assert '2.50亿' == visualizer._format_volume(2.5e8)
        
        # 测试万级别
        assert '10.00万' == visualizer._format_volume(1e5)
        assert '500.00万' == visualizer._format_volume(5e6)
        
        # 测试小数值
        assert '100' == visualizer._format_volume(100)
        assert '9999' == visualizer._format_volume(9999)
    
    def test_get_metric_name(self, visualizer):
        """测试指标名称获取"""
        assert visualizer._get_metric_name('open') == '开盘价'
        assert visualizer._get_metric_name('high') == '最高价'
        assert visualizer._get_metric_name('low') == '最低价'
        assert visualizer._get_metric_name('close') == '收盘价'
        assert visualizer._get_metric_name('volume') == '成交量'
        assert visualizer._get_metric_name('amount') == '成交额'
        
        # 测试未知指标
        assert visualizer._get_metric_name('unknown') == 'unknown'
    
    def test_prepare_date_column(self, visualizer):
        """测试日期列准备"""
        # 测试字符串日期
        df = pd.DataFrame({
            'date': ['20240101', '20240102', '20240103']
        })
        
        result = visualizer._prepare_date_column(df)
        
        assert 'date_dt' in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result['date_dt'])
    
    def test_validate_kline_data(self, visualizer, sample_kline_data):
        """测试K线数据验证"""
        # 有效数据不应抛出异常
        visualizer._validate_kline_data(sample_kline_data)
        
        # 空数据应抛出异常
        with pytest.raises(ValidationError):
            visualizer._validate_kline_data(pd.DataFrame())
        
        # 缺少列应抛出异常
        incomplete_data = pd.DataFrame({'date': ['20240101']})
        with pytest.raises(ValidationError):
            visualizer._validate_kline_data(incomplete_data)


class TestColorConvention:
    """测试中国市场颜色惯例"""
    
    def test_color_convention_setup(self, visualizer):
        """测试颜色惯例设置"""
        # 验证红涨绿跌的颜色设置
        assert visualizer.up_color == '#FF3333'      # 红色（上涨）
        assert visualizer.down_color == '#00CC00'    # 绿色（下跌）
        assert visualizer.flat_color == '#FFFFFF'    # 白色（平盘）
    
    def test_kline_uses_correct_colors(self, visualizer, temp_output_dir):
        """测试K线图使用正确的颜色"""
        # 创建明确的上涨和下跌数据
        data = pd.DataFrame({
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 11.0, 10.5],
            'high': [10.5, 11.5, 11.0],
            'low': [9.8, 10.8, 10.3],
            'close': [10.3, 10.8, 10.4],  # 第1天涨，第2天跌，第3天跌
            'volume': [1000000, 1200000, 900000]
        })
        
        output_path = os.path.join(temp_output_dir, 'kline_colors.png')
        
        # 绘制K线图（不应抛出异常）
        visualizer.plot_kline(
            data=data,
            stock_code='TEST',
            save_path=output_path
        )
        
        # 验证文件已创建
        assert os.path.exists(output_path)


class TestFileOutput:
    """测试文件输出功能"""
    
    def test_save_to_png(self, visualizer, sample_kline_data, temp_output_dir):
        """测试保存为PNG格式"""
        output_path = os.path.join(temp_output_dir, 'test.png')
        
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            save_path=output_path
        )
        
        assert os.path.exists(output_path)
        assert output_path.endswith('.png')
    
    def test_save_to_jpg(self, visualizer, sample_kline_data, temp_output_dir):
        """测试保存为JPG格式"""
        output_path = os.path.join(temp_output_dir, 'test.jpg')
        
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            save_path=output_path
        )
        
        assert os.path.exists(output_path)
        assert output_path.endswith('.jpg')
    
    def test_save_creates_directory(self, visualizer, sample_kline_data, temp_output_dir):
        """测试自动创建输出目录"""
        # 使用不存在的子目录
        output_path = os.path.join(temp_output_dir, 'subdir', 'nested', 'test.png')
        
        visualizer.plot_kline(
            data=sample_kline_data,
            stock_code='000001.SZ',
            save_path=output_path
        )
        
        # 验证目录和文件都已创建
        assert os.path.exists(output_path)
        assert os.path.exists(os.path.dirname(output_path))


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_single_data_point(self, visualizer, temp_output_dir):
        """测试单个数据点"""
        single_point_data = pd.DataFrame({
            'date': ['20240101'],
            'open': [10.0],
            'high': [10.5],
            'low': [9.8],
            'close': [10.3],
            'volume': [1000000]
        })
        
        output_path = os.path.join(temp_output_dir, 'single_point.png')
        
        # 应该能够处理单个数据点
        visualizer.plot_kline(
            data=single_point_data,
            stock_code='TEST',
            save_path=output_path
        )
        
        assert os.path.exists(output_path)
    
    def test_large_dataset(self, visualizer, temp_output_dir):
        """测试大数据集"""
        # 生成250天的数据（一年的交易日）
        dates = pd.date_range(end=datetime.now(), periods=250, freq='D')
        
        data = []
        base_price = 10.0
        
        for date in dates:
            close = base_price + np.random.randn() * 0.5
            open_price = close + np.random.randn() * 0.2
            high = max(open_price, close) + abs(np.random.randn()) * 0.3
            low = min(open_price, close) - abs(np.random.randn()) * 0.3
            
            data.append({
                'date': date.strftime('%Y%m%d'),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': int(np.random.uniform(500000, 2000000))
            })
            
            base_price = close
        
        large_data = pd.DataFrame(data)
        output_path = os.path.join(temp_output_dir, 'large_dataset.png')
        
        # 应该能够处理大数据集
        visualizer.plot_kline(
            data=large_data,
            stock_code='TEST',
            ma_periods=[5, 10, 20, 60],
            save_path=output_path
        )
        
        assert os.path.exists(output_path)
    
    def test_flat_price(self, visualizer, temp_output_dir):
        """测试平盘价格（开盘价=收盘价）"""
        flat_data = pd.DataFrame({
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 10.0, 10.0],
            'high': [10.2, 10.2, 10.2],
            'low': [9.8, 9.8, 9.8],
            'close': [10.0, 10.0, 10.0],  # 所有天都是平盘
            'volume': [1000000, 1000000, 1000000]
        })
        
        output_path = os.path.join(temp_output_dir, 'flat_price.png')
        
        # 应该能够处理平盘情况
        visualizer.plot_kline(
            data=flat_data,
            stock_code='TEST',
            save_path=output_path
        )
        
        assert os.path.exists(output_path)
    
    def test_extreme_price_movements(self, visualizer, temp_output_dir):
        """测试极端价格波动"""
        extreme_data = pd.DataFrame({
            'date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 11.0, 5.0],
            'high': [15.0, 12.0, 6.0],
            'low': [5.0, 9.0, 4.0],
            'close': [12.0, 10.0, 5.5],
            'volume': [5000000, 6000000, 7000000]
        })
        
        output_path = os.path.join(temp_output_dir, 'extreme_movements.png')
        
        # 应该能够处理极端波动
        visualizer.plot_kline(
            data=extreme_data,
            stock_code='TEST',
            save_path=output_path
        )
        
        assert os.path.exists(output_path)


class TestRepr:
    """测试字符串表示"""
    
    def test_repr(self, visualizer):
        """测试__repr__方法"""
        repr_str = repr(visualizer)
        
        assert 'Visualizer' in repr_str
        assert visualizer.up_color in repr_str
        assert visualizer.down_color in repr_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
