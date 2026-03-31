/* ===== 校园二手交易平台 - 专业交互系统 ===== */

// 滚动监听 - 导航栏效果
class ScrollManager {
    constructor() {
        this.navbar = document.getElementById('mainNav');
        this.lastScrollY = window.scrollY;
        this.init();
    }

    init() {
        if (this.navbar) {
            window.addEventListener('scroll', this.handleScroll.bind(this));
            this.handleScroll(); // 初始化状态
        }
    }

    handleScroll() {
        const currentScrollY = window.scrollY;
        
        // 滚动方向检测
        const scrollingDown = currentScrollY > this.lastScrollY;
        
        // 导航栏滚动效果
        if (currentScrollY > 100) {
            this.navbar.classList.add('scrolled');
            if (scrollingDown && currentScrollY > 200) {
                this.navbar.style.transform = 'translateY(-100%)';
            } else {
                this.navbar.style.transform = 'translateY(0)';
            }
        } else {
            this.navbar.classList.remove('scrolled');
            this.navbar.style.transform = 'translateY(0)';
        }
        
        this.lastScrollY = currentScrollY;
    }
}

// 卡片悬停效果增强
class CardAnimator {
    constructor() {
        this.cards = document.querySelectorAll('.card-pro');
        this.init();
    }

    init() {
        this.cards.forEach(card => {
            card.addEventListener('mouseenter', this.handleMouseEnter.bind(this));
            card.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
        });
    }

    handleMouseEnter(e) {
        const card = e.currentTarget;
        card.style.transform = 'translateY(-8px) scale(1.02)';
        card.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
    }

    handleMouseLeave(e) {
        const card = e.currentTarget;
        card.style.transform = 'translateY(0) scale(1)';
        card.style.boxShadow = '';
    }
}

// 按钮交互效果
class ButtonAnimator {
    constructor() {
        this.buttons = document.querySelectorAll('.btn-pro');
        this.init();
    }

    init() {
        this.buttons.forEach(button => {
            button.addEventListener('mousedown', this.handleMouseDown.bind(this));
            button.addEventListener('mouseup', this.handleMouseUp.bind(this));
            button.addEventListener('mouseleave', this.handleMouseUp.bind(this));
        });
    }

    handleMouseDown(e) {
        const button = e.currentTarget;
        button.style.transform = 'scale(0.95)';
    }

    handleMouseUp(e) {
        const button = e.currentTarget;
        button.style.transform = 'scale(1)';
    }
}

// 表单交互增强
class FormEnhancer {
    constructor() {
        this.inputs = document.querySelectorAll('.form-control-pro');
        this.init();
    }

    init() {
        this.inputs.forEach(input => {
            input.addEventListener('focus', this.handleFocus.bind(this));
            input.addEventListener('blur', this.handleBlur.bind(this));
            
            // 实时验证效果
            input.addEventListener('input', this.handleInput.bind(this));
        });
    }

    handleFocus(e) {
        const input = e.currentTarget;
        input.parentElement.classList.add('focused');
    }

    handleBlur(e) {
        const input = e.currentTarget;
        input.parentElement.classList.remove('focused');
        
        // 验证状态
        if (input.value.trim() === '') {
            input.classList.remove('valid', 'invalid');
        } else if (this.validateInput(input)) {
            input.classList.add('valid');
            input.classList.remove('invalid');
        } else {
            input.classList.add('invalid');
            input.classList.remove('valid');
        }
    }

    handleInput(e) {
        const input = e.currentTarget;
        
        // 实时验证提示
        if (input.value.trim() !== '') {
            if (this.validateInput(input)) {
                this.showValidationHint(input, 'valid', '✓ 格式正确');
            } else {
                this.showValidationHint(input, 'invalid', '⚠ 请检查格式');
            }
        } else {
            this.hideValidationHint(input);
        }
    }

    validateInput(input) {
        const type = input.type || input.getAttribute('data-type');
        const value = input.value.trim();
        
        switch (type) {
            case 'email':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'tel':
                return /^1[3-9]\d{9}$/.test(value);
            case 'password':
                return value.length >= 6;
            default:
                return value.length > 0;
        }
    }

    showValidationHint(input, type, message) {
        let hint = input.parentElement.querySelector('.validation-hint');
        if (!hint) {
            hint = document.createElement('div');
            hint.className = 'validation-hint';
            input.parentElement.appendChild(hint);
        }
        hint.textContent = message;
        hint.className = `validation-hint ${type}`;
    }

    hideValidationHint(input) {
        const hint = input.parentElement.querySelector('.validation-hint');
        if (hint) {
            hint.remove();
        }
    }
}

// 加载状态管理
class LoadingManager {
    static show(element, text = '加载中...') {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-overlay';
        loadingEl.innerHTML = `
            <div class="loading-spinner">
                <div class="loading-pro"></div>
                <span>${text}</span>
            </div>
        `;
        
        element.style.position = 'relative';
        element.appendChild(loadingEl);
        
        return loadingEl;
    }

    static hide(loadingEl) {
        if (loadingEl && loadingEl.parentElement) {
            loadingEl.parentElement.removeChild(loadingEl);
        }
    }

    static async withLoading(element, asyncFunction, loadingText = '加载中...') {
        const loadingEl = this.show(element, loadingText);
        
        try {
            const result = await asyncFunction();
            return result;
        } finally {
            this.hide(loadingEl);
        }
    }
}

// 通知系统
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.init();
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    }

    init() {
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1060;
                max-width: 400px;
            }
            
            .notification {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 10px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                animation: slideInRight 0.3s ease-out;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .notification.success {
                border-left: 4px solid #10b981;
            }
            
            .notification.error {
                border-left: 4px solid #ef4444;
            }
            
            .notification.warning {
                border-left: 4px solid #f59e0b;
            }
            
            .notification.info {
                border-left: 4px solid #3b82f6;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            ${icon}
            <span>${message}</span>
        `;
        
        this.container.appendChild(notification);
        
        // 自动消失
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
        
        // 点击关闭
        notification.addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        });
        
        return notification;
    }

    getIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle" style="color: #10b981;"></i>',
            error: '<i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>',
            warning: '<i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>',
            info: '<i class="fas fa-info-circle" style="color: #3b82f6;"></i>'
        };
        return icons[type] || icons.info;
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化各个管理器
    new ScrollManager();
    new CardAnimator();
    new ButtonAnimator();
    new FormEnhancer();
    
    // 全局通知系统
    window.notification = new NotificationSystem();
    
    // 添加CSS动画样式
    const animationStyles = document.createElement('style');
    animationStyles.textContent = `
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .validation-hint {
            font-size: 0.75rem;
            margin-top: 4px;
            display: block;
        }
        
        .validation-hint.valid {
            color: #10b981;
        }
        
        .validation-hint.invalid {
            color: #ef4444;
        }
        
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            border-radius: inherit;
        }
        
        .loading-spinner {
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }
        
        .form-group-pro.focused .form-label-pro {
            color: #0ea5e9;
        }
        
        .form-control-pro.valid {
            border-color: #10b981 !important;
        }
        
        .form-control-pro.invalid {
            border-color: #ef4444 !important;
        }
    `;
    document.head.appendChild(animationStyles);
    
    // 页面加载完成后的动画效果
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transition = 'opacity 0.3s ease-in';
    }, 100);
});

// 页面加载时的初始样式
document.body.style.opacity = '0';

// 导出到全局作用域
window.DesignSystem = {
    ScrollManager,
    CardAnimator,
    ButtonAnimator,
    FormEnhancer,
    LoadingManager,
    NotificationSystem
};