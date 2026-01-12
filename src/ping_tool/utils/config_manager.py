"""
配置管理模块
支持从 env/ 目录下的 YAML 文件读取和管理多个环境配置
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional, List


class ConfigManager:
    """配置管理器 - 从 env/ 目录加载环境配置"""
    
    def __init__(self, env_dir: str = None):
        """
        初始化配置管理器
        
        Args:
            env_dir: 环境配置目录路径，默认使用项目根目录下的 env/
        """
        if env_dir is None:
            # 默认环境配置目录
            project_root = Path(__file__).parent.parent.parent.parent
            env_dir = project_root / "env"
        
        self.env_dir = Path(env_dir)
        self.profiles = {}
        
        # 加载所有环境配置
        self.load_profiles()
    
    def load_profiles(self):
        """从 env/ 目录加载所有环境配置"""
        if not self.env_dir.exists():
            print(f"警告: 环境配置目录不存在: {self.env_dir}")
            return False
        
        try:
            # 扫描所有 .yaml 文件
            for yaml_file in self.env_dir.glob("*.yaml"):
                # 文件名（去除扩展名）作为环境 ID
                env_id = yaml_file.stem
                
                # 读取配置
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if config:
                            self.profiles[env_id] = config
                except Exception as e:
                    print(f"警告: 无法加载环境配置 {yaml_file}: {e}")
            
            return True
        except Exception as e:
            print(f"警告: 扫描环境配置目录失败 {self.env_dir}: {e}")
            return False
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """
        获取指定的配置
        
        Args:
            profile_name: 配置名称
            
        Returns:
            配置字典，如果不存在返回 None
        """
        return self.profiles.get(profile_name)
    
    def list_profiles(self) -> List[str]:
        """列出所有可用的配置名称"""
        return list(self.profiles.keys())
    
    def get_profile_info(self, profile_name: str) -> str:
        """
        获取配置的描述信息
        
        Args:
            profile_name: 配置名称
            
        Returns:
            配置的描述信息
        """
        profile = self.get_profile(profile_name)
        if profile:
            name = profile.get('name', profile_name)
            desc = profile.get('description', '无描述')
            return f"{name}: {desc}"
        return f"{profile_name}: 未找到"
    
    def profile_exists(self, profile_name: str) -> bool:
        """检查配置是否存在"""
        return profile_name in self.profiles
    
    def get_default_profile(self) -> Optional[Dict]:
        """获取默认配置"""
        return self.get_profile('default')


def interactive_select_environment(config_manager: ConfigManager) -> Optional[str]:
    """
    交互式选择环境（第一步：选择项目）
    
    Args:
        config_manager: 配置管理器
        
    Returns:
        Excel 文件路径，如果取消或选择手动输入返回 None
    """
    profiles = config_manager.list_profiles()
    
    if not profiles:
        print("没有找到任何配置环境")
        return None
    
    print("\n" + "=" * 70)
    print("可用的配置环境:")
    print("=" * 70)
    
    for i, profile_name in enumerate(profiles, 1):
        profile = config_manager.get_profile(profile_name)
        name = profile.get('name', profile_name)
        print(f"  {i}. {name}")
    
    print("=" * 70)
    
    while True:
        try:
            choice = input("\n请选择环境（输入序号，回车进入手动输入）: ").strip()
            
            # 回车进入手动输入模式
            if not choice:
                return None
            
            # 选择配置
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                profile_name = profiles[idx]
                profile = config_manager.get_profile(profile_name)
                file_path = profile.get('file')
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"✗ 错误: 文件不存在: {file_path}")
                    retry = input("  重新选择? (y/n) [y]: ").strip().lower()
                    if retry == 'n':
                        return None
                    continue
                
                print(f"✓ 已选择环境: {profile.get('name', profile_name)}")
                print(f"  文件: {file_path}")
                return file_path
            else:
                print(f"无效的选择，请输入 1-{len(profiles)}")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return None


def interactive_select_sheet() -> Optional[str]:
    """
    交互式选择 Sheet 页（第二步：必选）
    
    Returns:
        Sheet 名称，如果取消返回 None
    """
    print("\n" + "=" * 70)
    print("选择要测试的 Sheet 页:")
    print("=" * 70)
    print("  1. network&security")
    print("  2. server&security")
    print("=" * 70)
    
    while True:
        try:
            choice = input("\n请选择 Sheet（必选，输入 q 退出）: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice == '1':
                print("✓ 已选择: network&security")
                return "network&security"
            elif choice == '2':
                print("✓ 已选择: server&security")
                return "server&security"
            else:
                print("无效的选择，请输入 1 或 2")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return None


def interactive_select_column(sheet_name: str) -> Optional[str]:
    """
    交互式选择要 ping 的列
    
    Args:
        sheet_name: Sheet 名称
        
    Returns:
        列名: 'MGMT'、'管理网地址' 或 'IPMI'，如果取消返回 None
    """
    # network&security 固定使用 MGMT 列
    if sheet_name == "network&security":
        return "MGMT"
    
    # server&security 需要选择（只有管理网地址和 IPMI）
    print("\n" + "=" * 70)
    print("选择要 ping 的列:")
    print("=" * 70)
    print("  1. 管理网地址")
    print("  2. IPMI")
    print("=" * 70)
    
    while True:
        try:
            choice = input("\n请选择列（输入 q 退出）: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice == '1':
                print("✓ 已选择: 管理网地址")
                return "管理网地址"
            elif choice == '2':
                print("✓ 已选择: IPMI")
                return "IPMI"
            else:
                print("无效的选择，请输入 1 或 2")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return None


def interactive_select_color_filter() -> str:
    """
    交互式选择颜色过滤
    
    Returns:
        颜色过滤选项: 'green' 或 'none'
    """
    print("\n" + "=" * 70)
    print("颜色过滤设置:")
    print("=" * 70)
    
    while True:
        try:
            choice = input("是否只 ping 绿色单元格？(y/n) [n]: ").strip().lower()
            
            if not choice or choice == 'n':
                print("✓ 不过滤颜色，ping 所有设备")
                return 'none'
            elif choice == 'y':
                print("✓ 只 ping 绿色单元格")
                return 'green'
            else:
                print("请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return 'none'


def interactive_select_ping_mode(sheet_name: str) -> Optional[Dict]:
    """
    交互式选择 ping 模式（仅 server&security 需要）
    
    Args:
        sheet_name: Sheet 名称
        
    Returns:
        dict: ping 模式配置
            {
                'use_remote_server': bool,  # 是否从服务器ping
                'server_identifier': str    # 服务器标识（hostname或IP）
            }
        如果取消返回 None
    """
    # 只有 server&security 需要选择 ping 模式
    if sheet_name != "server&security":
        return {
            'use_remote_server': False,
            'server_identifier': None
        }
    
    print("\n" + "=" * 70)
    print("Ping 模式选择:")
    print("=" * 70)
    print("  1. 从本地 ping（默认）")
    print("  2. 从服务器 ping（登录到某台服务器后 ping 其他设备）")
    print("=" * 70)
    
    while True:
        try:
            choice = input("\n请选择 Ping 模式（输入 q 退出）[1]: ").strip()
            
            # 默认选择本地 ping
            if not choice:
                choice = '1'
            
            if choice.lower() == 'q':
                return None
            
            if choice == '1':
                print("✓ 已选择: 从本地 ping")
                return {
                    'use_remote_server': False,
                    'server_identifier': None
                }
            elif choice == '2':
                # 从服务器 ping，需要输入服务器标识
                print("✓ 已选择: 从服务器 ping")
                print()
                print("请输入要登录的服务器信息（hostname 或管理网IP地址）")
                print("提示: 脚本将在 Excel 中查找该服务器并使用其 System User/Password 登录")
                
                while True:
                    server_id = input("\n服务器标识（hostname或IP）: ").strip()
                    
                    if not server_id:
                        print("✗ 请输入服务器标识")
                        continue
                    
                    if server_id.lower() == 'q':
                        return None
                    
                    print(f"✓ 将从服务器 '{server_id}' ping 其他设备")
                    return {
                        'use_remote_server': True,
                        'server_identifier': server_id
                    }
            else:
                print("无效的选择，请输入 1 或 2")
        except KeyboardInterrupt:
            print("\n\n已取消")
            return None


def interactive_input_config() -> Optional[Dict]:
    """
    交互式输入配置信息（手动输入模式）
    
    Returns:
        配置字典，如果取消返回 None
    """
    print()
    print("=" * 70)
    print("手动输入模式")
    print("=" * 70)
    print("提示: 输入 'q' 或 Ctrl+C 可随时退出")
    print()
    
    try:
        # 1. 文件路径（必须输入，无默认值）
        while True:
            file_path = input("Excel 文件路径: ").strip()
            if file_path.lower() == 'q':
                return None
            
            if not file_path:
                print("✗ 请输入文件路径")
                continue
            
            # 展开 ~ 符号并检查文件是否存在
            file_path = os.path.expanduser(file_path)
            
            if os.path.exists(file_path):
                print(f"✓ 文件存在: {file_path}")
                break
            else:
                print(f"✗ 文件不存在: {file_path}")
                retry = input("  重新输入? (y/n) [y]: ").strip().lower()
                if retry == 'n':
                    return None
        
        # 2. Sheet 页（二选一）
        print()
        print("=" * 70)
        print("选择要测试的 Sheet 页:")
        print("=" * 70)
        print("  1. network&security（网络和安全）")
        print("  2. server&security（服务器和安全）")
        print("=" * 70)
        
        while True:
            choice = input("\n请选择 Sheet（输入 q 退出）: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if choice == '1':
                sheet = "network&security"
                print("✓ 已选择: network&security")
                break
            elif choice == '2':
                sheet = "server&security"
                print("✓ 已选择: server&security")
                break
            else:
                print("无效的选择，请输入 1 或 2")
        
        # 3. 选择列（server&security 需要选择，network&security 自动 MGMT）
        column = interactive_select_column(sheet)
        if column is None:
            return None
        
        # 4. 颜色过滤
        color_filter = interactive_select_color_filter()
        if color_filter is None:
            return None
        
        # 5. 排除删除线 - 默认排除，不询问
        exclude_strikethrough = True
        
        # 6. 本地 ping - 统一使用本地 ping
        use_local = True
        print(f"✓ {sheet} 使用本地 ping")
        
        # 7. 并发数 - 自动设置，不询问
        max_workers = None
        
        # 直接返回配置，不需要确认（与环境模式保持一致）
        print()
        
        return {
            'name': '手动输入配置',
            'description': '用户手动输入的配置',
            'file': file_path,
            'sheet': sheet,
            'column': column,
            'color_filter': color_filter,
            'exclude_strikethrough': exclude_strikethrough,
            'use_local': use_local,
            'max_workers': max_workers
        }
        
    except KeyboardInterrupt:
        print("\n\n已取消")
        return None
    except Exception as e:
        print(f"\n错误: {e}")
        return None
