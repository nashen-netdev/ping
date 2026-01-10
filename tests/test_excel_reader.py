"""
测试 Excel 读取模块
"""
import os
import pytest
from ping_tool.utils.excel_reader import (
    read_excel_with_calamine,
    read_network_security_ips,
    is_green_cell,
    list_available_colors
)


def test_read_excel_with_calamine():
    """测试使用 calamine 引擎读取 Excel"""
    # 这个测试需要实际的 Excel 文件
    # 在实际环境中运行
    pass


def test_is_green_cell():
    """测试绿色单元格判断"""
    # 测试已知的绿色
    assert is_green_cell({'fill_color': 'C6EFCE'}) == True
    assert is_green_cell({'fill_color': '00B050'}) == True
    
    # 测试非绿色
    assert is_green_cell({'fill_color': 'FF0000'}) == False
    assert is_green_cell({'fill_color': '0000FF'}) == False
    
    # 测试空值
    assert is_green_cell({}) == False
    assert is_green_cell({'fill_color': None}) == False
    assert is_green_cell(None) == False


def test_green_color_detection():
    """测试通用绿色检测算法"""
    # 测试 RGB 绿色检测
    # G > R 且 G > B 且 G > 100
    green_styles = [
        {'fill_color': '00FF00'},  # 纯绿色
        {'fill_color': '00AA00'},  # 深绿色
        {'fill_color': '50FF50'},  # 浅绿色
    ]
    
    for style in green_styles:
        assert is_green_cell(style) == True
    
    # 测试非绿色
    non_green_styles = [
        {'fill_color': 'FF0000'},  # 红色
        {'fill_color': '0000FF'},  # 蓝色
        {'fill_color': 'FFFF00'},  # 黄色
        {'fill_color': '808080'},  # 灰色
    ]
    
    for style in non_green_styles:
        assert is_green_cell(style) == False


def test_read_network_security_ips_structure():
    """测试返回数据结构"""
    # 这个测试需要模拟数据或实际文件
    # 验证返回的数据结构是否正确
    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
