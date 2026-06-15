"""
聚类算法对比测试脚本
运行此脚本生成聚类算法对比图表并保存模型到本地
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from predictive import compare_clustering_algorithms, list_saved_models

if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "聚类算法对比分析")
    print("=" * 70)
    print("\n本次对比将包括以下算法：")
    print("  1. KMeans - K均值聚类")
    print("  2. DBSCAN - 基于密度的聚类")
    print("  3. 层次聚类 - 凝聚层次聚类")
    print("  4. 高斯混合模型 - 基于概率的聚类")
    print("  5. 谱聚类 - 基于图论的聚类")
    print("\n评估指标：")
    print("  • 轮廓系数 (Silhouette Score): 范围[-1, 1]，越接近1越好")
    print("  • Davies-Bouldin指数: 越小越好")
    print("  • Calinski-Harabasz指数: 越大越好")
    print("\n功能：")
    print("  • 训练5种聚类算法")
    print("  • 生成对比图表")
    print("  • 保存模型到本地（models目录）")
    print("\n" + "=" * 70)
    
    # 运行对比分析
    results = compare_clustering_algorithms(
        n_clusters=5,  # 聚类数量
        save_path='clustering_comparison.png',  # 图表保存路径
        save_models=True  # 保存模型到本地
    )
    
    if results:
        print("\n" + "=" * 70)
        print("✓ 对比分析完成！")
        print("=" * 70)
        print("\n生成的文件：")
        print("  1. 图表文件: clustering_comparison.png")
        print("  2. 模型文件: models/ 目录")
        
        # 列出已保存的模型
        saved_models = list_saved_models()
        if saved_models:
            print(f"\n已保存 {len(saved_models)} 个模型:")
            for model_info in saved_models:
                print(f"  ✓ {model_info['name']}")
                print(f"    - 保存时间: {model_info['save_time']}")
        
        print("\n提示：")
        print("  - 图表包含5个聚类可视化和3个评估指标对比")
        print("  - 模型已保存到本地，下次可以直接加载使用")
        print("  - 可以根据不同指标选择最适合您数据的聚类算法")
        print("  - 建议综合考虑多个指标来评估算法性能")
    else:
        print("\n✗ 对比分析失败，请检查数据库连接和数据")

