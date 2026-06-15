# -*- coding: utf-8 -*-
"""旅游路径推荐API接口"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Predictive.predictive import recommend_for_user, recommend_anonymous
from Dao.db_connection import get_connection
import pymysql

path_recommendation_api = Blueprint('path_recommendation_api', __name__)

def get_travel_paths_by_filters(start_attraction_id, budget, companion_type, weather, limit=5):
    """
    根据用户条件过滤旅游路径
    
    参数:
        start_attraction_id: 起点景点ID
        budget: 预算
        companion_type: 陪伴类型
        weather: 天气
        limit: 返回数量
    
    返回:
        符合条件的旅游路径列表
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 构建SQL查询
        sql = """
            SELECT 
                id,
                user_id,
                path_name,
                attractions_ids,
                travel_date,
                duration_hours,
                total_cost,
                rating,
                companion_type,
                weather,
                satisfaction,
                notes,
                photos_count
            FROM travel_paths
            WHERE 1=1
        """
        
        params = []
        
        # 添加过滤条件
        if start_attraction_id:
            sql += " AND attractions_ids LIKE %s"
            params.append(f"%{start_attraction_id}%")
        
        if budget:
            sql += " AND total_cost <= %s"
            params.append(budget)
        
        if companion_type:
            sql += " AND companion_type = %s"
            params.append(companion_type)
        
        if weather:
            sql += " AND weather = %s"
            params.append(weather)
        
        # 按评分排序，限制数量
        sql += " ORDER BY rating DESC, satisfaction DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 转换为字典列表
        paths = []
        for row in results:
            path = {
                'id': row[0],
                'user_id': row[1],
                'path_name': row[2],
                'attractions_ids': row[3],
                'travel_date': str(row[4]),
                'duration_hours': float(row[5]),
                'total_cost': float(row[6]),
                'rating': float(row[7]),
                'companion_type': row[8],
                'weather': row[9],
                'satisfaction': int(row[10]),
                'notes': row[11],
                'photos_count': int(row[12])
            }
            paths.append(path)
        
        cursor.close()
        conn.close()
        
        return paths
        
    except Exception as e:
        print(f"查询旅游路径失败: {e}")
        return []

def get_attraction_name(attraction_id):
    """获取景点名称"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # 尝试多个可能的列名
        cursor.execute("SELECT name FROM attractions WHERE id = %s LIMIT 1", (attraction_id,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            conn.close()
            return result[0] if isinstance(result, tuple) else result.get('name', f'景点{attraction_id}')
        
        # 如果 name 列不存在，尝试 attraction_name
        cursor.execute("SELECT attraction_name FROM attractions WHERE id = %s LIMIT 1", (attraction_id,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            conn.close()
            return result[0] if isinstance(result, tuple) else result.get('attraction_name', f'景点{attraction_id}')
        
        cursor.close()
        conn.close()
        return f'景点{attraction_id}'
    except Exception as e:
        print(f"获取景点名称失败: {e}")
        return f'景点{attraction_id}'

@path_recommendation_api.route('/api/recommend_paths', methods=['POST'])
def recommend_paths():
    """旅游路径推荐接口"""
    try:
        data = request.get_json()
        
        start_attraction_id = data.get('start_attraction_id')
        budget = data.get('budget', 500)
        companion_type = data.get('companion_type')
        weather = data.get('weather')
        limit = data.get('limit', 5)
        
        print(f"收到推荐请求: start_attraction_id={start_attraction_id}, budget={budget}, companion_type={companion_type}, weather={weather}, limit={limit}")
        
        if not start_attraction_id or not companion_type or not weather:
            return jsonify({
                'code': 400,
                'msg': '缺少必要参数',
                'data': []
            })
        
        # 获取起点景点名称
        start_attraction_name = get_attraction_name(start_attraction_id)
        print(f"起点景点名称: {start_attraction_name}")
        
        # 生成推荐路线 - 基于起点和其他条件
        paths = []
        
        # 根据预算调整费用
        base_cost = budget * 0.6
        
        # 根据天气调整时长
        weather_hours_adjust = {
            '晴天': 0,
            '多云': 0.5,
            '阴天': 1,
            '小雨': 1.5,
            '雾霾': 2
        }
        hours_adjust = weather_hours_adjust.get(weather, 0)
        
        # 常见的北京景点组合
        destination_pairs = [
            ('天安门', '故宫'),
            ('颐和园', '圆明园'),
            ('长城', '明十三陵'),
            ('天坛', '国家博物馆'),
            ('景山公园', '北海公园'),
            ('798艺术区', '三里屯'),
            ('香山公园', '植物园'),
            ('朝阳公园', '龙潭湖公园'),
            ('清华大学', '北京大学'),
            ('古北水镇', '司马台长城'),
        ]
        
        # 生成推荐路线
        for idx in range(limit):
            if idx < len(destination_pairs):
                dest1, dest2 = destination_pairs[idx]
            else:
                # 如果超过预定义的组合数，循环使用
                dest1, dest2 = destination_pairs[idx % len(destination_pairs)]
            
            # 根据索引调整参数
            hours_base = 5 + (idx % 5)  # 5-9小时
            cost_adjust = 0.8 + (idx % 3) * 0.2  # 0.8-1.2倍
            rating_adjust = 0.1 * (idx % 5)  # 评分递减
            
            path = {
                'id': idx + 1,
                'path_name': f'{start_attraction_name} → {dest1} → {dest2}',
                'duration_hours': round(hours_base + hours_adjust, 1),
                'total_cost': int(base_cost * cost_adjust),
                'rating': round(4.8 - rating_adjust, 1),
                'companion_type': companion_type,
                'weather': weather,
                'satisfaction': max(1, 5 - (idx // 3)),
                'notes': f'推荐路线 {idx + 1}：从{start_attraction_name}出发，适合{companion_type}，{weather}天气推荐'
            }
            paths.append(path)
        
        print(f"返回推荐结果: {len(paths)} 条路线，起点: {start_attraction_name}")
        
        return jsonify({
            'code': 200,
            'msg': '推荐成功',
            'data': paths
        })
        
    except Exception as e:
        print(f"推荐接口错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'msg': f'推荐失败: {str(e)}',
            'data': []
        })

@path_recommendation_api.route('/api/path_recommendation', methods=['GET'])
def path_recommendation_page():
    """旅游路径推荐页面"""
    from flask import render_template
    return render_template('frontend/path_recommendation.html')

@path_recommendation_api.route('/api/get_attractions', methods=['GET'])
def get_attractions():
    """获取所有景点列表"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM attractions ORDER BY id LIMIT 200")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        attractions = [{'id': r[0], 'name': r[1]} for r in results]
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': attractions
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'获取失败: {str(e)}',
            'data': []
        })

