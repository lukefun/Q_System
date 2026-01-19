"""
XtDataClient单元测试

测试XtData客户端的连接管理、认证和错误处理功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.xtdata_client import XtDataClient
from config import ConnectionError


class TestXtDataClientInitialization:
    """测试XtDataClient初始化"""
    
    def test_init_with_credentials(self):
        """测试使用提供的凭证初始化"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345"
        )
        
        assert client.account_id == "test_account"
        assert client.account_key == "test_key_12345"
        assert not client.is_connected()
    
    def test_init_without_credentials_raises_error(self):
        """测试未提供凭证时抛出错误"""
        with patch('src.xtdata_client.XTDATA_ACCOUNT_ID', ''):
            with patch('src.xtdata_client.XTDATA_ACCOUNT_KEY', ''):
                with pytest.raises(ValueError) as exc_info:
                    XtDataClient()
                
                assert "账户信息未配置" in str(exc_info.value)
    
    def test_init_with_custom_timeout_and_retry(self):
        """测试自定义超时和重试参数"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345",
            timeout=60,
            retry_times=5,
            retry_delay=2.0
        )
        
        assert client.timeout == 60
        assert client.retry_times == 5
        assert client.retry_delay == 2.0


class TestXtDataClientConnection:
    """测试XtDataClient连接功能"""
    
    def test_connect_success(self):
        """测试连接成功场景"""
        # 模拟xtquant模块
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            client = XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            )
            
            result = client.connect()
            
            assert result is True
            assert client.is_connected()
    
    def test_connect_without_xtquant_module(self):
        """测试xtquant模块不存在时的错误处理"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345",
            retry_times=1  # 减少重试次数以加快测试
        )
        
        # 模拟导入失败
        def mock_import(name, *args, **kwargs):
            if 'xtquant' in name:
                raise ImportError(f"No module named '{name}'")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            with pytest.raises(ConnectionError) as exc_info:
                client.connect()
            
            # 检查错误消息
            error_msg = str(exc_info.value)
            assert "无法导入xtquant模块" in error_msg or "已重试" in error_msg
            assert not client.is_connected()
    
    @patch('src.xtdata_client.time.sleep')
    def test_connect_with_retry(self, mock_sleep):
        """测试连接失败后重试"""
        mock_xtdata = MagicMock()
        
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345",
            retry_times=3,
            retry_delay=1.0
        )
        
        # 模拟前两次认证失败，第三次成功
        call_count = [0]
        
        def mock_authenticate():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ConnectionError("认证失败")
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            with patch.object(client, '_authenticate', side_effect=mock_authenticate):
                result = client.connect()
                
                assert result is True
                assert client.is_connected()
                assert mock_sleep.call_count == 2  # 重试2次，sleep 2次
    
    def test_connect_already_connected(self):
        """测试已连接时再次调用connect"""
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            client = XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            )
            
            # 第一次连接
            client.connect()
            assert client.is_connected()
            
            # 第二次连接应该直接返回True
            result = client.connect()
            assert result is True
    
    @patch('src.xtdata_client.time.sleep')
    def test_connect_max_retries_exceeded(self, mock_sleep):
        """测试超过最大重试次数后抛出错误"""
        mock_xtdata = MagicMock()
        
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345",
            retry_times=2,
            retry_delay=0.1
        )
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            with patch.object(client, '_authenticate', side_effect=ConnectionError("认证失败")):
                with pytest.raises(ConnectionError) as exc_info:
                    client.connect()
                
                assert "已重试 2 次" in str(exc_info.value)
                assert not client.is_connected()


class TestXtDataClientAuthentication:
    """测试XtDataClient认证功能"""
    
    def test_authenticate_with_valid_credentials(self):
        """测试有效凭证的认证"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345"
        )
        
        # 认证应该成功（不抛出异常）
        client._authenticate()
    
    def test_authenticate_with_invalid_account_id(self):
        """测试无效账户ID的认证"""
        client = XtDataClient(
            account_id="abc",  # 太短
            account_key="test_key_12345"
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            client._authenticate()
        
        assert "账户ID格式无效" in str(exc_info.value)
    
    def test_authenticate_with_invalid_account_key(self):
        """测试无效账户密钥的认证"""
        client = XtDataClient(
            account_id="test_account",
            account_key="short"  # 太短
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            client._authenticate()
        
        assert "账户密钥格式无效" in str(exc_info.value)


class TestXtDataClientDisconnection:
    """测试XtDataClient断开连接功能"""
    
    def test_disconnect_when_connected(self):
        """测试已连接时断开连接"""
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            client = XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            )
            
            client.connect()
            assert client.is_connected()
            
            client.disconnect()
            assert not client.is_connected()
    
    def test_disconnect_when_not_connected(self):
        """测试未连接时断开连接"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345"
        )
        
        # 应该不抛出异常
        client.disconnect()
        assert not client.is_connected()


class TestXtDataClientContextManager:
    """测试XtDataClient上下文管理器"""
    
    def test_context_manager_usage(self):
        """测试使用with语句管理连接"""
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            with XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            ) as client:
                assert client.is_connected()
            
            # 退出with块后应该自动断开
            assert not client.is_connected()


class TestXtDataClientGetModule:
    """测试获取xtdata模块"""
    
    def test_get_xtdata_module_when_connected(self):
        """测试连接后获取xtdata模块"""
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            client = XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            )
            
            client.connect()
            module = client.get_xtdata_module()
            
            assert module is not None
    
    def test_get_xtdata_module_when_not_connected(self):
        """测试未连接时获取xtdata模块抛出错误"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345"
        )
        
        with pytest.raises(ConnectionError) as exc_info:
            client.get_xtdata_module()
        
        assert "客户端未连接" in str(exc_info.value)


class TestXtDataClientRepr:
    """测试XtDataClient字符串表示"""
    
    def test_repr_when_not_connected(self):
        """测试未连接时的字符串表示"""
        client = XtDataClient(
            account_id="test_account",
            account_key="test_key_12345"
        )
        
        repr_str = repr(client)
        
        assert "test" in repr_str
        assert "未连接" in repr_str
    
    def test_repr_when_connected(self):
        """测试已连接时的字符串表示"""
        mock_xtdata = MagicMock()
        
        with patch.dict('sys.modules', {'xtquant': MagicMock(), 'xtquant.xtdata': mock_xtdata}):
            client = XtDataClient(
                account_id="test_account",
                account_key="test_key_12345"
            )
            
            client.connect()
            repr_str = repr(client)
            
            assert "test" in repr_str
            assert "已连接" in repr_str
