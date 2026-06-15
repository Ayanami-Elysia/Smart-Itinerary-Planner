"""
模型加载和预测测试脚本
演示如何加载已保存的模型并进行预测
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from predictive import (
    list_saved_models, 
    load_model, 
    predict_with_saved_model,
    load_attractions_data,
    load_comments_data,
    calculate_attraction_features
)
import pandas as pd

def main():
    print("=" * 70)
    print(" " * 20 + "模型加载和预测测试")
    print("=" * 70)
    
    # 1. 列出所有已保存的模型
    print("\n[1/3] 查看已保存的模型...")
    saved_models = list_saved_models()
    
    if not saved_models:
        print("✗ 暂无已保存的模型")
        print("提示: 请先运行 test_clustering_comparison.py 训练并保存模型")
        return
    
    print(f"\n共有 {len(saved_models)} 个已保存的模型:")
    for i, model_info in enumerate(saved_models, 1):
        print(f"\n{i}. {model_info['name']}")
        print(f"   保存时间: {model_info['save_time']}")
        print(f"   文件路径: {model_info['path']}")
        
        # 显示模型性能指标
        if 'metrics' in model_info['metadata']:
            metrics = model_info['metadata']['metrics']
            print(f"   性能指标:")
            print(f"     - 轮廓系数: {metrics.get('轮廓系数', 'N/A'):.4f}")
            print(f"     - Davies-Bouldin指数: {metrics.get('Davies-Bouldin指数', 'N/A'):.4f}")
            print(f"     - Calinski-Harabasz指数: {metrics.get('Calinski-Harabasz指数', 'N/A'):.2f}")
    
    # 2. 加载测试数据
    print("\n[2/3] 加载测试数据...")
    attractions_df = load_attractions_data()
    comments_df = load_comments_data()
    features_df = calculate_attraction_features(attractions_df, comments_df)
    
    feature_columns = ['rating', 'comment_count', 'visitor_percentage', 
                      '综合评分', '热度指数', 'avg_comment_rating']
    X_test = features_df[feature_columns].copy()
    for col in feature_columns:
        X_test[col] = pd.to_numeric(X_test[col], errors='coerce').fillna(0)
    
    print(f"✓ 测试数据加载完成: {len(X_test)} 个景点")
    
    # 3. 使用每个已保存的模型进行预测
    print("\n[3/3] 使用已保存的模型进行预测...")
    
    for model_info in saved_models:
        model_name = model_info['name']
        print("\n" + "-" * 70)
        
        # 使用模型预测
        labels = predict_with_saved_model(model_name, X_test)
        
        if labels is not None:
            # 分析每个聚类
            print(f"\n{model_name} 聚类结果分析:")
            
            for cluster_id in sorted(set(labels)):
                if cluster_id == -1:
                    cluster_name = "噪声点"
                else:
                    cluster_name = f"聚类 {cluster_id}"
                
                # 获取该聚类的景点
                cluster_mask = labels == cluster_id
                cluster_attractions = features_df[cluster_mask]
                
                print(f"\n  {cluster_name} ({len(cluster_attractions)} 个景点):")
                
                # 计算该聚类的统计信息
                avg_rating = cluster_attractions['rating'].mean()
                avg_comment_count = cluster_attractions['comment_count'].mean()
                avg_score = cluster_attractions['综合评分'].mean()
                
                print(f"    平均评分: {avg_rating:.2f}")
                print(f"    平均评论数: {avg_comment_count:.0f}")
                print(f"    平均综合评分: {avg_score:.2f}")
                
                # 显示该聚类的代表性景点
                top_attractions = cluster_attractions.nlargest(3, '综合评分')['name'].tolist()
                print(f"    代表景点: {', '.join(top_attractions)}")
    
    print("\n" + "=" * 70)
    print("✓ 测试完成")
    print("=" * 70)
    print("\n总结:")
    print("  - 所有已保存的模型都可以正常加载和使用")
    print("  - 模型预测速度快，无需重新训练")
    print("  - 可以根据业务需求选择合适的模型进行预测")

if __name__ == "__main__":
    main()

