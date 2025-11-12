"""
SSH 连接管理模块
"""
import time
import logging
import paramiko


# 禁用paramiko的详细日志输出
logging.getLogger("paramiko").setLevel(logging.ERROR)


class SSHClient:
    """SSH客户端封装"""
    
    def __init__(self, hostname: str, username: str, password: str = None, key_file: str = None):
        """
        初始化SSH客户端
        
        Args:
            hostname: 主机地址
            username: 用户名
            password: 密码（可选）
            key_file: 密钥文件路径（可选）
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None

    def connect(self) -> bool:
        """
        建立SSH连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.password:
                self.client.connect(
                    self.hostname, 
                    username=self.username, 
                    password=self.password, 
                    timeout=10
                )
            else:
                key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client.connect(
                    self.hostname, 
                    username=self.username, 
                    pkey=key, 
                    timeout=10
                )
            return True
        except Exception as e:
            print(f"连接失败 {self.hostname}: {str(e)}")
            return False

    def execute_command(self, command: str, timeout: int = 30) -> str:
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            str: 命令输出结果
        """
        if not self.client:
            return None
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            return stdout.read().decode()
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
            return None

    def close(self):
        """关闭SSH连接"""
        if self.client:
            self.client.close()


class SSHConnectionPool:
    """SSH连接池，用于并发场景下管理多个SSH连接"""
    
    def __init__(
        self, 
        hostname: str, 
        username: str, 
        password: str = None, 
        key_file: str = None, 
        max_retries: int = 2
    ):
        """
        初始化SSH连接池
        
        Args:
            hostname: 主机地址
            username: 用户名
            password: 密码（可选）
            key_file: 密钥文件路径（可选）
            max_retries: 最大重试次数
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_file = key_file
        self.max_retries = max_retries
        # 禁用paramiko的日志输出，减少错误信息
        logging.getLogger("paramiko").setLevel(logging.WARNING)
    
    def create_connection(self, retry_count: int = 0):
        """
        创建一个新的SSH连接，带重试机制
        
        Args:
            retry_count: 当前重试次数
            
        Returns:
            SSHClient: SSH客户端实例或None
        """
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
    
    def execute_command_with_new_connection(self, command: str, timeout: int = 30) -> str:
        """
        使用新连接执行命令，执行完成后关闭连接
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            str: 命令输出结果
        """
        ssh = self.create_connection()
        if not ssh:
            return None
        try:
            result = ssh.execute_command(command, timeout)
            return result
        finally:
            ssh.close()

