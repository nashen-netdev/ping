import pandas as pd
import os
import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from subprocess import TimeoutExpired
import paramiko
from pathlib import Path
import socket
import time
import logging

# 禁用paramiko的详细日志输出
logging.getLogger("paramiko").setLevel(logging.ERROR)

def get_credentials(ip):
    """
    从Excel文件中获取认证信息
    """
    try:
        df = pd.read_excel('pass/credentials.xlsx')
        row = df[df['IP'] == ip].iloc[0]
        
        # 确保密码是字符串类型
        password = row['pass'] if pd.notna(row['pass']) else None
        if password is not None:
            password = str(password)  # 将任何类型的密码转换为字符串
            # 如果是整数，去掉小数点后的.0
            if password.endswith('.0') and password.replace('.0', '').isdigit():
                password = password.replace('.0', '')
        
        return {
            'username': str(row['user']),  # 确保用户名也是字符串
            'password': password,
            'is_server': bool(row['server']) if 'server' in row and pd.notna(row['server']) else False
        }
    except Exception as e:
        print(f"获取认证信息失败: {str(e)}")
        return None

def analyze_ping_output(output):
    """
    分析ping输出，提取RTT信息
    """
    try:
        if not output or isinstance(output, str) and "失败" in output:
            return None
        
        # 查找rtt统计行
        for line in output.split('\n'):
            if 'rtt min/avg/max/mdev' in line:
                # 提取RTT值
                stats = line.split('=')[1].strip().split('/')
                return {
                    'min': float(stats[0]),
                    'avg': float(stats[1]),
                    'max': float(stats[2]),
                    'mdev': float(stats[3].split()[0])
                }
        return None
    except Exception:
        return None

