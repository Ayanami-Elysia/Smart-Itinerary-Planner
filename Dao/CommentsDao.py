import pymysql

# 数据库连接
def get_connection():
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='py_beijing')

# 查询评论列表（支持分页和搜索）
def ListCommentsDao(attraction_name=None, username=None, page=1, limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 构建基础查询语句
    base_sql = "SELECT * FROM comments WHERE 1=1"
    count_sql = "SELECT COUNT(*) FROM comments WHERE 1=1"
    params = []
    
    # 如果有景点名称参数,添加搜索条件
    if attraction_name:
        base_sql += " AND attraction_name LIKE %s"
        count_sql += " AND attraction_name LIKE %s"
        params.append(f"%{attraction_name}%")
    
    # 如果有用户名参数,添加搜索条件
    if username:
        base_sql += " AND username LIKE %s"
        count_sql += " AND username LIKE %s"
        params.append(f"%{username}%")
    
    # 获取总数
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    # 执行分页查询（按创建时间倒序）
    base_sql += " ORDER BY created_at DESC LIMIT %s, %s"
    cursor.execute(base_sql, params + [offset, limit])
    data = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    return {
        "total": total,
        "data": data
    }

# 根据ID查询评论详情
def GetCommentByIdDao(comment_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM comments WHERE id = %s"
        cursor.execute(sql, (comment_id,))
        comment = cursor.fetchone()
        cursor.close()
        conn.close()
        return comment
    except Exception as e:
        print(f"获取评论信息失败: {str(e)}")
        return None

# 根据景点名称查询评论
def GetCommentsByAttractionDao(attraction_name, page=1, limit=20):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取总数
        count_sql = "SELECT COUNT(*) FROM comments WHERE attraction_name = %s"
        cursor.execute(count_sql, (attraction_name,))
        total = cursor.fetchone()[0]
        
        # 查询评论列表
        sql = "SELECT * FROM comments WHERE attraction_name = %s ORDER BY created_at DESC LIMIT %s, %s"
        cursor.execute(sql, (attraction_name, offset, limit))
        comments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "data": comments
        }
    except Exception as e:
        print(f"查询景点评论失败: {str(e)}")
        return {"total": 0, "data": []}

# 根据用户名查询评论
def GetCommentsByUserDao(username, page=1, limit=20):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取总数
        count_sql = "SELECT COUNT(*) FROM comments WHERE username = %s"
        cursor.execute(count_sql, (username,))
        total = cursor.fetchone()[0]
        
        # 查询评论列表
        sql = "SELECT * FROM comments WHERE username = %s ORDER BY created_at DESC LIMIT %s, %s"
        cursor.execute(sql, (username, offset, limit))
        comments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "data": comments
        }
    except Exception as e:
        print(f"查询用户评论失败: {str(e)}")
        return {"total": 0, "data": []}

# 新增评论
def AddCommentDao(rank_num, attraction_name, attraction_url, city, rating, total_comments,
                 comment_title, comment_url, comment_rating, comment_content, image_count,
                 image_urls, comment_date, username, user_url):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO comments(rank_num, attraction_name, attraction_url, city, rating,
                total_comments, comment_title, comment_url, comment_rating, comment_content,
                image_count, image_urls, comment_date, username, user_url) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (rank_num, attraction_name, attraction_url, city, rating, total_comments,
                           comment_title, comment_url, comment_rating, comment_content, image_count,
                           image_urls, comment_date, username, user_url))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"新增评论失败: {str(e)}")
        return False

