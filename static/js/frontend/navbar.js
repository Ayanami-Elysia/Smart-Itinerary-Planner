// 通用导航栏功能
(function() {
    'use strict';
    
    // 退出登录功能
    function logout() {
        console.log('执行退出登录');
        
        return fetch('/user/logout')
            .then(response => response.json())
            .then(data => {
                console.log('退出登录响应:', data);
                if (data.code === 200) {
                    // 清除 localStorage 中的用户信息
                    localStorage.removeItem('userInfo');
                    localStorage.removeItem('isLoggedIn');
                    
                    // 跳转到首页
                    window.location.href = '/';
                    return true;
                } else {
                    console.error('退出登录失败:', data.message);
                    return false;
                }
            })
            .catch(error => {
                console.error('退出登录失败:', error);
                // 即使出错也清除本地缓存
                localStorage.removeItem('userInfo');
                localStorage.removeItem('isLoggedIn');
                window.location.href = '/';
                return false;
            });
    }
    
    // 更新导航栏显示
    function updateNavbar() {
        const userInfo = localStorage.getItem('userInfo');
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        const loginBtn = document.getElementById('login-btn');
        const userDropdown = document.getElementById('user-dropdown');
        const usernameDisplay = document.getElementById('username-display');
        
        if (isLoggedIn === 'true' && userInfo && loginBtn && userDropdown && usernameDisplay) {
            const userData = JSON.parse(userInfo);
            loginBtn.style.display = 'none';
            userDropdown.style.display = 'inline-block';
            usernameDisplay.textContent = userData.username;
        } else if (loginBtn && userDropdown) {
            loginBtn.style.display = 'inline-block';
            userDropdown.style.display = 'none';
        }
    }
    
    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 更新导航栏显示
        updateNavbar();
        
        // 处理退出登录点击事件
        document.addEventListener('click', function(e) {
            if (e.target.closest('.nav-logout-btn') || e.target.closest('#nav-logout-btn')) {
                e.preventDefault();
                console.log('导航栏退出登录被点击');
                
                // 根据当前页面决定确认方式
                const currentPage = window.location.pathname;
                
                if (currentPage === '/profile') {
                    // 在个人信息页面，触发模态框
                    const logoutModal = document.getElementById('logout-modal');
                    if (logoutModal) {
                        logoutModal.style.display = 'flex';
                    } else {
                        // 如果没有模态框，直接确认
                        if (confirm('您确定要退出登录吗？')) {
                            logout();
                        }
                    }
                } else {
                    // 在其他页面，直接确认
                    if (confirm('您确定要退出登录吗？')) {
                        logout();
                    }
                }
            }
        });
    });
    
    // 暴露全局函数
    window.navbarLogout = logout;
    window.updateNavbar = updateNavbar;
})(); 