def main():
    # 设置路径
    log_dir = "./log"
    key_dir = "./pass/key"
    os.makedirs(log_dir, exist_ok=True)

    # 读取所有IP
    print("正在读取 credentials.xlsx 文件...")
    try:
        df = pd.read_excel('pass/credentials.xlsx')
        all_ips = df['IP'].tolist()
        
        # 找到标记为服务器的IP
        server_ips = []
        for ip in all_ips:
            creds = get_credentials(ip)
            if creds and creds.get('is_server'):
                server_ips.append(ip)
        
        # 使用IP列作为目标IP，但排除服务器IP
        target_ips = [ip for ip in all_ips if ip not in server_ips]
        
        print(f"成功读取 {len(all_ips)} 个IP地址")
        print(f"找到 {len(server_ips)} 个服务器IP")
        print(f"成功读取 {len(target_ips)} 个目标IP地址")
    except Exception as e:
        print(f"读取 Excel 文件失败: {str(e)}")
        return

    if not target_ips:
        print("没有找到可ping的目标IP")
        return

    # 使用找到的服务器IP
    server_ip = None
    server_credentials = None
    server_ssh_pool = None

    if server_ips:
        server_ip = server_ips[0]
        server_credentials = get_credentials(server_ip)
        print(f"使用服务器IP: {server_ip}")
    
    if not server_ip:
        print("未找到标记为服务器的IP，将使用本地执行ping测试")

    # 确定ping测试的来源
    source_ip = server_ip if server_ip else get_local_ip()
    print(f"测试来源IP: {source_ip}")

    if server_ip:
        # 创建SSH连接池用于并发测试
        username = server_credentials['username']
        password = server_credentials['password']
        key_file = os.path.join(key_dir, username) if not password else None

        print(f"正在测试服务器 {server_ip} 连接...")
        # 先测试连接是否可用
        test_ssh = SSHClient(server_ip, username, password, key_file)
        if not test_ssh.connect():
            print(f"无法连接到服务器 {server_ip}，将使用本地执行ping测试")
            server_ssh_pool = None
        else:
            print(f"成功连接到服务器 {server_ip}，创建连接池用于并发测试")
            test_ssh.close()
            # 创建连接池
            server_ssh_pool = SSHConnectionPool(server_ip, username, password, key_file)

    # 用于存储结果
    single_reachable = []
    single_unreachable = []
    networks_summary = []
    all_ping_results = {}  # 存储所有ping结果

    # 分离网段和单个IP
    single_ips = [target for target in target_ips if '/' not in target]
    network_targets = [target for target in target_ips if '/' in target]
    
    # 处理单个IP（并发）
    if single_ips:
        total_single = len(single_ips)
        # 根据是否使用远程服务器调整并发数
        if server_ssh_pool:
            max_workers = 5  # 远程SSH并发限制为5，避免超过服务器连接限制
            print(f"\n开始从远程服务器并发处理 {total_single} 个单独IP（并发数: {max_workers}，每个IP使用独立SSH连接）...")
        else:
            max_workers = 20  # 本地并发可以更高
            print(f"\n开始从本地并发处理 {total_single} 个单独IP（并发数: {max_workers}）...")
        
        completed = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            if server_ssh_pool:
                future_to_ip = {executor.submit(ping_ip_remote, server_ssh_pool, ip): ip 
                              for ip in single_ips}
            else:
                future_to_ip = {executor.submit(ping_ip_local, ip): ip 
                              for ip in single_ips}
            
            for future in as_completed(future_to_ip):
                try:
                    ip, success, output = future.result()
                    all_ping_results[ip] = output
                    if success:
                        single_reachable.append(ip)
                    else:
                        single_unreachable.append(ip)
                    
                    # 更新进度
                    completed += 1
                    progress = (completed / total_single) * 100
                    print(f"单个IP进度: {completed}/{total_single} ({progress:.1f}%) - 最新: {ip} {'✓' if success else '✗'}")
                except Exception as e:
                    print(f"处理IP时出错: {str(e)}")
        
        print(f"\n单个IP处理完成！可达: {len(single_reachable)}, 不可达: {len(single_unreachable)}")
    
    # 处理网段（串行，但网段内部并发）
    if network_targets:
        print(f"\n开始处理 {len(network_targets)} 个网段...")
        for i, target in enumerate(network_targets, 1):
            print(f"\n处理网段 {i}/{len(network_targets)}: {target}")
            try:
                network = ipaddress.ip_network(target, strict=False)
                reachable, unreachable, ping_results = ping_network(network, server_ssh_pool if server_ssh_pool else None)
                networks_summary.append({
                    "network": target,
                    "reachable": reachable,
                    "unreachable": unreachable,
                    "ping_results": ping_results
                })
            except ValueError as e:
                print(f"处理网段 {target} 时出错: {str(e)}")
                continue

    # 注意：使用连接池时，连接会在每次使用后自动关闭，无需手动关闭
    if server_ssh_pool:
        print("所有SSH连接已在使用后自动关闭")

    # 用于存储高延迟IP
    high_latency_ips = []

    # 分析所有可达IP的延迟
    for ip in single_reachable:
        rtt_stats = analyze_ping_output(all_ping_results[ip])
        if rtt_stats and rtt_stats['max'] > 1.0:  # 最大延迟超过1ms
            high_latency_ips.append((ip, rtt_stats))

    # 分析网段中的IP延迟
    for summary in networks_summary:
        for ip in summary['reachable']:
            rtt_stats = analyze_ping_output(summary['ping_results'][ip])
            if rtt_stats and rtt_stats['max'] > 1.0:  # 最大延迟超过1ms
                high_latency_ips.append((ip, rtt_stats))

    # 写入日志文件
    log_file_path = os.path.join(log_dir, "ping_results.log")
    with open(log_file_path, "w") as log_file:
        # 计算总计统计信息
        total_pinged = len(single_reachable) + len(single_unreachable) + \
                      sum(len(summary["reachable"]) + len(summary["unreachable"]) 
                          for summary in networks_summary)
        total_reachable = len(single_reachable) + \
                         sum(len(summary["reachable"]) for summary in networks_summary)
        total_unreachable = len(single_unreachable) + \
                           sum(len(summary["unreachable"]) for summary in networks_summary)
        total_high_latency = len(high_latency_ips)

        # 写入总计统计信息
        log_file.write(f"总计统计信息:\n")
        log_file.write("-" * 40 + "\n")
        log_file.write(f"测试来源: {source_ip}\n")
        log_file.write(f"总计ping的IP数量: {total_pinged}\n")
        log_file.write(f"总计可达IP数量: {total_reachable}\n")
        log_file.write(f"总计不可达IP数量: {total_unreachable}\n")
        log_file.write(f"延迟质量较差IP数量: {total_high_latency} (最大RTT > 1ms)\n")
        log_file.write("-" * 40 + "\n\n")

        # 写入延迟质量分析
        if high_latency_ips:
            log_file.write(f"延迟质量分析:\n")
            log_file.write("-" * 40 + "\n")
            log_file.write("以下IP的最大响应时间超过1ms:\n\n")
            
            # 按最大延迟排序
            high_latency_ips.sort(key=lambda x: x[1]['max'], reverse=True)
            
            for ip, stats in high_latency_ips:
                log_file.write(f"IP: {ip}\n")
                log_file.write(f"  最小延迟: {stats['min']:.3f} ms\n")
                log_file.write(f"  平均延迟: {stats['avg']:.3f} ms\n")
                log_file.write(f"  最大延迟: {stats['max']:.3f} ms\n")
                log_file.write(f"  延迟抖动: {stats['mdev']:.3f} ms\n")
                log_file.write("-" * 20 + "\n")
            log_file.write("\n")

        # 写入测试信息头
        log_file.write(f"Ping测试详细信息:\n")
        log_file.write("-" * 40 + "\n")
        log_file.write(f"测试来源: {source_ip}\n")
        log_file.write("-" * 40 + "\n\n")

        # 写入单个IP结果
        if single_reachable:
            log_file.write(f"从 {source_ip} 可达的IP:\n")
            for ip in single_reachable:
                log_file.write(f"\n{ip}\n")
                log_file.write("-" * 20 + "\n")
                log_file.write(all_ping_results[ip])
                log_file.write("\n")
            log_file.write("\n")

        if single_unreachable:
            log_file.write(f"从 {source_ip} 不可达的IP:\n")
            for ip in single_unreachable:
                log_file.write(f"\n{ip}\n")
                log_file.write("-" * 20 + "\n")
                log_file.write(all_ping_results[ip])
                log_file.write("\n")
            log_file.write("\n")

        # 写入网段结果
        for summary in networks_summary:
            log_file.write("-" * 40 + "\n")
            log_file.write(f"网段: {summary['network']}\n")
            log_file.write(f"从 {source_ip} 可达的IP:\n")
            for ip in summary['reachable']:
                log_file.write(f"\n{ip}\n")
                log_file.write("-" * 20 + "\n")
                log_file.write(summary['ping_results'][ip])
                log_file.write("\n")
            
            log_file.write(f"\n从 {source_ip} 不可达的IP:\n")
            for ip in summary['unreachable']:
                log_file.write(f"\n{ip}\n")
                log_file.write("-" * 20 + "\n")
                log_file.write(summary['ping_results'][ip])
                log_file.write("\n")
            log_file.write("-" * 40 + "\n\n")

    print(f"结果已写入: {log_file_path}")
    print("程序执行完成！")

