// 新闻列表页面JavaScript
let currentPage = 1;
let pageSize = 10;
let deleteNewsId = null;
let editNewsId = null;
let currentDetailNewsId = null;
let uploadedImages = []; // 存储上传的图片
let coverImageUrl = null; // 封面图片URL

document.addEventListener('DOMContentLoaded', function() {
    // 加载统计信息
    loadStatistics();
    
    // 加载分类列表
    loadCategories();
    
    // 加载新闻列表
    loadNewsList();
    
    // 监听搜索框回车事件
    document.getElementById('keyword').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchNews();
        }
    });
});

// 加载统计信息
function loadStatistics() {
    fetch('/news/statistics')
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const stats = data.data;
                document.getElementById('total-count').textContent = stats.total;
                document.getElementById('published-count').textContent = stats.published;
                document.getElementById('draft-count').textContent = stats.drafts;
                document.getElementById('today-count').textContent = stats.today;
            }
        })
        .catch(error => {
            console.error('加载统计信息失败:', error);
        });
}

// 加载分类列表
function loadCategories() {
    fetch('/news/categories')
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const categorySelect = document.getElementById('category-filter');
                const newsCategorySelect = document.getElementById('news-category');
                
                data.data.forEach(category => {
                    // 添加到筛选下拉框
                    const option1 = document.createElement('option');
                    option1.value = category;
                    option1.textContent = category;
                    categorySelect.appendChild(option1);
                    
                    // 添加到新闻表单下拉框（如果不存在）
                    const existingOption = Array.from(newsCategorySelect.options).find(opt => opt.value === category);
                    if (!existingOption) {
                        const option2 = document.createElement('option');
                        option2.value = category;
                        option2.textContent = category;
                        newsCategorySelect.appendChild(option2);
                    }
                });
            }
        })
        .catch(error => {
            console.error('加载分类失败:', error);
        });
}

