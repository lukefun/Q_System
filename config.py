"""
配置文件：Week 2 - XtData金融数据工程系统

管理API密钥、存储路径、日志配置和系统参数
"""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


# ============================================================================
# 项目路径配置
# ============================================================================

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

# 数据存储目录
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# HDF5数据库路径
HDF5_PATH = DATA_DIR / "market_data.h5"

# CSV导出目录
CSV_EXPORT_DIR = DATA_DIR / "csv_exports"
CSV_EXPORT_DIR.mkdir(exist_ok=True)

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 缓存目录
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


# ============================================================================
# XtData API配置
# ============================================================================

# XtData账户配置（从环境变量读取，避免硬编码敏感信息）
XTDATA_ACCOUNT_ID = os.getenv("XTDATA_ACCOUNT_ID", "")
XTDATA_ACCOUNT_KEY = os.getenv("XTDATA_ACCOUNT_KEY", "")

# API连接配置
API_TIMEOUT = 30  # 秒
API_RETRY_TIMES = 3  # 重试次数
API_RETRY_DELAY = 1  # 重试延迟（秒）

# API速率限制配置
API_RATE_LIMIT_DELAY = 0.1  # 批量请求间延迟（秒）
API_BATCH_SIZE = 50  # 批量请求大小


# ============================================================================
# 数据配置
# ============================================================================

# 默认数据周期
DEFAULT_PERIOD = "1d"  # 日线数据

# 默认复权类型
DEFAULT_ADJUST_TYPE = "front"  # 前复权（用于回测）

# 数据质量检查阈值
PRICE_MIN_THRESHOLD = 0.01  # 最低价格阈值
PRICE_MAX_THRESHOLD = 10000.0  # 最高价格阈值
VOLUME_MIN_THRESHOLD = 0  # 最低成交量阈值

# 数据缺口容忍度（天）
MAX_DATA_GAP_DAYS = 10


# ============================================================================
# 存储配置
# ============================================================================

# HDF5压缩配置
HDF5_COMPRESSION = "blosc:zstd"  # 压缩算法
HDF5_COMPLEVEL = 5  # 压缩级别 (0-9)

# 数据存储格式
HDF5_DATE_FORMAT = "%Y%m%d"
CSV_DATE_FORMAT = "%Y-%m-%d"


# ============================================================================
# 可视化配置
# ============================================================================

# 图表样式
PLOT_STYLE = "seaborn-v0_8-darkgrid"  # matplotlib样式

# 中国市场颜色惯例（红涨绿跌）
COLOR_UP = "red"  # 上涨颜色
COLOR_DOWN = "green"  # 下跌颜色

# 图表默认尺寸
FIGURE_SIZE = (12, 8)
DPI = 100


# ============================================================================
# 日志配置
# ============================================================================

# 日志级别
LOG_LEVEL = logging.INFO

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件配置
LOG_FILE = LOG_DIR / f"xtdata_system_{datetime.now().strftime('%Y%m%d')}.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5


def setup_logging(
    level: int = LOG_LEVEL,
    log_file: Optional[Path] = LOG_FILE,
    console: bool = True
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径，None表示不写文件
        console: 是否输出到控制台
    
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger("xtdata")
    logger.setLevel(level)
    
    # 清除已有的handlers
    logger.handlers.clear()
    
    # 创建formatter
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # 文件handler
    if log_file:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 控制台handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# 自定义异常类
# ============================================================================

class XtDataError(Exception):
    """XtData系统基础异常"""
    pass


class ConnectionError(XtDataError):
    """API连接相关错误"""
    pass


class DataError(XtDataError):
    """数据相关错误"""
    pass


class ValidationError(XtDataError):
    """数据验证错误"""
    pass


class StorageError(XtDataError):
    """存储相关错误"""
    pass


# ============================================================================
# 初始化
# ============================================================================

# 创建默认logger
logger = setup_logging()

# 配置验证
if not XTDATA_ACCOUNT_ID or not XTDATA_ACCOUNT_KEY:
    logger.warning(
        "XtData API credentials not configured. "
        "Please set XTDATA_ACCOUNT_ID and XTDATA_ACCOUNT_KEY environment variables."
    )


# ============================================================================
# 配置导出
# ============================================================================

__all__ = [
    # 路径
    "PROJECT_ROOT",
    "DATA_DIR",
    "HDF5_PATH",
    "CSV_EXPORT_DIR",
    "LOG_DIR",
    "CACHE_DIR",
    
    # API配置
    "XTDATA_ACCOUNT_ID",
    "XTDATA_ACCOUNT_KEY",
    "API_TIMEOUT",
    "API_RETRY_TIMES",
    "API_RETRY_DELAY",
    "API_RATE_LIMIT_DELAY",
    "API_BATCH_SIZE",
    
    # 数据配置
    "DEFAULT_PERIOD",
    "DEFAULT_ADJUST_TYPE",
    "PRICE_MIN_THRESHOLD",
    "PRICE_MAX_THRESHOLD",
    "VOLUME_MIN_THRESHOLD",
    "MAX_DATA_GAP_DAYS",
    
    # 存储配置
    "HDF5_COMPRESSION",
    "HDF5_COMPLEVEL",
    "HDF5_DATE_FORMAT",
    "CSV_DATE_FORMAT",
    
    # 可视化配置
    "PLOT_STYLE",
    "COLOR_UP",
    "COLOR_DOWN",
    "FIGURE_SIZE",
    "DPI",
    
    # 日志
    "setup_logging",
    "logger",
    
    # 异常类
    "XtDataError",
    "ConnectionError",
    "DataError",
    "ValidationError",
    "StorageError",
]
