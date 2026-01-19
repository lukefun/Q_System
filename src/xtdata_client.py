"""
XtData客户端封装模块

提供XtData API的底层调用封装，处理认证、连接管理和错误处理
"""

import time
from typing import Optional
from config import (
    logger,
    ConnectionError,
    XTDATA_ACCOUNT_ID,
    XTDATA_ACCOUNT_KEY,
    API_TIMEOUT,
    API_RETRY_TIMES,
    API_RETRY_DELAY
)


class XtDataClient:
    """
    XtData API客户端封装
    
    封装XtData API的底层调用，提供连接管理、认证处理和错误重试机制。
    
    Attributes:
        account_id: XtData账户ID
        account_key: XtData账户密钥
        timeout: API调用超时时间（秒）
        retry_times: 连接失败重试次数
        retry_delay: 重试间隔（秒）
    
    Example:
        >>> client = XtDataClient(account_id="your_id", account_key="your_key")
        >>> if client.connect():
        ...     print("连接成功")
        ...     # 使用客户端进行数据操作
        ...     client.disconnect()
    """
    
    def __init__(
        self,
        account_id: Optional[str] = None,
        account_key: Optional[str] = None,
        timeout: int = API_TIMEOUT,
        retry_times: int = API_RETRY_TIMES,
        retry_delay: float = API_RETRY_DELAY
    ):
        """
        初始化XtData客户端
        
        Args:
            account_id: XtData账户ID，None则从配置读取
            account_key: XtData账户密钥，None则从配置读取
            timeout: API调用超时时间（秒）
            retry_times: 连接失败重试次数
            retry_delay: 重试间隔（秒）
        
        Raises:
            ValueError: 账户ID或密钥为空
        """
        self.account_id = account_id or XTDATA_ACCOUNT_ID
        self.account_key = account_key or XTDATA_ACCOUNT_KEY
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        
        # 验证账户信息
        if not self.account_id or not self.account_key:
            raise ValueError(
                "XtData账户信息未配置。请提供account_id和account_key，"
                "或设置XTDATA_ACCOUNT_ID和XTDATA_ACCOUNT_KEY环境变量。"
            )
        
        # 连接状态
        self._connected = False
        self._xtdata_module = None
        
        logger.info(f"XtDataClient初始化完成，账户ID: {self.account_id[:4]}****")
    
    def connect(self) -> bool:
        """
        连接到XtData服务
        
        尝试导入xtquant模块并建立连接。如果连接失败，会根据配置的重试次数
        进行重试。
        
        Returns:
            连接是否成功
        
        Raises:
            ConnectionError: 连接失败且重试次数用尽
        
        Example:
            >>> client = XtDataClient(account_id="test", account_key="test")
            >>> success = client.connect()
            >>> if success:
            ...     print("连接成功")
        """
        if self._connected:
            logger.info("XtData客户端已连接")
            return True
        
        # 尝试导入xtquant模块
        for attempt in range(self.retry_times):
            try:
                logger.info(f"尝试连接XtData服务 (尝试 {attempt + 1}/{self.retry_times})...")
                
                # 导入xtquant模块
                try:
                    import xtquant.xtdata as xtdata
                    self._xtdata_module = xtdata
                except ImportError as e:
                    error_msg = (
                        "无法导入xtquant模块。请确保已安装xtquant库。\n"
                        "安装方法：\n"
                        "1. 通过QMT客户端自动配置\n"
                        "2. pip install xtquant\n"
                        "3. 从QMT安装目录复制xtquant模块"
                    )
                    logger.error(error_msg)
                    raise ConnectionError(error_msg) from e
                
                # 连接到XtData服务
                # 注意：实际的xtquant可能不需要显式连接，这里模拟连接过程
                # 真实实现需要根据xtquant的实际API调整
                
                # 模拟认证过程
                self._authenticate()
                
                self._connected = True
                logger.info("XtData服务连接成功")
                return True
                
            except ConnectionError as e:
                logger.warning(f"连接失败: {str(e)}")
                
                if attempt < self.retry_times - 1:
                    logger.info(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    error_msg = f"连接XtData服务失败，已重试 {self.retry_times} 次"
                    logger.error(error_msg)
                    raise ConnectionError(error_msg) from e
            
            except Exception as e:
                error_msg = f"连接过程中发生未预期错误: {str(e)}"
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e
        
        return False
    
    def _authenticate(self) -> None:
        """
        执行认证过程
        
        使用账户ID和密钥进行认证。
        
        Raises:
            ConnectionError: 认证失败
        """
        try:
            # 注意：这里是模拟认证过程
            # 实际的xtquant API可能有不同的认证方式
            # 需要根据实际API文档调整
            
            # 验证账户信息格式
            if len(self.account_id) < 4:
                raise ConnectionError("账户ID格式无效")
            
            if len(self.account_key) < 8:
                raise ConnectionError("账户密钥格式无效")
            
            logger.debug("认证成功")
            
        except Exception as e:
            error_msg = f"认证失败: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    def disconnect(self) -> None:
        """
        断开XtData连接
        
        清理资源并断开与XtData服务的连接。
        
        Example:
            >>> client = XtDataClient(account_id="test", account_key="test")
            >>> client.connect()
            >>> # 使用客户端...
            >>> client.disconnect()
        """
        if not self._connected:
            logger.info("XtData客户端未连接，无需断开")
            return
        
        try:
            # 清理资源
            self._xtdata_module = None
            self._connected = False
            
            logger.info("XtData连接已断开")
            
        except Exception as e:
            logger.error(f"断开连接时发生错误: {str(e)}")
            # 即使出错也标记为未连接
            self._connected = False
    
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            是否已连接到XtData服务
        
        Example:
            >>> client = XtDataClient(account_id="test", account_key="test")
            >>> print(client.is_connected())  # False
            >>> client.connect()
            >>> print(client.is_connected())  # True
        """
        return self._connected
    
    def get_xtdata_module(self):
        """
        获取xtdata模块实例
        
        供其他模块使用，用于调用xtquant的具体API。
        
        Returns:
            xtdata模块实例
        
        Raises:
            ConnectionError: 客户端未连接
        
        Example:
            >>> client = XtDataClient(account_id="test", account_key="test")
            >>> client.connect()
            >>> xtdata = client.get_xtdata_module()
            >>> # 使用xtdata进行数据操作
        """
        if not self._connected:
            raise ConnectionError("客户端未连接，请先调用connect()方法")
        
        return self._xtdata_module
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        return False
    
    def __repr__(self) -> str:
        """字符串表示"""
        status = "已连接" if self._connected else "未连接"
        return f"XtDataClient(account_id={self.account_id[:4]}****, status={status})"
