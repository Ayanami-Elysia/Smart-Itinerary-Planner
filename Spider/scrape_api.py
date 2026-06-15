"""
使用去哪儿网API爬取北京景点数据
API: https://touch.go.qunar.com/299914/sights?_json&limit=10&page=X
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
import re

def parse_html_item(html_str):
    """解析单个景点的HTML字符串"""
    soup = BeautifulSoup(html_str, 'lxml')
    
    attraction = {}
    
    # 提取链接和ID
    link = soup.find('a', class_='list_link')
    if link:
        href = link.get('href', '')
        attraction['url'] = 'https:' + href if href.startswith('//') else href
        # 从URL提取ID
        if '/poi/' in href:
            poi_id = href.split('/poi/')[-1].strip('"')
            attraction['poi_id'] = poi_id
    
    # 提取景点名称
    dt = soup.find('dt')
    attraction['name'] = dt.get_text(strip=True) if dt else ''
    
    # 提取评分
    score_span = soup.find('span', class_='score')
    if score_span:
        score_text = score_span.get_text(strip=True)
        # 提取数字评分，如 "4.8分"
        score_match = re.search(r'(\d+\.?\d*)分', score_text)
        if score_match:
            attraction['rating'] = score_match.group(1)
        else:
            attraction['rating'] = '0'
    else:
        attraction['rating'] = '0'
    
    # 提取评论数
    comment_span = soup.find('span', class_='comment')
    if comment_span:
        comment_num = comment_span.find('span')
        attraction['comment_count'] = comment_num.get_text(strip=True) if comment_num else '0'
    else:
        attraction['comment_count'] = '0'
    
    # 提取标签/关键词
    bd_div = soup.find('div', class_='bd')
    if bd_div:
        tags_span = bd_div.find('span')
        attraction['tags'] = tags_span.get_text(strip=True) if tags_span else ''
    else:
        attraction['tags'] = ''
    
    # 提取排名
    rate_div = soup.find('div', class_='rate')
    if rate_div:
        rank_text = rate_div.get_text(strip=True)
        # 提取 "景点排名第X"
        rank_match = re.search(r'景点排名第(\d+)', rank_text)
        if rank_match:
            attraction['rank'] = rank_match.group(1)
            attraction['city_rank'] = rank_match.group(1)
        else:
            attraction['rank'] = ''
            attraction['city_rank'] = ''
    else:
        attraction['rank'] = ''
        attraction['city_rank'] = ''
    
    # 提取价格
    pricebox = soup.find('span', class_='pricebox')
    if pricebox:
        price_text = pricebox.get_text(strip=True)
        attraction['ticket_price'] = price_text.replace('￥', '') + '元'
    else:
        attraction['ticket_price'] = '无'
    
    # 提取描述
    disp_div = soup.find('div', class_='disp')
    if disp_div:
        desc_span = disp_div.find('span')
        attraction['description'] = desc_span.get_text(strip=True) if desc_span else ''
    else:
        attraction['description'] = ''
    
    # 提取图片
    img = soup.find('img', class_='img')
    if img:
        img_src = img.get('src', '')
        attraction['image'] = 'https:' + img_src if img_src.startswith('//') else img_src
    else:
        attraction['image'] = ''
    
    # 设置默认值
    attraction['name_en'] = ''
    attraction['strategy_count'] = '0'
    attraction['visitor_percentage'] = ''
    attraction['city'] = '北京'
    attraction['latitude'] = ''
    attraction['longitude'] = ''
    attraction['score'] = attraction['rating']
    attraction['address'] = ''
    attraction['open_time'] = ''
    attraction['introduction'] = '无'
    attraction['suggested_duration'] = ''
    attraction['traffic'] = ''
    attraction['best_season'] = '无'
    attraction['images'] = []
    attraction['phone'] = ''
    attraction['website'] = '无'
    
    return attraction

def scrape_api_page(page, limit=10):
    """爬取单页数据"""
    url = f'https://touch.go.qunar.com/299914/sights?_json&limit={limit}&page={page}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://touch.go.qunar.com/299914/sights',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    try:
        print(f'正在爬取第 {page} 页...', end=' ')
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f'✗ 请求失败，状态码: {response.status_code}')
            return [], False
        
        data = response.json()
        
        if not data.get('ret'):
            print(f'✗ API返回错误: {data.get("errmsg", "未知错误")}')
            return [], False
        
        html_content = data.get('data', {}).get('html', '')
        has_more = data.get('data', {}).get('more', False)
        
        if not html_content:
            print('✗ 无数据')
            return [], False
        
        # 解析HTML，分割成单个景点
        # 每个景点是一个 <a class="list_link"> 标签
        soup = BeautifulSoup(html_content, 'lxml')
        items = soup.find_all('a', class_='list_link')
        
        attractions = []
        for item in items:
            try:
                attraction = parse_html_item(str(item))
                attractions.append(attraction)
            except Exception as e:
                print(f'\n  ✗ 解析景点失败: {e}')
                continue
        
        print(f'✓ 获取 {len(attractions)} 个景点')
        return attractions, has_more
        
    except Exception as e:
        print(f'✗ 爬取失败: {e}')
        return [], False

def scrape_all_from_api(output_file='qunar_xian_attractions_api.json', max_pages=50):
    """从API爬取所有景点数据"""
    
    print('='*80)
    print('去哪儿网API景点爬虫')
    print('='*80)
    print(f'\nAPI: https://touch.go.qunar.com/299914/sights')
    print(f'目标: 北京景点数据\n')
    
    all_attractions = []
    page = 1
    
    while page <= max_pages:
        attractions, has_more = scrape_api_page(page)
        
        if attractions:
            all_attractions.extend(attractions)
            print(f'  当前总数: {len(all_attractions)} 个景点\n')
        else:
            print(f'  第 {page} 页无数据，停止爬取\n')
            break
        
        # 如果API返回没有更多数据，停止
        if not has_more:
            print('✓ 已到最后一页\n')
            break
        
        page += 1
        
        # 随机延迟
        if page <= max_pages:
            delay = random.uniform(2, 4)
            print(f'  等待 {delay:.1f} 秒...\n')
            time.sleep(delay)
    
    print('='*80)
    print(f'✓ 爬取完成！总共获取 {len(all_attractions)} 个景点')
    print('='*80)
    print()
    
    if all_attractions:
        # 保存为JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_attractions, f, ensure_ascii=False, indent=2)
        print(f'✓ 数据已保存到 {output_file}')
        
        # 保存为CSV
        csv_file = output_file.replace('.json', '.csv')
        keys = all_attractions[0].keys()
        with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_attractions)
        print(f'✓ 数据已保存到 {csv_file}')
        
        # 显示统计
        print(f'\n数据统计:')
        print(f'  总景点数: {len(all_attractions)}')
        
        # 计算平均评分
        ratings = [float(a["rating"]) for a in all_attractions if a["rating"] and a["rating"] != '0']
        if ratings:
            print(f'  平均评分: {sum(ratings)/len(ratings):.2f}')
        
        # 显示前5条
        print(f'\n前5个景点:')
        print('-'*80)
        for i, item in enumerate(all_attractions[:5], 1):
            print(f'{i}. {item["name"]}')
            print(f'   排名: 第{item["rank"]}名 | 评分: {item["rating"]}分 | 评论: {item["comment_count"]}条')
            print(f'   {item["description"]}')
            print()
    else:
        print('✗ 未能获取任何数据')

if __name__ == '__main__':
    import sys
    
    # 默认参数
    output_file = 'qunar_xian_attractions_api.json'
    max_pages = 50
    
    # 命令行参数
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    if len(sys.argv) > 2:
        max_pages = int(sys.argv[2])
    
    scrape_all_from_api(output_file=output_file, max_pages=max_pages)

