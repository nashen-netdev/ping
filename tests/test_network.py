"""
测试网络工具模块
"""
import pytest
from ping_tool.utils.network import get_local_ip


def test_get_local_ip():
    """测试获取本地IP"""
    ip = get_local_ip()
    
    # 应该返回一个IP地址或"本地主机"
    assert isinstance(ip, str)
    assert len(ip) > 0
    
    # 如果返回的是IP地址，应该包含点号
    if ip != "本地主机":
        assert "." in ip

