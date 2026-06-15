from flask import Blueprint, jsonify, request
from Dao.AnalysisDao import *

analysis_api = Blueprint('analysis_api', __name__)

# 获取评分分布
@analysis_api.route('/rating_distribution', methods=['GET'])
def get_rating_distribution():
    try:
        data = GetRatingDistributionDao()
        result = [{'rating': int(item[0]), 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取评分分布错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取城市景点数量
@analysis_api.route('/city_attraction_count', methods=['GET'])
def get_city_attraction_count():
    try:
        data = GetCityAttractionCountDao()
        result = [{'city': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取城市景点数量错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取评论数TOP10景点
@analysis_api.route('/top_commented_attractions', methods=['GET'])
def get_top_commented_attractions():
    try:
        data = GetTopCommentedAttractionsDao()
        result = [{'name': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取热门景点错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取评分TOP10景点
@analysis_api.route('/top_rated_attractions', methods=['GET'])
def get_top_rated_attractions():
    try:
        data = GetTopRatedAttractionsDao()
        result = [{'name': item[0], 'rating': float(item[1])} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取高分景点错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取评论时间分布
@analysis_api.route('/comment_time_distribution', methods=['GET'])
def get_comment_time_distribution():
    try:
        data = GetCommentTimeDistributionDao()
        result = [{'year': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取评论时间分布错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取评论长度分布
@analysis_api.route('/comment_length_distribution', methods=['GET'])
def get_comment_length_distribution():
    try:
        data = GetCommentLengthDistributionDao()
        result = [{'type': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取评论长度分布错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取有图评论占比
@analysis_api.route('/image_comment_ratio', methods=['GET'])
def get_image_comment_ratio():
    try:
        data = GetImageCommentRatioDao()
        result = [{'type': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取有图评论占比错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 情感分析
@analysis_api.route('/sentiment_analysis', methods=['GET'])
def get_sentiment_analysis():
    try:
        data = AnalyzeCommentSentimentDao()
        result = [{'sentiment': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"情感分析错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取热门关键词
@analysis_api.route('/hot_keywords', methods=['GET'])
def get_hot_keywords():
    try:
        data = GetHotKeywordsDao()
        result = [{'keyword': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取热门关键词错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取用户活跃度
@analysis_api.route('/user_activity', methods=['GET'])
def get_user_activity():
    try:
        data = GetUserActivityDao()
        result = [{'username': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取用户活跃度错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取门票价格分布
@analysis_api.route('/ticket_price_distribution', methods=['GET'])
def get_ticket_price_distribution():
    try:
        data = GetTicketPriceDistributionDao()
        result = [{'range': item[0], 'count': item[1]} for item in data]
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': result
        })
    except Exception as e:
        print(f"获取门票价格分布错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })

# 获取综合统计
@analysis_api.route('/overall_statistics', methods=['GET'])
def get_overall_statistics():
    try:
        data = GetOverallStatisticsDao()
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': data
        })
    except Exception as e:
        print(f"获取综合统计错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '查询失败'
        })
