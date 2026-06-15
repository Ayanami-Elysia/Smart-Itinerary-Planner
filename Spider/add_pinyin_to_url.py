"""
为景点URL添加拼音后缀
将短URL（如 https://travel.qunar.com/p-oi710603）
转换为长URL（如 https://travel.qunar.com/p-oi710603-gugongbowuyuan）
"""
import json
import csv
import re
from pypinyin import lazy_pinyin

def name_to_pinyin(name):
    """将中文名称转换为拼音（小写，无分隔符）"""
    # 移除特殊字符
    name = re.sub(r'[·\-\s\(\)（）]', '', name)
    # 转换为拼音
    pinyin_list = lazy_pinyin(name)
    # 合并为一个字符串，全部小写
    pinyin = ''.join(pinyin_list).lower()
    return pinyin

def add_pinyin_to_url(url, name):
    """为URL添加拼音后缀"""
    # 移除URL末尾的斜杠和查询参数
    base_url = url.split('?')[0].split('#')[0].rstrip('/')
    
    # 检查URL是否已经有拼音部分
    if re.match(r'https://travel\.qunar\.com/p-oi\d+-[a-z]+', base_url):
        # 已经有拼音，不需要修改
        return url
    
    # 检查是否是短URL格式
    if re.match(r'https://travel\.qunar\.com/p-oi\d+$', base_url):
        # 生成拼音
        pinyin = name_to_pinyin(name)
        # 添加拼音后缀
        new_url = f'{base_url}-{pinyin}'
        return new_url
    
    # 其他格式，不修改
    return url

def process_json_file(input_file, output_file):
    """处理JSON文件"""
    print(f'正在处理: {input_file}')
    
    # 读取JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'  总共 {len(data)} 个景点')
    
    # 处理每个景点
    updated_count = 0
    for item in data:
        old_url = item.get('url', '')
        name = item.get('name', '')
        
        if old_url and name:
            new_url = add_pinyin_to_url(old_url, name)
            if new_url != old_url:
                item['url'] = new_url
                updated_count += 1
                print(f'  ✓ {name}')
                print(f'    {old_url} -> {new_url}')
    
    # 保存JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'\n✓ 已更新 {updated_count} 个URL')
    print(f'✓ 数据已保存到: {output_file}')
    
    return data

def process_csv_file(input_file, output_file):
    """处理CSV文件"""
    print(f'\n正在处理: {input_file}')
    
    # 读取CSV
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f'  总共 {len(data)} 个景点')
    
    # 处理每个景点
    updated_count = 0
    for item in data:
        old_url = item.get('url', '')
        name = item.get('name', '')
        
        if old_url and name:
            new_url = add_pinyin_to_url(old_url, name)
            if new_url != old_url:
                item['url'] = new_url
                updated_count += 1
    
    # 保存CSV
    if data:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f'\n✓ 已更新 {updated_count} 个URL')
    print(f'✓ 数据已保存到: {output_file}')

def main():
    print('='*80)
    print('景点URL拼音添加工具')
    print('='*80)
    print()
    
    # 处理JSON文件
    json_data = process_json_file(
        'my_data_enriched.json',
        'my_data_enriched_with_pinyin.json'
    )
    
    # 处理CSV文件
    process_csv_file(
        'my_data_enriched.csv',
        'my_data_enriched_with_pinyin.csv'
    )
    
    print('\n' + '='*80)
    print('✓ 处理完成！')
    print('='*80)
    print('\n生成的文件:')
    print('  - my_data_enriched_with_pinyin.json')
    print('  - my_data_enriched_with_pinyin.csv')
    print('\n示例:')
    if json_data:
        for i, item in enumerate(json_data[:3], 1):
            print(f'\n{i}. {item.get("name", "")}')
            print(f'   URL: {item.get("url", "")}')

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print('✗ 缺少 pypinyin 库')
        print('请先安装: pip install pypinyin')
    except Exception as e:
        print(f'✗ 错误: {e}')

