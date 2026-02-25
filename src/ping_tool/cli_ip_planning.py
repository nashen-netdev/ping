"""
IP 地址规划表 Ping 工具 CLI (增强版)
专门用于 ping IP 地址规划表中的设备

支持两种使用方式：
1. 网段模式：直接传入 CIDR 网段快速扫描
2. 交互式模式：通过问答方式选择环境和配置
"""
import os
import ipaddress
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .core.ping import ping_ip_local, ping_ip_remote, ping_network
from .core.ssh import SSHClient, SSHConnectionPool
from .utils.network import get_local_ip
from .utils.excel_reader import read_network_security_ips, list_available_colors, find_server_credentials
from .utils.analysis import analyze_ping_output
from .utils.config_manager import (
    ConfigManager, 
    interactive_select_environment, 
    interactive_select_sheet,
    interactive_select_column,
    interactive_select_color_filter,
    interactive_select_ping_mode,
    interactive_input_config
)


def _ping_subnet_mode(args):
    """网段模式：直接 ping 指定 CIDR 网段中的所有主机"""
    try:
        network = ipaddress.ip_network(args.subnet, strict=False)
    except ValueError as e:
        print(f"错误: 无效的网段格式 '{args.subnet}': {e}")
        print("正确格式示例: 192.168.1.0/24, 10.0.0.0/16")
        return

    all_ips = list(network.hosts())
    total = len(all_ips)

    if total == 0:
        print(f"错误: 网段 {network} 中没有可用的主机地址")
        return

    if total > 1024:
        confirm = input(f"网段 {network} 包含 {total} 个 IP，确认继续？(y/n) [n]: ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return

    source_ip = get_local_ip()
    max_workers = args.max_workers or 30

    print()
    print("=" * 60)
    print("网段 Ping 扫描")
    print("=" * 60)
    print(f"网段: {network}")
    print(f"主机数量: {total}")
    print(f"测试来源: {source_ip} (本地)")
    print(f"并发数: {max_workers}")
    print("=" * 60)
    print()

    reachable, unreachable, ping_results = ping_network(network, ssh_pool=None, max_workers=max_workers)

    # 延迟分析
    latency_analysis = {}
    high_latency_ips = []

    for ip in reachable:
        output = ping_results.get(str(ip), '')
        rtt_info = analyze_ping_output(output)
        if rtt_info:
            latency_analysis[str(ip)] = rtt_info
            if rtt_info['max'] > 1.0:
                high_latency_ips.append((str(ip), rtt_info))

    high_latency_ips.sort(key=lambda x: x[1]['max'], reverse=True)

    # 统计
    print()
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"网段: {network}")
    print(f"总计 IP 数量: {total}")
    print(f"可达 IP 数量: {len(reachable)}")
    print(f"不可达 IP 数量: {len(unreachable)}")
    print(f"可达率: {len(reachable) / total * 100:.1f}%")
    print(f"延迟质量较差 IP 数量: {len(high_latency_ips)} (最大RTT > 1ms)")
    print("=" * 60)

    if high_latency_ips:
        print(f"\n延迟质量较差的 IP ({len(high_latency_ips)}):")
        print("（最大RTT > 1ms，按延迟从高到低排序）")
        for ip, rtt_info in high_latency_ips[:10]:
            print(f"  ⚠ {ip:15s}")
            print(f"     最小: {rtt_info['min']:.3f} ms, "
                  f"平均: {rtt_info['avg']:.3f} ms, "
                  f"最大: {rtt_info['max']:.3f} ms")
        if len(high_latency_ips) > 10:
            print(f"  ... 还有 {len(high_latency_ips) - 10} 个（详见日志文件）")

    if reachable:
        print(f"\n可达的 IP ({len(reachable)}):")
        for ip in sorted(reachable, key=lambda x: int(ipaddress.ip_address(str(x))))[:20]:
            print(f"  ✓ {str(ip):15s}")
        if len(reachable) > 20:
            print(f"  ... 还有 {len(reachable) - 20} 个（详见日志文件）")

    if unreachable:
        print(f"\n不可达的 IP ({len(unreachable)}):")
        for ip in sorted(unreachable, key=lambda x: int(ipaddress.ip_address(str(x))))[:20]:
            print(f"  ✗ {str(ip):15s}")
        if len(unreachable) > 20:
            print(f"  ... 还有 {len(unreachable) - 20} 个（详见日志文件）")

    # 写入日志
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    subnet_name = str(network).replace('/', '_')
    log_file = os.path.join(log_dir, f"ping_results_subnet_{subnet_name}.log")

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"总计统计信息:\n")
        f.write("-" * 40 + "\n")
        f.write(f"网段: {network}\n")
        f.write(f"测试来源: {source_ip}\n")
        f.write(f"总计ping的IP数量: {total}\n")
        f.write(f"总计可达IP数量: {len(reachable)}\n")
        f.write(f"总计不可达IP数量: {len(unreachable)}\n")
        f.write(f"延迟质量较差IP数量: {len(high_latency_ips)} (最大RTT > 1ms)\n")
        f.write("-" * 40 + "\n\n")

        if high_latency_ips:
            f.write(f"延迟质量分析:\n")
            f.write("-" * 40 + "\n")
            for ip, rtt_info in high_latency_ips:
                f.write(f"IP: {ip}\n")
                f.write(f"  最小延迟: {rtt_info['min']:.3f} ms\n")
                f.write(f"  平均延迟: {rtt_info['avg']:.3f} ms\n")
                f.write(f"  最大延迟: {rtt_info['max']:.3f} ms\n")
                f.write(f"  延迟抖动: {rtt_info['mdev']:.3f} ms\n")
                f.write("-" * 20 + "\n")
            f.write("\n")

        f.write(f"Ping测试详细信息:\n")
        f.write("-" * 40 + "\n")
        f.write(f"测试来源: {source_ip}\n")
        f.write("-" * 40 + "\n\n")

        if reachable:
            f.write(f"从 {source_ip} 可达的IP:\n\n")
            for ip in sorted(reachable, key=lambda x: int(ipaddress.ip_address(str(x)))):
                ip_str = str(ip)
                f.write(f"{ip_str}\n")
                f.write("-" * 40 + "\n")
                if ip_str in latency_analysis:
                    rtt = latency_analysis[ip_str]
                    f.write(f"延迟统计: min={rtt['min']:.3f}ms, "
                            f"avg={rtt['avg']:.3f}ms, "
                            f"max={rtt['max']:.3f}ms, "
                            f"mdev={rtt['mdev']:.3f}ms\n")
                    f.write("-" * 40 + "\n")
                f.write(ping_results.get(ip_str, ''))
                f.write("\n\n")

        if unreachable:
            f.write(f"\n从 {source_ip} 不可达的IP:\n\n")
            for ip in sorted(unreachable, key=lambda x: int(ipaddress.ip_address(str(x)))):
                ip_str = str(ip)
                f.write(f"{ip_str}\n")
                f.write("-" * 40 + "\n")
                f.write(ping_results.get(ip_str, ''))
                f.write("\n\n")

    print(f"\n详细结果已写入: {log_file}")
    print("程序执行完成！")