# 更新评论信息
def UpdateCommentDao(comment_id, rank_num, attraction_name, attraction_url, city, rating,
                    total_comments, comment_title, comment_url, comment_rating, comment_content,
                    image_count, image_urls, comment_date, username, user_url):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """UPDATE comments SET rank_num=%s, attraction_name=%s, attraction_url=%s, city=%s,
                rating=%s, total_comments=%s, comment_title=%s, comment_url=%s, comment_rating=%s,
                comment_content=%s, image_count=%s, image_urls=%s, comment_date=%s, username=%s,
                user_url=%s WHERE id=%s"""
        cursor.execute(sql, (rank_num, attraction_name, attraction_url, city, rating, total_comments,
                           comment_title, comment_url, comment_rating, comment_content, image_count,
                           image_urls, comment_date, username, user_url, comment_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"更新评论信息失败: {str(e)}")
        return False

# 删除评论
def DeleteCommentDao(comment_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM comments WHERE id = %s"
        cursor.execute(sql, (comment_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"删除评论失败: {str(e)}")
        return False

# 批量删除评论（根据景点名称）
def DeleteCommentsByAttractionDao(attraction_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM comments WHERE attraction_name = %s"
        cursor.execute(sql, (attraction_name,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows
    except Exception as e:
        print(f"批量删除评论失败: {str(e)}")
        return 0

# 搜索评论（模糊搜索评论内容）
def SearchCommentsDao(keyword):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """SELECT * FROM comments 
                WHERE comment_content LIKE %s OR comment_title LIKE %s 
                ORDER BY created_at DESC"""
        search_param = f"%{keyword}%"
        cursor.execute(sql, (search_param, search_param))
        comments = cursor.fetchall()
        cursor.close()
        conn.close()
        return comments
    except Exception as e:
        print(f"搜索评论失败: {str(e)}")
        return []

# 获取最新评论
def GetLatestCommentsDao(limit=10):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM comments ORDER BY created_at DESC LIMIT %s"
        cursor.execute(sql, (limit,))
        comments = cursor.fetchall()
        cursor.close()
        conn.close()
        return comments
    except Exception as e:
        print(f"获取最新评论失败: {str(e)}")
        return []

# 获取热门评论（按图片数量排序）
def GetHotCommentsDao(limit=10):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM comments WHERE image_count > 0 ORDER BY image_count DESC LIMIT %s"
        cursor.execute(sql, (limit,))
        comments = cursor.fetchall()
        cursor.close()
        conn.close()
        return comments
    except Exception as e:
        print(f"获取热门评论失败: {str(e)}")
        return []

# 统计评论数据
def GetCommentsStatsDao():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 总评论数
        cursor.execute("SELECT COUNT(*) FROM comments")
        total_count = cursor.fetchone()[0]
        
        # 有图片的评论数
        cursor.execute("SELECT COUNT(*) FROM comments WHERE image_count > 0")
        with_images = cursor.fetchone()[0]
        
        # 各景点评论数量排行
        cursor.execute("""SELECT attraction_name, COUNT(*) as count 
                         FROM comments 
                         GROUP BY attraction_name 
                         ORDER BY count DESC 
                         LIMIT 10""")
        attraction_stats = cursor.fetchall()
        
        # 活跃用户排行
        cursor.execute("""SELECT username, COUNT(*) as count 
                         FROM comments 
                         WHERE username IS NOT NULL 
                         GROUP BY username 
                         ORDER BY count DESC 
                         LIMIT 10""")
        user_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total_count": total_count,
            "with_images": with_images,
            "attraction_stats": attraction_stats,
            "user_stats": user_stats
        }
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        return None

# 获取景点的评论统计
def GetAttractionCommentStatsDao(attraction_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 评论总数
        cursor.execute("SELECT COUNT(*) FROM comments WHERE attraction_name = %s", (attraction_name,))
        total_count = cursor.fetchone()[0]
        
        # 有图片的评论数
        cursor.execute("SELECT COUNT(*) FROM comments WHERE attraction_name = %s AND image_count > 0", (attraction_name,))
        with_images = cursor.fetchone()[0]
        
        # 平均评分
        cursor.execute("SELECT AVG(comment_rating) FROM comments WHERE attraction_name = %s AND comment_rating > 0", (attraction_name,))
        avg_rating = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "total_count": total_count,
            "with_images": with_images,
            "avg_rating": float(avg_rating) if avg_rating else 0
        }
    except Exception as e:
        print(f"获取景点评论统计失败: {str(e)}")
        return None
