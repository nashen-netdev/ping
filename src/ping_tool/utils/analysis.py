"""
延迟分析工具模块
"""


def analyze_ping_output(output: str) -> dict:
    """
    分析ping输出，提取RTT信息
    
    Args:
        output: ping命令的输出结果
        
    Returns:
        dict: 包含min/avg/max/mdev的延迟统计，失败返回None
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

