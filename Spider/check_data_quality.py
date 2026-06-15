import pandas as pd
import json

# 读取enriched数据
df = pd.read_csv('qunar_xian_attractions_enriched.csv')

print('='*80)
print('北京景点数据完整性分析')
print('='*80)
print()

# 基本信息
print(f'总景点数: {len(df)}')
print()

# 检查每个字段的缺失情况
print('字段完整性统计:')
print('-'*80)
print(f'{"字段名":<25} {"有效数据":<10} {"缺失数据":<10} {"完整率":<10}')
print('-'*80)

for col in df.columns:
    total = len(df)
    # 统计非空且不是空字符串的数据
    valid = df[col].notna().sum()
    if df[col].dtype == 'object':
        valid = ((df[col].notna()) & (df[col] != '') & (df[col] != '[]')).sum()
    
    missing = total - valid
    completeness = (valid / total * 100) if total > 0 else 0
    
    status = '✓' if completeness > 80 else '⚠' if completeness > 50 else '✗'
    print(f'{status} {col:<23} {valid:<10} {missing:<10} {completeness:>6.1f}%')

print()
print('='*80)

# 详细分析关键字段
print('\n关键字段详细分析:')
print('-'*80)

# 检查name字段
name_missing = df[df['name'].isna() | (df['name'] == '')]
if len(name_missing) > 0:
    print(f'\n⚠ 缺失景点名称的记录: {len(name_missing)} 条')
    print('  行号:', name_missing.index.tolist()[:10])

# 检查详细信息字段
detail_fields = ['description', 'address', 'open_time', 'ticket_price', 
                 'introduction', 'suggested_duration', 'traffic', 'phone']

print('\n详细信息字段缺失统计:')
for field in detail_fields:
    if field in df.columns:
        missing_count = ((df[field].isna()) | (df[field] == '')).sum()
        print(f'  {field:<20}: 缺失 {missing_count} 条 ({missing_count/len(df)*100:.1f}%)')

# 检查哪些景点缺失最多信息
print('\n缺失信息最多的景点 (Top 20):')
print('-'*80)

# 计算每行的缺失字段数
df_check = df.copy()
missing_counts = []
for idx, row in df_check.iterrows():
    missing = 0
    for col in df_check.columns:
        if pd.isna(row[col]) or row[col] == '' or row[col] == '[]':
            missing += 1
    missing_counts.append({
        'index': idx,
        'rank': row['rank'] if 'rank' in row and pd.notna(row['rank']) else '?',
        'name': row['name'] if pd.notna(row['name']) else '未知',
        'url': row['url'] if pd.notna(row['url']) else '',
        'missing_fields': missing,
        'total_fields': len(df_check.columns)
    })

# 按缺失字段数排序
missing_counts.sort(key=lambda x: x['missing_fields'], reverse=True)

for i, item in enumerate(missing_counts[:20], 1):
    completeness = (item['total_fields'] - item['missing_fields']) / item['total_fields'] * 100
    print(f"{i:2d}. 排名{item['rank']:>3} | {item['name']:<30} | 缺失: {item['missing_fields']:>2}/{item['total_fields']} ({completeness:.0f}%完整)")

print()
print('='*80)

# 保存需要重新爬取的URL列表
incomplete_items = [item for item in missing_counts if item['missing_fields'] > 10]
if incomplete_items:
    print(f'\n建议重新爬取的景点数量: {len(incomplete_items)}')
    
    with open('incomplete_attractions.json', 'w', encoding='utf-8') as f:
        json.dump(incomplete_items, f, ensure_ascii=False, indent=2)
    
    print('已保存到: incomplete_attractions.json')
