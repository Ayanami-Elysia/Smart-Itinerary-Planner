from flask import Blueprint, jsonify, request, render_template, session
from Dao.CommentsDao import *

comments_api = Blueprint('comments_api', __name__)

# 查询评论列表
@comments_api.route('/commentslist', methods=['POST'])
def get_comments_list():
    try:
        data = request.get_json()
        attraction_name = data.get('attraction_name')
        username = data.get('username')
        page = data.get('page', 1)
        limit = data.get('limit', 20)
        
        res = ListCommentsDao(attraction_name=attraction_name, username=username, page=page, limit=limit)
        data_list = res['data']
        total = res['total']
        
        comments_list = []
        for comment in data_list:
            body = {
                'id': comment[0],
                'rank_num': comment[1],
                'attraction_name': comment[2],
                'attraction_url': comment[3],
                'city': comment[4],
                'rating': float(comment[5]) if comment[5] else None,
                'total_comments': comment[6],
                'comment_title': comment[7],
                'comment_url': comment[8],
                'comment_rating': comment[9],
                'comment_content': comment[10],
                'image_count': comment[11],
                'image_urls': comment[12],
                'comment_date': comment[13],
                'username': comment[14],
                'user_url': comment[15],
                'created_at': str(comment[16]) if comment[16] else None
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': comments_list,
            'total': total,
            'code': 200
        })
    except Exception as e:
        print(f"查询评论列表错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 根据ID获取评论详情
@comments_api.route('/comment/<int:id>', methods=['GET'])
def get_comment_detail(id):
    try:
        comment = GetCommentByIdDao(id)
        
        if comment:
            data = {
                'id': comment[0],
                'rank_num': comment[1],
                'attraction_name': comment[2],
                'attraction_url': comment[3],
                'city': comment[4],
                'rating': float(comment[5]) if comment[5] else None,
                'total_comments': comment[6],
                'comment_title': comment[7],
                'comment_url': comment[8],
                'comment_rating': comment[9],
                'comment_content': comment[10],
                'image_count': comment[11],
                'image_urls': comment[12],
                'comment_date': comment[13],
                'username': comment[14],
                'user_url': comment[15],
                'created_at': str(comment[16]) if comment[16] else None
            }
            
            return jsonify({
                'msg': '查询成功',
                'data': data,
                'code': 200
            })
        else:
            return jsonify({
                'msg': '评论不存在',
                'code': 404
            })
    except Exception as e:
        print(f"查询评论详情错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 根据景点名称查询评论
@comments_api.route('/attraction/<attraction_name>', methods=['POST'])
def get_comments_by_attraction(attraction_name):
    try:
        data = request.get_json()
        page = data.get('page', 1)
        limit = data.get('limit', 20)
        
        res = GetCommentsByAttractionDao(attraction_name, page, limit)
        data_list = res['data']
        total = res['total']
        
        comments_list = []
        for comment in data_list:
            body = {
                'id': comment[0],
                'comment_content': comment[10],
                'comment_rating': comment[9],
                'image_count': comment[11],
                'image_urls': comment[12],
                'comment_date': comment[13],
                'username': comment[14]
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': comments_list,
            'total': total,
            'code': 200
        })
    except Exception as e:
        print(f"查询景点评论错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 根据用户名查询评论
@comments_api.route('/user/<username>', methods=['POST'])
def get_comments_by_user(username):
    try:
        data = request.get_json()
        page = data.get('page', 1)
        limit = data.get('limit', 20)
        
        res = GetCommentsByUserDao(username, page, limit)
        data_list = res['data']
        total = res['total']
        
        comments_list = []
        for comment in data_list:
            body = {
                'id': comment[0],
                'attraction_name': comment[2],
                'comment_content': comment[10],
                'comment_rating': comment[9],
                'image_count': comment[11],
                'comment_date': comment[13]
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': comments_list,
            'total': total,
            'code': 200
        })
    except Exception as e:
        print(f"查询用户评论错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 新增评论
@comments_api.route('/add', methods=['POST'])
def add_comment():
    try:
        data = request.get_json()
        
        rank_num = data.get('rank_num')
        attraction_name = data.get('attraction_name')
        attraction_url = data.get('attraction_url')
        city = data.get('city')
        rating = data.get('rating')
        total_comments = data.get('total_comments')
        comment_title = data.get('comment_title')
        comment_url = data.get('comment_url')
        comment_rating = data.get('comment_rating')
        comment_content = data.get('comment_content')
        image_count = data.get('image_count')
        image_urls = data.get('image_urls')
        comment_date = data.get('comment_date')
        username = data.get('username')
        user_url = data.get('user_url')
        
        # 验证必填字段
        if not attraction_name or not comment_content:
            return jsonify({
                'msg': '景点名称和评论内容不能为空',
                'code': 400
            })
        
        success = AddCommentDao(
            rank_num, attraction_name, attraction_url, city, rating, total_comments,
            comment_title, comment_url, comment_rating, comment_content, image_count,
            image_urls, comment_date, username, user_url
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
        print(f"添加评论错误: {str(e)}")
        return jsonify({
            'msg': '添加失败',
            'code': 500
        })

# 编辑评论
@comments_api.route('/edit', methods=['POST'])
def edit_comment():
    try:
        data = request.get_json()
        
        comment_id = data.get('id')
        rank_num = data.get('rank_num')
        attraction_name = data.get('attraction_name')
        attraction_url = data.get('attraction_url')
        city = data.get('city')
        rating = data.get('rating')
        total_comments = data.get('total_comments')
        comment_title = data.get('comment_title')
        comment_url = data.get('comment_url')
        comment_rating = data.get('comment_rating')
        comment_content = data.get('comment_content')
        image_count = data.get('image_count')
        image_urls = data.get('image_urls')
        comment_date = data.get('comment_date')
        username = data.get('username')
        user_url = data.get('user_url')
        
        # 验证必填字段
        if not comment_id or not attraction_name or not comment_content:
            return jsonify({
                'msg': 'ID、景点名称和评论内容不能为空',
                'code': 400
            })
        
        success = UpdateCommentDao(
            comment_id, rank_num, attraction_name, attraction_url, city, rating,
            total_comments, comment_title, comment_url, comment_rating, comment_content,
            image_count, image_urls, comment_date, username, user_url
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
        print(f"更新评论错误: {str(e)}")
        return jsonify({
            'msg': '更新失败',
            'code': 500
        })

# 删除评论
@comments_api.route('/delete/<int:id>', methods=['POST'])
def delete_comment(id):
    try:
        success = DeleteCommentDao(id)
        
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
        print(f"删除评论错误: {str(e)}")
        return jsonify({
            'msg': '删除失败',
            'code': 500
        })

# 批量删除评论（根据景点名称）
@comments_api.route('/delete_by_attraction', methods=['POST'])
def delete_comments_by_attraction():
    try:
        data = request.get_json()
        attraction_name = data.get('attraction_name')
        
        if not attraction_name:
            return jsonify({
                'msg': '景点名称不能为空',
                'code': 400
            })
        
        affected_rows = DeleteCommentsByAttractionDao(attraction_name)
        
        return jsonify({
            'msg': f'成功删除 {affected_rows} 条评论',
            'code': 200
        })
    except Exception as e:
        print(f"批量删除评论错误: {str(e)}")
        return jsonify({
            'msg': '删除失败',
            'code': 500
        })

# 搜索评论
@comments_api.route('/search', methods=['POST'])
def search_comments():
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        
        if not keyword:
            return jsonify({
                'msg': '搜索关键词不能为空',
                'code': 400
            })
        
        comments = SearchCommentsDao(keyword)
        
        comments_list = []
        for comment in comments:
            body = {
                'id': comment[0],
                'attraction_name': comment[2],
                'comment_content': comment[10],
                'comment_rating': comment[9],
                'username': comment[14],
                'comment_date': comment[13]
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '搜索成功',
            'data': comments_list,
            'code': 200
        })
    except Exception as e:
        print(f"搜索评论错误: {str(e)}")
        return jsonify({
            'msg': '搜索失败',
            'code': 500
        })

# 获取最新评论
@comments_api.route('/latest', methods=['GET'])
def get_latest_comments():
    try:
        limit = request.args.get('limit', 10, type=int)
        comments = GetLatestCommentsDao(limit)
        
        comments_list = []
        for comment in comments:
            body = {
                'id': comment[0],
                'attraction_name': comment[2],
                'comment_content': comment[10],
                'comment_rating': comment[9],
                'username': comment[14],
                'comment_date': comment[13],
                'created_at': str(comment[16]) if comment[16] else None
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': comments_list,
            'code': 200
        })
    except Exception as e:
        print(f"查询最新评论错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 获取热门评论
@comments_api.route('/hot', methods=['GET'])
def get_hot_comments():
    try:
        limit = request.args.get('limit', 10, type=int)
        comments = GetHotCommentsDao(limit)
        
        comments_list = []
        for comment in comments:
            body = {
                'id': comment[0],
                'attraction_name': comment[2],
                'comment_content': comment[10],
                'image_count': comment[11],
                'image_urls': comment[12],
                'username': comment[14],
                'comment_date': comment[13]
            }
            comments_list.append(body)
        
        return jsonify({
            'msg': '查询成功',
            'data': comments_list,
            'code': 200
        })
    except Exception as e:
        print(f"查询热门评论错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 获取评论统计数据
@comments_api.route('/stats', methods=['GET'])
def get_comments_stats():
    try:
        stats = GetCommentsStatsDao()
        
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

# 获取景点的评论统计
@comments_api.route('/attraction_stats/<attraction_name>', methods=['GET'])
def get_attraction_comment_stats(attraction_name):
    try:
        stats = GetAttractionCommentStatsDao(attraction_name)
        
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
        print(f"查询景点评论统计错误: {str(e)}")
        return jsonify({
            'msg': '查询失败',
            'code': 500
        })

# 编辑评论页面
@comments_api.route('/editcomment')
def edit_comment_page():
    comment_id = request.args.get('id')
    comment_tuple = GetCommentByIdDao(comment_id)
    
    if not comment_tuple:
        return "评论不存在", 404
    
    # 将元组转换为字典
    comment = {
        'id': comment_tuple[0],
        'rank_num': comment_tuple[1],
        'attraction_name': comment_tuple[2],
        'attraction_url': comment_tuple[3],
        'city': comment_tuple[4],
        'rating': comment_tuple[5],
        'total_comments': comment_tuple[6],
        'comment_title': comment_tuple[7],
        'comment_url': comment_tuple[8],
        'comment_rating': comment_tuple[9],
        'comment_content': comment_tuple[10],
        'image_count': comment_tuple[11],
        'image_urls': comment_tuple[12],
        'comment_date': comment_tuple[13],
        'username': comment_tuple[14],
        'user_url': comment_tuple[15]
    }
    
    return render_template('editcomment.html', comment=comment)
