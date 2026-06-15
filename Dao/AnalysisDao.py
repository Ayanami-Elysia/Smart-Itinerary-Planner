import pymysql
import re
from collections import Counter

# 数据库连接
def get_connection():
    return pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='py_beijing')

# 获取景点评分分布
def GetRatingDistributionDao():
    """获取景点评分分布"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 
                FLOOR(rating) as rating_level,
                COUNT(*) as count
            FROM attractions 
            WHERE rating IS NOT NULL
            GROUP BY FLOOR(rating)
            ORDER BY rating_level
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取评分分布失败: {str(e)}")
        return []

# 获取城市景点数量统计
def GetCityAttractionCountDao():
    """获取各城市景点数量"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT city, COUNT(*) as count
            FROM attractions
            WHERE city IS NOT NULL AND city != ''
            GROUP BY city
            ORDER BY count DESC
            LIMIT 10
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取城市景点数量失败: {str(e)}")
        return []

# 获取评论数量TOP10景点
def GetTopCommentedAttractionsDao():
    """获取评论数量最多的景点"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT name, comment_count
            FROM attractions
            WHERE comment_count IS NOT NULL
            ORDER BY comment_count DESC
            LIMIT 10
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取热门景点失败: {str(e)}")
        return []

# 获取评分TOP10景点
def GetTopRatedAttractionsDao():
    """获取评分最高的景点"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT name, rating
            FROM attractions
            WHERE rating IS NOT NULL
            ORDER BY rating DESC, comment_count DESC
            LIMIT 10
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取高分景点失败: {str(e)}")
        return []

# 获取评论时间分布
def GetCommentTimeDistributionDao():
    """获取评论时间分布（按年份）"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 
                SUBSTRING(comment_date, 1, 4) as year,
                COUNT(*) as count
            FROM comments
            WHERE comment_date IS NOT NULL AND comment_date != ''
            GROUP BY SUBSTRING(comment_date, 1, 4)
            ORDER BY year
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取评论时间分布失败: {str(e)}")
        return []

# 获取评论长度分布
def GetCommentLengthDistributionDao():
    """获取评论长度分布"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 
                CASE 
                    WHEN LENGTH(comment_content) < 20 THEN '短评(0-20字)'
                    WHEN LENGTH(comment_content) < 50 THEN '中评(20-50字)'
                    WHEN LENGTH(comment_content) < 100 THEN '长评(50-100字)'
                    ELSE '超长评(100字以上)'
                END as length_type,
                COUNT(*) as count
            FROM comments
            WHERE comment_content IS NOT NULL
            GROUP BY length_type
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取评论长度分布失败: {str(e)}")
        return []

# 获取有图评论占比
def GetImageCommentRatioDao():
    """获取有图评论占比"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 
                CASE WHEN image_count > 0 THEN '有图评论' ELSE '无图评论' END as type,
                COUNT(*) as count
            FROM comments
            GROUP BY type
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取有图评论占比失败: {str(e)}")
        return []

# 简单的情感分析（基于关键词）
def AnalyzeCommentSentimentDao():
    """分析评论情感倾向"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 定义情感关键词
        positive_keywords = ['好', '美', '棒', '赞', '喜欢', '推荐', '值得', '不错', '漂亮', '壮观', '震撼', '精彩']
        negative_keywords = ['差', '烂', '坑', '失望', '不好', '糟糕', '后悔', '不值', '一般', '无聊']
        
        sql = "SELECT comment_content FROM comments WHERE comment_content IS NOT NULL"
        cursor.execute(sql)
        comments = cursor.fetchall()
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for comment in comments:
            content = comment[0]
            pos_score = sum(1 for keyword in positive_keywords if keyword in content)
            neg_score = sum(1 for keyword in negative_keywords if keyword in content)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        cursor.close()
        conn.close()
        
        return [
            ('积极', positive_count),
            ('消极', negative_count),
            ('中性', neutral_count)
        ]
    except Exception as e:
        print(f"情感分析失败: {str(e)}")
        return []

