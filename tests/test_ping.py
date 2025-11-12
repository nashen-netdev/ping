"""
测试Ping功能模块
"""
import pytest
from unittest.mock import Mock, patch
from ping_tool.core.ping import ping_ip_local, ping_ip_remote, ping_network


class TestPingLocal:
    """测试本地Ping功能"""
    
    @patch('ping_tool.core.ping.subprocess.run')
    def test_ping_ip_local_success(self, mock_run):
        """测试本地ping成功的情况"""
        # 模拟成功的ping输出
        mock_run.return_value = Mock(
            returncode=0,
            stdout="PING 192.168.1.1: 56 data bytes\n64 bytes from 192.168.1.1: time=0.5 ms\n"
        )
        
        ip, success, output = ping_ip_local("192.168.1.1")
        
        assert ip == "192.168.1.1"
        assert success is True
        assert "192.168.1.1" in output
    
    @patch('ping_tool.core.ping.subprocess.run')
    def test_ping_ip_local_failure(self, mock_run):
        """测试本地ping失败的情况"""
        # 模拟失败的ping输出
        mock_run.return_value = Mock(
            returncode=1,
            stdout="Request timeout"
        )
        
        ip, success, output = ping_ip_local("192.168.1.999")
        
        assert ip == "192.168.1.999"
        assert success is False
    
    @patch('ping_tool.core.ping.subprocess.run')
    def test_ping_ip_local_timeout(self, mock_run):
        """测试本地ping超时的情况"""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("ping", 8)
        
        ip, success, output = ping_ip_local("192.168.1.1")
        
        assert ip == "192.168.1.1"
        assert success is False
        assert "超时或异常" in output


class TestPingRemote:
    """测试远程Ping功能"""
    
    def test_ping_ip_remote_success(self):
        """测试远程ping成功的情况"""
        from ping_tool.core.ssh import SSHConnectionPool
        
        # 创建模拟的SSH连接池
        mock_pool = Mock(spec=SSHConnectionPool)
        mock_pool.execute_command_with_new_connection.return_value = (
            "PING 192.168.1.1: 56 data bytes\n"
            "64 bytes from 192.168.1.1: time=0.5 ms\n"
            "--- 192.168.1.1 ping statistics ---\n"
            "3 packets transmitted, 3 received, 0% packet loss\n"
        )
        
        ip, success, output = ping_ip_remote(mock_pool, "192.168.1.1")
        
        assert ip == "192.168.1.1"
        assert success is True
        assert "0% packet loss" in output
    
    def test_ping_ip_remote_failure(self):
        """测试远程ping失败的情况"""
        mock_pool = Mock()
        mock_pool.execute_command_with_new_connection.return_value = (
            "PING 192.168.1.1: 56 data bytes\n"
            "--- 192.168.1.1 ping statistics ---\n"
            "3 packets transmitted, 0 received, 100% packet loss\n"
        )
        
        ip, success, output = ping_ip_remote(mock_pool, "192.168.1.1")
        
        assert ip == "192.168.1.1"
        assert success is False
    
    def test_ping_ip_remote_connection_fail(self):
        """测试远程连接失败的情况"""
        from ping_tool.core.ssh import SSHConnectionPool
        
        mock_pool = Mock(spec=SSHConnectionPool)
        mock_pool.execute_command_with_new_connection.return_value = None
        
        ip, success, output = ping_ip_remote(mock_pool, "192.168.1.1")
        
        assert ip == "192.168.1.1"
        assert success is False
        assert "远程连接失败" in output


class TestPingNetwork:
    """测试网段Ping功能"""
    
    @patch('ping_tool.core.ping.ping_ip_local')
    def test_ping_network_local(self, mock_ping):
        """测试本地网段ping"""
        import ipaddress
        
        # 模拟ping结果
        mock_ping.return_value = ("192.168.1.1", True, "success")
        
        network = ipaddress.ip_network("192.168.1.0/30", strict=False)
        reachable, unreachable, results = ping_network(network, ssh_pool=None, max_workers=2)
        
        # /30网段只有2个主机IP
        assert len(reachable) + len(unreachable) == 2
        assert isinstance(results, dict)