// 加载新闻列表
function loadNewsList(page = 1) {
    currentPage = page;
    const category = document.getElementById('category-filter').value;
    const status = document.getElementById('status-filter').value;
    const keyword = document.getElementById('keyword').value;
    
    const params = new URLSearchParams({
        page: page,
        pageSize: pageSize
    });
    
    if (category) params.append('category', category);
    if (status !== '') params.append('status', status);
    if (keyword) params.append('keyword', keyword);
    
    fetch(`/news/list?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const newsList = data.data.list;
                const total = data.data.total;
                const totalPages = data.data.total_pages;
                
                // 填充新闻列表
                const tbody = document.getElementById('news-list');
                tbody.innerHTML = '';
                
                newsList.forEach(news => {
                    const row = document.createElement('tr');
                    
                    // 封面图片
                    const coverCell = document.createElement('td');
                    if (news.cover_image) {
                        coverCell.innerHTML = `<img src="${news.cover_image}" alt="封面" class="cover-thumbnail">`;
                    } else {
                        coverCell.innerHTML = '<span style="color: #999;">无封面</span>';
                    }
                    
                    row.innerHTML = `
                        <td>${news.id}</td>
                        <td></td>
                        <td>${news.title}</td>
                        <td>${news.category}</td>
                        <td>${news.author}</td>
                        <td><span class="status-${news.status ? 'published' : 'draft'}">${news.status ? '已发布' : '草稿'}</span></td>
                        <td>${news.view_count}</td>
                        <td>${formatDateTime(news.create_time)}</td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-info" onclick="showDetailModal(${news.id})">
                                    <i class="fas fa-eye"></i> 查看
                                </button>
                                <button class="btn btn-sm btn-primary" onclick="showEditModal(${news.id})">
                                    <i class="fas fa-edit"></i> 编辑
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="showDeleteModal(${news.id})">
                                    <i class="fas fa-trash"></i> 删除
                                </button>
                            </div>
                        </td>
                    `;
                    
                    // 插入封面图片到第二列
                    row.children[1].replaceWith(coverCell);
                    
                    tbody.appendChild(row);
                });
                
                // 生成分页
                generatePagination(totalPages, page);
            }
        })
        .catch(error => {
            console.error('加载新闻列表失败:', error);
        });
}

// 生成分页
function generatePagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // 上一页
    if (currentPage > 1) {
        const prevBtn = document.createElement('button');
        prevBtn.textContent = '上一页';
        prevBtn.onclick = () => loadNewsList(currentPage - 1);
        pagination.appendChild(prevBtn);
    }
    
    // 页码
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => loadNewsList(i);
        pagination.appendChild(pageBtn);
    }
    
    // 下一页
    if (currentPage < totalPages) {
        const nextBtn = document.createElement('button');
        nextBtn.textContent = '下一页';
        nextBtn.onclick = () => loadNewsList(currentPage + 1);
        pagination.appendChild(nextBtn);
    }
}

// 搜索新闻
function searchNews() {
    loadNewsList(1);
}

// 重置搜索
function resetSearch() {
    document.getElementById('keyword').value = '';
    document.getElementById('category-filter').value = '';
    document.getElementById('status-filter').value = '';
    loadNewsList(1);
}

// 显示添加模态框
function showAddModal() {
    editNewsId = null;
    document.getElementById('modal-title').textContent = '添加新闻';
    
    // 清空表单
    document.getElementById('news-form').reset();
    
    // 重置图片相关变量
    uploadedImages = [];
    coverImageUrl = null;
    
    // 重置图片显示
    resetImageUpload();
    
    document.getElementById('news-modal').style.display = 'flex';
}

// 显示编辑模态框
function showEditModal(newsId) {
    editNewsId = newsId;
    document.getElementById('modal-title').textContent = '编辑新闻';
    
    // 获取新闻详情
    fetch(`/news/detail/${newsId}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const news = data.data;
                
                // 填充表单
                document.getElementById('news-title').value = news.title;
                document.getElementById('news-author').value = news.author;
                document.getElementById('news-category').value = news.category;
                document.getElementById('news-status').value = news.status;
                document.getElementById('news-summary').value = news.summary || '';
                
                // 处理内容中的图片标签，转换为文本标记以便编辑
                let content = news.content;
                const imgRegex = /<img[^>]+src="([^"]+)"[^>]*>/g;
                let match;
                const contentImages = [];
                
                while ((match = imgRegex.exec(news.content)) !== null) {
                    const imgUrl = match[1];
                    contentImages.push(imgUrl);
                    content = content.replace(match[0], `[图片: ${imgUrl}]`);
                }
                
                document.getElementById('news-content').value = content;
                
                // 设置封面图片
                coverImageUrl = news.cover_image;
                if (coverImageUrl) {
                    showCoverPreview(coverImageUrl);
                }
                
                // 设置内容图片
                uploadedImages = contentImages;
                updateUploadedImagesDisplay();
                
                document.getElementById('news-modal').style.display = 'flex';
            }
        })
        .catch(error => {
            console.error('获取新闻详情失败:', error);
            showMessage('获取新闻详情失败', 'error');
        });
}

// 显示详情模态框
function showDetailModal(newsId) {
    currentDetailNewsId = newsId;
    
    // 获取新闻详情
    fetch(`/news/detail/${newsId}`)
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                const news = data.data;
                
                // 填充详情
                document.getElementById('detail-title').textContent = news.title;
                document.getElementById('detail-author').textContent = news.author;
                document.getElementById('detail-category').textContent = news.category;
                document.getElementById('detail-create-time').textContent = formatDateTime(news.create_time);
                document.getElementById('detail-view-count').textContent = news.view_count;
                
                // 状态显示
                const statusEl = document.getElementById('detail-status');
                statusEl.textContent = news.status ? '已发布' : '草稿';
                statusEl.className = `status-badge status-${news.status ? 'published' : 'draft'}`;
                
                // 封面图片
                const coverSection = document.getElementById('detail-cover-section');
                if (news.cover_image) {
                    document.getElementById('detail-cover-image').src = news.cover_image;
                    coverSection.style.display = 'block';
                } else {
                    coverSection.style.display = 'none';
                }
                
                // 摘要
                const summarySection = document.getElementById('detail-summary-section');
                if (news.summary) {
                    document.getElementById('detail-summary').textContent = news.summary;
                    summarySection.style.display = 'block';
                } else {
                    summarySection.style.display = 'none';
                }
                
                // 内容 - 直接使用innerHTML来显示HTML内容
                const contentEl = document.getElementById('detail-content');
                contentEl.innerHTML = news.content;
                
                document.getElementById('detail-modal').style.display = 'flex';
            }
        })
        .catch(error => {
            console.error('获取新闻详情失败:', error);
            showMessage('获取新闻详情失败', 'error');
        });
}

