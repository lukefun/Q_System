"""
Week 2 - XtData金融数据工程系统

本模块提供完整的金融数据工程解决方案，包括：
- XtData API集成
- 价格复权处理
- 基本面数据ETL
- 行业分类管理
- 数据持久化和增量更新
- 金融数据可视化
"""

from .xtdata_client import XtDataClient

__version__ = "0.1.0"
__author__ = "Q_System"

__all__ = [
    "XtDataClient",
]
