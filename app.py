from flask import Flask, render_template, request, redirect, url_for, jsonify, session as flask_session
from Controller.UserAPI import *
from Controller.AttractionsAPI import *
from Controller.CommentsAPI import *
from Controller.AnalysisAPI import *
from Controller.FrontendAPI import frontend_api, attraction_api
from Controller.PathRecommendationAPI import path_recommendation_api
from flask_cors import CORS
import hashlib
import os

app = Flask(__name__)
# 设置 secret_key 来保证 session 的安全性
app.secret_key = os.urandom(24)  # 使用随机生成的 24 字节密钥
CORS(app)
app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(attractions_api, url_prefix='/attractions')
app.register_blueprint(comments_api, url_prefix='/comments')
app.register_blueprint(analysis_api, url_prefix='/analysis')
app.register_blueprint(frontend_api, url_prefix='/frontend')
app.register_blueprint(attraction_api, url_prefix='/attraction')  # API调用路径
app.register_blueprint(path_recommendation_api)  # 旅游路径推荐API



@app.route('/')
def index():
    return render_template("login.html")

@app.route('/index')
@app.route('/index.html')
def index1():
    # 获取统计数据
    from Dao.db_connection import get_connection
    
    # 初始化默认值
    stats = {
        'user_count': 0,
        'news_count': 0,
        'report_count': 0,
        'last_update': None
    }
    
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # 获取用户数量
            cursor.execute("SELECT COUNT(*) as count FROM py_user")
            result = cursor.fetchone()
            if result and 'count' in result:
                stats['user_count'] = result['count']
                
            # 获取新闻数量
            cursor.execute("SELECT COUNT(*) as count FROM news")
            result = cursor.fetchone()
            if result and 'count' in result:
                stats['news_count'] = result['count']
                
            # 获取最近更新时间（从新闻表）
            cursor.execute("SELECT update_time FROM news ORDER BY update_time DESC LIMIT 1")
            result = cursor.fetchone()
            if result and 'update_time' in result:
                from datetime import datetime
                last_update = result['update_time']
                now = datetime.now()
                
                # 计算天数差
                if isinstance(last_update, datetime):
                    days_diff = (now - last_update).days
                    if days_diff == 0:
                        stats['last_update'] = "今天"
                    else:
                        stats['last_update'] = f"{days_diff}天前"
                else:
                    stats['last_update'] = "未知"
            else:
                stats['last_update'] = "未知"
                
            # 模拟分析报告数量（实际项目中应从对应表获取）
            stats['report_count'] = 6
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"获取统计数据失败: {e}")
    
    return render_template("index.html", stats=stats)

@app.route('/frontend')
def frontend_home():
    """用户前端首页"""
    # 获取统计数据
    from Dao.db_connection import get_connection
    
    # 初始化默认值
    stats = {
        'user_count': 0,
        'news_count': 0,
        'report_count': 0,
        'dataset_count': 0,
        'customer_count': 0
    }
    
    latest_news = []
    
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # 获取用户数量
            cursor.execute("SELECT COUNT(*) as count FROM py_user")
            result = cursor.fetchone()
            if result and 'count' in result:
                stats['user_count'] = result['count']
                
            # 获取新闻数量
            cursor.execute("SELECT COUNT(*) as count FROM news")
            result = cursor.fetchone()
            if result and 'count' in result:
                stats['news_count'] = result['count']
            
            # 模拟其他统计数据
            stats['report_count'] = stats['news_count'] * 5 or 25000 # 模拟生成报告数
            stats['dataset_count'] = int(stats['news_count'] / 5) + 1000 # 模拟数据集数量
            stats['customer_count'] = int(stats['user_count'] / 10) + 200 # 模拟企业客户数
            
            # 获取最新3条新闻
            cursor.execute("""
                SELECT
                    id, title, summary, content, cover_image, 
                    author, category, status,
                    DATE_FORMAT(create_time, '%%Y-%%m-%%d') as create_time
                FROM news 
                WHERE status = 1
                ORDER BY create_time DESC
                LIMIT 3
            """)
            latest_news = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"获取前端统计数据失败: {e}")
    
    # 使用新版前端模板
    return render_template("frontend/home_v2.html", stats=stats, latest_news=latest_news)

@app.route('/frontend/profile')
def frontend_profile():
    """用户个人资料页面"""
    # 检查用户是否登录
    if not flask_session.get('logged_in'):
        return redirect('/login')
    
    user_id = flask_session.get('user_id')
    
    # 从数据库获取用户详细信息
    from Dao.UserDao import get_user_by_id
    
    user_info = get_user_by_id(user_id)
    
    if user_info:
        user = {
            'id': user_info[0],
            'username': user_info[1],
            'nickname': user_info[3],
            'sex': user_info[4],
            'age': user_info[5],
            'phone': user_info[6],
            'email': user_info[7],
            'birthday': user_info[8],
            'card': user_info[9],
            'content': user_info[10],
            'remarks': user_info[11],
            'role': flask_session.get('role')
        }
        
        return render_template("frontend/profile.html", user=user)
    else:
        return redirect('/login')

