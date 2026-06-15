"""
CSV数据导入数据库脚本
将景点数据和评论数据从CSV文件导入到MySQL数据库
"""

import pandas as pd
import pymysql
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'py_beijing',
    'charset': 'utf8mb4'
}

# CSV文件路径
ATTRACTIONS_CSV = r"my_data_enriched_with_pinyin.csv"
COMMENTS_CSV = r"my_data_comments_flat.csv"

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def clean_value(value):
    """清理数据值"""
    if pd.isna(value) or value == '' or value == '无':
        return None
    return str(value).strip()

def import_attractions():
    """导入景点数据"""
    print("=" * 70)
    print("开始导入景点数据")
    print("=" * 70)
    
    try:
        # 读取CSV文件
        print("\n[1/4] 读取CSV文件...")
        df = pd.read_csv(ATTRACTIONS_CSV, encoding='utf-8')
        print(f"   ✓ 读取成功，共 {len(df)} 条景点数据")
        
        # 连接数据库
        print("\n[2/4] 连接数据库...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("   ✓ 数据库连接成功")
        
        # 清空现有数据
        print("\n[3/4] 清空现有数据...")
        cursor.execute("TRUNCATE TABLE attractions")
        conn.commit()
        print("   ✓ 已清空 attractions 表")
        
        # 插入数据
        print("\n[4/4] 插入景点数据...")
        
        insert_sql = """
        INSERT INTO attractions (
            rank_num, name, name_en, url, strategy_count, comment_count,
            visitor_percentage, rating, city_rank, city, description, image,
            latitude, longitude, score, address, open_time, ticket_price,
            introduction, suggested_duration, traffic, best_season, images,
            phone, website
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 准备数据
                data = (
                    clean_value(row['rank']),
                    clean_value(row['name']),
                    clean_value(row['name_en']),
                    clean_value(row['url']),
                    clean_value(row['strategy_count']),
                    clean_value(row['comment_count']),
                    clean_value(row['visitor_percentage']),
                    clean_value(row['rating']),
                    clean_value(row['city_rank']),
                    clean_value(row['city']),
                    clean_value(row['description']),
                    clean_value(row['image']),
                    clean_value(row['latitude']),
                    clean_value(row['longitude']),
                    clean_value(row['score']),
                    clean_value(row['address']),
                    clean_value(row['open_time']),
                    clean_value(row['ticket_price']),
                    clean_value(row['introduction']),
                    clean_value(row['suggested_duration']),
                    clean_value(row['traffic']),
                    clean_value(row['best_season']),
                    clean_value(row['images']),
                    clean_value(row['phone']),
                    clean_value(row['website'])
                )
                
                cursor.execute(insert_sql, data)
                success_count += 1
                
                if (index + 1) % 50 == 0:
                    print(f"   进度: {index + 1}/{len(df)}")
                    
            except Exception as e:
                error_count += 1
                print(f"   ✗ 第 {index + 1} 条数据插入失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ 景点数据导入完成！")
        print(f"   成功: {success_count} 条")
        print(f"   失败: {error_count} 条")
        
        return success_count, error_count
        
    except Exception as e:
        print(f"\n✗ 导入景点数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def import_comments():
    """导入评论数据"""
    print("\n" + "=" * 70)
    print("开始导入评论数据")
    print("=" * 70)
    
    try:
        # 读取CSV文件
        print("\n[1/4] 读取CSV文件...")
        df = pd.read_csv(COMMENTS_CSV, encoding='utf-8')
        print(f"   ✓ 读取成功，共 {len(df)} 条评论数据")
        
        # 连接数据库
        print("\n[2/4] 连接数据库...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("   ✓ 数据库连接成功")
        
        # 清空现有数据
        print("\n[3/4] 清空现有数据...")
        cursor.execute("TRUNCATE TABLE comments")
        conn.commit()
        print("   ✓ 已清空 comments 表")
        
        # 插入数据
        print("\n[4/4] 插入评论数据...")
        
        insert_sql = """
        INSERT INTO comments (
            rank_num, attraction_name, attraction_url, city, rating,
            total_comments, comment_title, comment_url, comment_rating,
            comment_content, image_count, image_urls, comment_date,
            username, user_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # 准备数据
                data = (
                    clean_value(row['attraction_rank']),
                    clean_value(row['attraction_name']),
                    clean_value(row['attraction_url']),
                    clean_value(row['attraction_city']),
                    clean_value(row['attraction_rating']),
                    None,  # total_comments (CSV中没有这个字段)
                    clean_value(row['comment_title']),
                    None,  # comment_url (CSV中没有这个字段)
                    clean_value(row['comment_rating']),
                    clean_value(row['comment_content']),
                    clean_value(row['comment_image_count']),
                    None,  # image_urls (CSV中没有这个字段)
                    clean_value(row['comment_date']),
                    clean_value(row['comment_user']),
                    None   # user_url (CSV中没有这个字段)
                )
                
                cursor.execute(insert_sql, data)
                success_count += 1
                
                if (index + 1) % 100 == 0:
                    print(f"   进度: {index + 1}/{len(df)}")
                    
            except Exception as e:
                error_count += 1
                print(f"   ✗ 第 {index + 1} 条数据插入失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ 评论数据导入完成！")
        print(f"   成功: {success_count} 条")
        print(f"   失败: {error_count} 条")
        
        return success_count, error_count
        
    except Exception as e:
        print(f"\n✗ 导入评论数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def verify_import():
    """验证导入结果"""
    print("\n" + "=" * 70)
    print("验证导入结果")
    print("=" * 70)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查景点数量
        cursor.execute("SELECT COUNT(*) FROM attractions")
        attractions_count = cursor.fetchone()[0]
        print(f"\n✓ attractions 表: {attractions_count} 条记录")
        
        # 检查评论数量
        cursor.execute("SELECT COUNT(*) FROM comments")
        comments_count = cursor.fetchone()[0]
        print(f"✓ comments 表: {comments_count} 条记录")
        
        # 显示示例数据
        print("\n景点示例数据：")
        cursor.execute("SELECT id, name, rating, comment_count FROM attractions LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, 名称: {row[1]}, 评分: {row[2]}, 评论数: {row[3]}")
        
        print("\n评论示例数据：")
        cursor.execute("SELECT id, attraction_name, comment_rating, username FROM comments LIMIT 5")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, 景点: {row[1]}, 评分: {row[2]}, 用户: {row[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ 验证失败: {e}")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print(" " * 20 + "CSV数据导入工具")
    print("=" * 70)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 导入景点数据
    attr_success, attr_error = import_attractions()
    
    # 导入评论数据
    comm_success, comm_error = import_comments()
    
    # 验证导入结果
    verify_import()
    
    # 总结
    print("\n" + "=" * 70)
    print("导入总结")
    print("=" * 70)
    print(f"\n景点数据:")
    print(f"  ✓ 成功: {attr_success} 条")
    print(f"  ✗ 失败: {attr_error} 条")
    print(f"\n评论数据:")
    print(f"  ✓ 成功: {comm_success} 条")
    print(f"  ✗ 失败: {comm_error} 条")
    print(f"\n总计:")
    print(f"  ✓ 成功: {attr_success + comm_success} 条")
    print(f"  ✗ 失败: {attr_error + comm_error} 条")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()

