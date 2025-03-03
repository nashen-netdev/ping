import os
import subprocess
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from subprocess import TimeoutExpired

def ping_ip(ip):
    """
    Ping 单个 IP 地址，返回是否可达
    """
    try:
        result = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        return ip, result.returncode == 0
    except TimeoutExpired:
        return ip, False
    except Exception:
        return ip, False

def ping_network(network, max_workers=20):
    """
    Ping 一个 IP 网段中的所有 IP 地址，使用多线程并发
    """
    reachable_ips = []
    unreachable_ips = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(ping_ip, str(ip)): ip for ip in network.hosts()}
        for future in as_completed(future_to_ip):
            ip, success = future.result()
            if success:
                reachable_ips.append(ip)
            else:
                unreachable_ips.append(ip)

    return reachable_ips, unreachable_ips

def main():
    # 设置路径
    address_dir = "./address"
    log_dir = "./log"
    os.makedirs(log_dir, exist_ok=True)

    for filename in os.listdir(address_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(address_dir, filename)
            log_file_path = os.path.join(log_dir, f"log_{filename}")

            # 用于缓存单个 IP 和网段的结果
            single_reachable = []
            single_unreachable = []
            networks_summary = []

            with open(file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        if '/' in line:
                            # 对整个网段进行 ping
                            network = ipaddress.ip_network(line, strict=False)
                            reachable, unreachable = ping_network(network)
                            networks_summary.append({
                                "network": line,
                                "reachable": reachable,
                                "unreachable": unreachable
                            })
                        else:
                            # 对单个 IP 进行 ping
                            ip = ipaddress.ip_address(line)
                            _, success = ping_ip(str(ip))
                            if success:
                                single_reachable.append(line)
                            else:
                                single_unreachable.append(line)
                    except ValueError:
                        continue

            # 写入日志文件
            with open(log_file_path, "w") as log_file:
                # 写单个 IP 的结果
                if single_reachable:
                    log_file.write("reachable\n")
                    log_file.write("\n".join(single_reachable) + "\n\n")

                if single_unreachable:
                    log_file.write("unreachable\n")
                    log_file.write("\n".join(single_unreachable) + "\n\n")

                # 写网段的结果
                for summary in networks_summary:
                    log_file.write("------------------------------------\n")
                    log_file.write(f"{summary['network']}\n\n")
                    log_file.write(f"reachable: {len(summary['reachable'])}\n")
                    log_file.write("\n".join(summary['reachable']) + "\n")
                    log_file.write("-----------------------------------\n\n")
                    log_file.write(f"Unreachable: {len(summary['unreachable'])}\n")
                    log_file.write("\n".join(summary['unreachable']) + "\n")
                    log_file.write("----------------------------------\n\n")

                # 写总计
                total_pinged = len(single_reachable) + len(single_unreachable) + \
                               sum(len(summary["reachable"]) + len(summary["unreachable"]) for summary in networks_summary)
                total_reachable = len(single_reachable) + sum(len(summary["reachable"]) for summary in networks_summary)
                total_unreachable = len(single_unreachable) + sum(len(summary["unreachable"]) for summary in networks_summary)

                log_file.write(f"Total pinged IPs: {total_pinged}\n")
                log_file.write(f"Total reachable IPs: {total_reachable}\n")
                log_file.write(f"Total unreachable IPs: {total_unreachable}\n")

            print(f"Results written to: {log_file_path}")

if __name__ == "__main__":
    main()