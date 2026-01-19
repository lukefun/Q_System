"""
可视化器模块

提供金融数据可视化功能，支持K线图、成交量图和多股票对比图
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from pathlib import Path
from config import logger, ValidationError


class Visualizer:
    """
    金融数据可视化器
    
    生成金融图表和技术分析可视化，支持K线图、成交量图和多股票对比。
    使用中国市场颜色惯例（红涨绿跌），支持移动平均线叠加和图表保存。
    
    颜色惯例：
        - 红色：上涨（收盘价 > 开盘价）
        - 绿色：下跌（收盘价 < 开盘价）
        - 白色：平盘（收盘价 = 开盘价）
    
    Attributes:
        style: matplotlib样式
        up_color: 上涨颜色（红色）
        down_color: 下跌颜色（绿色）
        flat_color: 平盘颜色（白色）
    
    Example:
        >>> viz = Visualizer()
        >>> # 绘制K线图
        >>> viz.plot_kline(data, '000001.SZ', ma_periods=[5, 10, 20])
        >>> # 绘制多股票对比
        >>> viz.plot_multiple_stocks({'000001.SZ': data1, '600000.SH': data2})
    """
    
    def __init__(self, style: str = 'default'):
        """
        初始化可视化器
        
        Args:
            style: matplotlib样式，可选 'default', 'seaborn', 'ggplot' 等
        
        Example:
            >>> viz = Visualizer(style='seaborn')
        """
        # 设置matplotlib样式
        try:
            plt.style.use(style)
        except:
            logger.warning(f"样式 {style} 不可用，使用默认样式")
            plt.style.use('default')
        
        # 中国市场颜色惯例：红涨绿跌
        self.up_color = '#FF3333'      # 红色（上涨）
        self.down_color = '#00CC00'    # 绿色（下跌）
        self.flat_color = '#FFFFFF'    # 白色（平盘）
        
        # 设置中文字体支持
        self._setup_chinese_font()
        
        logger.info("Visualizer初始化完成")
    
    def _setup_chinese_font(self):
        """设置中文字体支持"""
        try:
            # 尝试设置常见的中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        except:
            logger.warning("中文字体设置失败，可能无法正确显示中文")
    
    def plot_kline(
        self,
        data: pd.DataFrame,
        stock_code: str,
        ma_periods: Optional[List[int]] = None,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 8),
        show_volume: bool = True
    ) -> None:
        """
        绘制K线图
        
        绘制蜡烛图（K线图）展示OHLC数据，可选叠加移动平均线和成交量。
        使用中国市场颜色惯例（红涨绿跌）。
        
        Args:
            data: 包含OHLCV的DataFrame，必须包含列：
                  'date', 'open', 'high', 'low', 'close', 'volume'
            stock_code: 股票代码（用于标题）
            ma_periods: 移动平均线周期列表，如 [5, 10, 20, 60]
            save_path: 保存路径，None表示显示不保存
            figsize: 图表大小，默认 (14, 8)
            show_volume: 是否显示成交量子图，默认 True
        
        Raises:
            ValidationError: 数据验证失败
        
        Example:
            >>> viz.plot_kline(
            ...     data,
            ...     '000001.SZ',
            ...     ma_periods=[5, 10, 20],
            ...     save_path='charts/000001_kline.png'
            ... )
        """
        # 数据验证
        self._validate_kline_data(data)
        
        logger.info(
            f"绘制K线图: 股票={stock_code}, "
            f"数据量={len(data)}, MA={ma_periods}"
        )
        
        # 准备数据
        df = data.copy()
        df = self._prepare_date_column(df)
        df = df.sort_values('date_dt').reset_index(drop=True)
        
        # 创建图表
        if show_volume:
            fig, (ax1, ax2) = plt.subplots(
                2, 1,
                figsize=figsize,
                gridspec_kw={'height_ratios': [3, 1]},
                sharex=True
            )
        else:
            fig, ax1 = plt.subplots(figsize=figsize)
            ax2 = None
        
        # 绘制K线
        self._plot_candlesticks(ax1, df)
        
        # 绘制移动平均线
        if ma_periods:
            self._plot_moving_averages(ax1, df, ma_periods)
        
        # 设置价格轴
        self._setup_price_axis(ax1, stock_code, ma_periods)
        
        # 绘制成交量
        if show_volume and ax2 is not None:
            self.plot_volume(df, ax=ax2)
        
        # 设置日期轴
        self._setup_date_axis(ax2 if show_volume else ax1, df)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            self._save_figure(fig, save_path)
        else:
            plt.show()
        
        plt.close(fig)
        
        logger.info(f"K线图绘制完成")
    
    def plot_volume(
        self,
        data: pd.DataFrame,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        绘制成交量柱状图
        
        绘制成交量柱状图，使用与K线相同的颜色惯例（红涨绿跌）。
        
        Args:
            data: 包含volume列的DataFrame，必须包含：
                  'date', 'volume', 'open', 'close'
            ax: matplotlib轴对象，None表示创建新图
        
        Returns:
            matplotlib轴对象
        
        Raises:
            ValidationError: 数据验证失败
        
        Example:
            >>> fig, ax = plt.subplots()
            >>> viz.plot_volume(data, ax=ax)
            >>> plt.show()
        """
        # 数据验证
        required_columns = ['volume', 'open', 'close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValidationError(
                f"数据缺少必需列: {missing_columns}"
            )
        
        # 准备数据
        df = data.copy()
        df = self._prepare_date_column(df)
        df = df.sort_values('date_dt').reset_index(drop=True)
        
        # 创建轴（如果需要）
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 3))
        
        # 确定颜色
        colors = []
        for _, row in df.iterrows():
            if row['close'] > row['open']:
                colors.append(self.up_color)      # 上涨：红色
            elif row['close'] < row['open']:
                colors.append(self.down_color)    # 下跌：绿色
            else:
                colors.append(self.flat_color)    # 平盘：白色
        
        # 绘制柱状图
        ax.bar(
            df.index,
            df['volume'],
            color=colors,
            alpha=0.6,
            width=0.8,
            edgecolor='black',
            linewidth=0.5
        )
        
        # 设置标签
        ax.set_ylabel('成交量', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 格式化Y轴（使用万、亿等单位）
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: self._format_volume(x))
        )
        
        logger.debug("成交量图绘制完成")
        
        return ax
    
    def plot_multiple_stocks(
        self,
        data_dict: Dict[str, pd.DataFrame],
        metric: str = 'close',
        normalize: bool = True,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 8),
        title: Optional[str] = None
    ) -> None:
        """
        绘制多只股票对比图
        
        在同一图表中绘制多只股票的指定指标，便于对比分析。
        支持归一化处理，将所有股票的起始值设为100。
        
        Args:
            data_dict: 股票代码到数据的映射，如 {'000001.SZ': df1, '600000.SH': df2}
            metric: 要绘制的指标，如 'close', 'volume', 'open' 等
            normalize: 是否归一化（起始值=100），默认 True
            save_path: 保存路径，None表示显示不保存
            figsize: 图表大小，默认 (14, 8)
            title: 图表标题，None则自动生成
        
        Raises:
            ValidationError: 数据验证失败
        
        Example:
            >>> data_dict = {
            ...     '000001.SZ': data1,
            ...     '600000.SH': data2,
            ...     '000002.SZ': data3
            ... }
            >>> viz.plot_multiple_stocks(
            ...     data_dict,
            ...     metric='close',
            ...     normalize=True,
            ...     save_path='charts/comparison.png'
            ... )
        """
        # 数据验证
        if not data_dict:
            raise ValidationError("data_dict不能为空")
        
        for stock_code, df in data_dict.items():
            if metric not in df.columns:
                raise ValidationError(
                    f"股票 {stock_code} 的数据缺少列: {metric}"
                )
        
        logger.info(
            f"绘制多股票对比图: 股票数={len(data_dict)}, "
            f"指标={metric}, 归一化={normalize}"
        )
        
        # 创建图表
        fig, ax = plt.subplots(figsize=figsize)
        
        # 颜色列表
        colors = plt.cm.tab10(range(len(data_dict)))
        
        # 绘制每只股票
        for i, (stock_code, df) in enumerate(data_dict.items()):
            # 准备数据
            plot_df = df.copy()
            plot_df = self._prepare_date_column(plot_df)
            plot_df = plot_df.sort_values('date_dt').reset_index(drop=True)
            
            # 提取指标数据
            values = plot_df[metric].values
            
            # 归一化处理
            if normalize and len(values) > 0 and values[0] != 0:
                values = (values / values[0]) * 100
            
            # 绘制线条
            ax.plot(
                plot_df['date_dt'],
                values,
                label=stock_code,
                color=colors[i],
                linewidth=2,
                alpha=0.8
            )
        
        # 设置标题
        if title is None:
            metric_name = self._get_metric_name(metric)
            if normalize:
                title = f"多股票{metric_name}对比（归一化，起始值=100）"
            else:
                title = f"多股票{metric_name}对比"
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # 设置标签
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        
        if normalize:
            ax.set_ylabel('归一化值（起始=100）', fontsize=12, fontweight='bold')
        else:
            metric_name = self._get_metric_name(metric)
            ax.set_ylabel(metric_name, fontsize=12, fontweight='bold')
        
        # 设置图例
        ax.legend(
            loc='best',
            fontsize=10,
            framealpha=0.9,
            edgecolor='black'
        )
        
        # 设置网格
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 格式化日期轴
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            self._save_figure(fig, save_path)
        else:
            plt.show()
        
        plt.close(fig)
        
        logger.info("多股票对比图绘制完成")
    
    # ========================================================================
    # 内部辅助方法
    # ========================================================================
    
    def _validate_kline_data(self, data: pd.DataFrame) -> None:
        """
        验证K线数据
        
        Args:
            data: 要验证的数据
        
        Raises:
            ValidationError: 数据验证失败
        """
        if not isinstance(data, pd.DataFrame):
            raise ValidationError(f"数据必须是DataFrame类型，当前类型: {type(data)}")
        
        if data.empty:
            raise ValidationError("数据不能为空")
        
        required_columns = ['date', 'open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValidationError(
                f"数据缺少必需列: {missing_columns}。"
                f"必需列: {required_columns}"
            )
    
    def _prepare_date_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        准备日期列
        
        将日期字符串转换为datetime对象，用于绘图。
        
        Args:
            df: 数据DataFrame
        
        Returns:
            添加了date_dt列的DataFrame
        """
        if 'date_dt' not in df.columns:
            if df['date'].dtype == 'object':
                # 字符串格式日期
                df['date_dt'] = pd.to_datetime(df['date'], format='%Y%m%d')
            else:
                # 已经是datetime类型
                df['date_dt'] = pd.to_datetime(df['date'])
        
        return df
    
    def _plot_candlesticks(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """
        绘制蜡烛图
        
        Args:
            ax: matplotlib轴对象
            df: 数据DataFrame
        """
        for idx, row in df.iterrows():
            # 确定颜色
            if row['close'] > row['open']:
                color = self.up_color      # 上涨：红色
                edge_color = self.up_color
            elif row['close'] < row['open']:
                color = self.down_color    # 下跌：绿色
                edge_color = self.down_color
            else:
                color = self.flat_color    # 平盘：白色
                edge_color = 'black'
            
            # 绘制影线（high-low）
            ax.plot(
                [idx, idx],
                [row['low'], row['high']],
                color=edge_color,
                linewidth=1,
                solid_capstyle='round'
            )
            
            # 绘制实体（open-close）
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['open'], row['close'])
            
            rect = Rectangle(
                (idx - 0.4, body_bottom),
                0.8,
                body_height if body_height > 0 else 0.01,  # 避免高度为0
                facecolor=color,
                edgecolor=edge_color,
                linewidth=1.5,
                alpha=0.9
            )
            ax.add_patch(rect)
    
    def _plot_moving_averages(
        self,
        ax: plt.Axes,
        df: pd.DataFrame,
        ma_periods: List[int]
    ) -> None:
        """
        绘制移动平均线
        
        Args:
            ax: matplotlib轴对象
            df: 数据DataFrame
            ma_periods: 移动平均线周期列表
        """
        # MA线条颜色
        ma_colors = {
            5: '#FF6B6B',    # 浅红
            10: '#4ECDC4',   # 青色
            20: '#45B7D1',   # 蓝色
            30: '#FFA07A',   # 橙色
            60: '#9B59B6',   # 紫色
            120: '#F39C12',  # 黄色
            250: '#E74C3C'   # 深红
        }
        
        for period in ma_periods:
            # 计算移动平均
            ma_values = df['close'].rolling(window=period).mean()
            
            # 选择颜色
            color = ma_colors.get(period, '#95A5A6')  # 默认灰色
            
            # 绘制MA线
            ax.plot(
                df.index,
                ma_values,
                label=f'MA{period}',
                color=color,
                linewidth=1.5,
                alpha=0.8,
                linestyle='-'
            )
    
    def _setup_price_axis(
        self,
        ax: plt.Axes,
        stock_code: str,
        ma_periods: Optional[List[int]]
    ) -> None:
        """
        设置价格轴
        
        Args:
            ax: matplotlib轴对象
            stock_code: 股票代码
            ma_periods: 移动平均线周期
        """
        # 设置标题
        title = f"{stock_code} K线图"
        if ma_periods:
            ma_str = ', '.join([f'MA{p}' for p in ma_periods])
            title += f" ({ma_str})"
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # 设置Y轴标签
        ax.set_ylabel('价格', fontsize=12, fontweight='bold')
        
        # 设置图例
        if ma_periods:
            ax.legend(
                loc='upper left',
                fontsize=9,
                framealpha=0.9,
                edgecolor='black'
            )
        
        # 设置网格
        ax.grid(True, alpha=0.3, linestyle='--')
    
    def _setup_date_axis(self, ax: plt.Axes, df: pd.DataFrame) -> None:
        """
        设置日期轴
        
        Args:
            ax: matplotlib轴对象
            df: 数据DataFrame
        """
        # 设置X轴标签
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        
        # 设置X轴刻度
        # 根据数据量调整刻度密度
        num_points = len(df)
        
        if num_points <= 30:
            # 少于30个点，显示所有日期
            tick_indices = range(0, num_points)
        elif num_points <= 90:
            # 30-90个点，每隔几天显示
            step = max(1, num_points // 15)
            tick_indices = range(0, num_points, step)
        else:
            # 超过90个点，显示更少的刻度
            step = max(1, num_points // 10)
            tick_indices = range(0, num_points, step)
        
        # 设置刻度位置和标签
        ax.set_xticks(tick_indices)
        
        if 'date_dt' in df.columns:
            tick_labels = [
                df.iloc[i]['date_dt'].strftime('%Y-%m-%d')
                for i in tick_indices
            ]
        else:
            tick_labels = [
                df.iloc[i]['date']
                for i in tick_indices
            ]
        
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    def _format_volume(self, value: float) -> str:
        """
        格式化成交量
        
        将成交量转换为易读的格式（万、亿等）。
        
        Args:
            value: 成交量值
        
        Returns:
            格式化后的字符串
        """
        if value >= 1e8:
            return f'{value/1e8:.2f}亿'
        elif value >= 1e4:
            return f'{value/1e4:.2f}万'
        else:
            return f'{value:.0f}'
    
    def _get_metric_name(self, metric: str) -> str:
        """
        获取指标中文名称
        
        Args:
            metric: 指标英文名
        
        Returns:
            指标中文名
        """
        metric_names = {
            'open': '开盘价',
            'high': '最高价',
            'low': '最低价',
            'close': '收盘价',
            'volume': '成交量',
            'amount': '成交额'
        }
        
        return metric_names.get(metric, metric)
    
    def _save_figure(self, fig: plt.Figure, save_path: str) -> None:
        """
        保存图表
        
        Args:
            fig: matplotlib图表对象
            save_path: 保存路径
        """
        # 确保输出目录存在
        output_file = Path(save_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 确定文件格式
        file_ext = output_file.suffix.lower()
        
        if file_ext in ['.png', '.jpg', '.jpeg', '.pdf', '.svg']:
            # 保存图表
            fig.savefig(
                save_path,
                dpi=300,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            logger.info(f"图表已保存: {save_path}")
        else:
            logger.warning(
                f"不支持的文件格式: {file_ext}。"
                f"支持的格式: .png, .jpg, .jpeg, .pdf, .svg"
            )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"Visualizer("
            f"up_color={self.up_color}, "
            f"down_color={self.down_color})"
        )
