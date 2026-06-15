from flask import Blueprint, jsonify, request, render_template, session as flask_session, redirect, make_response
from Dao.AttractionsDao import *
from Dao.CommentsDao import *
from Dao.db_connection import get_connection

frontend_api = Blueprint('frontend_api', __name__)
attraction_api = Blueprint('attraction_api', __name__)

@frontend_api.route('/attraction_home')
def attraction_home():
    response = make_response(render_template('frontend/attraction_home.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@frontend_api.route('/attraction_list')
def attraction_list():
    response = make_response(render_template('frontend/attraction_list.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@frontend_api.route('/attraction_detail')
def attraction_detail():
    response = make_response(render_template('frontend/attraction_detail.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@frontend_api.route('/path_recommendation')
def path_recommendation():
    response = make_response(render_template('frontend/path_recommendation.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@frontend_api.route('/attractionlist', methods=['POST'])
def get_attraction_list():
    try:
        data = request.get_json()
        attraction_name = data.get('attraction_name')
        city_name = data.get('city_name')
        page = data.get('page', 1)
        limit = data.get('limit', 12)
        
        res = ListAttractionsDao(name=attraction_name, city=city_name, page=page, limit=limit)
        data_list = res['data']
        total = res['total']
        
        attractions_list = []
        for attraction in data_list:
            body = {
                'id': attraction[0],
                'attraction_id': attraction[0],
                'attraction_name': attraction[2],
                'zone_name': attraction[10] if attraction[10] else '北京',
                'address': attraction[16] if attraction[16] else '',
                'comment_score': float(attraction[8]) if attraction[8] else 4.5,
                'comment_count': attraction[6] if attraction[6] else 0,
                'one_sentence_tag': attraction[11] if attraction[11] else '',
                'image_url': attraction[12] if attraction[12] else '',
                'star': attraction[1] if attraction[1] and attraction[1] <= 5 else 5,
                'hygiene_score': float(attraction[8]) if attraction[8] else 4.5,
                'facility_score': float(attraction[8]) if attraction[8] else 4.5,
                'environment_score': float(attraction[8]) if attraction[8] else 4.5,
                'service_score': float(attraction[8]) if attraction[8] else 4.5,
                'ticket_price': attraction[18] if attraction[18] else '免费',
                'open_time': attraction[17] if attraction[17] else '全天开放',
            }
            attractions_list.append(body)
        
        return jsonify({'msg': '查询成功', 'data': attractions_list, 'total': total, 'code': 200})
    except Exception as e:
        print(f"查询景点列表错误: {str(e)}")
        return jsonify({'msg': f'查询失败: {str(e)}', 'code': 500})

@frontend_api.route('/getAttractionInfo', methods=['GET'])
def get_attraction_info():
    try:
        attraction_id = request.args.get('id')
        if not attraction_id:
            return jsonify({'msg': '缺少景点ID参数', 'code': 400})
        
        attraction = GetAttractionByIdDao(attraction_id)
        if not attraction:
            return jsonify({'msg': '景点不存在', 'code': 404})
        
        attraction_info = {
            'id': attraction[0],
            'attraction_id': attraction[0],
            'attraction_name': attraction[2],
            'zone_name': attraction[10] if attraction[10] else '北京',
            'address': attraction[16] if attraction[16] else '',
            'comment_score': float(attraction[8]) if attraction[8] else 4.5,
            'comment_count': attraction[6] if attraction[6] else 0,
            'one_sentence_tag': attraction[11] if attraction[11] else '',
            'image_url': attraction[12] if attraction[12] else '',
            'star': attraction[1] if attraction[1] and attraction[1] <= 5 else 5,
            'hygiene_score': float(attraction[8]) if attraction[8] else 4.5,
            'facility_score': float(attraction[8]) if attraction[8] else 4.5,
            'environment_score': float(attraction[8]) if attraction[8] else 4.5,
            'service_score': float(attraction[8]) if attraction[8] else 4.5,
            'ticket_price': attraction[18] if attraction[18] else '免费',
            'open_time': attraction[17] if attraction[17] else '全天开放',
            'introduction': attraction[19] if attraction[19] else '',
            'suggested_duration': attraction[20] if attraction[20] else '2-3小时',
            'traffic': attraction[21] if attraction[21] else '',
            'best_season': attraction[22] if attraction[22] else '四季皆宜',
            'phone': attraction[24] if attraction[24] else '',
        }
        return jsonify({'msg': '查询成功', 'data': attraction_info, 'code': 200})
    except Exception as e:
        print(f"查询景点详情错误: {str(e)}")
        return jsonify({'msg': f'查询失败: {str(e)}', 'code': 500})

@frontend_api.route('/recommend', methods=['POST'])
def recommend_attractions():
    try:
        data = request.get_json()
        limit = data.get('limit', 6)
        user_id = flask_session.get('user_id')
        
        try:
            from Predictive.predictive import recommend_for_user, recommend_anonymous
            if user_id:
                result = recommend_for_user(user_id, limit=limit)
            else:
                result = recommend_anonymous(limit=limit)
            
            if result['success'] and result['recommendations']:
                attractions_list = []
                for rec in result['recommendations']:
                    attraction = GetAttractionByIdDao(rec['id'])
                    if attraction:
                        body = {
                            'id': attraction[0],
                            'attraction_id': attraction[0],
                            'attraction_name': attraction[2],
                            'zone_name': attraction[10] if attraction[10] else '北京',
                            'comment_score': float(attraction[8]) if attraction[8] else 4.5,
                            'comment_count': attraction[6] if attraction[6] else 0,
                            'one_sentence_tag': attraction[11] if attraction[11] else '',
                            'image_url': attraction[12] if attraction[12] else '',
                        }
                        attractions_list.append(body)
                return jsonify({'msg': '推荐成功', 'data': attractions_list, 'method': 'deep_learning', 'code': 200})
        except Exception as e:
            print(f"深度学习推荐失败: {e}")
        
        attractions = GetTopAttractionsDao(limit)
        attractions_list = []
        for attraction in attractions:
            body = {
                'id': attraction[0],
                'attraction_id': attraction[0],
                'attraction_name': attraction[2],
                'zone_name': attraction[10] if attraction[10] else '北京',
                'comment_score': float(attraction[8]) if attraction[8] else 4.5,
                'comment_count': attraction[6] if attraction[6] else 0,
                'one_sentence_tag': attraction[11] if attraction[11] else '',
                'image_url': attraction[12] if attraction[12] else '',
            }
            attractions_list.append(body)
        return jsonify({'msg': '推荐成功', 'data': attractions_list, 'method': 'traditional', 'code': 200})
    except Exception as e:
        print(f"推荐景点错误: {str(e)}")
        return jsonify({'msg': f'推荐失败: {str(e)}', 'code': 500})

@frontend_api.route('/commentlist', methods=['POST'])
def get_comment_list():
    try:
        data = request.get_json()
        attraction_id = data.get('attraction_id')
        page = data.get('page', 1)
        limit = data.get('limit', 10)
        
        attraction_name = None
        if attraction_id:
            attraction = GetAttractionByIdDao(attraction_id)
            if attraction:
                attraction_name = attraction[2]
        
        if attraction_name:
            res = GetCommentsByAttractionDao(attraction_name, page, limit)
        else:
            res = ListCommentsDao(page=page, limit=limit)
        
        data_list = res['data']
        total = res['total']
        
        comments_list = []
        for comment in data_list:
            body = {
                'id': comment[0],
                'user_name': comment[14] if comment[14] else '匿名用户',
                'user_level': 1,
                'comment_score': float(comment[9]) if comment[9] else 5.0,
                'comment_title': comment[7] if comment[7] else '',
                'comment_content': comment[10] if comment[10] else '',
                'comment_date': comment[13] if comment[13] else '',
                'room_type': '',
                'check_in_date': '',
                'useful_count': comment[11] if comment[11] else 0,
            }
            comments_list.append(body)
        
        return jsonify({'msg': '查询成功', 'data': comments_list, 'total': total, 'code': 200})
    except Exception as e:
        print(f"查询评论列表错误: {str(e)}")
        return jsonify({'msg': f'查询失败: {str(e)}', 'code': 500})

@frontend_api.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM attractions")
        total_attractions = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(rating) FROM attractions WHERE rating IS NOT NULL")
        avg_score = cursor.fetchone()[0]
        avg_score = float(avg_score) if avg_score else 4.5
        cursor.execute("SELECT COUNT(*) FROM comments")
        total_comments = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT city) FROM attractions WHERE city IS NOT NULL")
        city_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({'msg': '查询成功', 'data': {'totalAttractions': total_attractions, 'avgScore': round(avg_score, 1), 'totalComments': total_comments, 'cityCount': city_count}, 'code': 200})
    except Exception as e:
        print(f"查询统计数据错误: {str(e)}")
        return jsonify({'msg': f'查询失败: {str(e)}', 'code': 500})

@attraction_api.route('/attractionlist', methods=['POST'])
def attraction_get_attraction_list():
    return get_attraction_list()

@attraction_api.route('/getAttractionInfo', methods=['GET'])
def attraction_get_attraction_info():
    return get_attraction_info()

@attraction_api.route('/recommend', methods=['POST'])
def attraction_recommend_attractions():
    return recommend_attractions()

@attraction_api.route('/commentlist', methods=['POST'])
def attraction_get_comment_list():
    return get_comment_list()

@attraction_api.route('/stats', methods=['GET'])
def attraction_get_stats():
    return get_stats()
