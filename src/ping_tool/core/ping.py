"""
Ping 核心功能模块
"""
import subprocess
from subprocess import TimeoutExpired
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.ssh import SSHConnectionPool


def ping_ip_local(ip: str) -> tuple[str, bool, str]:
    """
    在本地执行ping命令（优化并发版本）
    
    Args:
        ip: 目标IP地址
        
    Returns:
        tuple: (IP地址, 是否成功, ping输出结果)
    """
    try:
        # 使用更激进的参数优化ping速度
        # -c 3: 发送3个包（保证统计准确性）
        # -W 2: 每个包最多等待2秒
        # -i 0.2: 包间隔0.2秒（加快速度）
        result = subprocess.run(
            ['ping', '-c', '3', '-W', '2', '-i', '0.2', ip], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            timeout=8
        )
        success = result.returncode == 0
        return ip, success, result.stdout
    except (TimeoutExpired, Exception) as e:
        return ip, False, f"Ping超时或异常: {str(e)}"


def ping_ip_remote(ssh_pool, ip: str) -> tuple[str, bool, str]:
    """
    通过SSH在远程服务器上执行ping命令（优化并发版本，使用独立连接）
    
    Args:
        ssh_pool: SSHConnectionPool对象或SSHClient对象
        ip: 目标IP地址
        
    Returns:
        tuple: (IP地址, 是否成功, ping输出结果)
    """
    try:
        # 优化参数：3个包，2秒超时，0.2秒间隔
        # 如果是连接池，使用新连接；如果是单个客户端，使用现有连接
        if isinstance(ssh_pool, SSHConnectionPool):
            result = ssh_pool.execute_command_with_new_connection(
                f'ping -c 3 -W 2 -i 0.2 {ip}', 
                timeout=8
            )
        else:
            result = ssh_pool.execute_command(f'ping -c 3 -W 2 -i 0.2 {ip}', timeout=8)
        
        if result is None:
            return ip, False, "远程连接失败"
        success = ' 0% packet loss' in result
        return ip, success, result
    except Exception as e:
        return ip, False, f"远程Ping异常: {str(e)}"


def ping_network(network, ssh_pool=None, max_workers=None) -> tuple[list, list, dict]:
    """
    对网段进行ping测试，支持本地或远程执行（优化并发版本）
    
    Args:
        network: ipaddress.ip_network对象
        ssh_pool: SSHConnectionPool对象（每个线程使用独立连接）或None（本地执行）
        max_workers: 并发数，如果为None则自动设置
        
    Returns:
        tuple: (可达IP列表, 不可达IP列表, ping结果字典)
    """
    reachable_ips = []
    unreachable_ips = []
    ping_results = {}  # 存储ping的详细结果
    
    # 获取网段中的所有IP
    all_ips = list(network.hosts())
    total_ips = len(all_ips)
    
    # 自动设置并发数
    if max_workers is None:
        max_workers = 5 if ssh_pool else 30
    
    if ssh_pool:
        print(f"开始从远程服务器并发 ping 网段 {network}，共 {total_ips} 个IP（并发数: {max_workers}，每个IP独立SSH连接）")
    else:
        print(f"开始从本地并发 ping 网段 {network}，共 {total_ips} 个IP（并发数: {max_workers}）")
    
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if ssh_pool:
            future_to_ip = {
                executor.submit(ping_ip_remote, ssh_pool, str(ip)): ip 
                for ip in all_ips
            }
        else:
            future_to_ip = {
                executor.submit(ping_ip_local, str(ip)): ip 
                for ip in all_ips
            }

        for future in as_completed(future_to_ip):
            ip, success, output = future.result()
            ping_results[ip] = output
            if success:
                reachable_ips.append(ip)
            else:
                unreachable_ips.append(ip)
                
            # 更新进度
            completed += 1
            if total_ips > 10:  # 只有当IP数量较多时才显示进度
                progress = (completed / total_ips) * 100
                status = '✓' if success else '✗'
                print(f"网段进度: {completed}/{total_ips} ({progress:.1f}%) - {ip} {status}")

    print(f"网段 {network} ping 测试完成！可达: {len(reachable_ips)}, 不可达: {len(unreachable_ips)}")
    return reachable_ips, unreachable_ips, ping_results

