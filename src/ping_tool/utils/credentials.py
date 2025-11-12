"""
凭证管理模块
"""
import pandas as pd


def get_credentials(ip: str, credentials_file: str = 'pass/credentials.xlsx') -> dict:
    """
    从Excel文件中获取认证信息
    
    Args:
        ip: IP地址
        credentials_file: 凭证文件路径
        
    Returns:
        dict: 包含username、password、is_server的字典，失败返回None
    """
    try:
        df = pd.read_excel(credentials_file)
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

