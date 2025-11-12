"""
网络 Ping 测试工具

一个专业的网络连通性测试工具，支持本地和远程并发测试。
"""

__version__ = "2.0.0"
__author__ = "Network Team"

from .core.ping import ping_ip_local, ping_ip_remote, ping_network
from .core.ssh import SSHClient, SSHConnectionPool
from .utils.analysis import analyze_ping_output
from .utils.network import get_local_ip

__all__ = [
    "ping_ip_local",
    "ping_ip_remote", 
    "ping_network",
    "SSHClient",
    "SSHConnectionPool",
    "analyze_ping_output",
    "get_local_ip",
]