// 从详情页编辑
function editFromDetail() {
    if (currentDetailNewsId) {
        closeDetailModal();
        showEditModal(currentDetailNewsId);
    }
}

// 关闭详情模态框
function closeDetailModal() {
    currentDetailNewsId = null;
    document.getElementById('detail-modal').style.display = 'none';
}

// 关闭新闻模态框
function closeNewsModal() {
    editNewsId = null;
    uploadedImages = [];
    coverImageUrl = null;
    resetImageUpload();
    document.getElementById('news-modal').style.display = 'none';
}

// 重置图片上传相关显示
function resetImageUpload() {
    // 重置封面图片
    document.getElementById('cover-preview').style.display = 'none';
    document.getElementById('cover-upload-area').style.display = 'block';
    
    // 重置已上传图片
    document.getElementById('uploaded-images-section').style.display = 'none';
    document.getElementById('uploaded-images').innerHTML = '';
}

// 处理封面图片上传
function handleCoverUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/news/upload/image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            coverImageUrl = data.data.url;
            showCoverPreview(coverImageUrl);
            showMessage('封面上传成功', 'success');
        } else {
            showMessage(data.msg || '上传失败', 'error');
        }
    })
    .catch(error => {
        console.error('上传失败:', error);
        showMessage('上传失败', 'error');
    });
}

// 显示封面预览
function showCoverPreview(url) {
    document.getElementById('cover-image').src = url;
    document.getElementById('cover-preview').style.display = 'block';
    document.getElementById('cover-upload-area').style.display = 'none';
}

// 移除封面图片
function removeCoverImage() {
    coverImageUrl = null;
    document.getElementById('cover-preview').style.display = 'none';
    document.getElementById('cover-upload-area').style.display = 'block';
}

// 插入图片到内容
function insertImageToContent() {
    document.getElementById('content-image-upload').click();
}

// 处理内容图片上传
function handleContentImageUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/news/upload/image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            const imageUrl = data.data.url;
            uploadedImages.push(imageUrl);
            
            // 在内容中插入图片标记
            const textarea = document.getElementById('news-content');
            const imageText = `[图片: ${imageUrl}]`;
            
            const cursorPos = textarea.selectionStart;
            const textBefore = textarea.value.substring(0, cursorPos);
            const textAfter = textarea.value.substring(cursorPos);
            
            textarea.value = textBefore + '\n' + imageText + '\n' + textAfter;
            
            // 更新已上传图片显示
            updateUploadedImagesDisplay();
            
            showMessage('图片上传成功', 'success');
        } else {
            showMessage(data.msg || '上传失败', 'error');
        }
    })
    .catch(error => {
        console.error('上传失败:', error);
        showMessage('上传失败', 'error');
    });
}

