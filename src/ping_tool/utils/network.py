"""
网络工具模块
"""
import socket


def get_local_ip() -> str:
    """
    获取本机IP地址
    
    Returns:
        str: 本机IP地址，失败返回"本地主机"
    """
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接一个公网IP（不会真实建立连接）
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "本地主机"