def ping_ip_planning_main():
    """IP 地址规划表 Ping 工具主程序"""
    parser = argparse.ArgumentParser(
        description='Ping IP 地址规划表中的设备',
        epilog="""
使用方法:
  网段模式（快速扫描）:
     ping-ip-planning 192.168.1.0/24
     ping-ip-planning 10.0.0.0/16
  
  交互式模式（无参数时自动进入）:
     ping-ip-planning
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 位置参数：网段（可选）
    parser.add_argument('subnet', nargs='?', default=None,
                        help='CIDR 网段，如 192.168.1.0/24')
    
    # 可选参数
    parser.add_argument('--color', '-c', choices=['green', 'none'],
                        help='过滤颜色: green=只 ping 绿色单元格, none=不过滤颜色')
    parser.add_argument('--no-exclude-strikethrough', action='store_true',
                        help='不排除删除线的 IP（默认会排除）')
    parser.add_argument('--list-colors', action='store_true',
                        help='列出 MGMT 列使用的所有颜色')
    parser.add_argument('--local', action='store_true',
                        help='强制使用本地 ping（不使用远程服务器）')
    parser.add_argument('--max-workers', type=int, default=None,
                        help='并发数（默认：本地30）')
    
    args = parser.parse_args()
    
    # 网段模式：直接 ping 整个网段
    if args.subnet:
        _ping_subnet_mode(args)
        return
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 进入交互式模式
    print("\n欢迎使用 IP 地址规划表 Ping 工具")
    print("=" * 70)
    
    # 第一步：选择环境（项目）
    file_path = None
    if config_manager.list_profiles():
        file_path = interactive_select_environment(config_manager)
    
    # 如果没有选择环境，进入手动输入模式
    if file_path is None:
        print("\n进入手动输入模式...")
        config = interactive_input_config()
        if config is None:
            print("已退出")
            return
    else:
        # 第二步：选择 Sheet（必选）
        sheet_name = interactive_select_sheet()
        if sheet_name is None:
            print("已退出")
            return
        
        # 第三步：选择列（server&security 需要选择）
        column = interactive_select_column(sheet_name)
        if column is None:
            print("已退出")
            return
        
        # 第四步：选择 ping 模式（server&security 需要）
        ping_mode = interactive_select_ping_mode(sheet_name)
        if ping_mode is None:
            print("已退出")
            return
        
        # 第五步：颜色过滤
        color_filter = interactive_select_color_filter()
        
        # 组装配置
        config = {
            'file': file_path,
            'sheet': sheet_name,
            'column': column,
            'color_filter': color_filter,
            'exclude_strikethrough': True,
            'use_local': not ping_mode.get('use_remote_server', False),
            'use_remote_server': ping_mode.get('use_remote_server', False),
            'server_identifier': ping_mode.get('server_identifier'),
            'max_workers': None
        }
    
    # 从配置中读取参数（命令行参数可以覆盖部分配置）
    if not config:
        print("错误: 未获取到配置信息")
        return
    
    file_path = config.get('file', 'pass/IP地址规划表-金茂1.xlsx')
    sheet_name = config.get('sheet', 'net&sec')
    column = config.get('column', 'MGMT')  # 从配置读取列名
    color_filter = args.color or config.get('color_filter', 'none')
    exclude_strikethrough = not args.no_exclude_strikethrough and config.get('exclude_strikethrough', True)
    use_local = args.local or config.get('use_local', True)
    max_workers = args.max_workers or config.get('max_workers')
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return
    
    # 如果只是列出颜色
    if args.list_colors:
        print(f"正在读取 {file_path} 的 {sheet_name} sheet 中 MGMT 列的颜色...")
        colors = list_available_colors(file_path, sheet_name, 'MGMT')
        if colors:
            print(f"\n找到 {len(colors)} 种颜色:")
            for color in colors:
                print(f"  - {color}")
        else:
            print("未找到任何颜色，或无法读取样式信息")
        return
    
    # 显示配置信息
    print()
    print("=" * 60)
    print(f"IP 地址规划表 Ping 工具")
    print("=" * 60)
    print(f"文件: {file_path}")
    print(f"Sheet: {sheet_name}")
    print(f"Ping 列: {column}")
    print(f"颜色过滤: {'绿色' if color_filter == 'green' else '无'}")
    print(f"排除删除线: {'是' if exclude_strikethrough else '否'}")
    print("=" * 60)
    print()
    
    # 读取 IP 地址
    try:
        ip_list = read_network_security_ips(
            file_path,
            sheet_name=sheet_name,
            ip_column=column,
            filter_color=color_filter if color_filter != 'none' else None,
            exclude_strikethrough=exclude_strikethrough
        )
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    if not ip_list:
        print("没有找到符合条件的 IP 地址")
        return
    
    print(f"\n找到 {len(ip_list)} 个 IP 地址:")
    for item in ip_list[:10]:  # 只显示前10个
        print(f"  - {item['ip']:15s} ({item['hostname']})")
    if len(ip_list) > 10:
        print(f"  ... 还有 {len(ip_list) - 10} 个")
    print()
    
    # 确定是否使用远程服务器
    server_ssh_pool = None
    source_ip = get_local_ip()
    
    # 检查是否从指定的服务器 ping（新功能）
    use_remote_server = config and config.get('use_remote_server', False)
    server_identifier = config and config.get('server_identifier')
    
    if use_remote_server and server_identifier:
        # 从 Excel 中查找服务器凭据
        print()
        print("=" * 60)
        print("正在查找服务器凭据...")
        print("=" * 60)
        try:
            server_creds = find_server_credentials(file_path, sheet_name, server_identifier)
            if server_creds:
                server_ip = server_creds['mgmt_ip']
                username = server_creds['username']
                password = server_creds['password']
                hostname = server_creds['hostname']
                
                print(f"服务器信息:")
                print(f"  主机名: {hostname}")
                print(f"  管理网IP: {server_ip}")
                print(f"  用户名: {username}")
                print()
                
                # 测试 SSH 连接
                print(f"正在测试服务器连接...")
                test_ssh = SSHClient(server_ip, username, password)
                if test_ssh.connect():
                    print(f"✓ 成功连接到服务器 {hostname} ({server_ip})")
                    test_ssh.close()
                    server_ssh_pool = SSHConnectionPool(server_ip, username, password)
                    source_ip = server_ip
                else:
                    print(f"✗ 无法连接到服务器 {hostname} ({server_ip})，将使用本地 ping")
            else:
                print(f"✗ 未找到服务器 '{server_identifier}'，将使用本地 ping")
        except Exception as e:
            print(f"查找服务器凭据时出错: {e}")
            import traceback
            traceback.print_exc()
            print("将使用本地 ping")
        print("=" * 60)
        print()
    
    # 显示测试来源
    if server_ssh_pool:
        print(f"测试来源: {source_ip} (远程)")
    else:
        print(f"测试来源: {source_ip} (本地)")
    
    # 确定并发数
    if max_workers is None:
        max_workers = 5 if server_ssh_pool else 20
    
    print(f"并发数: {max_workers}")
    print()
    
    # 开始 ping 测试
    reachable = []
    unreachable = []
    ping_results = {}
    
    print(f"开始 ping 测试...")
    print("-" * 60)
    
    completed = 0
    total = len(ip_list)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if server_ssh_pool:
            future_to_item = {
                executor.submit(ping_ip_remote, server_ssh_pool, item['ip']): item
                for item in ip_list
            }
        else:
            future_to_item = {
                executor.submit(ping_ip_local, item['ip']): item
                for item in ip_list
            }
        
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                ip, success, output = future.result()
                ping_results[ip] = output
                
                if success:
                    reachable.append(item)
                    print(f"✓ {ip:15s} ({item['hostname']:30s}) - 可达")
                else:
                    unreachable.append(item)
                    print(f"✗ {ip:15s} ({item['hostname']:30s}) - 不可达")
                
                completed += 1
                if total > 10:
                    progress = (completed / total) * 100
                    print(f"  进度: {completed}/{total} ({progress:.1f}%)")
            except Exception as e:
                print(f"✗ {item['ip']:15s} ({item['hostname']:30s}) - 异常: {e}")
                unreachable.append(item)
                completed += 1
    
    # 关闭连接池
    if server_ssh_pool:
        print("\nSSH 连接已关闭")
    
    # 分析延迟质量
    print("\n正在分析延迟质量...")
    latency_analysis = {}
    high_latency_ips = []
    
    for item in reachable:
        ip = item['ip']
        output = ping_results.get(ip, '')
        rtt_info = analyze_ping_output(output)
        if rtt_info:
            latency_analysis[ip] = rtt_info
            # 识别高延迟IP（最大RTT > 1ms）
            if rtt_info['max'] > 1.0:
                high_latency_ips.append((ip, item['hostname'], rtt_info))
    
    # 按最大延迟从高到低排序
    high_latency_ips.sort(key=lambda x: x[2]['max'], reverse=True)
    
    # 输出统计信息
    print()
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"总计 IP 数量: {total}")
    print(f"可达 IP 数量: {len(reachable)}")
    print(f"不可达 IP 数量: {len(unreachable)}")
    print(f"可达率: {len(reachable) / total * 100:.1f}%")
    print(f"延迟质量较差 IP 数量: {len(high_latency_ips)} (最大RTT > 1ms)")
    print("=" * 60)
    
    # 输出高延迟IP
    if high_latency_ips:
        print(f"\n延迟质量较差的 IP ({len(high_latency_ips)}):")
        print("（最大RTT > 1ms，按延迟从高到低排序）")
        for ip, hostname, rtt_info in high_latency_ips[:10]:  # 只显示前10个
            print(f"  ⚠ {ip:15s} ({hostname:30s})")
            print(f"     最小延迟: {rtt_info['min']:.3f} ms, "
                  f"平均延迟: {rtt_info['avg']:.3f} ms, "
                  f"最大延迟: {rtt_info['max']:.3f} ms")
        if len(high_latency_ips) > 10:
            print(f"  ... 还有 {len(high_latency_ips) - 10} 个（详见日志文件）")
    
    # 输出详细结果
    if reachable:
        print(f"\n可达的 IP ({len(reachable)}):")
        for item in reachable[:10]:  # 只显示前10个
            print(f"  ✓ {item['ip']:15s} ({item['hostname']})")
        if len(reachable) > 10:
            print(f"  ... 还有 {len(reachable) - 10} 个（详见日志文件）")
    
    if unreachable:
        print(f"\n不可达的 IP ({len(unreachable)}):")
        for item in unreachable:
            print(f"  ✗ {item['ip']:15s} ({item['hostname']})")
    
    # 写入日志文件
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ping_results_{sheet_name.replace('&', '_')}.log")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        # 总计统计信息
        f.write(f"总计统计信息:\n")
        f.write("-" * 40 + "\n")
        f.write(f"测试来源: {source_ip}\n")
        f.write(f"总计ping的IP数量: {total}\n")
        f.write(f"总计可达IP数量: {len(reachable)}\n")
        f.write(f"总计不可达IP数量: {len(unreachable)}\n")
        f.write(f"延迟质量较差IP数量: {len(high_latency_ips)} (最大RTT > 1ms)\n")
        f.write("-" * 40 + "\n\n")
        
        # 延迟质量分析
        if high_latency_ips:
            f.write(f"延迟质量分析:\n")
            f.write("-" * 40 + "\n")
            f.write(f"以下IP的最大响应时间超过1ms:\n\n")
            for ip, hostname, rtt_info in high_latency_ips:
                f.write(f"IP: {ip} - {hostname}\n")
                f.write(f"  最小延迟: {rtt_info['min']:.3f} ms\n")
                f.write(f"  平均延迟: {rtt_info['avg']:.3f} ms\n")
                f.write(f"  最大延迟: {rtt_info['max']:.3f} ms\n")
                f.write(f"  延迟抖动: {rtt_info['mdev']:.3f} ms\n")
                f.write("-" * 20 + "\n")
            f.write("\n")
        
        # Ping测试详细信息
        f.write(f"Ping测试详细信息:\n")
        f.write("-" * 40 + "\n")
        f.write(f"测试来源: {source_ip}\n")
        f.write("-" * 40 + "\n\n")
        
        if reachable:
            f.write(f"从 {source_ip} 可达的IP:\n\n")
            for item in reachable:
                f.write(f"{item['ip']} - {item['hostname']}\n")
                f.write("-" * 40 + "\n")
                # 添加延迟分析信息
                if item['ip'] in latency_analysis:
                    rtt_info = latency_analysis[item['ip']]
                    f.write(f"延迟统计: min={rtt_info['min']:.3f}ms, "
                           f"avg={rtt_info['avg']:.3f}ms, "
                           f"max={rtt_info['max']:.3f}ms, "
                           f"mdev={rtt_info['mdev']:.3f}ms\n")
                    f.write("-" * 40 + "\n")
                f.write(ping_results.get(item['ip'], ''))
                f.write("\n\n")
        
        if unreachable:
            f.write(f"\n从 {source_ip} 不可达的IP:\n\n")
            for item in unreachable:
                f.write(f"{item['ip']} - {item['hostname']}\n")
                f.write("-" * 40 + "\n")
                f.write(ping_results.get(item['ip'], ''))
                f.write("\n\n")
    
    print(f"\n详细结果已写入: {log_file}")
    print("程序执行完成！")


if __name__ == '__main__':
    ping_ip_planning_main()
