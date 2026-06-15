"""
从景点URL页面获取详细信息
读取my_data.csv，访问每个景点的URL，获取详细数据
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
import re

def get_attraction_detail(url, name):
    """访问景点页面，获取详细信息（与qunar_xian_attractions_final.csv字段一致）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://travel.qunar.com/',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f'  正在访问: {url}', end=' ')
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f'✗ 状态码: {response.status_code}')
            return {}
        
        soup = BeautifulSoup(response.text, 'lxml')
        detail = {}
        
        # 提取景点名称（中文）
        title = soup.find('h1', class_='cn_tit')
        if title:
            detail['name'] = title.get_text(strip=True)
        
        # 提取英文名称 - class名是entit
        en_title = soup.find('span', class_='entit')
        if en_title:
            detail['name_en'] = en_title.get_text(strip=True)
        else:
            # 也尝试en_tit（兼容旧版）
            en_title = soup.find('span', class_='en_tit')
            detail['name_en'] = en_title.get_text(strip=True) if en_title else ''
        
        # 提取评分
        score_span = soup.find('span', class_='cur_score')
        detail['score'] = score_span.get_text(strip=True) if score_span else ''
        
        # 提取点评数
        comment_link = soup.find('a', class_='comment_sum')
        if comment_link:
            comment_text = comment_link.get_text(strip=True)
            detail['comment_count'] = comment_text.replace('条点评', '').strip()
        
        # 提取地址 - 在dt/dd结构中
        address_dt = soup.find('dt', string='地址:')
        if address_dt:
            address_dd = address_dt.find_next('dd')
            if address_dd:
                detail['address'] = address_dd.get_text(strip=True)
        else:
            detail['address'] = ''
        
        # 提取开放时间
        opentime_dt = soup.find('dt', string='开放时间:')
        if opentime_dt:
            opentime_dd = opentime_dt.find_next('dd')
            if opentime_dd:
                detail['open_time'] = opentime_dd.get_text(strip=True)
        else:
            detail['open_time'] = ''
        
        # 提取门票价格 - 在门票section中
        ticket_section = soup.find('div', class_='b_detail_ticket')
        if ticket_section:
            ticket_content = ticket_section.find('div', class_='e_db_content_box')
            if ticket_content:
                detail['ticket_price'] = ticket_content.get_text(strip=True)
        else:
            detail['ticket_price'] = ''
        
        # 提取景点介绍 - 在概述section中
        intro_section = soup.find('div', class_='b_detail_intro')
        if intro_section:
            intro_content = intro_section.find('div', class_='e_db_content_box')
            if intro_content:
                detail['introduction'] = intro_content.get_text(strip=True)
        else:
            detail['introduction'] = '无'
        
        # 提取建议游览时间
        time_div = soup.find('div', class_='time')
        if time_div:
            time_text = time_div.get_text(strip=True)
            detail['suggested_duration'] = time_text.replace('建议游览时间：', '').strip()
        else:
            detail['suggested_duration'] = ''
        
        # 提取交通指南
        traffic_section = soup.find('div', class_='b_detail_traffic')
        if traffic_section:
            traffic_content = traffic_section.find('div', class_='e_db_content_box')
            if traffic_content:
                detail['traffic'] = traffic_content.get_text(strip=True)
        else:
            detail['traffic'] = ''
        
        # 提取旅游时节
        season_section = soup.find('div', class_='b_detail_season')
        if season_section:
            season_content = season_section.find('div', class_='e_db_content_box')
            if season_content:
                detail['best_season'] = season_content.get_text(strip=True)
        else:
            detail['best_season'] = '无'
        
        # 提取图片
        images = []
        img_list = soup.find('ul', id='idSlider')
        if img_list:
            img_tags = img_list.find_all('img')
            for img in img_tags:
                src = img.get('src', '') or img.get('data-src', '')
                if src and 'http' in src and 'noimg' not in src:
                    # 转换为标准格式
                    if '_r_480x360x95_' not in src:
                        src = src.replace('.jpg', '_480x360x95_' + src.split('/')[-1].split('.')[0][-8:] + '.jpg')
                    images.append(src)
        detail['images'] = images[:6]  # 最多6张
        
        # 提取电话
        phone_dt = soup.find('dt', string='电话:')
        if phone_dt:
            phone_dd = phone_dt.find_next('dd')
            if phone_dd:
                detail['phone'] = phone_dd.get_text(strip=True)
        else:
            detail['phone'] = ''
        
        # 提取官网
        website_dt = soup.find('dt', string='官网:')
        if website_dt:
            website_dd = website_dt.find_next('dd')
            if website_dd:
                website_link = website_dd.find('a')
                detail['website'] = website_link.get('href', '') if website_link else website_dd.get_text(strip=True)
        else:
            detail['website'] = '无'
        
        # 提取经纬度 - 从mapbox中的latlng属性
        map_box = soup.find('div', class_='mapbox')
        if map_box:
            latlng = map_box.get('latlng', '')
            if latlng:
                # latlng格式可能是 "lat,lng" 或 "lat|lng"
                if ',' in latlng:
                    lat, lng = latlng.split(',', 1)
                    detail['latitude'] = lat.strip()
                    detail['longitude'] = lng.strip()
                elif '|' in latlng:
                    lat, lng = latlng.split('|', 1)
                    detail['latitude'] = lat.strip()
                    detail['longitude'] = lng.strip()
                else:
                    detail['latitude'] = ''
                    detail['longitude'] = ''
            else:
                detail['latitude'] = ''
                detail['longitude'] = ''
        else:
            # 备用方案：尝试从js_map中获取
            map_div = soup.find('div', id='js_map')
            if map_div:
                detail['latitude'] = map_div.get('data-lat', '')
                detail['longitude'] = map_div.get('data-lng', '')
            else:
                detail['latitude'] = ''
                detail['longitude'] = ''
        
        # 提取攻略数
        strategy_link = soup.find('a', class_='strategy_sum')
        if strategy_link:
            strategy_text = strategy_link.get_text(strip=True)
            match = re.search(r'(\d+)', strategy_text)
            if match:
                detail['strategy_count'] = match.group(1)
        
        # 提取去过的驴友比例
        visitor_div = soup.find('div', class_='txtbox')
        if visitor_div:
            visitor_span = visitor_div.find('span', class_='sum')
            if visitor_span:
                detail['visitor_percentage'] = visitor_span.get_text(strip=True)
        
        print(f'✓')
        return detail
        
    except Exception as e:
        print(f'✗ 错误: {e}')
        return {}

