import os
import json
import sys
from pathlib import Path

def extract_textures_from_json(data):
    """
    从不同格式的index.json中提取textures数组
    支持两种格式：
    1. 标准格式: {"textures": [...]}
    2. Live2D Cubism 3.0+ 格式: {"FileReferences": {"Textures": [...]}}
    """
    textures = None
    
    # 格式1: 标准格式
    if 'textures' in data and isinstance(data['textures'], list):
        textures = data['textures']
        return textures, "标准格式"
    
    # 格式2: Live2D Cubism 3.0+ 格式
    if 'FileReferences' in data and isinstance(data['FileReferences'], dict):
        file_refs = data['FileReferences']
        if 'Textures' in file_refs and isinstance(file_refs['Textures'], list):
            textures = file_refs['Textures']
            return textures, "Cubism 3.0+ 格式"
    
    return None, "未知格式"

def generate_textures_cache(directory):
    """
    遍历指定目录下的所有文件夹，找出index.json文件，
    根据其中的textures字段生成textures.cache文件
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"错误: 目录 '{directory}' 不存在")
        return
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # 递归遍历所有子目录
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        
        # 检查当前目录是否包含index.json
        index_json_path = root_path / "index.json"
        
        if index_json_path.exists():
            try:
                # 读取index.json文件
                with open(index_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取textures数组
                textures, format_type = extract_textures_from_json(data)
                
                if textures is not None:
                    # 生成textures.cache文件路径
                    cache_path = root_path / "textures.cache"
                    
                    # 写入textures.cache文件
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(textures, f, ensure_ascii=False, indent=4)
                    
                    print(f"✓ 已生成: {cache_path}")
                    print(f"  格式: {format_type}")
                    print(f"  包含 {len(textures)} 个纹理文件")
                    
                    # 显示纹理文件列表（如果数量不多的话）
                    if len(textures) <= 5:
                        for i, texture in enumerate(textures):
                            print(f"    {i+1}. {texture}")
                    else:
                        print(f"    1. {textures[0]}")
                        print(f"    2. {textures[1]}")
                        print(f"    ...")
                        print(f"    {len(textures)}. {textures[-1]}")
                    
                    processed_count += 1
                else:
                    print(f"⚠ 跳过: {index_json_path}")
                    print(f"  原因: 没有找到支持的textures字段格式")
                    print(f"  检测到的格式: {format_type}")
                    skipped_count += 1
                    
            except json.JSONDecodeError as e:
                print(f"✗ JSON错误: {index_json_path}")
                print(f"  错误详情: {e}")
                error_count += 1
            except Exception as e:
                print(f"✗ 处理错误: {index_json_path}")
                print(f"  错误详情: {e}")
                error_count += 1
            
            print("-" * 50)
    
    # 显示统计信息
    print(f"\n📊 处理统计:")
    print(f"✓ 成功生成: {processed_count} 个 textures.cache 文件")
    print(f"⚠ 跳过文件: {skipped_count} 个")
    print(f"✗ 错误文件: {error_count} 个")
    print(f"📁 总计处理: {processed_count + skipped_count + error_count} 个 index.json 文件")

def preview_mode(directory):
    """
    预览模式：只扫描不生成文件，显示会处理哪些文件
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"错误: 目录 '{directory}' 不存在")
        return
    
    print("🔍 预览模式 - 扫描结果:")
    print("-" * 50)
    
    found_files = []
    
    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        index_json_path = root_path / "index.json"
        
        if index_json_path.exists():
            try:
                with open(index_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                textures, format_type = extract_textures_from_json(data)
                
                if textures is not None:
                    found_files.append({
                        'path': index_json_path,
                        'format': format_type,
                        'texture_count': len(textures),
                        'textures': textures
                    })
            except:
                pass
    
    if found_files:
        for i, file_info in enumerate(found_files, 1):
            print(f"{i}. {file_info['path']}")
            print(f"   格式: {file_info['format']}")
            print(f"   纹理数量: {file_info['texture_count']}")
            print(f"   将生成: {file_info['path'].parent / 'textures.cache'}")
        
        print(f"\n总共找到 {len(found_files)} 个可处理的 index.json 文件")
        
        # 询问是否继续
        response = input("\n是否继续生成 textures.cache 文件? (y/N): ").strip().lower()
        if response in ['y', 'yes', '是']:
            print("\n开始生成...")
            print("=" * 50)
            generate_textures_cache(directory)
        else:
            print("已取消操作")
    else:
        print("没有找到可处理的 index.json 文件")

def main():
    print("Live2D Textures Cache 生成器")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("使用方法:")
            print("  python generate_textures_cache.py [目录路径] [选项]")
            print("\n选项:")
            print("  -p, --preview    预览模式，仅扫描不生成")
            print("  -h, --help       显示帮助信息")
            print("\n示例:")
            print("  python generate_textures_cache.py")
            print("  python generate_textures_cache.py /path/to/models")
            print("  python generate_textures_cache.py /path/to/models --preview")
            return
        
        preview = '--preview' in sys.argv or '-p' in sys.argv
        
        # 获取目录参数
        target_directory = "."
        for arg in sys.argv[1:]:
            if not arg.startswith('-'):
                target_directory = arg
                break
    else:
        target_directory = "."
        preview = False
    
    print(f"目标目录: {os.path.abspath(target_directory)}")
    print(f"支持格式: 标准格式 + Live2D Cubism 3.0+ 格式")
    print("-" * 50)
    
    if preview:
        preview_mode(target_directory)
    else:
        generate_textures_cache(target_directory)

if __name__ == "__main__":
    main()