class SSHClient:
    def __init__(self, hostname, username, password=None, key_file=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.password:
                self.client.connect(self.hostname, username=self.username, password=self.password, timeout=10)
            else:
                key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client.connect(self.hostname, username=self.username, pkey=key, timeout=10)
            return True
        except Exception as e:
            print(f"连接失败 {self.hostname}: {str(e)}")
            return False

    def execute_command(self, command, timeout=30):
        if not self.client:
            return None
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            return stdout.read().decode()
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
            return None

    def close(self):
        if self.client:
            self.client.close()

class SSHConnectionPool:
    """SSH连接池，用于并发场景下管理多个SSH连接"""
    def __init__(self, hostname, username, password=None, key_file=None, max_retries=2):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
        self.max_retries = max_retries
        # 禁用paramiko的日志输出，减少错误信息
        logging.getLogger("paramiko").setLevel(logging.WARNING)
    
    def create_connection(self, retry_count=0):
        """创建一个新的SSH连接，带重试机制"""
        try:
            # 添加小延迟，避免瞬间大量连接
            if retry_count > 0:
                time.sleep(0.5 * retry_count)  # 递增延迟
            
            ssh = SSHClient(self.hostname, self.username, self.password, self.key_file)
            if ssh.connect():
                return ssh
        except Exception:
            pass
        
        # 重试机制
        if retry_count < self.max_retries:
            return self.create_connection(retry_count + 1)
        return None
    
    def execute_command_with_new_connection(self, command, timeout=30):
        """使用新连接执行命令，执行完成后关闭连接"""
        ssh = self.create_connection()
        if not ssh:
            return None
        try:
            result = ssh.execute_command(command, timeout)
            return result
        finally:
            ssh.close()

def get_local_ip():
    """
    获取本机IP地址
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

def ping_ip_remote(ssh_pool, ip):
    """
    通过SSH在远程服务器上执行ping命令（优化并发版本，使用独立连接）
    ssh_pool: SSHConnectionPool对象或SSHClient对象
    """
    try:
        # 优化参数：3个包，2秒超时，0.2秒间隔
        # 如果是连接池，使用新连接；如果是单个客户端，使用现有连接
        if isinstance(ssh_pool, SSHConnectionPool):
            result = ssh_pool.execute_command_with_new_connection(f'ping -c 3 -W 2 -i 0.2 {ip}', timeout=8)
        else:
            result = ssh_pool.execute_command(f'ping -c 3 -W 2 -i 0.2 {ip}', timeout=8)
        
        if result is None:
            return ip, False, "远程连接失败"
        success = ' 0% packet loss' in result
        return ip, success, result
    except Exception as e:
        return ip, False, f"远程Ping异常: {str(e)}"

def ping_ip_local(ip):
    """
    在本地执行ping命令（优化并发版本）
    """
    try:
        # 使用更激进的参数优化ping速度
        # -c 3: 发送3个包（保证统计准确性）
        # -W 2: 每个包最多等待2秒
        # -i 0.2: 包间隔0.2秒（加快速度）
        result = subprocess.run(['ping', '-c', '3', '-W', '2', '-i', '0.2', ip], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               timeout=8)
        success = result.returncode == 0
        return ip, success, result.stdout
    except (TimeoutExpired, Exception) as e:
        return ip, False, f"Ping超时或异常: {str(e)}"

def ping_network(network, ssh_pool=None, max_workers=None):
    """
    对网段进行ping测试，支持本地或远程执行（优化并发版本）
    ssh_pool: SSHConnectionPool对象（每个线程使用独立连接）或None（本地执行）
    max_workers: 并发数，如果为None则自动设置
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
            future_to_ip = {executor.submit(ping_ip_remote, ssh_pool, str(ip)): ip 
                          for ip in all_ips}
        else:
            future_to_ip = {executor.submit(ping_ip_local, str(ip)): ip 
                          for ip in all_ips}

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

if __name__ == "__main__":
    main() 