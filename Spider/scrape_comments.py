import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

def get_comments_from_page(url, page=1, retry_count=3):
    """从指定页面获取评论，支持重试"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://travel.qunar.com/'
    }
    
    # 构建分页URL
    # URL格式: https://travel.qunar.com/p-oi722610-qinshihuangdilingbowu-1-2
    if page > 1:
        # 移除URL末尾的斜杠和可能的查询参数
        base_url = url.split('?')[0].split('#')[0].rstrip('/')
        
        # 检查URL是否已经包含分页格式（-1-数字）
        if re.search(r'-1-\d+$', base_url):
            # 如果已经有分页，替换页码
            base_url = re.sub(r'-1-\d+$', '', base_url)
        
        # 检查URL格式
        # 长URL格式: https://travel.qunar.com/p-oi722610-qinshihuangdilingbowu
        # 短URL格式: https://travel.qunar.com/p-oi710603
        if re.match(r'https://travel\.qunar\.com/p-oi\d+-[a-z]+', base_url):
            # 有拼音部分，可以正常分页
            page_url = f'{base_url}-1-{page}'
        else:
            # 短URL，使用评论列表API
            # 从URL提取poi_id: p-oi710603 -> 710603
            poi_match = re.search(r'p-oi(\d+)', base_url)
            if poi_match:
                poi_id = poi_match.group(1)
                # 使用评论API: https://travel.qunar.com/poi/review_list?poiId=710603&page=2
                page_url = f'https://travel.qunar.com/poi/review_list?poiId={poi_id}&page={page}'
            else:
                print(f'无法解析POI ID', end=' ')
                return []
    else:
        page_url = url
    
    for attempt in range(retry_count):
        try:
            response = requests.get(page_url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                if attempt < retry_count - 1:
                    print(f'状态码{response.status_code}，重试{attempt + 1}/{retry_count}...', end=' ')
                    time.sleep(2)
                    continue
                return []
            
            soup = BeautifulSoup(response.text, 'lxml')
            comments = []
            
            # 查找所有评论项
            comment_items = soup.find_all('li', class_='e_comment_item')
            
            # 如果没有找到评论且还有重试次数
            if not comment_items and attempt < retry_count - 1:
                print(f'未找到评论，重试{attempt + 1}/{retry_count}...', end=' ')
                time.sleep(3)
                continue
            
            for item in comment_items:
                comment = {}
                
                # 评论标题
                title_tag = item.find('div', class_='e_comment_title')
                if title_tag:
                    title_link = title_tag.find('a')
                    comment['title'] = title_link.get_text(strip=True) if title_link else ''
                    comment['comment_url'] = title_link.get('href', '') if title_link else ''
                
                # 评分
                star_box = item.find('div', class_='e_comment_star_box')
                if star_box:
                    star_span = star_box.find('span', class_='cur_star')
                    if star_span:
                        star_class = star_span.get('class', [])
                        for cls in star_class:
                            if 'star_' in cls:
                                comment['rating'] = cls.replace('star_', '')
                                break
                    else:
                        comment['rating'] = '无'
                else:
                    comment['rating'] = '无'
                
                # 评论内容
                content_div = item.find('div', class_='e_comment_content')
                if content_div:
                    # 移除"阅读全部"链接
                    see_more = content_div.find('a', class_='seeMore')
                    if see_more:
                        see_more.decompose()
                    comment['content'] = content_div.get_text(strip=True)
                else:
                    comment['content'] = ''
                
                # 评论图片
                images = []
                img_box = item.find('div', class_='e_comment_imgs_box')
                if img_box:
                    img_tags = img_box.find_all('img', class_='cmt_img')
                    for img in img_tags:
                        img_src = img.get('src', '')
                        if img_src:
                            images.append(img_src)
                comment['images'] = images
                comment['image_count'] = len(images)
                
                # 评论日期
                add_info = item.find('div', class_='e_comment_add_info')
                if add_info:
                    date_li = add_info.find('li')
                    comment['date'] = date_li.get_text(strip=True) if date_li else ''
                else:
                    comment['date'] = ''
                
                # 用户信息
                usr_div = item.find('div', class_='e_comment_usr')
                if usr_div:
                    usr_name = usr_div.find('div', class_='e_comment_usr_name')
                    if usr_name:
                        usr_link = usr_name.find('a')
                        comment['user_name'] = usr_link.get_text(strip=True) if usr_link else ''
                        comment['user_url'] = usr_link.get('href', '') if usr_link else ''
                    else:
                        comment['user_name'] = ''
                        comment['user_url'] = ''
                else:
                    comment['user_name'] = ''
                    comment['user_url'] = ''
                
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            if attempt < retry_count - 1:
                print(f'错误: {e}，重试{attempt + 1}/{retry_count}...', end=' ')
                time.sleep(3)
                continue
            else:
                print(f'✗ 获取评论失败: {e}')
                return []
    
    return []

def scrape_attraction_comments(attraction_name, attraction_url, max_pages=10, retry_on_empty=True):
    """爬取单个景点的评论，支持重试"""
    print(f'\n正在爬取: {attraction_name}')
    print(f'URL: {attraction_url}')
    
    all_comments = []
    consecutive_empty = 0  # 连续空页面计数
    
    for page in range(1, max_pages + 1):
        print(f'  页面 {page}/{max_pages}...', end=' ')
        
        comments = get_comments_from_page(attraction_url, page)
        
        if not comments:
            consecutive_empty += 1
            
            # 如果连续2页都没有数据，且启用了重试
            if consecutive_empty >= 2 and retry_on_empty and page > 1:
                print(f'连续{consecutive_empty}页无数据，停止爬取')
                break
            elif page == 1 and retry_on_empty:
                # 第一页就没数据，可能是网络问题，等待后重试整个景点
                print('第一页无数据，等待5秒后重试...')
                time.sleep(5)
                return scrape_attraction_comments(attraction_name, attraction_url, max_pages, retry_on_empty=False)
            else:
                print('无评论或已到最后一页')
                break
        else:
            consecutive_empty = 0  # 重置计数
            all_comments.extend(comments)
            print(f'获取 {len(comments)} 条评论')
        
        # 每页之间都休息，避免请求过快
        if page < max_pages:
            delay = random.uniform(2, 4)
            print(f'    等待 {delay:.1f} 秒...', end=' ')
            time.sleep(delay)
            print('继续')
    
    print(f'  ✓ 共获取 {len(all_comments)} 条评论')
    return all_comments

def scrape_all_attractions_comments(input_file='qunar_xian_attractions_final.json', 
                                   output_file='qunar_xian_attractions_comments.json',
                                   max_pages=10,
                                   start_index=0,
                                   max_count=None):
    """爬取所有景点的评论"""
    
    # 读取景点数据
    with open(input_file, 'r', encoding='utf-8') as f:
        attractions = json.load(f)
    
    print('='*80)
    print('北京景点评论爬取工具')
    print('='*80)
    print(f'\n总景点数: {len(attractions)}')
    print(f'每个景点最多爬取: {max_pages * 10} 条评论 ({max_pages}页)')
    
    # 限制处理数量
    if max_count:
        attractions = attractions[start_index:start_index + max_count]
    else:
        attractions = attractions[start_index:]
    
    print(f'本次处理: {len(attractions)} 个景点 (从第 {start_index + 1} 个开始)\n')
    
    results = []
    
    for i, attraction in enumerate(attractions, 1):
        attraction_data = {
            'rank': attraction.get('rank', ''),
            'name': attraction.get('name', ''),
            'url': attraction.get('url', ''),
            'city': attraction.get('city', ''),
            'rating': attraction.get('rating', ''),
            'comment_count': attraction.get('comment_count', ''),
            'comments': []
        }
        
        print(f'\n[{i}/{len(attractions)}] ', end='')
        
        if not attraction.get('url'):
            print(f'{attraction.get("name", "未知")} - 无URL，跳过')
            results.append(attraction_data)
            continue
        
        # 爬取评论
        comments = scrape_attraction_comments(
            attraction.get('name', '未知'),
            attraction.get('url', ''),
            max_pages=max_pages
        )
        
        attraction_data['comments'] = comments
        attraction_data['scraped_comment_count'] = len(comments)
        results.append(attraction_data)
        
        # 保存进度
        if i % 5 == 0:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f'\n  💾 已保存进度 ({i}/{len(attractions)})')
        
        # 延迟
        if i < len(attractions):
            delay = random.uniform(3, 6)
            print(f'  等待 {delay:.1f} 秒...')
            time.sleep(delay)
    
    # 最终保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存为CSV格式（扁平化数据）
    csv_file = output_file.replace('.json', '_flat.csv')
    import csv
    
    # 创建扁平化的评论数据
    flat_data = []
    for attraction in results:
        for comment in attraction.get('comments', []):
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
                'comment_url': comment.get('comment_url', '')
            }
            flat_data.append(flat_row)
    
    if flat_data:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)
    
    print('\n' + '='*80)
    print('✓ 爬取完成！')
    print('='*80)
    
    # 统计
    total_comments = sum(item['scraped_comment_count'] for item in results)
    has_comments = sum(1 for item in results if item['scraped_comment_count'] > 0)
    
    print(f'\n统计信息:')
    print(f'  处理景点数: {len(results)}')
    print(f'  有评论的景点: {has_comments}')
    print(f'  总评论数: {total_comments}')
    print(f'  平均每个景点: {total_comments/len(results):.1f} 条评论')
    print(f'\n数据已保存到:')
    print(f'  - {output_file} (JSON格式)')
    print(f'  - {csv_file} (CSV格式)')

if __name__ == '__main__':
    import sys
    
    # 默认参数
    max_pages = 10  # 每个景点最多10页，即100条评论
    start = 0
    count = 200  # 默认处理10个景点
    
    # 命令行参数
    if len(sys.argv) > 1:
        start = int(sys.argv[1])
    if len(sys.argv) > 2:
        count = int(sys.argv[2])
    if len(sys.argv) > 3:
        max_pages = int(sys.argv[3])
    
    scrape_all_attractions_comments(
        start_index=start,
        max_count=count,
        max_pages=max_pages
    )
