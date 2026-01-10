"""
Excel 文件读取模块，支持读取单元格格式（颜色、删除线等）
"""
import pandas as pd
import openpyxl
from typing import Optional, Dict, List, Tuple
from openpyxl.styles import Font
from openpyxl.styles.fills import PatternFill


def read_excel_data_only(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    读取 Excel 文件数据
    
    Args:
        file_path: Excel 文件路径
        sheet_name: sheet 页名称
        
    Returns:
        pd.DataFrame: 数据框
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
        return df
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        raise


def get_cell_style_info(file_path: str, sheet_name: str, row_idx: int, col_idx: int) -> Dict:
    """
    获取单元格的样式信息（颜色、删除线等）
    注意：此函数可能因为 Excel 文件格式问题而失败
    
    Args:
        file_path: Excel 文件路径
        sheet_name: sheet 页名称
        row_idx: 行索引（从1开始）
        col_idx: 列索引（从1开始）
        
    Returns:
        dict: 包含样式信息的字典
            {
                'fill_color': 'RRGGBB' or None,
                'font_strikethrough': bool,
                'font_color': 'RRGGBB' or None
            }
    """
    try:
        # 尝试只读取样式信息
        wb = openpyxl.load_workbook(file_path, data_only=False, keep_vba=False)
        ws = wb[sheet_name]
        cell = ws.cell(row=row_idx, column=col_idx)
        
        style_info = {
            'fill_color': None,
            'font_strikethrough': False,
            'font_color': None
        }
        
        # 获取填充颜色
        if cell.fill and cell.fill.patternType:
            if hasattr(cell.fill, 'fgColor') and cell.fill.fgColor:
                if hasattr(cell.fill.fgColor, 'rgb') and cell.fill.fgColor.rgb:
                    # 去掉透明度通道（前两位）
                    style_info['fill_color'] = str(cell.fill.fgColor.rgb)[-6:]
        
        # 获取字体样式
        if cell.font:
            style_info['font_strikethrough'] = bool(cell.font.strike)
            if hasattr(cell.font, 'color') and cell.font.color:
                if hasattr(cell.font.color, 'rgb') and cell.font.color.rgb:
                    style_info['font_color'] = str(cell.font.color.rgb)[-6:]
        
        wb.close()
        return style_info
    except Exception as e:
        # 如果读取样式失败，返回默认值
        return {
            'fill_color': None,
            'font_strikethrough': False,
            'font_color': None
        }


def get_sheet_style_map(file_path: str, sheet_name: str, max_rows: int = 1000) -> Dict[Tuple[int, int], Dict]:
    """
    批量获取整个 sheet 的样式信息（优化性能）
    
    Args:
        file_path: Excel 文件路径
        sheet_name: sheet 页名称
        max_rows: 最大读取行数
        
    Returns:
        dict: {(row, col): style_info}
    """
    style_map = {}
    try:
        wb = openpyxl.load_workbook(file_path, data_only=False, keep_vba=False)
        ws = wb[sheet_name]
        
        for row_idx, row in enumerate(ws.iter_rows(max_row=max_rows), 1):
            for col_idx, cell in enumerate(row, 1):
                style_info = {
                    'fill_color': None,
                    'font_strikethrough': False,
                    'font_color': None
                }
                
                # 获取填充颜色
                if cell.fill and cell.fill.patternType:
                    if hasattr(cell.fill, 'fgColor') and cell.fill.fgColor:
                        if hasattr(cell.fill.fgColor, 'rgb') and cell.fill.fgColor.rgb:
                            style_info['fill_color'] = str(cell.fill.fgColor.rgb)[-6:]
                
                # 获取字体样式
                if cell.font:
                    style_info['font_strikethrough'] = bool(cell.font.strike)
                    if hasattr(cell.font, 'color') and cell.font.color:
                        if hasattr(cell.font.color, 'rgb') and cell.font.color.rgb:
                            style_info['font_color'] = str(cell.font.color.rgb)[-6:]
                
                # 只存储有样式的单元格
                if any(style_info.values()):
                    style_map[(row_idx, col_idx)] = style_info
        
        wb.close()
        print(f"成功读取 {len(style_map)} 个有样式的单元格")
    except Exception as e:
        print(f"警告: 无法读取单元格样式信息: {e}")
        print("将跳过颜色和删除线过滤功能")
    
    return style_map


def is_green_cell(style_info: Dict) -> bool:
    """
    判断单元格是否为绿色
    
    Args:
        style_info: 样式信息字典
        
    Returns:
        bool: 是否为绿色单元格
    """
    if not style_info or not style_info.get('fill_color'):
        return False
    
    color = style_info['fill_color'].upper()
    # 常见的绿色值（可以根据实际情况调整）
    green_colors = [
        'C6EFCE',  # 浅绿色
        '00B050',  # Excel 标准绿色
        '92D050',  # 亮绿色
        'E2EFDA',  # 很浅的绿色
        '70AD47',  # 深绿色
    ]
    
    # 检查是否匹配已知的绿色
    for green in green_colors:
        if color == green:
            return True
    
    # 通用绿色检测：R 分量小，G 分量大
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        # 绿色的特征：G > R 且 G > B
        if g > r and g > b and g > 100:
            return True
    except:
        pass
    
    return False


def read_network_security_ips(file_path: str, 
                               filter_color: Optional[str] = None,
                               exclude_strikethrough: bool = True) -> List[Dict]:
    """
    从 net&sec sheet 读取网络和安全设备的 IP 地址和 hostname
    
    Args:
        file_path: Excel 文件路径
        filter_color: 过滤颜色，'green' 表示只读取绿色单元格，None 表示不过滤
        exclude_strikethrough: 是否排除删除线单元格
        
    Returns:
        list: [{'ip': '...', 'hostname': '...', 'row': ...}, ...]
    """
    sheet_name = 'net&sec'
    
    # 使用多种方式尝试读取数据
    print(f"正在读取 {file_path} 的 {sheet_name} sheet...")
    df = read_excel_data_only(file_path, sheet_name)
    
    # 查找表头行（包含 MGMT 和 hostname）
    header_row_idx = None
    mgmt_col_idx = None
    hostname_col_idx = None
    
    for idx, row in df.iterrows():
        row_values = [str(x).strip() if pd.notna(x) else '' for x in row.values]
        if 'MGMT' in row_values and 'hostname' in row_values:
            header_row_idx = idx
            mgmt_col_idx = row_values.index('MGMT')
            hostname_col_idx = row_values.index('hostname')
            print(f"找到表头行: 第{header_row_idx}行")
            print(f"MGMT 列索引: {mgmt_col_idx}, hostname 列索引: {hostname_col_idx}")
            break
    
    if header_row_idx is None:
        raise ValueError(f"在 {sheet_name} sheet 中未找到包含 'MGMT' 和 'hostname' 的表头行")
    
    # 尝试读取样式信息（如果需要过滤颜色或删除线）
    style_map = {}
    if filter_color or exclude_strikethrough:
        print("正在读取单元格样式信息...")
        style_map = get_sheet_style_map(file_path, sheet_name, max_rows=len(df))
    
    # 读取数据行
    results = []
    data_start_row = header_row_idx + 1
    
    print(f"开始从第{data_start_row}行读取数据...")
    for idx in range(data_start_row, len(df)):
        row = df.iloc[idx]
        mgmt_ip = row.iloc[mgmt_col_idx]
        hostname = row.iloc[hostname_col_idx]
        
        # 跳过空 IP
        if pd.isna(mgmt_ip) or str(mgmt_ip).strip() == '':
            continue
        
        mgmt_ip = str(mgmt_ip).strip()
        hostname = str(hostname).strip() if pd.notna(hostname) else ''
        
        # 检查样式（Excel 行号从1开始，pandas 从0开始）
        excel_row = idx + 1
        excel_col = mgmt_col_idx + 1
        style_info = style_map.get((excel_row, excel_col), {})
        
        # 过滤删除线
        if exclude_strikethrough and style_info.get('font_strikethrough', False):
            print(f"跳过删除线 IP: {mgmt_ip} ({hostname})")
            continue
        
        # 过滤颜色
        if filter_color == 'green':
            if not is_green_cell(style_info):
                continue
        
        results.append({
            'ip': mgmt_ip,
            'hostname': hostname,
            'row': idx
        })
    
    print(f"成功读取 {len(results)} 个 IP 地址")
    return results


def list_available_colors(file_path: str, sheet_name: str = 'net&sec', column_name: str = 'MGMT') -> List[str]:
    """
    列出 sheet 中某一列使用的所有颜色
    
    Args:
        file_path: Excel 文件路径
        sheet_name: sheet 页名称
        column_name: 列名
        
    Returns:
        list: 颜色列表
    """
    # 读取数据找到列索引
    df = read_excel_data_only(file_path, sheet_name)
    
    # 查找列索引
    col_idx = None
    for idx, row in df.iterrows():
        row_values = [str(x).strip() if pd.notna(x) else '' for x in row.values]
        if column_name in row_values:
            col_idx = row_values.index(column_name) + 1  # Excel 列从1开始
            break
    
    if col_idx is None:
        return []
    
    # 读取样式
    style_map = get_sheet_style_map(file_path, sheet_name, max_rows=len(df))
    
    # 收集所有颜色
    colors = set()
    for (row, col), style in style_map.items():
        if col == col_idx and style.get('fill_color'):
            colors.add(style['fill_color'])
    
    return sorted(list(colors))