# 获取热门关键词
def GetHotKeywordsDao():
    """提取评论中的热门关键词"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT comment_content FROM comments WHERE comment_content IS NOT NULL LIMIT 1000"
        cursor.execute(sql)
        comments = cursor.fetchall()
        
        # 定义常见关键词列表
        keywords = ['景色', '风景', '门票', '人多', '值得', '推荐', '漂亮', '美丽', '壮观', '历史', 
                   '文化', '古迹', '建筑', '拍照', '游客', '排队', '交通', '方便', '服务', '导游',
                   '兵马俑', '城墙', '大雁塔', '华清池', '华山', '博物馆', '钟楼', '鼓楼']
        
        keyword_counts = Counter()
        
        for comment in comments:
            content = comment[0]
            for keyword in keywords:
                if keyword in content:
                    keyword_counts[keyword] += 1
        
        cursor.close()
        conn.close()
        
        # 返回前20个热门关键词
        return keyword_counts.most_common(20)
    except Exception as e:
        print(f"获取热门关键词失败: {str(e)}")
        return []

# 获取用户活跃度分析
def GetUserActivityDao():
    """获取用户活跃度（评论数量分布）"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 
                username,
                COUNT(*) as comment_count
            FROM comments
            WHERE username IS NOT NULL AND username != '' AND username != '去哪儿用户'
            GROUP BY username
            HAVING comment_count > 1
            ORDER BY comment_count DESC
            LIMIT 15
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"获取用户活跃度失败: {str(e)}")
        return []

# 获取门票价格分布
def GetTicketPriceDistributionDao():
    """获取门票价格分布（兼容MySQL 5.7）"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 先获取所有门票价格数据
        sql = "SELECT ticket_price FROM attractions WHERE ticket_price IS NOT NULL"
        cursor.execute(sql)
        prices = cursor.fetchall()
        
        # 在Python中进行分类统计
        price_distribution = {
            '免费': 0,
            '0-50元': 0,
            '50-100元': 0,
            '100-150元': 0,
            '150元以上': 0,
            '其他': 0
        }
        
        import re
        for price_tuple in prices:
            price_str = price_tuple[0] if price_tuple[0] else ''
            
            # 判断是否免费
            if '免费' in price_str or price_str == '无' or price_str == '':
                price_distribution['免费'] += 1
            else:
                # 提取数字
                numbers = re.findall(r'\d+', price_str)
                if numbers:
                    # 取第一个数字作为价格
                    price_num = int(numbers[0])
                    if price_num < 50:
                        price_distribution['0-50元'] += 1
                    elif price_num < 100:
                        price_distribution['50-100元'] += 1
                    elif price_num < 150:
                        price_distribution['100-150元'] += 1
                    else:
                        price_distribution['150元以上'] += 1
                else:
                    price_distribution['其他'] += 1
        
        cursor.close()
        conn.close()
        
        # 转换为元组列表格式
        result = [(k, v) for k, v in price_distribution.items() if v > 0]
        return result
    except Exception as e:
        print(f"获取门票价格分布失败: {str(e)}")
        return []

# 获取综合统计数据
def GetOverallStatisticsDao():
    """获取综合统计数据"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 景点总数
        cursor.execute("SELECT COUNT(*) as count FROM attractions")
        stats['total_attractions'] = cursor.fetchone()[0]
        
        # 评论总数
        cursor.execute("SELECT COUNT(*) as count FROM comments")
        stats['total_comments'] = cursor.fetchone()[0]
        
        # 平均评分
        cursor.execute("SELECT AVG(rating) as avg_rating FROM attractions WHERE rating IS NOT NULL")
        result = cursor.fetchone()
        stats['avg_rating'] = round(float(result[0]), 2) if result[0] else 0
        
        # 有图评论数
        cursor.execute("SELECT COUNT(*) as count FROM comments WHERE image_count > 0")
        stats['image_comments'] = cursor.fetchone()[0]
        
        # 城市数量
        cursor.execute("SELECT COUNT(DISTINCT city) as count FROM attractions WHERE city IS NOT NULL AND city != ''")
        stats['total_cities'] = cursor.fetchone()[0]
        
        # 活跃用户数
        cursor.execute("SELECT COUNT(DISTINCT username) as count FROM comments WHERE username IS NOT NULL AND username != ''")
        stats['active_users'] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return stats
    except Exception as e:
        print(f"获取综合统计失败: {str(e)}")
        return {}
