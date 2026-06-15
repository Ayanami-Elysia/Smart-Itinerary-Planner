from flask import Blueprint, jsonify, request, render_template, session
from Dao.AttractionsDao import *

attractions_api = Blueprint('attractions_api', __name__)

# 查询景点列表
@attractions_api.route('/attractionslist', methods=['POST'])
def get_attractions_list():
    try:
        data = request.get_json()
        name = data.get('name')
        city = data.get('city')
        page = data.get('page', 1)
        limit = data.get('limit', 20)
        
        res = ListAttractionsDao(name=name, city=city, page=page, limit=limit)
        data_list = res['data']
        total = res['total']
        
        attractions_list = []
        for attraction in data_list:
            body = {
                'id': attraction[0],
                'rank_num': attraction[1],
                'name': attraction[2],
                'name_en': attraction[3],
                'url': attraction[4],
                'strategy_count': attraction[5],
                'comment_count': attraction[6],
                'visitor_percentage': attraction[7],
                'rating': float(attraction[8]) if attraction[8] else None,
                'city_rank': attraction[9],
                'city': attraction[10],
                'description': attraction[11],
                'image': attraction[12],
                'latitude': float(attraction[13]) if attraction[13] else None,
                'longitude': float(attraction[14]) if attraction[14] else None,
                'score': attraction[15],
                'address': attraction[16],
                'open_time': attraction[17],
                'ticket_price': attraction[18],
                'introduction': attraction[19],
                'suggested_duration': attraction[20],
                'traffic': attraction[21],
                'best_season': attraction[22],
                'images': attraction[23],
                'phone': attraction[24],
                'website': attraction[25]
            }
            attractions_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': attractions_list,
            'total': total,
            'code': 200
        })
    except Exception as e:
        print(f"查询景点列表错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 根据ID获取景点详情
@attractions_api.route('/attraction/<int:id>', methods=['GET'])
def get_attraction_detail(id):
    try:
        attraction = GetAttractionByIdDao(id)
        
        if attraction:
            data = {
                'id': attraction[0],
                'rank_num': attraction[1],
                'name': attraction[2],
                'name_en': attraction[3],
                'url': attraction[4],
                'strategy_count': attraction[5],
                'comment_count': attraction[6],
                'visitor_percentage': attraction[7],
                'rating': float(attraction[8]) if attraction[8] else None,
                'city_rank': attraction[9],
                'city': attraction[10],
                'description': attraction[11],
                'image': attraction[12],
                'latitude': float(attraction[13]) if attraction[13] else None,
                'longitude': float(attraction[14]) if attraction[14] else None,
                'score': attraction[15],
                'address': attraction[16],
                'open_time': attraction[17],
                'ticket_price': attraction[18],
                'introduction': attraction[19],
                'suggested_duration': attraction[20],
                'traffic': attraction[21],
                'best_season': attraction[22],
                'images': attraction[23],
                'phone': attraction[24],
                'website': attraction[25]
            }
            
            return jsonify({
                'msg': '查询成功',
                'data': data,
                'code': 200
            })
        else:
            return jsonify({
                'msg': '景点不存在',
                'code': 404
            })
    except Exception as e:
        print(f"查询景点详情错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 新增景点
@attractions_api.route('/add', methods=['POST'])
def add_attraction():
    try:
        data = request.get_json()
        
        rank_num = data.get('rank_num')
        name = data.get('name')
        name_en = data.get('name_en')
        url = data.get('url')
        strategy_count = data.get('strategy_count')
        comment_count = data.get('comment_count')
        visitor_percentage = data.get('visitor_percentage')
        rating = data.get('rating')
        city_rank = data.get('city_rank')
        city = data.get('city')
        description = data.get('description')
        image = data.get('image')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        score = data.get('score')
        address = data.get('address')
        open_time = data.get('open_time')
        ticket_price = data.get('ticket_price')
        introduction = data.get('introduction')
        suggested_duration = data.get('suggested_duration')
        traffic = data.get('traffic')
        best_season = data.get('best_season')
        images = data.get('images')
        phone = data.get('phone')
        website = data.get('website')
        
        # 验证必填字段
        if not name:
            return jsonify({
                'msg': '景点名称不能为空',
                'code': 400
            })
        
        success = AddAttractionDao(
            rank_num, name, name_en, url, strategy_count, comment_count,
            visitor_percentage, rating, city_rank, city, description, image,
            latitude, longitude, score, address, open_time, ticket_price,
            introduction, suggested_duration, traffic, best_season, images, phone, website
        )
        
        if success:
            return jsonify({
                'msg': '添加成功',
                'code': 200
            })
        else:
            return jsonify({
                'msg': '添加失败',
                'code': 500
            })
    except Exception as e:
        print(f"添加景点错误: {str(e)}")
        return jsonify({
            'msg': '添加失败',
            'code': 500
        })

# 编辑景点
@attractions_api.route('/edit', methods=['POST'])
def edit_attraction():
    try:
        data = request.get_json()
        
        attraction_id = data.get('id')
        rank_num = data.get('rank_num')
        name = data.get('name')
        name_en = data.get('name_en')
        url = data.get('url')
        strategy_count = data.get('strategy_count')
        comment_count = data.get('comment_count')
        visitor_percentage = data.get('visitor_percentage')
        rating = data.get('rating')
        city_rank = data.get('city_rank')
        city = data.get('city')
        description = data.get('description')
        image = data.get('image')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        score = data.get('score')
        address = data.get('address')
        open_time = data.get('open_time')
        ticket_price = data.get('ticket_price')
        introduction = data.get('introduction')
        suggested_duration = data.get('suggested_duration')
        traffic = data.get('traffic')
        best_season = data.get('best_season')
        images = data.get('images')
        phone = data.get('phone')
        website = data.get('website')
        
        # 验证必填字段
        if not attraction_id or not name:
            return jsonify({
                'msg': 'ID和景点名称不能为空',
                'code': 400
            })
        
        success = UpdateAttractionDao(
            attraction_id, rank_num, name, name_en, url, strategy_count, comment_count,
            visitor_percentage, rating, city_rank, city, description, image,
            latitude, longitude, score, address, open_time, ticket_price,
            introduction, suggested_duration, traffic, best_season, images, phone, website
        )
        
        if success:
            return jsonify({
                'msg': '更新成功',
                'code': 200
            })
        else:
            return jsonify({
                'msg': '更新失败',
                'code': 500
            })
    except Exception as e:
        print(f"更新景点错误: {str(e)}")
        return jsonify({
            'msg': '更新失败',
            'code': 500
        })

# 删除景点
@attractions_api.route('/delete/<int:id>', methods=['POST'])
def delete_attraction(id):
    try:
        success = DeleteAttractionDao(id)
        
        if success:
            return jsonify({
                'msg': '删除成功',
                'code': 200
            })
        else:
            return jsonify({
                'msg': '删除失败',
                'code': 500
            })
    except Exception as e:
        print(f"删除景点错误: {str(e)}")
        return jsonify({
            'msg': '删除失败',
            'code': 500
        })

# 根据城市查询景点
@attractions_api.route('/city/<city>', methods=['GET'])
def get_attractions_by_city(city):
    try:
        attractions = GetAttractionsByCityDao(city)
        
        attractions_list = []
        for attraction in attractions:
            body = {
                'id': attraction[0],
                'rank_num': attraction[1],
                'name': attraction[2],
                'name_en': attraction[3],
                'rating': float(attraction[8]) if attraction[8] else None,
                'city': attraction[10],
                'description': attraction[11],
                'image': attraction[12],
                'address': attraction[16],
                'ticket_price': attraction[18]
            }
            attractions_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': attractions_list,
            'code': 200
        })
    except Exception as e:
        print(f"查询城市景点错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 获取热门景点
@attractions_api.route('/top', methods=['GET'])
def get_top_attractions():
    try:
        limit = request.args.get('limit', 10, type=int)
        attractions = GetTopAttractionsDao(limit)
        
        attractions_list = []
        for attraction in attractions:
            body = {
                'id': attraction[0],
                'rank_num': attraction[1],
                'name': attraction[2],
                'name_en': attraction[3],
                'rating': float(attraction[8]) if attraction[8] else None,
                'comment_count': attraction[6],
                'city': attraction[10],
                'description': attraction[11],
                'image': attraction[12],
                'address': attraction[16]
            }
            attractions_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': attractions_list,
            'code': 200
        })
    except Exception as e:
        print(f"查询热门景点错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 搜索景点
@attractions_api.route('/search', methods=['POST'])
def search_attractions():
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        
        if not keyword:
            return jsonify({
                'msg': '搜索关键词不能为空',
                'code': 400
            })
        
        attractions = SearchAttractionsDao(keyword)
        
        attractions_list = []
        for attraction in attractions:
            body = {
                'id': attraction[0],
                'rank_num': attraction[1],
                'name': attraction[2],
                'name_en': attraction[3],
                'rating': float(attraction[8]) if attraction[8] else None,
                'city': attraction[10],
                'description': attraction[11],
                'image': attraction[12],
                'address': attraction[16]
            }
            attractions_list.append(body)
        
        return jsonify({
            'msg': '搜索成功',
            'data': attractions_list,
            'code': 200
        })
    except Exception as e:
        print(f"搜索景点错误: {str(e)}")
        return jsonify({
            'msg': '搜索失败',
            'code': 500
        })

# 获取所有城市列表
@attractions_api.route('/cities', methods=['GET'])
def get_all_cities():
    try:
        cities = GetAllCitiesDao()
        
        return jsonify({
            'msg': '查询成功',
            'data': cities,
            'code': 200
        })
    except Exception as e:
        print(f"查询城市列表错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 获取景点统计数据
@attractions_api.route('/stats', methods=['GET'])
def get_attractions_stats():
    try:
        stats = GetAttractionsStatsDao()
        
        if stats:
            return jsonify({
                'msg': '查询成功',
                'data': stats,
                'code': 200
            })
        else:
            return jsonify({
                'msg': '查询失败',
                'code': 500
            })
    except Exception as e:
        print(f"查询统计数据错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 编辑景点页面
@attractions_api.route('/editattraction')
def edit_attraction_page():
    attraction_id = request.args.get('id')
    attraction_tuple = GetAttractionByIdDao(attraction_id)
    
    if not attraction_tuple:
        return "景点不存在", 404
    
    # 将元组转换为字典
    attraction = {
        'id': attraction_tuple[0],
        'rank_num': attraction_tuple[1],
        'name': attraction_tuple[2],
        'name_en': attraction_tuple[3],
        'url': attraction_tuple[4],
        'strategy_count': attraction_tuple[5],
        'comment_count': attraction_tuple[6],
        'visitor_percentage': attraction_tuple[7],
        'rating': attraction_tuple[8],
        'city_rank': attraction_tuple[9],
        'city': attraction_tuple[10],
        'description': attraction_tuple[11],
        'image': attraction_tuple[12],
        'latitude': attraction_tuple[13],
        'longitude': attraction_tuple[14],
        'score': attraction_tuple[15],
        'address': attraction_tuple[16],
        'open_time': attraction_tuple[17],
        'ticket_price': attraction_tuple[18],
        'introduction': attraction_tuple[19],
        'suggested_duration': attraction_tuple[20],
        'traffic': attraction_tuple[21],
        'best_season': attraction_tuple[22],
        'images': attraction_tuple[23],
        'phone': attraction_tuple[24],
        'website': attraction_tuple[25]
    }
    
    return render_template('editattraction.html', attraction=attraction)
