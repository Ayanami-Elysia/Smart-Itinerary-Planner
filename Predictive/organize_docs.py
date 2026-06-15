"""
清理和整理项目文档
"""
import os
import shutil

# 项目目录
project_dir = r"C:\Users\admin\Desktop\2026代码\K94194旅游景点\Project\Predictive"
docs_dir = os.path.join(project_dir, "docs")

# 创建docs目录
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)
    print(f"✓ 创建文档目录: {docs_dir}")

# 需要移动的文档文件
doc_files = [
    "PPT展示大纲.md",
    "README_聚类对比.md",
    "使用说明.md",
    "完成总结.md",
    "快速参考.md",
    "快速开始指南.md",
    "推荐模块更新说明.md",
    "推荐算法详细说明.md",
    "模型保存功能说明.md",
    "聚类算法对比报告.md",
    "页面多推荐模块说明.md",
    "项目功能完成总结.md",
]

print("\n" + "=" * 70)
print("开始整理文档")
print("=" * 70)

moved_count = 0
for doc_file in doc_files:
    src = os.path.join(project_dir, doc_file)
    dst = os.path.join(docs_dir, doc_file)
    
    if os.path.exists(src):
        try:
            shutil.move(src, dst)
            print(f"✓ 移动: {doc_file}")
            moved_count += 1
        except Exception as e:
            print(f"✗ 移动失败 {doc_file}: {e}")
    else:
        print(f"⊘ 文件不存在: {doc_file}")

print("\n" + "=" * 70)
print(f"✓ 完成！共移动 {moved_count} 个文档文件到 docs/ 目录")
print("=" * 70)

# 显示整理后的目录结构
print("\n整理后的目录结构：")
print("\nPredictive/")
print("├── docs/                    # 📚 文档目录")
for doc_file in sorted(doc_files):
    if os.path.exists(os.path.join(docs_dir, doc_file)):
        print(f"│   ├── {doc_file}")
print("├── models/                  #  模型文件")
print("├── predictive.py            # 🔧 主程序")
print("├── test_clustering_comparison.py")
print("├── test_load_models.py")
print("├── verify_page.py")
print("├── verify_update.py")
print("└── clustering_comparison.png")

print("\n" + "=" * 70)
print("文档已整理完成！")
print("=" * 70)


