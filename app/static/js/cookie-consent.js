/**
 * Система управления согласием на использование куки
 * Показывает плашку только на главной странице и только если пользователь еще не дал согласие
 */

class CookieConsentManager {
    constructor() {
        this.consentKey = 'cysu_cookie_consent';
        this.consentExpiry = 365; // дней
        this.bannerId = 'cookie-consent-banner';
        this.isMainPage = window.location.pathname === '/' || window.location.pathname === '';
        
        this.init();
    }

    init() {
        // Показываем плашку только на главной странице и только если нет сохраненного согласия
        if (this.isMainPage && !this.hasConsent()) {
            this.showBanner();
            this.bindEvents();
        }
    }

    hasConsent() {
        const consent = this.getCookie(this.consentKey);
        return consent === 'accepted' || consent === 'declined';
    }

    showBanner() {
        const banner = document.getElementById(this.bannerId);
        if (banner) {
            banner.style.display = 'block';
            
            // Плавное появление
            setTimeout(() => {
                banner.classList.add('show');
            }, 100);
        }
    }

    hideBanner() {
        const banner = document.getElementById(this.bannerId);
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => {
                banner.style.display = 'none';
            }, 300);
        }
    }

    acceptCookies() {
        this.setCookie(this.consentKey, 'accepted', this.consentExpiry);
        this.hideBanner();
        this.enableAnalytics();
        this.showSuccessMessage('Согласие на использование куки принято');
    }

    declineCookies() {
        this.setCookie(this.consentKey, 'declined', this.consentExpiry);
        this.hideBanner();
        this.disableAnalytics();
        this.showSuccessMessage('Использование куки отклонено');
    }

    enableAnalytics() {
        // Включаем аналитику и другие куки
        console.log('Аналитика включена');
        
        // Здесь можно добавить код для включения Google Analytics, Yandex Metrica и т.д.
        // Например:
        // if (typeof gtag !== 'undefined') {
        //     gtag('consent', 'update', {
        //         'analytics_storage': 'granted'
        //     });
        // }
    }

    disableAnalytics() {
        // Отключаем аналитику
        console.log('Аналитика отключена');
        
        // Здесь можно добавить код для отключения аналитики
        // Например:
        // if (typeof gtag !== 'undefined') {
        //     gtag('consent', 'update', {
        //         'analytics_storage': 'denied'
        //     });
        // }
    }

    showSuccessMessage(message) {
        // Показываем уведомление о принятом решении
        const toast = document.createElement('div');
        toast.className = 'cookie-consent-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Показываем toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Убираем через 3 секунды
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    bindEvents() {
        const acceptBtn = document.getElementById('cookie-consent-accept');
        const declineBtn = document.getElementById('cookie-consent-decline');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => this.acceptCookies());
        }

        if (declineBtn) {
            declineBtn.addEventListener('click', () => this.declineCookies());
        }
    }

    setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }

    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // Метод для проверки статуса согласия (для других скриптов)
    static getConsentStatus() {
        const manager = new CookieConsentManager();
        return manager.getCookie(manager.consentKey);
    }

    // Метод для сброса согласия (для тестирования)
    static resetConsent() {
        const manager = new CookieConsentManager();
        manager.setCookie(manager.consentKey, '', -1);
        console.log('Согласие на куки сброшено');
    }
}

// Инициализируем при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    new CookieConsentManager();
});

// Экспортируем для использования в других скриптах
window.CookieConsentManager = CookieConsentManager;
