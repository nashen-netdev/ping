"""
CLI主程序
"""
import os
import ipaddress
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from .core.ping import ping_ip_local, ping_ip_remote, ping_network
from .core.ssh import SSHClient, SSHConnectionPool
from .utils.credentials import get_credentials
from .utils.network import get_local_ip
from .utils.analysis import analyze_ping_output


def main():
    """主程序入口"""
    # 设置路径
    log_dir = "./logs"
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


if __name__ == "__main__":
    main()

