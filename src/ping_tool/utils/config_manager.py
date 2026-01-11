"""
配置管理模块
支持从 YAML 配置文件读取和管理多个配置环境（profile）
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional, List


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认使用 configs/ip_planning_profiles.yaml
        """
        if config_file is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent.parent
            config_file = project_root / "configs" / "ip_planning_profiles.yaml"
        
        self.config_file = Path(config_file)
        self.profiles = {}
        
        if self.config_file.exists():
            self.load_profiles()
    
    def load_profiles(self):
        """从 YAML 文件加载所有配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.profiles = yaml.safe_load(f) or {}
            return True
        except Exception as e:
            print(f"警告: 无法加载配置文件 {self.config_file}: {e}")
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
    print("  1. network&security（网络和安全）")
    print("  2. server&security（服务器和安全）")
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


def interactive_select_color_filter() -> str:
    """
    交互式选择颜色过滤（第三步）
    
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


def interactive_input_config() -> Optional[Dict]:
    """
    交互式输入配置信息
    
    Returns:
        配置字典，如果取消返回 None
    """
    print()
    print("=" * 70)
    print("交互式配置")
    print("=" * 70)
    print("提示: 直接回车使用默认值，输入 'q' 或 Ctrl+C 退出")
    print()
    
    try:
        # 1. 文件路径
        while True:
            file_path = input("Excel 文件路径 [pass/IP地址规划表-金茂1.xlsx]: ").strip()
            if file_path.lower() == 'q':
                return None
            
            if not file_path:
                file_path = "pass/IP地址规划表-金茂1.xlsx"
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                print(f"✓ 文件存在: {file_path}")
                break
            else:
                print(f"✗ 文件不存在: {file_path}")
                retry = input("  重新输入? (y/n) [y]: ").strip().lower()
                if retry == 'n':
                    return None
        
        # 2. Sheet 页
        sheet = input("Sheet 页名称 [net&sec]: ").strip()
        if sheet.lower() == 'q':
            return None
        if not sheet:
            sheet = "net&sec"
        
        # 3. 颜色过滤
        color = input("颜色过滤 (green/none) [none]: ").strip().lower()
        if color == 'q':
            return None
        if not color or color not in ['green', 'none']:
            color = 'none'
        
        # 4. 排除删除线
        exclude = input("排除删除线的 IP? (y/n) [y]: ").strip().lower()
        if exclude == 'q':
            return None
        exclude_strikethrough = exclude != 'n'
        
        # 5. 本地 ping
        local = input("使用本地 ping? (y/n) [n]: ").strip().lower()
        if local == 'q':
            return None
        use_local = local == 'y'
        
        # 6. 并发数
        workers = input("并发数 (留空自动) [auto]: ").strip()
        if workers.lower() == 'q':
            return None
        
        max_workers = None
        if workers and workers.isdigit():
            max_workers = int(workers)
        
        print()
        print("=" * 70)
        print("配置确认:")
        print("=" * 70)
        print(f"  文件: {file_path}")
        print(f"  Sheet: {sheet}")
        print(f"  颜色过滤: {color}")
        print(f"  排除删除线: {'是' if exclude_strikethrough else '否'}")
        print(f"  本地 ping: {'是' if use_local else '否'}")
        print(f"  并发数: {max_workers if max_workers else '自动'}")
        print("=" * 70)
        
        confirm = input("\n确认以上配置? (y/n) [y]: ").strip().lower()
        if confirm == 'n':
            print("已取消")
            return None
        
        return {
            'name': '交互式配置',
            'description': '用户手动输入的配置',
            'file': file_path,
            'sheet': sheet,
            'color_filter': color,
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
