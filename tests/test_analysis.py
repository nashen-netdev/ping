"""
测试延迟分析模块
"""
import pytest
from ping_tool.utils.analysis import analyze_ping_output


def test_analyze_ping_output_success():
    """测试成功的ping输出解析"""
    output = """PING 192.168.1.1 (192.168.1.1): 56 data bytes
64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=0.5 ms
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.6 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.7 ms

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 0.5/0.6/0.7/0.08 ms
"""
    
    result = analyze_ping_output(output)
    
    assert result is not None
    assert result['min'] == 0.5
    assert result['avg'] == 0.6
    assert result['max'] == 0.7
    assert result['mdev'] == 0.08


def test_analyze_ping_output_failure():
    """测试失败的ping输出"""
    output = "ping: unknown host 192.168.1.999"
    
    result = analyze_ping_output(output)
    
    assert result is None


def test_analyze_ping_output_empty():
    """测试空输出"""
    result = analyze_ping_output("")
    
    assert result is None


def test_analyze_ping_output_none():
    """测试None输入"""
    result = analyze_ping_output(None)
    
    assert result is None

