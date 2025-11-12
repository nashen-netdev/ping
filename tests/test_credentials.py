"""
测试凭证管理模块
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from ping_tool.utils.credentials import get_credentials


class TestCredentials:
    """测试凭证管理功能"""
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_success(self, mock_read_excel):
        """测试成功获取凭证"""
        # 模拟Excel数据
        mock_df = pd.DataFrame({
            'IP': ['192.168.1.1', '192.168.1.2'],
            'user': ['root', 'admin'],
            'pass': ['password123', 'pass456'],
            'server': [1, 0]
        })
        mock_read_excel.return_value = mock_df
        
        result = get_credentials('192.168.1.1')
        
        assert result is not None
        assert result['username'] == 'root'
        assert result['password'] == 'password123'
        assert result['is_server'] is True
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_with_integer_password(self, mock_read_excel):
        """测试整数密码自动转换"""
        # 模拟Excel中密码为整数
        mock_df = pd.DataFrame({
            'IP': ['192.168.1.1'],
            'user': ['root'],
            'pass': [123456.0],  # Excel可能将整数存为浮点数
            'server': [0]
        })
        mock_read_excel.return_value = mock_df
        
        result = get_credentials('192.168.1.1')
        
        assert result is not None
        assert result['password'] == '123456'  # 去除.0后缀
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_with_null_password(self, mock_read_excel):
        """测试空密码处理"""
        # 模拟Excel中密码为空
        mock_df = pd.DataFrame({
            'IP': ['192.168.1.1'],
            'user': ['admin'],
            'pass': [None],
            'server': [0]
        })
        mock_read_excel.return_value = mock_df
        
        result = get_credentials('192.168.1.1')
        
        assert result is not None
        assert result['password'] is None
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_no_server_column(self, mock_read_excel):
        """测试没有server列的情况"""
        # 模拟Excel没有server列
        mock_df = pd.DataFrame({
            'IP': ['192.168.1.1'],
            'user': ['root'],
            'pass': ['password']
        })
        mock_read_excel.return_value = mock_df
        
        result = get_credentials('192.168.1.1')
        
        assert result is not None
        assert result['is_server'] is False  # 默认值
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_ip_not_found(self, mock_read_excel):
        """测试IP不存在的情况"""
        mock_df = pd.DataFrame({
            'IP': ['192.168.1.1'],
            'user': ['root'],
            'pass': ['password'],
            'server': [0]
        })
        mock_read_excel.return_value = mock_df
        
        result = get_credentials('192.168.1.999')
        
        assert result is None
    
    @patch('ping_tool.utils.credentials.pd.read_excel')
    def test_get_credentials_file_not_found(self, mock_read_excel):
        """测试文件不存在的情况"""
        mock_read_excel.side_effect = FileNotFoundError("File not found")
        
        result = get_credentials('192.168.1.1')
        
        assert result is None