def enrich_data_from_urls(input_file='my_data.csv', output_file='my_data_enriched.json'):
    """读取CSV，访问每个URL获取详细信息"""
    
    print('='*80)
    print('景点详细信息获取工具')
    print('='*80)
    print(f'\n输入文件: {input_file}')
    print(f'输出文件: {output_file}\n')
    
    # 读取CSV
    attractions = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        attractions = list(reader)
    
    print(f'✓ 已加载 {len(attractions)} 个景点\n')
    print('开始获取详细信息')
    print('-'*80)
    
    enriched_data = []
    
    for i, attraction in enumerate(attractions, 1):
        print(f'\n[{i}/{len(attractions)}] {attraction.get("name", "未知")}')
        
        url = attraction.get('url', '')
        if not url:
            print('  ✗ 无URL，跳过')
            enriched_data.append(attraction)
            continue
        
        # 获取详细信息
        detail = get_attraction_detail(url, attraction.get('name', ''))
        
        # 合并数据（详细信息优先，但保留原有的非空值）
        for key, value in detail.items():
            if value:  # 如果详细信息有值
                if value != '无' and value != '':  # 且不是默认值
                    attraction[key] = value
                elif not attraction.get(key) or attraction.get(key) == '':  # 原数据为空时才用默认值
                    attraction[key] = value
        
        # 确保images是列表格式
        if 'images' in attraction:
            if isinstance(attraction['images'], str):
                try:
                    attraction['images'] = eval(attraction['images'])
                except:
                    attraction['images'] = []
        
        # 确保所有必需字段都存在（与qunar_xian_attractions_final.csv一致）
        required_fields = {
            'rank': attraction.get('rank', ''),
            'name': attraction.get('name', ''),
            'name_en': attraction.get('name_en', ''),
            'url': attraction.get('url', ''),
            'strategy_count': attraction.get('strategy_count', '0'),
            'comment_count': attraction.get('comment_count', '0'),
            'visitor_percentage': attraction.get('visitor_percentage', ''),
            'rating': attraction.get('rating', '0'),
            'city_rank': attraction.get('city_rank', ''),
            'city': attraction.get('city', '北京'),
            'description': attraction.get('description', ''),
            'image': attraction.get('image', ''),
            'latitude': attraction.get('latitude', ''),
            'longitude': attraction.get('longitude', ''),
            'score': attraction.get('score', attraction.get('rating', '0')),
            'address': attraction.get('address', ''),
            'open_time': attraction.get('open_time', ''),
            'ticket_price': attraction.get('ticket_price', ''),
            'introduction': attraction.get('introduction', '无'),
            'suggested_duration': attraction.get('suggested_duration', ''),
            'traffic': attraction.get('traffic', ''),
            'best_season': attraction.get('best_season', '无'),
            'images': attraction.get('images', []),
            'phone': attraction.get('phone', ''),
            'website': attraction.get('website', '无'),
        }
        
        # 更新景点数据
        attraction.update(required_fields)
        enriched_data.append(attraction)
        
        # 每10个景点保存一次
        if i % 10 == 0:
            save_data(enriched_data, output_file)
            print(f'\n  💾 已保存进度 ({i}/{len(attractions)})')
        
        # 延迟
        if i < len(attractions):
            delay = random.uniform(3, 5)
            print(f'  等待 {delay:.1f} 秒...')
            time.sleep(delay)
    
    # 最终保存
    save_data(enriched_data, output_file)
    
    print('\n' + '='*80)
    print('✓ 获取完成！')
    print('='*80)
    
    # 统计
    has_address = sum(1 for item in enriched_data if item.get('address') and item['address'] != '无')
    has_phone = sum(1 for item in enriched_data if item.get('phone') and item['phone'] != '无')
    has_open_time = sum(1 for item in enriched_data if item.get('open_time') and item['open_time'] != '无')
    has_images = sum(1 for item in enriched_data if item.get('images') and len(item['images']) > 0)
    
    print(f'\n数据统计:')
    print(f'  总景点数: {len(enriched_data)}')
    print(f'  有地址: {has_address} 个')
    print(f'  有电话: {has_phone} 个')
    print(f'  有开放时间: {has_open_time} 个')
    print(f'  有图片: {has_images} 个')
    
    csv_file = output_file.replace('.json', '.csv')
    print(f'\n数据已保存到:')
    print(f'  - {output_file} (JSON格式)')
    print(f'  - {csv_file} (CSV格式)')

def save_data(data, output_file):
    """保存数据到JSON和CSV（字段顺序与qunar_xian_attractions_final.csv一致）"""
    # 保存JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 保存CSV - 使用固定的字段顺序
    csv_file = output_file.replace('.json', '.csv')
    if data:
        # 定义字段顺序（与qunar_xian_attractions_final.csv一致）
        fieldnames = [
            'rank', 'name', 'name_en', 'url', 'strategy_count', 'comment_count',
            'visitor_percentage', 'rating', 'city_rank', 'city', 'description',
            'image', 'latitude', 'longitude', 'score', 'address', 'open_time',
            'ticket_price', 'introduction', 'suggested_duration', 'traffic',
            'best_season', 'images', 'phone', 'website'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)

if __name__ == '__main__':
    import sys
    
    # 默认参数
    input_file = 'my_data.csv'
    output_file = 'my_data_enriched.json'
    
    # 命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    enrich_data_from_urls(input_file=input_file, output_file=output_file)

