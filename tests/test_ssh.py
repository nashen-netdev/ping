"""
测试SSH连接模块
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from ping_tool.core.ssh import SSHClient, SSHConnectionPool


class TestSSHClient:
    """测试SSH客户端"""
    
    @patch('ping_tool.core.ssh.paramiko.SSHClient')
    def test_connect_with_password_success(self, mock_ssh):
        """测试使用密码连接成功"""
        client = SSHClient("192.168.1.1", "root", password="test123")
        
        result = client.connect()
        
        assert result is True
        mock_ssh.return_value.connect.assert_called_once()
    
    @patch('ping_tool.core.ssh.paramiko.SSHClient')
    def test_connect_with_password_failure(self, mock_ssh):
        """测试使用密码连接失败"""
        mock_ssh.return_value.connect.side_effect = Exception("Connection failed")
        
        client = SSHClient("192.168.1.1", "root", password="test123")
        result = client.connect()
        
        assert result is False
    
    @patch('ping_tool.core.ssh.paramiko.RSAKey')
    @patch('ping_tool.core.ssh.paramiko.SSHClient')
    def test_connect_with_key(self, mock_ssh, mock_key):
        """测试使用密钥连接"""
        client = SSHClient("192.168.1.1", "root", key_file="/path/to/key")
        
        result = client.connect()
        
        assert result is True
        mock_key.from_private_key_file.assert_called_once_with("/path/to/key")
    
    def test_execute_command_success(self):
        """测试执行命令成功"""
        client = SSHClient("192.168.1.1", "root", password="test123")
        
        # 模拟已连接的客户端
        mock_client = Mock()
        mock_stdout = Mock()
        mock_stdout.read.return_value = b"command output"
        mock_client.exec_command.return_value = (None, mock_stdout, None)
        
        client.client = mock_client
        
        result = client.execute_command("ls -l")
        
        assert result == "command output"
        mock_client.exec_command.assert_called_once_with("ls -l", timeout=30)
    
    def test_execute_command_no_client(self):
        """测试在未连接时执行命令"""
        client = SSHClient("192.168.1.1", "root", password="test123")
        
        result = client.execute_command("ls -l")
        
        assert result is None
    
    def test_close(self):
        """测试关闭连接"""
        client = SSHClient("192.168.1.1", "root", password="test123")
        client.client = Mock()
        
        client.close()
        
        client.client.close.assert_called_once()


class TestSSHConnectionPool:
    """测试SSH连接池"""
    
    @patch('ping_tool.core.ssh.SSHClient')
    def test_create_connection_success(self, mock_ssh_client):
        """测试创建连接成功"""
        mock_client = Mock()
        mock_client.connect.return_value = True
        mock_ssh_client.return_value = mock_client
        
        pool = SSHConnectionPool("192.168.1.1", "root", password="test123")
        result = pool.create_connection()
        
        assert result == mock_client
    
    @patch('ping_tool.core.ssh.SSHClient')
    def test_create_connection_with_retry(self, mock_ssh_client):
        """测试连接失败后重试"""
        mock_client = Mock()
        # 第一次失败，第二次成功
        mock_client.connect.side_effect = [False, True]
        mock_ssh_client.return_value = mock_client
        
        pool = SSHConnectionPool("192.168.1.1", "root", password="test123", max_retries=2)
        result = pool.create_connection()
        
        assert result == mock_client
        assert mock_client.connect.call_count == 2
    
    @patch('ping_tool.core.ssh.SSHClient')
    def test_create_connection_max_retries_exceeded(self, mock_ssh_client):
        """测试超过最大重试次数"""
        mock_client = Mock()
        mock_client.connect.return_value = False
        mock_ssh_client.return_value = mock_client
        
        pool = SSHConnectionPool("192.168.1.1", "root", password="test123", max_retries=1)
        result = pool.create_connection()
        
        assert result is None
    
    @patch('ping_tool.core.ssh.SSHClient')
    def test_execute_command_with_new_connection(self, mock_ssh_client):
        """测试使用新连接执行命令"""
        mock_client = Mock()
        mock_client.connect.return_value = True
        mock_client.execute_command.return_value = "command output"
        mock_ssh_client.return_value = mock_client
        
        pool = SSHConnectionPool("192.168.1.1", "root", password="test123")
        result = pool.execute_command_with_new_connection("ls -l")
        
        assert result == "command output"
        mock_client.close.assert_called_once()
    
    @patch('ping_tool.core.ssh.SSHClient')
    def test_execute_command_connection_fail(self, mock_ssh_client):
        """测试连接失败时执行命令"""
        mock_client = Mock()
        mock_client.connect.return_value = False
        mock_ssh_client.return_value = mock_client
        
        pool = SSHConnectionPool("192.168.1.1", "root", password="test123", max_retries=0)
        result = pool.execute_command_with_new_connection("ls -l")
        
        assert result is None

