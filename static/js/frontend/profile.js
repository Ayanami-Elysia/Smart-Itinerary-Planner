document.addEventListener('DOMContentLoaded', function() {
    const backToHomeBtn = document.getElementById('back-to-home-btn');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const profileLogoutBtn = document.getElementById('profile-logout-btn');
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const editForm = document.getElementById('edit-form');
    const logoutModal = document.getElementById('logout-modal');
    const closeModal = document.getElementById('close-modal');
    const cancelLogoutBtn = document.getElementById('cancel-logout-btn');
    const confirmLogoutBtn = document.getElementById('confirm-logout-btn');
    
    let currentUserData = null;
    
    // 首先检查 localStorage 中的用户信息
    const userInfo = localStorage.getItem('userInfo');
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    
    if (isLoggedIn === 'true' && userInfo) {
        // 从 localStorage 中获取用户信息
        const userData = JSON.parse(userInfo);
        currentUserData = userData;
        loadUserProfile(userData);
        updateNavbar(userData);
    } else {
        // 检查服务器端的登录状态
        fetch('/user/checkLogin')
            .then(response => response.json())
            .then(data => {
                if (data.code === 200) {
                    // 用户已登录，更新 localStorage
                    const userInfo = {
                        user_id: data.data.user_id,
                        username: data.data.username,
                        nickname: data.data.nickname,
                        role: data.data.role,
                        loginTime: new Date().getTime()
                    };
                    localStorage.setItem('userInfo', JSON.stringify(userInfo));
                    localStorage.setItem('isLoggedIn', 'true');
                    
                    currentUserData = data.data;
                    loadUserProfile(data.data);
                    updateNavbar(data.data);
                } else {
                    // 用户未登录，跳转到登录页面
                    localStorage.removeItem('userInfo');
                    localStorage.removeItem('isLoggedIn');
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                console.error('检查登录状态失败:', error);
                localStorage.removeItem('userInfo');
                localStorage.removeItem('isLoggedIn');
                window.location.href = '/login';
            });
    }
    
    // 更新导航栏显示
    function updateNavbar(userData) {
        const loginBtn = document.getElementById('login-btn');
        const userDropdown = document.getElementById('user-dropdown');
        const usernameDisplay = document.getElementById('username-display');
        
        if (loginBtn && userDropdown && usernameDisplay) {
            loginBtn.style.display = 'none';
            userDropdown.style.display = 'inline-block';
            usernameDisplay.textContent = userData.username;
        }
    }
    
    // 加载用户个人信息
    function loadUserProfile(userData) {
        // 设置基本信息
        document.getElementById('profile-nickname').textContent = userData.nickname || userData.username;
        document.getElementById('profile-role').textContent = userData.role;
        document.getElementById('profile-username').textContent = userData.username;
        
        // 如果 localStorage 中有完整信息，直接使用
        if (userData.email || userData.phone || userData.sex || userData.age) {
            document.getElementById('profile-email').textContent = userData.email || '未设置';
            document.getElementById('profile-phone').textContent = userData.phone || '未设置';
            document.getElementById('profile-sex').textContent = userData.sex || '未设置';
            document.getElementById('profile-age').textContent = userData.age || '未设置';
        } else {
            // 否则从服务器获取完整信息
            fetch(`/user/getUserInfo?id=${userData.user_id}`)
                .then(response => response.json())
                .then(data => {
                    if (data.code === 200) {
                        const userInfo = data.data;
                        document.getElementById('profile-email').textContent = userInfo.email || '未设置';
                        document.getElementById('profile-phone').textContent = userInfo.phone || '未设置';
                        document.getElementById('profile-sex').textContent = userInfo.sex || '未设置';
                        document.getElementById('profile-age').textContent = userInfo.age || '未设置';
                        
                        // 更新 localStorage 中的用户信息
                        const updatedUserInfo = Object.assign(userData, {
                            email: userInfo.email,
                            phone: userInfo.phone,
                            sex: userInfo.sex,
                            age: userInfo.age
                        });
                        currentUserData = updatedUserInfo;
                        localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo));
                    } else {
                        console.error('获取用户信息失败:', data.message);
                    }
                })
                .catch(error => {
                    console.error('获取用户信息失败:', error);
                });
        }
    }
    
    // 返回首页
    if (backToHomeBtn) {
        backToHomeBtn.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
    
    // 编辑个人信息
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            // 填充编辑表单
            document.getElementById('edit-username').value = currentUserData.username;
            document.getElementById('edit-nickname').value = currentUserData.nickname || '';
            document.getElementById('edit-email').value = currentUserData.email || '';
            document.getElementById('edit-phone').value = currentUserData.phone || '';
            document.getElementById('edit-sex').value = currentUserData.sex || '';
            document.getElementById('edit-age').value = currentUserData.age || '';
            
            // 切换到编辑模式
            viewMode.style.display = 'none';
            editMode.style.display = 'block';
        });
    }
    
    // 取消编辑
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function() {
            // 切换回查看模式
            editMode.style.display = 'none';
            viewMode.style.display = 'block';
        });
    }
    
    // 保存个人信息
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = {
                id: currentUserData.user_id,
                username: document.getElementById('edit-username').value,
                nickname: document.getElementById('edit-nickname').value,
                email: document.getElementById('edit-email').value,
                phone: document.getElementById('edit-phone').value,
                sex: document.getElementById('edit-sex').value,
                age: document.getElementById('edit-age').value
            };
            
            // 表单验证
            if (!formData.nickname) {
                showMessage('请输入昵称', 'warning');
                return;
            }
            
            if (formData.email && !validateEmail(formData.email)) {
                showMessage('请输入有效的邮箱地址', 'warning');
                return;
            }
            
            if (formData.phone && !validatePhone(formData.phone)) {
                showMessage('请输入有效的手机号码', 'warning');
                return;
            }
            
            if (formData.age && (formData.age < 1 || formData.age > 120)) {
                showMessage('年龄必须在1-120之间', 'warning');
                return;
            }
            
            // 发送更新请求
            fetch('/user/edit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.code === 200) {
                    showMessage('个人信息更新成功', 'success');
                    
                    // 更新当前用户数据和localStorage
                    currentUserData = Object.assign(currentUserData, formData);
                    localStorage.setItem('userInfo', JSON.stringify(currentUserData));
                    
                    // 更新显示
                    loadUserProfile(currentUserData);
                    
                    // 切换回查看模式
                    setTimeout(() => {
                        editMode.style.display = 'none';
                        viewMode.style.display = 'block';
                    }, 1000);
                } else {
                    showMessage(data.message || '更新失败，请重试', 'error');
                }
            })
            .catch(error => {
                console.error('更新个人信息失败:', error);
                showMessage('更新失败，请检查网络连接', 'error');
            });
        });
    }
    
    // 表单验证函数
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validatePhone(phone) {
        const re = /^1[3-9]\d{9}$/;
        return re.test(phone);
    }
    
    // 显示退出登录确认对话框
    if (profileLogoutBtn) {
        profileLogoutBtn.addEventListener('click', function() {
            console.log('退出登录按钮被点击');
            logoutModal.style.display = 'flex';
        });
    }
    
    // 关闭模态框
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            logoutModal.style.display = 'none';
        });
    }
    
    if (cancelLogoutBtn) {
        cancelLogoutBtn.addEventListener('click', function() {
            logoutModal.style.display = 'none';
        });
    }
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === logoutModal) {
            logoutModal.style.display = 'none';
        }
    });
    
    // 确认退出登录
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener('click', function() {
            console.log('确认退出登录');
            logout();
        });
    }
    
    // 退出登录功能
    function logout() {
        console.log('执行退出登录');
        
        // 关闭模态框
        logoutModal.style.display = 'none';
        
        fetch('/user/logout')
            .then(response => response.json())
            .then(data => {
                console.log('退出登录响应:', data);
                if (data.code === 200) {
                    // 清除 localStorage 中的用户信息
                    localStorage.removeItem('userInfo');
                    localStorage.removeItem('isLoggedIn');
                    
                    showMessage('退出登录成功', 'success');
                    
                    // 延迟跳转到首页
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    showMessage('退出登录失败，请重试', 'error');
                }
            })
            .catch(error => {
                console.error('退出登录失败:', error);
                // 即使出错也清除本地缓存
                localStorage.removeItem('userInfo');
                localStorage.removeItem('isLoggedIn');
                showMessage('退出登录失败，但已清除本地缓存', 'warning');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            });
    }
    
    // 显示消息提示
    function showMessage(message, type = 'success') {
        const messageBox = document.getElementById('message-box');
        const messageIcon = messageBox.querySelector('.message-icon');
        const messageText = messageBox.querySelector('.message-text');
        
        // 设置图标和样式
        let icon = '';
        messageBox.className = 'message-box show ' + type;
        
        switch(type) {
            case 'success':
                icon = '✓';
                break;
            case 'error':
                icon = '✗';
                break;
            case 'warning':
                icon = '⚠';
                break;
            default:
                icon = 'ℹ';
        }
        
        messageIcon.textContent = icon;
        messageText.textContent = message;
        
        // 显示消息框
        messageBox.style.display = 'flex';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            messageBox.classList.remove('show');
            setTimeout(() => {
                messageBox.style.display = 'none';
            }, 300);
        }, 3000);
    }
    
    // 处理导航栏中的退出登录按钮
    document.addEventListener('click', function(e) {
        // 检查是否点击了导航栏中的退出登录链接
        if (e.target.closest('.nav-logout-btn') || e.target.closest('#nav-logout-btn')) {
            e.preventDefault();
            console.log('导航栏退出登录被点击');
            logoutModal.style.display = 'flex';
        }
    });
}); 