@app.route('/frontend/news')
def frontend_news():
    """新闻列表页面"""
    from Dao.db_connection import get_connection
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    news_list = []
    total_count = 0
    
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = "status = 1"
            params = []
            
            if category:
                where_clause += " AND category = %s"
                params.append(category)
                
            if keyword:
                where_clause += " AND (title LIKE %s OR summary LIKE %s OR content LIKE %s)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param])
            
            # 获取总记录数
            count_sql = f"SELECT COUNT(*) as count FROM news WHERE {where_clause}"
            cursor.execute(count_sql, params)
            result = cursor.fetchone()
            if result and 'count' in result:
                total_count = result['count']
            
            # 获取分页数据
            news_sql = f"""
                SELECT
                    id, title, summary, content, cover_image, 
                    author, category, status,
                    DATE_FORMAT(create_time, '%%Y-%%m-%%d') as create_time
                FROM news 
                WHERE {where_clause}
                ORDER BY create_time DESC
                LIMIT %s, %s
            """
            
            # 添加分页参数
            params.extend([offset, limit])
            
            cursor.execute(news_sql, params)
            news_list = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"获取新闻列表失败: {e}")
    
    # 计算总页数
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    return render_template(
        "frontend/news.html", 
        news_list=news_list, 
        total_count=total_count,
        current_page=page,
        total_pages=total_pages,
        category=category,
        request=request
    )

@app.route('/frontend/news/<int:news_id>')
def frontend_news_detail(news_id):
    """新闻详情页面"""
    from Dao.db_connection import get_connection
    from Dao.NewsDao import get_news_by_id, update_view_count
    
    news = None
    related_news = []
    prev_news = None
    next_news = None
    
    try:
        # 获取新闻详情
        news_data = get_news_by_id(news_id)
        if news_data:
            news = {
                'id': news_data[0],
                'title': news_data[1],
                'summary': news_data[2],
                'content': news_data[3],
                'cover_image': news_data[4],
                'images': news_data[5],
                'author': news_data[6],
                'category': news_data[7],
                'status': news_data[8],
                'view_count': news_data[9],
                'create_time': news_data[10],
                'update_time': news_data[11]
            }
            
            # 更新浏览量
            update_view_count(news_id)
            
            # 获取相关数据
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                
                # 获取相关新闻（同类别的其他新闻）
                related_sql = """
                    SELECT
                        id, title, cover_image, category,
                        DATE_FORMAT(create_time, '%%Y-%%m-%%d') as create_time
                    FROM news 
                    WHERE status = 1 AND category = %s AND id != %s
                    ORDER BY create_time DESC
                    LIMIT 4
                """
                
                cursor.execute(related_sql, (news['category'], news_id))
                related_news = cursor.fetchall()
                
                # 获取上一篇文章
                prev_sql = """
                    SELECT id, title
                    FROM news
                    WHERE status = 1 AND create_time < (
                        SELECT create_time FROM news WHERE id = %s
                    )
                    ORDER BY create_time DESC
                    LIMIT 1
                """
                
                cursor.execute(prev_sql, (news_id,))
                prev_result = cursor.fetchone()
                if prev_result:
                    prev_news = {
                        'id': prev_result['id'],
                        'title': prev_result['title']
                    }
                
                # 获取下一篇文章
                next_sql = """
                    SELECT id, title
                    FROM news
                    WHERE status = 1 AND create_time > (
                        SELECT create_time FROM news WHERE id = %s
                    )
                    ORDER BY create_time ASC
                    LIMIT 1
                """
                
                cursor.execute(next_sql, (news_id,))
                next_result = cursor.fetchone()
                if next_result:
                    next_news = {
                        'id': next_result['id'],
                        'title': next_result['title']
                    }
                
                cursor.close()
                conn.close()
        
    except Exception as e:
        print(f"获取新闻详情失败: {e}")
    
    # 如果新闻不存在，重定向到新闻列表页
    if not news:
        return redirect('/frontend/news')
    
    return render_template(
        "frontend/news_detail.html", 
        news=news,
        related_news=related_news,
        prev_news=prev_news,
        next_news=next_news,
        request=request
    )

@app.route('/home')
def home():
    return render_template("base.html")

@app.route('/userlist')
def user_list():
    # 传递包含至少一个菜单项的示例数据

    return render_template("userlist.html")


@app.route('/newlist')
def newslist():
    # 传递包含至少一个菜单项的示例数据

    return render_template("newlist.html")

@app.route('/adminlist')
def adminlist():
    # 传递包含至少一个菜单项的示例数据

    return render_template("adminlist.html")

@app.route('/attractionslist')
def attractions_list():
    """景点列表页面"""
    return render_template("attractionslist.html")

@app.route('/commentslist')
def comments_list():
    """评论列表页面"""
    return render_template("commentslist.html")

@app.route('/analysis')
def analysis_page():
    """数据分析页面"""
    return render_template("analysis.html")


if __name__ == '__main__':
    app.run(debug=True)