// 更新已上传图片显示
function updateUploadedImagesDisplay() {
    const container = document.getElementById('uploaded-images');
    const section = document.getElementById('uploaded-images-section');
    
    if (uploadedImages.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    container.innerHTML = '';
    
    uploadedImages.forEach((url, index) => {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'uploaded-image';
        imageDiv.innerHTML = `
            <img src="${url}" alt="已上传图片">
            <button type="button" class="remove-btn" onclick="removeUploadedImage(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(imageDiv);
    });
}

// 移除已上传的图片
function removeUploadedImage(index) {
    const removedUrl = uploadedImages[index];
    uploadedImages.splice(index, 1);
    
    // 从内容中移除对应的图片标记
    const textarea = document.getElementById('news-content');
    const imageText = `[图片: ${removedUrl}]`;
    textarea.value = textarea.value.replace(imageText, '');
    
    updateUploadedImagesDisplay();
}

// 保存新闻
function saveNews() {
    const title = document.getElementById('news-title').value.trim();
    const author = document.getElementById('news-author').value.trim();
    const category = document.getElementById('news-category').value;
    const status = parseInt(document.getElementById('news-status').value);
    const summary = document.getElementById('news-summary').value.trim();
    let content = document.getElementById('news-content').value.trim();
    
    // 基础验证
    if (!title) {
        showMessage('请输入新闻标题', 'warning');
        return;
    }
    
    if (!author) {
        showMessage('请输入作者', 'warning');
        return;
    }
    
    if (!content) {
        showMessage('请输入新闻内容', 'warning');
        return;
    }
    
    // 处理内容中的图片标记，转换为HTML img标签
    uploadedImages.forEach(url => {
        const imageText = `[图片: ${url}]`;
        const imgTag = `<img src="${url}" alt="新闻图片" style="max-width: 100%; height: auto; margin: 10px 0; border-radius: 4px;">`;
        content = content.replace(new RegExp(escapeRegExp(imageText), 'g'), imgTag);
    });
    
    // 处理换行符
    content = content.replace(/\n/g, '<br>');
    
    const newsData = {
        title,
        author,
        category,
        status,
        summary,
        content,
        coverImage: coverImageUrl,
        images: uploadedImages
    };
    
    const url = editNewsId ? `/news/update/${editNewsId}` : '/news/add';
    const method = 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newsData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            showMessage(editNewsId ? '更新成功' : '添加成功', 'success');
            closeNewsModal();
            loadNewsList(currentPage);
            loadStatistics(); // 重新加载统计信息
        } else {
            showMessage(data.msg || '操作失败', 'error');
        }
    })
    .catch(error => {
        console.error('操作失败:', error);
        showMessage('操作失败', 'error');
    });
}

// 转义正则表达式特殊字符
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 显示删除确认模态框
function showDeleteModal(newsId) {
    deleteNewsId = newsId;
    document.getElementById('delete-modal').style.display = 'flex';
}

// 关闭删除模态框
function closeDeleteModal() {
    deleteNewsId = null;
    document.getElementById('delete-modal').style.display = 'none';
}

// 确认删除
function confirmDelete() {
    if (!deleteNewsId) return;
    
    fetch(`/news/delete/${deleteNewsId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.code === 200) {
            showMessage('删除成功', 'success');
            closeDeleteModal();
            loadNewsList(currentPage);
            loadStatistics(); // 重新加载统计信息
        } else {
            showMessage(data.msg || '删除失败', 'error');
        }
    })
    .catch(error => {
        console.error('删除失败:', error);
        showMessage('删除失败', 'error');
    });
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 显示消息提示
function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // 添加样式
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-size: 14px;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // 根据类型设置背景色
    switch(type) {
        case 'success':
            messageEl.style.backgroundColor = '#28a745';
            break;
        case 'error':
            messageEl.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            messageEl.style.backgroundColor = '#ffc107';
            messageEl.style.color = '#212529';
            break;
        default:
            messageEl.style.backgroundColor = '#17a2b8';
    }
    
    // 添加到页面
    document.body.appendChild(messageEl);
    
    // 显示动画
    setTimeout(() => {
        messageEl.style.transform = 'translateX(0)';
    }, 10);
    
    // 3秒后自动隐藏
    setTimeout(() => {
        messageEl.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(messageEl);
        }, 300);
    }, 3000);
} 