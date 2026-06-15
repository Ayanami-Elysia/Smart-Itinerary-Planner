import pymysql

# 数据库连接
def get_connection():
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='py_beijing')

# 查询景点列表（支持分页和搜索）
def ListAttractionsDao(name=None, city=None, page=1, limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 计算偏移量
    offset = (page - 1) * limit
    
    # 构建基础查询语句
    base_sql = "SELECT * FROM attractions WHERE 1=1"
    count_sql = "SELECT COUNT(*) FROM attractions WHERE 1=1"
    params = []
    
    # 如果有景点名称参数,添加搜索条件
    if name:
        base_sql += " AND name LIKE %s"
        count_sql += " AND name LIKE %s"
        params.append(f"%{name}%")
    
    # 如果有城市参数,添加搜索条件
    if city:
        base_sql += " AND city LIKE %s"
        count_sql += " AND city LIKE %s"
        params.append(f"%{city}%")
    
    # 获取总数
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    # 执行分页查询
    base_sql += " ORDER BY rank_num LIMIT %s, %s"
    cursor.execute(base_sql, params + [offset, limit])
    data = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    return {
        "total": total,
        "data": data
    }

# 根据ID查询景点详情
def GetAttractionByIdDao(attraction_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM attractions WHERE id = %s"
        cursor.execute(sql, (attraction_id,))
        attraction = cursor.fetchone()
        cursor.close()
        conn.close()
        return attraction
    except Exception as e:
        print(f"获取景点信息失败: {str(e)}")
        return None

# 新增景点
def AddAttractionDao(rank_num, name, name_en, url, strategy_count, comment_count, 
                     visitor_percentage, rating, city_rank, city, description, image,
                     latitude, longitude, score, address, open_time, ticket_price,
                     introduction, suggested_duration, traffic, best_season, images, phone, website):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO attractions(rank_num, name, name_en, url, strategy_count, comment_count,
                visitor_percentage, rating, city_rank, city, description, image, latitude, longitude,
                score, address, open_time, ticket_price, introduction, suggested_duration, traffic,
                best_season, images, phone, website) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (rank_num, name, name_en, url, strategy_count, comment_count,
                           visitor_percentage, rating, city_rank, city, description, image,
                           latitude, longitude, score, address, open_time, ticket_price,
                           introduction, suggested_duration, traffic, best_season, images, phone, website))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"新增景点失败: {str(e)}")
        return False

# 更新景点信息
def UpdateAttractionDao(attraction_id, rank_num, name, name_en, url, strategy_count, comment_count,
                       visitor_percentage, rating, city_rank, city, description, image,
                       latitude, longitude, score, address, open_time, ticket_price,
                       introduction, suggested_duration, traffic, best_season, images, phone, website):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """UPDATE attractions SET rank_num=%s, name=%s, name_en=%s, url=%s, strategy_count=%s,
                comment_count=%s, visitor_percentage=%s, rating=%s, city_rank=%s, city=%s,
                description=%s, image=%s, latitude=%s, longitude=%s, score=%s, address=%s,
                open_time=%s, ticket_price=%s, introduction=%s, suggested_duration=%s, traffic=%s,
                best_season=%s, images=%s, phone=%s, website=%s WHERE id=%s"""
        cursor.execute(sql, (rank_num, name, name_en, url, strategy_count, comment_count,
                           visitor_percentage, rating, city_rank, city, description, image,
                           latitude, longitude, score, address, open_time, ticket_price,
                           introduction, suggested_duration, traffic, best_season, images, phone, website, attraction_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"更新景点信息失败: {str(e)}")
        return False

# 删除景点
def DeleteAttractionDao(attraction_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM attractions WHERE id = %s"
        cursor.execute(sql, (attraction_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"删除景点失败: {str(e)}")
        return False

# 根据城市查询景点
def GetAttractionsByCityDao(city):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM attractions WHERE city = %s ORDER BY rank_num"
        cursor.execute(sql, (city,))
        attractions = cursor.fetchall()
        cursor.close()
        conn.close()
        return attractions
    except Exception as e:
        print(f"查询城市景点失败: {str(e)}")
        return []

# 获取热门景点（按评分排序）
def GetTopAttractionsDao(limit=10):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM attractions WHERE rating IS NOT NULL ORDER BY rating DESC, comment_count DESC LIMIT %s"
        cursor.execute(sql, (limit,))
        attractions = cursor.fetchall()
        cursor.close()
        conn.close()
        return attractions
    except Exception as e:
        print(f"查询热门景点失败: {str(e)}")
        return []

# 搜索景点（模糊搜索名称、地址、描述）
def SearchAttractionsDao(keyword):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """SELECT * FROM attractions 
                WHERE name LIKE %s OR address LIKE %s OR description LIKE %s 
                ORDER BY rank_num"""
        search_param = f"%{keyword}%"
        cursor.execute(sql, (search_param, search_param, search_param))
        attractions = cursor.fetchall()
        cursor.close()
        conn.close()
        return attractions
    except Exception as e:
        print(f"搜索景点失败: {str(e)}")
        return []

# 获取所有城市列表
def GetAllCitiesDao():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT DISTINCT city FROM attractions WHERE city IS NOT NULL AND city != '' ORDER BY city"
        cursor.execute(sql)
        cities = cursor.fetchall()
        cursor.close()
        conn.close()
        return [city[0] for city in cities]
    except Exception as e:
        print(f"获取城市列表失败: {str(e)}")
        return []

# 统计景点数据
def GetAttractionsStatsDao():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 总景点数
        cursor.execute("SELECT COUNT(*) FROM attractions")
        total_count = cursor.fetchone()[0]
        
        # 平均评分
        cursor.execute("SELECT AVG(rating) FROM attractions WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        
        # 各城市景点数量
        cursor.execute("SELECT city, COUNT(*) as count FROM attractions WHERE city IS NOT NULL GROUP BY city ORDER BY count DESC")
        city_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total_count": total_count,
            "avg_rating": float(avg_rating) if avg_rating else 0,
            "city_stats": city_stats
        }
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        return None
