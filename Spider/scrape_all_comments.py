"""
批量爬取所有景点评论的脚本
从已有景点数据读取，自动跳过已爬取评论的景点
"""
import json
import csv
import time
import random
import os
from scrape_comments import scrape_attraction_comments

def load_attractions(input_file):
    """加载景点数据"""
    if not os.path.exists(input_file):
        print(f'✗ 找不到景点数据文件: {input_file}')
        return []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f'✓ 已加载景点数据: {len(data)} 个景点')
        return data
    except Exception as e:
        print(f'✗ 加载景点数据失败: {e}')
        return []

def load_existing_comments(output_file):
    """加载已有的评论数据"""
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'✓ 已加载现有评论数据: {len(data)} 个景点')
            return data
        except:
            print('✗ 加载现有评论数据失败，将重新开始')
            return []
    return []

def get_scraped_urls(existing_data):
    """获取已爬取评论的景点URL集合（只统计有评论的）"""
    scraped = set()
    for item in existing_data:
        url = item.get('url', '')
        # 只有真正爬取过评论的才算（有comments字段且不为空，或者scraped_comment_count > 0）
        if url and (item.get('comments') or item.get('scraped_comment_count', 0) > 0):
            scraped.add(url)
    return scraped

def merge_data(attractions, existing_comments):
    """合并景点数据和已有评论数据"""
    # 创建URL到评论数据的映射
    comment_map = {item.get('url'): item for item in existing_comments if item.get('url')}
    
    merged = []
    for attraction in attractions:
        url = attraction.get('url', '')
        if url in comment_map:
            # 使用已有的评论数据
            merged.append(comment_map[url])
        else:
            # 新景点，添加评论字段
            attraction['comments'] = []
            attraction['scraped_comment_count'] = 0
            merged.append(attraction)
    
    return merged

def scrape_all_comments(input_file='qunar_xian_attractions_final.json',
                       output_file='qunar_xian_attractions_comments.json',
                       max_comment_pages=10):
    """爬取所有景点的评论，跳过已爬取的"""
    
    print('='*80)
    print('北京景点评论批量爬取工具')
    print('='*80)
    print(f'\n功能: 为所有景点爬取评论')
    print(f'每个景点最多爬取: {max_comment_pages * 10} 条评论')
    print(f'自动跳过已爬取评论的景点\n')
    
    # 加载景点数据
    attractions = load_attractions(input_file)
    if not attractions:
        return
    
    # 加载已有评论数据
    existing_comments = load_existing_comments(output_file)
    
    # 合并数据
    all_data = merge_data(attractions, existing_comments)
    
    # 获取已爬取的URL
    scraped_urls = get_scraped_urls(all_data)
    
    # 找出需要爬取的景点
    to_scrape = [item for item in all_data if item.get('url') and item.get('url') not in scraped_urls]
    
    print(f'数据统计:')
    print(f'  总景点数: {len(all_data)}')
    print(f'  已爬取评论: {len(scraped_urls)} 个景点')
    print(f'  待爬取评论: {len(to_scrape)} 个景点\n')
    
    if not to_scrape:
        print('✓ 所有景点的评论都已爬取完成！')
        return
    
    print('开始爬取评论')
    print('-'*80)
    
    for i, attraction in enumerate(to_scrape, 1):
        print(f'\n[{i}/{len(to_scrape)}] {attraction.get("name", "未知")}')
        print(f'  排名: 第{attraction.get("rank", "?")}名 | 评分: {attraction.get("rating", "?")}')
        
        if not attraction.get('url'):
            print('  ✗ 无URL，跳过')
            continue
        
        # 爬取评论
        try:
            comments = scrape_attraction_comments(
                attraction.get('name', '未知'),
                attraction.get('url', ''),
                max_pages=max_comment_pages
            )
            
            attraction['comments'] = comments
            attraction['scraped_comment_count'] = len(comments)
            
        except Exception as e:
            print(f'  ✗ 爬取评论失败: {e}')
            attraction['comments'] = []
            attraction['scraped_comment_count'] = 0
        
        # 每5个景点保存一次
        if i % 5 == 0:
            save_data(all_data, output_file)
            print(f'\n  💾 已保存进度 ({i}/{len(to_scrape)} 个景点已处理)')
        
        # 延迟
        if i < len(to_scrape):
            delay = random.uniform(3, 6)
            print(f'  等待 {delay:.1f} 秒...')
            time.sleep(delay)
    
    # 最终保存
    save_data(all_data, output_file)
    
    print('\n' + '='*80)
    print('✓ 爬取完成！')
    print('='*80)
    
    # 统计
    total_comments = sum(item.get('scraped_comment_count', 0) for item in all_data)
    has_comments = sum(1 for item in all_data if item.get('scraped_comment_count', 0) > 0)
    
    print(f'\n最终统计:')
    print(f'  总景点数: {len(all_data)}')
    print(f'  本次爬取: {len(to_scrape)} 个景点')
    print(f'  有评论的景点: {has_comments}')
    print(f'  总评论数: {total_comments}')
    if all_data:
        print(f'  平均每个景点: {total_comments/len(all_data):.1f} 条评论')
    
    csv_file = output_file.replace('.json', '_flat.csv')
    print(f'\n数据已保存到:')
    print(f'  - {output_file} (JSON格式)')
    print(f'  - {csv_file} (CSV格式)')

def save_data(data, output_file):
    """保存数据到JSON和CSV"""
    # 保存JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 保存CSV（扁平化）
    csv_file = output_file.replace('.json', '_flat.csv')
    flat_data = []
    
    for attraction in data:
        if attraction.get('comments'):
            for comment in attraction['comments']:
                flat_row = {
                    'attraction_rank': attraction.get('rank', ''),
                    'attraction_name': attraction.get('name', ''),
                    'attraction_url': attraction.get('url', ''),
                    'attraction_city': attraction.get('city', ''),
                    'attraction_rating': attraction.get('rating', ''),
                    'comment_title': comment.get('title', ''),
                    'comment_rating': comment.get('rating', ''),
                    'comment_content': comment.get('content', ''),
                    'comment_date': comment.get('date', ''),
                    'comment_user': comment.get('user_name', ''),
                    'comment_image_count': comment.get('image_count', 0),
                }
                flat_data.append(flat_row)
    
    if flat_data:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)

if __name__ == '__main__':
    import sys
    
    # 默认参数
    input_file = 'my_data_enriched_with_pinyin.json'  # 景点数据文件
    output_file = 'my_data_comments.json'  # 输出文件
    max_comment_pages = 10  # 每个景点最多10页评论
    
    # 命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        max_comment_pages = int(sys.argv[3])
    
    scrape_all_comments(
        input_file=input_file,
        output_file=output_file,
        max_comment_pages=max_comment_pages
    )
