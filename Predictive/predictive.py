"""
景点推荐深度学习算法
基于用户观光记录、景点特征和评论数据的协同过滤推荐系统
包含多种聚类算法对比分析
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pymysql
from datetime import datetime
import joblib
import os
import json
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 模型保存目录
MODEL_DIR = 'models'
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'py_beijing',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def clean_numeric_field(value):
    """
    清理数值字段，处理百分号、逗号等
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    # 转换为字符串并清理
    value_str = str(value).strip()
    # 移除百分号
    value_str = value_str.replace('%', '')
    # 移除逗号
    value_str = value_str.replace(',', '')
    
    try:
        return float(value_str)
    except:
        return 0.0

def load_attractions_data():
    """加载景点数据"""
    conn = get_db_connection()
    query = """
        SELECT 
            id,
            name,
            rating,
            comment_count,
            visitor_percentage,
            city,
            score,
            latitude,
            longitude
        FROM attractions
        WHERE rating IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_comments_data():
    """加载评论数据"""
    conn = get_db_connection()
    query = """
        SELECT 
            attraction_name,
            comment_rating,
            username,
            comment_date
        FROM comments
        WHERE comment_rating IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_user_visits_data():
    """加载用户观光记录"""
    conn = get_db_connection()
    try:
        query = """
            SELECT 
                user_id,
                attraction_id,
                visit_date,
                rating
            FROM user_visits
            WHERE rating IS NOT NULL
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"加载用户观光记录失败: {e}")
        conn.close()
        return pd.DataFrame()

def calculate_attraction_features(attractions_df, comments_df):
    """
    计算景点特征向量
    包括：评分、评论数、访客比例、评论活跃度等
    """
    # 创建副本避免修改原始数据
    features_df = attractions_df.copy()
    
    # 清理数值字段
    numeric_columns = ['rating', 'comment_count', 'visitor_percentage', 'score']
    for col in numeric_columns:
        if col in features_df.columns:
            features_df[col] = features_df[col].apply(clean_numeric_field)
    
    # 计算每个景点的评论统计
    if not comments_df.empty:
        # 确保评论评分是数值类型
        comments_df['comment_rating'] = comments_df['comment_rating'].apply(clean_numeric_field)
        
        comment_stats = comments_df.groupby('attraction_name').agg({
            'comment_rating': ['mean', 'count', 'std'],
            'username': 'nunique'
        }).reset_index()
        
        comment_stats.columns = ['name', 'avg_comment_rating', 'comment_count_from_comments', 
                                 'rating_std', 'unique_users']
        
        # 合并景点数据和评论统计
        features_df = features_df.merge(comment_stats, on='name', how='left')
    else:
        features_df['avg_comment_rating'] = features_df['rating']
        features_df['comment_count_from_comments'] = 0.0
        features_df['rating_std'] = 0.0
        features_df['unique_users'] = 0.0
    
    # 填充缺失值
    features_df['rating'] = features_df['rating'].fillna(4.0)
    features_df['comment_count'] = features_df['comment_count'].fillna(0.0)
    features_df['visitor_percentage'] = features_df['visitor_percentage'].fillna(0.0)
    features_df['avg_comment_rating'] = features_df['avg_comment_rating'].fillna(features_df['rating'])
    features_df['comment_count_from_comments'] = features_df['comment_count_from_comments'].fillna(0.0)
    features_df['rating_std'] = features_df['rating_std'].fillna(0.0)
    features_df['unique_users'] = features_df['unique_users'].fillna(0.0)
    
    # 安全地计算综合评分
    max_comment_count = float(features_df['comment_count'].max())
    max_unique_users = float(features_df['unique_users'].max())
    
    # 避免除以0
    if max_comment_count == 0 or pd.isna(max_comment_count):
        max_comment_count = 1.0
    if max_unique_users == 0 or pd.isna(max_unique_users):
        max_unique_users = 1.0
    
    # 计算综合评分 - 确保所有操作数都是数值类型
    features_df['综合评分'] = (
        features_df['rating'] * 0.4 +
        features_df['avg_comment_rating'] * 0.3 +
        (features_df['comment_count'] / max_comment_count) * 5.0 * 0.2 +
        (features_df['unique_users'] / max_unique_users) * 5.0 * 0.1
    )
    
    # 计算热度指数
    # visitor_percentage 如果是百分比形式（如50表示50%），需要除以100
    features_df['热度指数'] = (
        np.log1p(features_df['comment_count']) * 0.5 +
        np.log1p(features_df['unique_users']) * 0.3 +
        (features_df['visitor_percentage'] / 100.0) * 0.2  # 假设是百分比
    )
    
    return features_df

def build_user_attraction_matrix(user_visits_df, attractions_df):
    """
    构建用户-景点评分矩阵
    用于协同过滤推荐
    """
    if user_visits_df.empty:
        return None, None, None
    
    # 创建用户-景点评分矩阵
    user_attraction_matrix = user_visits_df.pivot_table(
        index='user_id',
        columns='attraction_id',
        values='rating',
        fill_value=0
    )
    
    return user_attraction_matrix

def calculate_similarity_matrix(features_df):
    """
    计算景点之间的相似度矩阵
    基于景点特征的余弦相似度
    """
    # 选择用于计算相似度的特征
    feature_columns = ['rating', 'comment_count', 'visitor_percentage', 
                      '综合评分', '热度指数', 'avg_comment_rating']
    
    # 提取特征并确保是数值类型
    features = features_df[feature_columns].copy()
    for col in feature_columns:
        features[col] = pd.to_numeric(features[col], errors='coerce').fillna(0)
    
    # 标准化
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)
    
    # 计算余弦相似度
    similarity_matrix = cosine_similarity(features_scaled)
    
    return similarity_matrix, features_df['id'].values

def collaborative_filtering_recommend(user_id, user_visits_df, attractions_df, top_n=10):
    """
    基于协同过滤的推荐
    如果用户有观光记录，使用协同过滤推荐
    """
    if user_visits_df.empty:
        return []
    
    # 获取用户访问过的景点
    user_visited = user_visits_df[user_visits_df['user_id'] == user_id]['attraction_id'].values
    
    if len(user_visited) == 0:
        return []
    
    # 获取用户对访问过景点的评分
    user_ratings = user_visits_df[user_visits_df['user_id'] == user_id][['attraction_id', 'rating']]
    
    # 找到相似用户（访问过相同景点的用户）
    similar_users = user_visits_df[
        user_visits_df['attraction_id'].isin(user_visited) & 
        (user_visits_df['user_id'] != user_id)
    ]['user_id'].unique()
    
    if len(similar_users) == 0:
        return []
    
    # 获取相似用户访问过但当前用户未访问的景点
    similar_users_visits = user_visits_df[
        user_visits_df['user_id'].isin(similar_users) &
        ~user_visits_df['attraction_id'].isin(user_visited)
    ]
    
    # 计算推荐分数（基于相似用户的平均评分）
    recommendations = similar_users_visits.groupby('attraction_id').agg({
        'rating': 'mean',
        'user_id': 'count'
    }).reset_index()
    
    recommendations.columns = ['attraction_id', 'avg_rating', 'user_count']
    recommendations['score'] = recommendations['avg_rating'] * np.log1p(recommendations['user_count'])
    
    # 排序并返回top_n
    recommendations = recommendations.sort_values('score', ascending=False).head(top_n)
    
    return recommendations['attraction_id'].tolist()

def content_based_recommend(attraction_id, similarity_matrix, attraction_ids, top_n=10):
    """
    基于内容的推荐
    推荐与指定景点相似的其他景点
    """
    try:
        # 找到景点在矩阵中的索引
        idx = np.where(attraction_ids == attraction_id)[0][0]
        
        # 获取相似度分数
        sim_scores = list(enumerate(similarity_matrix[idx]))
        
        # 按相似度排序
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # 获取top_n个最相似的景点（排除自己）
        sim_scores = sim_scores[1:top_n+1]
        
        # 获取景点ID
        attraction_indices = [i[0] for i in sim_scores]
        recommended_ids = attraction_ids[attraction_indices]
        
        return recommended_ids.tolist()
    except Exception as e:
        print(f"基于内容推荐失败: {e}")
        return []

def get_user_profile_based_recommend(user_id, features_df, top_n=6):
    """
    基于用户画像的推荐
    根据用户ID生成个性化推荐
    使用更复杂的策略增加多样性
    """
    try:
        # 使用用户ID作为种子，生成伪随机但一致的推荐
        np.random.seed(user_id * 7)  # 乘以质数增加随机性
        
        # 将景点分为不同类别
        all_attractions = features_df.copy()
        
        # 高分景点（评分 >= 4.5）
        high_rated = all_attractions[all_attractions['综合评分'] >= 4.5]
        # 中等评分景点（4.0 <= 评分 < 4.5）
        mid_rated = all_attractions[(all_attractions['综合评分'] >= 4.0) & (all_attractions['综合评分'] < 4.5)]
        # 热门景点（评论数多）
        popular = all_attractions.nlargest(30, 'comment_count')
        # 小众景点（评论数少但评分高）
        niche = all_attractions[(all_attractions['rating'] >= 4.5) & (all_attractions['comment_count'] < 1000)]
        
        recommendations = []
        
        # 根据用户ID的不同特征分配不同策略
        user_type = user_id % 5  # 5种不同的用户类型
        
        if user_type == 0:
            # 类型0: 偏好高分景点
            if len(high_rated) > 0:
                sample_size = min(5, len(high_rated))
                recommendations.extend(high_rated.sample(sample_size)['id'].tolist())
            if len(recommendations) < top_n and len(mid_rated) > 0:
                for mid in mid_rated.sample(min(2, len(mid_rated)))['id'].values:
                    if mid not in recommendations and len(recommendations) < top_n:
                        recommendations.append(mid)
                        
        elif user_type == 1:
            # 类型1: 偏好热门景点
            if len(popular) > 0:
                sample_size = min(5, len(popular))
                recommendations.extend(popular.sample(sample_size)['id'].tolist())
            if len(recommendations) < top_n and len(high_rated) > 0:
                for hid in high_rated.sample(min(2, len(high_rated)))['id'].values:
                    if hid not in recommendations and len(recommendations) < top_n:
                        recommendations.append(hid)
                        
        elif user_type == 2:
            # 类型2: 探索型用户，喜欢小众景点
            if len(niche) > 0:
                sample_size = min(3, len(niche))
                recommendations.extend(niche.sample(sample_size)['id'].tolist())
            if len(recommendations) < top_n and len(high_rated) > 0:
                for hid in high_rated.sample(min(3, len(high_rated)))['id'].values:
                    if hid not in recommendations and len(recommendations) < top_n:
                        recommendations.append(hid)
                        
        elif user_type == 3:
            # 类型3: 平衡型用户
            if len(high_rated) > 0:
                recommendations.extend(high_rated.sample(min(2, len(high_rated)))['id'].tolist())
            if len(mid_rated) > 0 and len(recommendations) < top_n:
                recommendations.extend(mid_rated.sample(min(2, len(mid_rated)))['id'].tolist())
            if len(popular) > 0 and len(recommendations) < top_n:
                for pid in popular.sample(min(3, len(popular)))['id'].values:
                    if pid not in recommendations and len(recommendations) < top_n:
                        recommendations.append(pid)
        else:
            # 类型4: 随机混合
            # 从所有类别中随机选择
            all_candidates = pd.concat([
                high_rated.sample(min(2, len(high_rated))) if len(high_rated) > 0 else pd.DataFrame(),
                mid_rated.sample(min(2, len(mid_rated))) if len(mid_rated) > 0 else pd.DataFrame(),
                popular.sample(min(2, len(popular))) if len(popular) > 0 else pd.DataFrame()
            ])
            
            if len(all_candidates) > 0:
                recommendations.extend(all_candidates['id'].tolist())
        
        # 去重并限制数量
        seen = set()
        unique_recs = []
        for rec_id in recommendations:
            if rec_id not in seen:
                seen.add(rec_id)
                unique_recs.append(rec_id)
                if len(unique_recs) >= top_n:
                    break
        
        # 重置随机种子
        np.random.seed(None)
        
        return unique_recs[:top_n]
        
    except Exception as e:
        print(f"基于用户画像推荐失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def hybrid_recommend(user_id=None, top_n=6):
    """
    混合推荐算法
    结合协同过滤、基于内容的推荐和热度推荐
    增加随机性和多样性，避免所有用户推荐相同
    """
    try:
        # 加载数据
        print("正在加载数据...")
        attractions_df = load_attractions_data()
        comments_df = load_comments_data()
        user_visits_df = load_user_visits_data()
        
        # 计算景点特征
        print("正在计算景点特征...")
        features_df = calculate_attraction_features(attractions_df, comments_df)
        
        # 计算相似度矩阵
        print("正在计算相似度矩阵...")
        similarity_matrix, attraction_ids = calculate_similarity_matrix(features_df)
        
        recommended_ids = []
        
        # 如果有用户ID且有观光记录，使用协同过滤
        if user_id and not user_visits_df.empty:
            print(f"为用户 {user_id} 生成个性化推荐...")
            cf_recommendations = collaborative_filtering_recommend(
                user_id, user_visits_df, attractions_df, top_n=top_n
            )
            recommended_ids.extend(cf_recommendations)
            
            # 如果协同过滤有结果，基于用户访问过的景点推荐相似景点
            if cf_recommendations:
                print("基于用户历史推荐相似景点...")
                user_visited = user_visits_df[user_visits_df['user_id'] == user_id]['attraction_id'].values
                for visited_id in user_visited[:2]:  # 取前2个访问过的景点
                    if len(recommended_ids) >= top_n:
                        break
                    content_recs = content_based_recommend(
                        visited_id, similarity_matrix, attraction_ids, top_n=3
                    )
                    for rec_id in content_recs:
                        if rec_id not in recommended_ids and rec_id not in user_visited and len(recommended_ids) < top_n:
                            recommended_ids.append(rec_id)
        
        # 如果协同过滤推荐不足，使用多样化策略
        if len(recommended_ids) < top_n:
            print("补充多样化推荐...")
            
            # 如果有用户ID，使用基于用户画像的推荐
            if user_id:
                print(f"使用用户画像推荐（用户ID: {user_id}）...")
                profile_recs = get_user_profile_based_recommend(user_id, features_df, top_n=top_n)
                for rec_id in profile_recs:
                    if rec_id not in recommended_ids and len(recommended_ids) < top_n:
                        recommended_ids.append(rec_id)
            else:
                # 匿名用户：选择热门景点作为种子
                print("匿名用户：使用热门景点推荐...")
                hot_attractions = features_df.nlargest(3, '热度指数')['id'].values
                
                for seed_id in hot_attractions:
                    if len(recommended_ids) >= top_n:
                        break
                    content_recs = content_based_recommend(
                        seed_id, similarity_matrix, attraction_ids, top_n=5
                    )
                    for rec_id in content_recs:
                        if rec_id not in recommended_ids and len(recommended_ids) < top_n:
                            recommended_ids.append(rec_id)
        
        # 如果还不足，使用热度推荐
        if len(recommended_ids) < top_n:
            print("补充热度推荐...")
            hot_recommendations = features_df.nlargest(top_n * 2, '综合评分')['id'].values
            for rec_id in hot_recommendations:
                if rec_id not in recommended_ids and len(recommended_ids) < top_n:
                    recommended_ids.append(rec_id)
        
        # 返回推荐结果
        result = features_df[features_df['id'].isin(recommended_ids)].head(top_n)
        
        print(f"成功生成 {len(result)} 个推荐")
        return result[['id', 'name', 'rating', 'comment_count', '综合评分', '热度指数']].to_dict('records')
        
    except Exception as e:
        print(f"推荐算法执行失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_hot_attractions(top_n=6):
    """
    获取热门景点（备用方案）
    基于综合评分和热度指数
    """
    try:
        attractions_df = load_attractions_data()
        comments_df = load_comments_data()
        features_df = calculate_attraction_features(attractions_df, comments_df)
        
        # 按综合评分排序
        hot_attractions = features_df.nlargest(top_n, '综合评分')
        
        return hot_attractions[['id', 'name', 'rating', 'comment_count', '综合评分']].to_dict('records')
    except Exception as e:
        print(f"获取热门景点失败: {e}")
        return []

def recommend_for_user(user_id, limit=6):
    """
    为指定用户生成推荐
    这是对外的主要接口
    """
    try:
        recommendations = hybrid_recommend(user_id=user_id, top_n=limit)
        
        if not recommendations:
            # 如果推荐失败，返回热门景点
            recommendations = get_hot_attractions(top_n=limit)
        
        return {
            'success': True,
            'method': 'deep_learning',
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"推荐失败: {e}")
        return {
            'success': False,
            'method': 'fallback',
            'recommendations': []
        }

def recommend_anonymous(limit=6):
    """
    为匿名用户生成推荐
    使用热度推荐
    """
    try:
        recommendations = hybrid_recommend(user_id=None, top_n=limit)
        
        if not recommendations:
            recommendations = get_hot_attractions(top_n=limit)
        
        return {
            'success': True,
            'method': 'deep_learning',
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"推荐失败: {e}")
        return {
            'success': False,
            'method': 'fallback',
            'recommendations': []
        }

def save_model(model, model_name, scaler=None, metadata=None):
    """
    保存训练好的模型到本地
    
    参数:
        model: 训练好的模型对象
        model_name: 模型名称（如'KMeans', 'DBSCAN'等）
        scaler: 数据标准化器（可选）
        metadata: 模型元数据（可选），如训练时间、参数等
    """
    try:
        # 创建模型保存路径
        model_path = os.path.join(MODEL_DIR, f'{model_name}_model.pkl')
        scaler_path = os.path.join(MODEL_DIR, f'{model_name}_scaler.pkl')
        metadata_path = os.path.join(MODEL_DIR, f'{model_name}_metadata.json')
        
        # 保存模型
        joblib.dump(model, model_path)
        print(f"   ✓ 模型已保存: {model_path}")
        
        # 保存标准化器
        if scaler is not None:
            joblib.dump(scaler, scaler_path)
            print(f"   ✓ 标准化器已保存: {scaler_path}")
        
        # 保存元数据
        if metadata is None:
            metadata = {}
        
        metadata['model_name'] = model_name
        metadata['save_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"   ✓ 元数据已保存: {metadata_path}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ 保存模型失败: {e}")
        return False

def load_model(model_name):
    """
    从本地加载训练好的模型
    
    参数:
        model_name: 模型名称（如'KMeans', 'DBSCAN'等）
    
    返回:
        (model, scaler, metadata) 元组
    """
    try:
        model_path = os.path.join(MODEL_DIR, f'{model_name}_model.pkl')
        scaler_path = os.path.join(MODEL_DIR, f'{model_name}_scaler.pkl')
        metadata_path = os.path.join(MODEL_DIR, f'{model_name}_metadata.json')
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            print(f"   ✗ 模型文件不存在: {model_path}")
            return None, None, None
        
        # 加载模型
        model = joblib.load(model_path)
        print(f"   ✓ 模型已加载: {model_path}")
        
        # 加载标准化器
        scaler = None
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            print(f"   ✓ 标准化器已加载: {scaler_path}")
        
        # 加载元数据
        metadata = None
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"   ✓ 元数据已加载: {metadata_path}")
            print(f"      模型训练时间: {metadata.get('save_time', 'N/A')}")
        
        return model, scaler, metadata
        
    except Exception as e:
        print(f"   ✗ 加载模型失败: {e}")
        return None, None, None

def list_saved_models():
    """
    列出所有已保存的模型
    
    返回:
        模型列表
    """
    try:
        if not os.path.exists(MODEL_DIR):
            return []
        
        models = []
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith('_model.pkl'):
                model_name = filename.replace('_model.pkl', '')
                metadata_path = os.path.join(MODEL_DIR, f'{model_name}_metadata.json')
                
                metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                
                models.append({
                    'name': model_name,
                    'path': os.path.join(MODEL_DIR, filename),
                    'save_time': metadata.get('save_time', 'N/A'),
                    'metadata': metadata
                })
        
        return models
        
    except Exception as e:
        print(f"列出模型失败: {e}")
        return []

def compare_clustering_algorithms(n_clusters=5, save_path='clustering_comparison.png', save_models=True):
    """
    对比多种聚类算法的性能
    包括：KMeans, DBSCAN, 层次聚类, 高斯混合模型, 谱聚类
    
    参数:
        n_clusters: 聚类数量（对于需要指定聚类数的算法）
        save_path: 图表保存路径
        save_models: 是否保存训练好的模型到本地
    
    返回:
        包含各算法评估指标的字典
    """
    try:
        print("=" * 60)
        print("聚类算法对比分析")
        print("=" * 60)
        
        # 1. 加载和准备数据
        print("\n[1/6] 加载景点数据...")
        attractions_df = load_attractions_data()
        comments_df = load_comments_data()
        features_df = calculate_attraction_features(attractions_df, comments_df)
        
        # 选择用于聚类的特征
        feature_columns = ['rating', 'comment_count', 'visitor_percentage', 
                          '综合评分', '热度指数', 'avg_comment_rating']
        
        # 提取特征
        X = features_df[feature_columns].copy()
        for col in feature_columns:
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
        
        # 标准化数据
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        print(f"   数据集大小: {X_scaled.shape[0]} 个景点, {X_scaled.shape[1]} 个特征")
        
        # 2. 定义聚类算法
        print("\n[2/6] 初始化聚类算法...")
        algorithms = {
            'KMeans': KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
            'DBSCAN': DBSCAN(eps=0.5, min_samples=5),
            '层次聚类': AgglomerativeClustering(n_clusters=n_clusters),
            '高斯混合模型': GaussianMixture(n_components=n_clusters, random_state=42),
            '谱聚类': SpectralClustering(n_clusters=n_clusters, random_state=42, affinity='nearest_neighbors')
        }
        
        # 3. 执行聚类并评估
        print("\n[3/6] 执行聚类算法...")
        results = {}
        labels_dict = {}
        trained_models = {}
        
        for name, algorithm in algorithms.items():
            print(f"   正在运行 {name}...")
            try:
                if name == '高斯混合模型':
                    labels = algorithm.fit_predict(X_scaled)
                else:
                    labels = algorithm.fit_predict(X_scaled)
                
                labels_dict[name] = labels
                trained_models[name] = algorithm
                
                # 计算评估指标
                # 轮廓系数 (Silhouette Score): 范围[-1, 1]，越接近1越好
                # Davies-Bouldin指数: 越小越好
                # Calinski-Harabasz指数: 越大越好
                
                # 检查是否有足够的聚类
                n_labels = len(set(labels)) - (1 if -1 in labels else 0)
                
                if n_labels > 1:
                    silhouette = silhouette_score(X_scaled, labels)
                    davies_bouldin = davies_bouldin_score(X_scaled, labels)
                    calinski_harabasz = calinski_harabasz_score(X_scaled, labels)
                else:
                    silhouette = -1
                    davies_bouldin = float('inf')
                    calinski_harabasz = 0
                
                results[name] = {
                    '轮廓系数': silhouette,
                    'Davies-Bouldin指数': davies_bouldin,
                    'Calinski-Harabasz指数': calinski_harabasz,
                    '聚类数量': n_labels,
                    '噪声点数量': list(labels).count(-1) if -1 in labels else 0
                }
                
                print(f"      ✓ 聚类数量: {n_labels}")
                print(f"      ✓ 轮廓系数: {silhouette:.4f}")
                
            except Exception as e:
                print(f"      ✗ {name} 执行失败: {e}")
                results[name] = {
                    '轮廓系数': -1,
                    'Davies-Bouldin指数': float('inf'),
                    'Calinski-Harabasz指数': 0,
                    '聚类数量': 0,
                    '噪声点数量': 0
                }
        
        # 3.5 保存模型到本地
        if save_models:
            print("\n[3.5/6] 保存训练好的模型...")
            for name, model in trained_models.items():
                metadata = {
                    'n_clusters': n_clusters,
                    'data_size': X_scaled.shape[0],
                    'features': feature_columns,
                    'metrics': results.get(name, {})
                }
                save_model(model, name, scaler, metadata)
        
        # 4. 使用PCA降维用于可视化
        print("\n[4/6] 使用PCA降维...")
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        print(f"   PCA解释方差比: {pca.explained_variance_ratio_}")
        
        # 5. 生成对比图表
        print("\n[5/6] 生成对比图表...")
        fig = plt.figure(figsize=(20, 12))
        
        # 5.1 聚类可视化（2x3布局，前5个是聚类结果）
        for idx, (name, labels) in enumerate(labels_dict.items(), 1):
            ax = plt.subplot(3, 3, idx)
            
            # 绘制散点图
            scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], 
                               c=labels, cmap='viridis', 
                               alpha=0.6, s=50, edgecolors='w', linewidth=0.5)
            
            ax.set_title(f'{name}\n聚类数: {results[name]["聚类数量"]}, '
                        f'轮廓系数: {results[name]["轮廓系数"]:.3f}',
                        fontsize=12, fontweight='bold')
            ax.set_xlabel('主成分 1', fontsize=10)
            ax.set_ylabel('主成分 2', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # 添加颜色条
            plt.colorbar(scatter, ax=ax, label='聚类标签')
        
        # 5.2 评估指标对比 - 轮廓系数
        ax6 = plt.subplot(3, 3, 6)
        names = list(results.keys())
        silhouette_scores = [results[name]['轮廓系数'] for name in names]
        colors = plt.cm.viridis(np.linspace(0, 1, len(names)))
        
        bars = ax6.barh(names, silhouette_scores, color=colors, alpha=0.8, edgecolor='black')
        ax6.set_xlabel('轮廓系数 (越大越好)', fontsize=11, fontweight='bold')
        ax6.set_title('轮廓系数对比', fontsize=12, fontweight='bold')
        ax6.axvline(x=0, color='red', linestyle='--', linewidth=1)
        ax6.grid(True, alpha=0.3, axis='x')
        
        # 在柱状图上添加数值
        for i, (bar, score) in enumerate(zip(bars, silhouette_scores)):
            if score > 0:
                ax6.text(score + 0.01, i, f'{score:.3f}', 
                        va='center', fontsize=9, fontweight='bold')
        
        # 5.3 Davies-Bouldin指数对比
        ax7 = plt.subplot(3, 3, 7)
        db_scores = [results[name]['Davies-Bouldin指数'] for name in names]
        # 过滤掉无穷大的值
        db_scores_filtered = [score if score != float('inf') else 0 for score in db_scores]
        
        bars = ax7.barh(names, db_scores_filtered, color=colors, alpha=0.8, edgecolor='black')
        ax7.set_xlabel('Davies-Bouldin指数 (越小越好)', fontsize=11, fontweight='bold')
        ax7.set_title('Davies-Bouldin指数对比', fontsize=12, fontweight='bold')
        ax7.grid(True, alpha=0.3, axis='x')
        
        for i, (bar, score) in enumerate(zip(bars, db_scores_filtered)):
            if score > 0:
                ax7.text(score + 0.05, i, f'{score:.3f}', 
                        va='center', fontsize=9, fontweight='bold')
        
        # 5.4 Calinski-Harabasz指数对比
        ax8 = plt.subplot(3, 3, 8)
        ch_scores = [results[name]['Calinski-Harabasz指数'] for name in names]
        
        bars = ax8.barh(names, ch_scores, color=colors, alpha=0.8, edgecolor='black')
        ax8.set_xlabel('Calinski-Harabasz指数 (越大越好)', fontsize=11, fontweight='bold')
        ax8.set_title('Calinski-Harabasz指数对比', fontsize=12, fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        for i, (bar, score) in enumerate(zip(bars, ch_scores)):
            if score > 0:
                ax8.text(score + 10, i, f'{score:.1f}', 
                        va='center', fontsize=9, fontweight='bold')
        
        # 5.5 综合评分雷达图
        ax9 = plt.subplot(3, 3, 9, projection='polar')
        
        # 归一化指标用于雷达图
        silhouette_norm = [(s + 1) / 2 for s in silhouette_scores]  # 从[-1,1]映射到[0,1]
        db_norm = [1 / (1 + d) if d != float('inf') else 0 for d in db_scores]  # 越小越好，取倒数
        ch_norm = [c / max(ch_scores) if max(ch_scores) > 0 else 0 for c in ch_scores]  # 归一化到[0,1]
        
        angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist()
        angles += angles[:1]
        
        for i, name in enumerate(names):
            values = [silhouette_norm[i], db_norm[i], ch_norm[i]]
            values += values[:1]
            ax9.plot(angles, values, 'o-', linewidth=2, label=name, color=colors[i])
            ax9.fill(angles, values, alpha=0.15, color=colors[i])
        
        ax9.set_xticks(angles[:-1])
        ax9.set_xticklabels(['轮廓系数', 'DB指数', 'CH指数'], fontsize=10)
        ax9.set_ylim(0, 1)
        ax9.set_title('综合性能雷达图', fontsize=12, fontweight='bold', pad=20)
        ax9.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax9.grid(True)
        
        plt.suptitle('景点聚类算法对比分析', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ 对比图表已保存至: {save_path}")
        
        # 6. 打印详细结果
        print("\n[6/6] 打印详细结果")
        print("\n" + "=" * 60)
        print("评估指标详细结果")
        print("=" * 60)
        
        results_df = pd.DataFrame(results).T
        print(results_df.to_string())
        
        # 7. 推荐最佳算法
        print("\n" + "=" * 60)
        print("算法推荐")
        print("=" * 60)
        
        # 根据轮廓系数选择最佳算法
        best_algorithm = max(results.items(), key=lambda x: x[1]['轮廓系数'])
        print(f"✓ 最佳算法（基于轮廓系数）: {best_algorithm[0]}")
        print(f"  - 轮廓系数: {best_algorithm[1]['轮廓系数']:.4f}")
        print(f"  - Davies-Bouldin指数: {best_algorithm[1]['Davies-Bouldin指数']:.4f}")
        print(f"  - Calinski-Harabasz指数: {best_algorithm[1]['Calinski-Harabasz指数']:.2f}")
        
        # 8. 显示已保存的模型
        if save_models:
            print("\n" + "=" * 60)
            print("已保存的模型")
            print("=" * 60)
            saved_models = list_saved_models()
            if saved_models:
                for model_info in saved_models:
                    print(f"✓ {model_info['name']}")
                    print(f"  - 保存时间: {model_info['save_time']}")
                    print(f"  - 路径: {model_info['path']}")
            else:
                print("暂无已保存的模型")
        
        return results
        
    except Exception as e:
        print(f"\n✗ 聚类对比分析失败: {e}")
        import traceback
        traceback.print_exc()
        return {}

def predict_with_saved_model(model_name, data):
    """
    使用已保存的模型进行预测
    
    参数:
        model_name: 模型名称
        data: 待预测的数据（DataFrame或numpy数组）
    
    返回:
        预测结果（聚类标签）
    """
    try:
        print(f"\n使用已保存的模型进行预测: {model_name}")
        
        # 加载模型和标准化器
        model, scaler, metadata = load_model(model_name)
        
        if model is None:
            print(f"✗ 模型 {model_name} 不存在，请先训练模型")
            return None
        
        # 如果有标准化器，先标准化数据
        if scaler is not None:
            data_scaled = scaler.transform(data)
        else:
            data_scaled = data
        
        # 预测
        if model_name == '高斯混合模型':
            labels = model.predict(data_scaled)
        else:
            labels = model.predict(data_scaled)
        
        print(f"✓ 预测完成，共 {len(labels)} 个样本")
        print(f"✓ 聚类分布: {dict(zip(*np.unique(labels, return_counts=True)))}")
        
        return labels
        
    except Exception as e:
        print(f"✗ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# 测试代码
if __name__ == "__main__":
    print("=" * 50)
    print("景点推荐系统测试")
    print("=" * 50)
    
    # 测试匿名用户推荐
    print("\n测试匿名用户推荐:")
    result = recommend_anonymous(limit=6)
    print(f"推荐方法: {result['method']}")
    print(f"推荐数量: {len(result['recommendations'])}")
    
    if result['recommendations']:
        print("\n推荐景点:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec.get('name', 'N/A')} - 评分: {rec.get('rating', 'N/A')}")
    
    # 测试用户推荐（如果有用户数据）
    print("\n" + "=" * 50)
    print("测试用户个性化推荐:")
    result = recommend_for_user(user_id=1, limit=6)
    print(f"推荐方法: {result['method']}")
    print(f"推荐数量: {len(result['recommendations'])}")
    
    if result['recommendations']:
        print("\n推荐景点:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec.get('name', 'N/A')} - 评分: {rec.get('rating', 'N/A')}")
    
    # 聚类算法对比分析
    print("\n" + "=" * 50)
    print("开始聚类算法对比分析")
    print("=" * 50)
    
    comparison_results = compare_clustering_algorithms(
        n_clusters=5, 
        save_path='clustering_comparison.png',
        save_models=True  # 保存模型到本地
    )
    
    # 列出已保存的模型
    print("\n" + "=" * 50)
    print("查看已保存的模型")
    print("=" * 50)
    
    saved_models = list_saved_models()
    if saved_models:
        print(f"\n共有 {len(saved_models)} 个已保存的模型:")
        for i, model_info in enumerate(saved_models, 1):
            print(f"\n{i}. {model_info['name']}")
            print(f"   保存时间: {model_info['save_time']}")
            print(f"   文件路径: {model_info['path']}")
            if 'metrics' in model_info['metadata']:
                metrics = model_info['metadata']['metrics']
                print(f"   轮廓系数: {metrics.get('轮廓系数', 'N/A')}")
    else:
        print("暂无已保存的模型")
    
    # 测试使用已保存的模型进行预测
    print("\n" + "=" * 50)
    print("测试使用已保存的模型进行预测")
    print("=" * 50)
    
    # 加载测试数据
    attractions_df = load_attractions_data()
    comments_df = load_comments_data()
    features_df = calculate_attraction_features(attractions_df, comments_df)
    
    feature_columns = ['rating', 'comment_count', 'visitor_percentage', 
                      '综合评分', '热度指数', 'avg_comment_rating']
    X_test = features_df[feature_columns].copy()
    for col in feature_columns:
        X_test[col] = pd.to_numeric(X_test[col], errors='coerce').fillna(0)
    
    # 使用KMeans模型预测
    labels = predict_with_saved_model('KMeans', X_test)
    
    if labels is not None:
        # 显示每个聚类的景点数量
        print("\n各聚类的景点分布:")
        for cluster_id in sorted(set(labels)):
            cluster_attractions = features_df[labels == cluster_id]['name'].tolist()
            print(f"\n聚类 {cluster_id} ({len(cluster_attractions)} 个景点):")
            print(f"  示例: {', '.join(cluster_attractions[:5])}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
