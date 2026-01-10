"""
IP 地址规划表 Ping 工具 CLI
专门用于 ping IP 地址规划表中的设备
"""
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .core.ping import ping_ip_local, ping_ip_remote
from .core.ssh import SSHClient, SSHConnectionPool
from .utils.credentials import get_credentials
from .utils.network import get_local_ip
from .utils.excel_reader import read_network_security_ips, list_available_colors


def ping_ip_planning_main():
    """IP 地址规划表 Ping 工具主程序"""
    parser = argparse.ArgumentParser(description='Ping IP 地址规划表中的设备')
    parser.add_argument('--file', '-f', default='pass/IP地址规划表-金茂.xlsx',
                        help='IP 地址规划表文件路径')
    parser.add_argument('--sheet', '-s', default='net&sec',
                        help='Sheet 页名称，可选: net&sec, 服务器&安全')
    parser.add_argument('--color', '-c', choices=['green', 'none'], default='none',
                        help='过滤颜色: green=只 ping 绿色单元格, none=不过滤颜色')
    parser.add_argument('--no-exclude-strikethrough', action='store_true',
                        help='不排除删除线的 IP（默认会排除）')
    parser.add_argument('--list-colors', action='store_true',
                        help='列出 MGMT 列使用的所有颜色')
    parser.add_argument('--local', action='store_true',
                        help='强制使用本地 ping（不使用远程服务器）')
    parser.add_argument('--max-workers', type=int, default=None,
                        help='并发数（默认：远程5，本地20）')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误: 文件不存在: {args.file}")
        return
    
    # 如果只是列出颜色
    if args.list_colors:
        print(f"正在读取 {args.file} 的 {args.sheet} sheet 中 MGMT 列的颜色...")
        colors = list_available_colors(args.file, args.sheet, 'MGMT')
        if colors:
            print(f"\n找到 {len(colors)} 种颜色:")
            for color in colors:
                print(f"  - {color}")
        else:
            print("未找到任何颜色，或无法读取样式信息")
        return
    
    # 交互式选择是否过滤颜色
    if args.color == 'none':
        user_input = input("是否只 ping 绿色单元格？(y/n，默认 n): ").strip().lower()
        if user_input == 'y':
            args.color = 'green'
    
    # 设置过滤参数
    filter_color = args.color if args.color != 'none' else None
    exclude_strikethrough = not args.no_exclude_strikethrough
    
    print("\n" + "=" * 60)
    print(f"IP 地址规划表 Ping 工具")
    print("=" * 60)
    print(f"文件: {args.file}")
    print(f"Sheet: {args.sheet}")
    print(f"颜色过滤: {'绿色' if filter_color == 'green' else '无'}")
    print(f"排除删除线: {'是' if exclude_strikethrough else '否'}")
    print("=" * 60)
    print()
    
    # 读取 IP 地址
    try:
        ip_list = read_network_security_ips(
            args.file,
            filter_color=filter_color,
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
    
    if not args.local:
        # 尝试从 credentials.xlsx 中查找服务器
        try:
            import pandas as pd
            creds_file = 'pass/credentials.xlsx'
            if os.path.exists(creds_file):
                df = pd.read_excel(creds_file)
                server_ips = []
                for ip in df['IP'].tolist():
                    creds = get_credentials(ip)
                    if creds and creds.get('is_server'):
                        server_ips.append(ip)
                
                if server_ips:
                    server_ip = server_ips[0]
                    server_credentials = get_credentials(server_ip)
                    print(f"找到服务器: {server_ip}")
                    
                    # 创建 SSH 连接池
                    username = server_credentials['username']
                    password = server_credentials['password']
                    key_file = os.path.join('./pass/key', username) if not password else None
                    
                    print(f"正在测试服务器连接...")
                    test_ssh = SSHClient(server_ip, username, password, key_file)
                    if test_ssh.connect():
                        print(f"成功连接到服务器，将使用远程 ping")
                        test_ssh.close()
                        server_ssh_pool = SSHConnectionPool(server_ip, username, password, key_file)
                        source_ip = server_ip
                    else:
                        print(f"无法连接到服务器，将使用本地 ping")
        except Exception as e:
            print(f"查找服务器时出错: {e}")
    
    if server_ssh_pool:
        print(f"测试来源: {source_ip} (远程)")
    else:
        print(f"测试来源: {source_ip} (本地)")
    
    # 确定并发数
    if args.max_workers is None:
        max_workers = 5 if server_ssh_pool else 20
    else:
        max_workers = args.max_workers
    
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
    
    # 输出统计信息
    print()
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"总计 IP 数量: {total}")
    print(f"可达 IP 数量: {len(reachable)}")
    print(f"不可达 IP 数量: {len(unreachable)}")
    print(f"可达率: {len(reachable) / total * 100:.1f}%")
    print("=" * 60)
    
    # 输出详细结果
    if reachable:
        print(f"\n可达的 IP ({len(reachable)}):")
        for item in reachable:
            print(f"  ✓ {item['ip']:15s} ({item['hostname']})")
    
    if unreachable:
        print(f"\n不可达的 IP ({len(unreachable)}):")
        for item in unreachable:
            print(f"  ✗ {item['ip']:15s} ({item['hostname']})")
    
    # 写入日志文件
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"ping_results_{args.sheet.replace('&', '_')}.log")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"IP 地址规划表 Ping 测试结果\n")
        f.write("=" * 60 + "\n")
        f.write(f"文件: {args.file}\n")
        f.write(f"Sheet: {args.sheet}\n")
        f.write(f"测试来源: {source_ip}\n")
        f.write(f"颜色过滤: {'绿色' if filter_color == 'green' else '无'}\n")
        f.write(f"排除删除线: {'是' if exclude_strikethrough else '否'}\n")
        f.write(f"总计 IP: {total}\n")
        f.write(f"可达 IP: {len(reachable)}\n")
        f.write(f"不可达 IP: {len(unreachable)}\n")
        f.write(f"可达率: {len(reachable) / total * 100:.1f}%\n")
        f.write("=" * 60 + "\n\n")
        
        if reachable:
            f.write(f"可达的 IP ({len(reachable)}):\n")
            f.write("-" * 60 + "\n")
            for item in reachable:
                f.write(f"\n{item['ip']} - {item['hostname']}\n")
                f.write("-" * 40 + "\n")
                f.write(ping_results.get(item['ip'], ''))
                f.write("\n")
        
        if unreachable:
            f.write(f"\n不可达的 IP ({len(unreachable)}):\n")
            f.write("-" * 60 + "\n")
            for item in unreachable:
                f.write(f"\n{item['ip']} - {item['hostname']}\n")
                f.write("-" * 40 + "\n")
                f.write(ping_results.get(item['ip'], ''))
                f.write("\n")
    
    print(f"\n详细结果已写入: {log_file}")
    print("程序执行完成！")


if __name__ == '__main__':
    ping_ip_planning_main()
