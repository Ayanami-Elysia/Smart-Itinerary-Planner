/**
 * 首页特定的JavaScript功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 检查统计数据是否有动画效果
    animateStatNumbers();
    
    // 滚动效果
    handleScrollAnimations();
    
    // 图片延迟加载
    setupLazyLoading();
});

/**
 * 统计数字动画效果
 */
function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    // 观察者选项
    const options = {
        threshold: 0.5, // 当元素有50%进入视口时触发
        rootMargin: '0px'
    };
    
    // 创建交叉观察者
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // 获取目标值（去除非数字字符）
                const targetValue = parseInt(element.textContent.replace(/\D/g, ''));
                
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
                    element.textContent = currentValue.toLocaleString() + (element.textContent.includes('+') ? '+' : '');
                    
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
 * 处理滚动动画
 */
function handleScrollAnimations() {
    // 滚动时添加动画类
    const animatedElements = document.querySelectorAll('.feature-card, .news-card, .solution-card');
    
    const options = {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, options);
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    // 滚动时处理导航栏变化
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('nav');
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

/**
 * 设置图片延迟加载
 */
function setupLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const options = {
        threshold: 0.1,
        rootMargin: '200px 0px'
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    }, options);
    
    lazyImages.forEach(image => {
        observer.observe(image);
    });
}