@path_recommendation_api.route('/api/path_stats', methods=['GET'])
def path_stats():
    """获取旅游路径统计信息"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 总路径数
        cursor.execute("SELECT COUNT(*) FROM travel_paths")
        total_paths = cursor.fetchone()[0]
        
        # 平均评分
        cursor.execute("SELECT AVG(rating) FROM travel_paths")
        avg_rating = cursor.fetchone()[0] or 0
        
        # 平均花费
        cursor.execute("SELECT AVG(total_cost) FROM travel_paths")
        avg_cost = cursor.fetchone()[0] or 0
        
        # 平均时长
        cursor.execute("SELECT AVG(duration_hours) FROM travel_paths")
        avg_duration = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': {
                'total_paths': total_paths,
                'avg_rating': round(avg_rating, 2),
                'avg_cost': round(avg_cost, 2),
                'avg_duration': round(avg_duration, 1)
            }
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'获取失败: {str(e)}',
            'data': {}
        })

@path_recommendation_api.route('/api/companion_types', methods=['GET'])
def get_companion_types():
    """获取陪伴类型列表"""
    companion_types = ['独自一人', '情侣', '家人', '朋友', '同事']
    return jsonify({
        'code': 0,
        'msg': '获取成功',
        'data': companion_types
    })

@path_recommendation_api.route('/api/weather_types', methods=['GET'])
def get_weather_types():
    """获取天气类型列表"""
    weather_types = ['晴天', '多云', '阴天', '小雨', '雾霾']
    return jsonify({
        'code': 0,
        'msg': '获取成功',
        'data': weather_types
    })

@path_recommendation_api.route('/api/path_detail/<int:path_id>', methods=['GET'])
def get_path_detail(path_id):
    """获取单条路径详情"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, user_id, path_name, attractions_ids, travel_date,
                duration_hours, total_cost, rating, companion_type,
                weather, satisfaction, notes, photos_count
            FROM travel_paths
            WHERE id = %s
        """, (path_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({
                'code': 1,
                'msg': '路径不存在',
                'data': {}
            })
        
        path = {
            'id': result[0],
            'user_id': result[1],
            'path_name': result[2],
            'attractions_ids': result[3],
            'travel_date': str(result[4]),
            'duration_hours': float(result[5]),
            'total_cost': float(result[6]),
            'rating': float(result[7]),
            'companion_type': result[8],
            'weather': result[9],
            'satisfaction': int(result[10]),
            'notes': result[11],
            'photos_count': int(result[12])
        }
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': path
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'获取失败: {str(e)}',
            'data': {}
        })

@path_recommendation_api.route('/api/popular_paths', methods=['GET'])
def get_popular_paths():
    """获取热门路径"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, path_name, duration_hours, total_cost, rating,
                companion_type, weather, satisfaction, notes
            FROM travel_paths
            ORDER BY rating DESC, satisfaction DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        paths = []
        for row in results:
            path = {
                'id': row[0],
                'path_name': row[1],
                'duration_hours': float(row[2]),
                'total_cost': float(row[3]),
                'rating': float(row[4]),
                'companion_type': row[5],
                'weather': row[6],
                'satisfaction': int(row[7]),
                'notes': row[8]
            }
            paths.append(path)
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': paths
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'msg': f'获取失败: {str(e)}',
            'data': []
        })
