#!/usr/bin/env python3
"""
修复 Excel 文件格式，使其兼容 openpyxl

这个脚本会：
1. 使用 python-calamine 读取原文件
2. 创建新的 Excel 文件（兼容 openpyxl）
3. 保留所有数据但不保留样式
"""

import sys
import pandas as pd
from pathlib import Path


def fix_excel_file(input_file: str, output_file: str = None):
    """修复 Excel 文件格式"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"错误: 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}"
    
    print(f"正在修复 Excel 文件...")
    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    print()
    
    try:
        # 读取所有 sheet
        print("步骤 1: 读取原文件...")
        try:
            xls = pd.ExcelFile(input_file, engine='calamine')
            print(f"✓ 使用 calamine 引擎读取成功")
        except ImportError:
            print("错误: 需要安装 python-calamine")
            print("运行: pip install python-calamine")
            return False
        except Exception as e:
            print(f"✗ 读取失败: {e}")
            return False
        
        sheet_names = xls.sheet_names
        print(f"✓ 找到 {len(sheet_names)} 个 sheet 页: {sheet_names}")
        print()
        
        # 读取所有数据
        print("步骤 2: 读取所有数据...")
        sheets_data = {}
        for sheet_name in sheet_names:
            df = pd.read_excel(input_file, sheet_name=sheet_name, header=None, engine='calamine')
            sheets_data[sheet_name] = df
            print(f"  ✓ {sheet_name}: {len(df)} 行 x {len(df.columns)} 列")
        print()
        
        # 写入新文件
        print("步骤 3: 写入新文件...")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, df in sheets_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                print(f"  ✓ 已写入 {sheet_name}")
        
        xls.close()
        print()
        print("=" * 60)
        print("✓ 修复完成！")
        print("=" * 60)
        print()
        print(f"新文件: {output_file}")
        print()
        print("注意:")
        print("- 新文件可以被 openpyxl 读取")
        print("- 所有数据已保留")
        print("- 单元格样式（颜色、删除线等）已丢失")
        print()
        
        # 验证新文件
        print("步骤 4: 验证新文件...")
        try:
            test_df = pd.read_excel(output_file, sheet_name=sheet_names[0], header=None)
            print(f"✓ 新文件可以被 openpyxl 正常读取")
            print(f"✓ 验证通过！")
            return True
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  {sys.argv[0]} <输入文件> [输出文件]")
        print()
        print("示例:")
        print(f"  {sys.argv[0]} pass/IP地址规划表-金茂.xlsx")
        print(f"  {sys.argv[0]} pass/IP地址规划表-金茂.xlsx pass/IP地址规划表-金茂_fixed.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = fix_excel_file(input_file, output_file)
    sys.exit(0 if success else 1)
