/**
 * 前端首页 V2 JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // 初始化导航栏
    initNavbar();
    
    // 初始化统计数字动画
    initCountAnimation();
    
    // 添加滚动动画
    initScrollAnimations();
});

/**
 * 初始化导航栏
 */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    // 滚动时改变导航栏样式
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // 移动端菜单切换
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
    
    // 点击导航链接后关闭菜单
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    });
    
    // 下拉菜单处理（移动端）
    const dropdownItems = document.querySelectorAll('.nav-dropdown');
    dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link && window.innerWidth < 992) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                item.classList.toggle('active');
            });
        }
    });
}


/**
 * 初始化统计数字动画
 */
function initCountAnimation() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    // 观察者选项
    const options = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    // 创建交叉观察者
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // 获取目标值（去除非数字字符）
                const targetText = element.textContent;
                const targetValue = parseInt(targetText.replace(/\D/g, ''));
                
                // 如果无法解析为数字，不执行动画
                if (isNaN(targetValue)) return;
                
                // 设置初始值
                let startValue = 0;
                
                // 设置动画持续时间和帧数
                const duration = 2000; // 2秒
                const frameDuration = 1000 / 60; // 60fps
                const totalFrames = Math.round(duration / frameDuration);
                
                // 执行动画
                let frame = 0;
                const counter = setInterval(() => {
                    frame++;
                    
                    // 使用缓动函数使动画更自然
                    const progress = frame / totalFrames;
                    const easedProgress = easeOutQuart(progress);
                    
                    // 计算当前值
                    const currentValue = Math.round(targetValue * easedProgress);
                    
                    // 添加+符号和千位分隔符
                    element.textContent = currentValue.toLocaleString() + (targetText.includes('+') ? '+' : '');
                    
                    // 动画结束
                    if (frame === totalFrames) {
                        clearInterval(counter);
                    }
                }, frameDuration);
                
                // 停止观察该元素
                observer.unobserve(element);
            }
        });
    }, options);
    
    // 开始观察所有统计数字元素
    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
}

/**
 * 缓动函数 - 使动画更自然
 */
function easeOutQuart(x) {
    return 1 - Math.pow(1 - x, 4);
}

/**
 * 初始化滚动动画
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .news-card');
    
    const options = {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, options);
    
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        observer.observe(element);
    });
}
