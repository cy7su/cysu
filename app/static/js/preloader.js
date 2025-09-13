// Preloader/Spinner - красивый лоадер при загрузке страниц
class Preloader {
    constructor() {
        this.preloader = null;
        this.isFirstLoad = true;
        this.loadingTime = 0;
        this.minLoadingTime = 800; // Минимальное время показа 800ms
        this.maxLoadingTime = 3000; // Максимальное время показа 3s
        this.init();
    }

    init() {
        // Проверяем, первая ли это загрузка
        this.checkFirstLoad();
        
        if (this.isFirstLoad) {
            this.createPreloader();
            this.startLoading();
        }
    }

    checkFirstLoad() {
        // Проверяем, есть ли данные о предыдущих загрузках
        const lastLoad = localStorage.getItem('cysu_last_load');
        const now = Date.now();
        
        // Если прошло больше 30 минут или это первая загрузка
        if (!lastLoad || (now - parseInt(lastLoad)) > 30 * 60 * 1000) {
            this.isFirstLoad = true;
            localStorage.setItem('cysu_last_load', now.toString());
        } else {
            this.isFirstLoad = false;
        }
    }

    createPreloader() {
        // Создаем элемент прелоадера
        this.preloader = document.createElement('div');
        this.preloader.id = 'cysu-preloader';
        this.preloader.innerHTML = `
            <div class="preloader-backdrop"></div>
            <div class="preloader-content">
                <div class="preloader-logo">
                    <div class="logo-circle">
                        <span class="logo-text">cysu</span>
                    </div>
                </div>
                <div class="preloader-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="preloader-text">Загрузка...</div>
                <div class="preloader-progress">
                    <div class="progress-bar"></div>
                </div>
            </div>
        `;

        // Добавляем стили
        const style = document.createElement('style');
        style.textContent = `
            #cysu-preloader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 1;
                transition: opacity 0.5s ease;
            }

            #cysu-preloader.fade-out {
                opacity: 0;
                pointer-events: none;
            }

            .preloader-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #0e0e0f 0%, #1a1a1a 100%);
            }

            .preloader-content {
                position: relative;
                text-align: center;
                z-index: 1;
            }

            .preloader-logo {
                margin-bottom: 30px;
            }

            .logo-circle {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: linear-gradient(135deg, #B595FF 0%, #9A7FE6 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                box-shadow: 0 8px 32px rgba(181, 149, 255, 0.3);
                animation: logoPulse 2s ease-in-out infinite;
            }

            .logo-text {
                font-size: 24px;
                font-weight: 700;
                color: white;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }

            .preloader-spinner {
                position: relative;
                width: 60px;
                height: 60px;
                margin: 0 auto 20px;
            }

            .spinner-ring {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border: 3px solid transparent;
                border-top: 3px solid #B595FF;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            .spinner-ring:nth-child(2) {
                width: 80%;
                height: 80%;
                top: 10%;
                left: 10%;
                border-top-color: #9A7FE6;
                animation-duration: 1.5s;
                animation-direction: reverse;
            }

            .spinner-ring:nth-child(3) {
                width: 60%;
                height: 60%;
                top: 20%;
                left: 20%;
                border-top-color: #7C3AED;
                animation-duration: 2s;
            }

            .preloader-text {
                font-size: 16px;
                color: #B595FF;
                font-weight: 500;
                margin-bottom: 20px;
                animation: textPulse 1.5s ease-in-out infinite;
            }

            .preloader-progress {
                width: 200px;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                overflow: hidden;
                margin: 0 auto;
            }

            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #B595FF 0%, #9A7FE6 100%);
                width: 0%;
                border-radius: 2px;
                transition: width 0.3s ease;
            }

            @keyframes logoPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @keyframes textPulse {
                0%, 100% { opacity: 0.7; }
                50% { opacity: 1; }
            }

            @media (max-width: 768px) {
                .logo-circle {
                    width: 60px;
                    height: 60px;
                }
                
                .logo-text {
                    font-size: 20px;
                }
                
                .preloader-spinner {
                    width: 50px;
                    height: 50px;
                }
                
                .preloader-progress {
                    width: 150px;
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(this.preloader);
    }

    startLoading() {
        const startTime = Date.now();
        this.loadingTime = startTime;

        // Симулируем прогресс загрузки
        this.simulateProgress();

        // Слушаем события загрузки
        this.bindEvents();

        // Принудительно скрываем через максимальное время
        setTimeout(() => {
            this.hidePreloader();
        }, this.maxLoadingTime);
    }

    simulateProgress() {
        let progress = 0;
        const progressBar = this.preloader?.querySelector('.progress-bar');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 100);
    }

    bindEvents() {
        // События загрузки страницы
        window.addEventListener('load', () => {
            this.onPageLoaded();
        });

        // DOM готов
        if (document.readyState === 'complete') {
            this.onPageLoaded();
        }
    }

    onPageLoaded() {
        const currentTime = Date.now();
        const elapsed = currentTime - this.loadingTime;
        
        // Ждем минимум minLoadingTime
        const remainingTime = Math.max(0, this.minLoadingTime - elapsed);
        
        setTimeout(() => {
            this.hidePreloader();
        }, remainingTime);
    }

    hidePreloader() {
        if (this.preloader) {
            this.preloader.classList.add('fade-out');
            
            // Удаляем элемент после анимации
            setTimeout(() => {
                if (this.preloader && this.preloader.parentNode) {
                    this.preloader.parentNode.removeChild(this.preloader);
                }
                this.preloader = null;
            }, 500);
        }
    }

    // Метод для принудительного скрытия
    forceHide() {
        this.hidePreloader();
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Небольшая задержка для плавности
    setTimeout(() => {
        window.cysuPreloader = new Preloader();
    }, 50);
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Preloader;
}
