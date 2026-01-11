"""
环境配置快速创建工具
用于快速创建新的项目环境配置文件
"""
import os
import sys
import yaml
import argparse
from pathlib import Path


def create_env_config(env_id: str, file_path: str, display_name: str = None) -> bool:
    """
    创建环境配置文件
    
    Args:
        env_id: 环境 ID（文件名）
        file_path: Excel 文件路径
        display_name: 显示名称（可选，默认使用 env_id）
        
    Returns:
        是否创建成功
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    env_dir = project_root / "env"
    
    # 确保 env 目录存在
    env_dir.mkdir(exist_ok=True)
    
    # 目标文件路径
    env_file = env_dir / f"{env_id}.yaml"
    
    # 检查环境是否已存在
    if env_file.exists():
        print(f"❌ 错误: 环境 '{env_id}' 已存在")
        print(f"   文件: {env_file}")
        overwrite = input("是否覆盖？(y/n) [n]: ").strip().lower()
        if overwrite != 'y':
            print("已取消")
            return False
    
    # 检查 Excel 文件是否存在
    file_path = os.path.expanduser(file_path)  # 展开 ~ 符号
    if not os.path.exists(file_path):
        print(f"⚠️  警告: Excel 文件不存在: {file_path}")
        proceed = input("是否继续创建配置？(y/n) [y]: ").strip().lower()
        if proceed == 'n':
            print("已取消")
            return False
    
    # 确定显示名称
    if display_name is None:
        display_name = env_id
    
    # 创建配置内容
    config = {
        'name': display_name,
        'file': file_path
    }
    
    # 写入文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"# {display_name} 项目环境配置\n")
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        print()
        print("=" * 70)
        print(f"✅ 成功创建环境配置: {env_id}")
        print("=" * 70)
        print(f"  环境 ID: {env_id}")
        print(f"  显示名称: {display_name}")
        print(f"  文件路径: {file_path}")
        print(f"  配置文件: {env_file}")
        print("=" * 70)
        print()
        print("💡 使用方法:")
        print(f"  ping-ip-planning           # 交互式选择，可以看到新环境")
        print(f"  ping-ip-planning --list-profiles  # 列出所有环境")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False


def main():
    """主程序"""
    parser = argparse.ArgumentParser(
        description='快速创建 IP 地址规划表环境配置',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本用法
  ping-env-add bj08 /Users/sen/Desktop/IP地址规划表-金茂1.xlsx
  
  # 指定显示名称
  ping-env-add bj08 /path/to/file.xlsx --display-name "北京08机房"
  
  # 创建后查看所有环境
  ping-env-add myproject ~/file.xlsx && ping-ip-planning --list-profiles

配置文件会保存到项目的 env/ 目录下。
        """
    )
    
    parser.add_argument('env_id', 
                        help='环境 ID（使用英文、数字、下划线）')
    parser.add_argument('file_path', 
                        help='Excel 文件路径')
    parser.add_argument('--display-name', '-n', 
                        help='显示名称（可选，默认使用环境 ID）')
    
    args = parser.parse_args()
    
    # 验证 env_id 格式
    if not args.env_id.replace('_', '').replace('-', '').isalnum():
        print("❌ 错误: 环境 ID 只能包含字母、数字、下划线和连字符")
        return 1
    
    # 创建配置
    success = create_env_config(
        args.env_id, 
        args.file_path,
        args.display_name
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
