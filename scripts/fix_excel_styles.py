#!/usr/bin/env python3
"""
自动修复 Excel 文件中的空 fill 标签问题

问题：Excel 文件包含空的 <fill/> 标签，导致 openpyxl 无法读取
解决：将空的 <fill/> 替换为 <fill><patternFill patternType="none"/></fill>
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil


def fix_excel_styles(input_file: str, output_file: str = None, backup: bool = True):
    """
    修复 Excel 文件中的样式问题
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（None 则覆盖原文件）
        backup: 是否备份原文件
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"✗ 错误: 文件不存在: {input_file}")
        return False
    
    # 确定输出文件
    if output_file is None:
        output_path = input_path
        temp_path = input_path.parent / f"{input_path.stem}_temp{input_path.suffix}"
    else:
        output_path = Path(output_file)
        temp_path = output_path
    
    # 备份原文件
    if backup and output_file is None:
        backup_path = input_path.parent / f"{input_path.stem}_backup{input_path.suffix}"
        print(f"备份原文件: {backup_path}")
        shutil.copy2(input_path, backup_path)
    
    print("=" * 70)
    print("修复 Excel 文件样式问题")
    print("=" * 70)
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_path}")
    print()
    
    try:
        # 1. 读取并分析样式文件
        print("步骤 1: 分析样式文件...")
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            styles_xml = zip_ref.read('xl/styles.xml')
        
        # 解析 XML
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        root = ET.fromstring(styles_xml)
        fills = root.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}fills')
        
        if fills is None:
            print("✗ 未找到 fills 节点")
            return False
        
        # 查找空的 fill 标签
        empty_fills = []
        all_fills = fills.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}fill')
        
        for i, fill in enumerate(all_fills, 1):
            if len(fill) == 0:  # 空标签
                empty_fills.append(i)
        
        if not empty_fills:
            print("✓ 未发现空的 fill 标签，文件格式正常")
            return True
        
        print(f"✓ 找到 {len(empty_fills)} 个空的 fill 标签（位置: {empty_fills}）")
        print()
        
        # 2. 修复空的 fill 标签
        print("步骤 2: 修复空的 fill 标签...")
        fixed_count = 0
        
        for fill in all_fills:
            if len(fill) == 0:
                # 添加 patternFill 子元素
                pattern_fill = ET.SubElement(fill, '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}patternFill')
                pattern_fill.set('patternType', 'none')
                fixed_count += 1
        
        print(f"✓ 已修复 {fixed_count} 个空 fill 标签")
        print()
        
        # 3. 生成新的 styles.xml
        print("步骤 3: 生成新的样式文件...")
        new_styles_xml = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        
        # 4. 重新打包 Excel 文件
        print("步骤 4: 重新打包 Excel 文件...")
        
        with zipfile.ZipFile(input_path, 'r') as zip_read:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for item in zip_read.infolist():
                    if item.filename == 'xl/styles.xml':
                        # 使用修复后的 styles.xml
                        zip_write.writestr(item, new_styles_xml)
                    else:
                        # 复制其他文件
                        data = zip_read.read(item.filename)
                        zip_write.writestr(item, data)
        
        # 如果是覆盖原文件，移动临时文件
        if output_file is None:
            shutil.move(str(temp_path), str(output_path))
        
        print("✓ Excel 文件重新打包完成")
        print()
        
        # 5. 验证修复后的文件
        print("步骤 5: 验证修复后的文件...")
        try:
            import pandas as pd
            test_df = pd.read_excel(str(output_path), sheet_name=0, nrows=5)
            print("✓ 修复后的文件可以被 openpyxl 正常读取")
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            return False
        
        print()
        print("=" * 70)
        print("✓ 修复完成！")
        print("=" * 70)
        print()
        print("修复内容:")
        print(f"  - 修复了 {fixed_count} 个空的 <fill/> 标签")
        print(f"  - 将 <fill/> 替换为 <fill><patternFill patternType=\"none\"/></fill>")
        print()
        print("注意:")
        print("  - 文件现在可以被 openpyxl 正常读取")
        print("  - 所有单元格数据和样式都已保留")
        if backup and output_file is None:
            print(f"  - 原文件已备份到: {backup_path}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='修复 Excel 文件中的空 fill 标签问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 修复文件（原地修复，会备份）
  %(prog)s pass/IP地址规划表-金茂.xlsx
  
  # 修复并保存到新文件
  %(prog)s pass/IP地址规划表-金茂.xlsx -o pass/IP地址规划表-金茂_fixed.xlsx
  
  # 修复文件但不备份
  %(prog)s pass/IP地址规划表-金茂.xlsx --no-backup
        """
    )
    
    parser.add_argument('input', help='输入 Excel 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--no-backup', action='store_true', help='不备份原文件')
    
    args = parser.parse_args()
    
    success = fix_excel_styles(
        args.input,
        args.output,
        backup=not args.no_backup
    )
    
    sys.exit(0 if success else 1)
