// Scroll Progress Bar - индикатор прогресса чтения страницы
class ScrollProgressBar {
    constructor() {
        this.progressBar = null;
        this.isVisible = false;
        this.init();
    }

    init() {
        this.createProgressBar();
        this.bindEvents();
        this.updateProgress();
    }

    createProgressBar() {
        // Создаем элемент прогресс-бара
        this.progressBar = document.createElement('div');
        this.progressBar.id = 'scroll-progress-bar';
        this.progressBar.innerHTML = `
            <div class="progress-fill"></div>
        `;

        // Добавляем стили
        const style = document.createElement('style');
        style.textContent = `
            #scroll-progress-bar {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: rgba(0, 0, 0, 0.1);
                z-index: 9999;
                transition: opacity 0.3s ease;
                opacity: 0;
            }

            #scroll-progress-bar.visible {
                opacity: 1;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #B595FF 0%, #9A7FE6 100%);
                width: 0%;
                transition: width 0.1s ease;
                position: relative;
            }

        `;

        document.head.appendChild(style);
        document.body.appendChild(this.progressBar);
    }

    bindEvents() {
        // Отслеживаем скролл
        window.addEventListener('scroll', () => {
            this.updateProgress();
        }, { passive: true });

        // Отслеживаем изменение размера окна
        window.addEventListener('resize', () => {
            this.updateProgress();
        }, { passive: true });
    }

    updateProgress() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100));

        if (this.progressBar) {
            const fill = this.progressBar.querySelector('.progress-fill');

            if (fill) {
                fill.style.width = `${progress}%`;
            }

            // Показываем/скрываем прогресс-бар
            if (progress > 5 && !this.isVisible) {
                this.showProgressBar();
            } else if (progress <= 5 && this.isVisible) {
                this.hideProgressBar();
            }
        }
    }

    showProgressBar() {
        if (this.progressBar) {
            this.progressBar.classList.add('visible');
            this.isVisible = true;
        }
    }

    hideProgressBar() {
        if (this.progressBar) {
            this.progressBar.classList.remove('visible');
            this.isVisible = false;
        }
    }

    // Метод для принудительного скрытия (например, при загрузке)
    forceHide() {
        if (this.progressBar) {
            this.progressBar.style.display = 'none';
        }
    }

    // Метод для показа (например, после загрузки)
    forceShow() {
        if (this.progressBar) {
            this.progressBar.style.display = 'block';
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Небольшая задержка для плавности
    setTimeout(() => {
        window.scrollProgressBar = new ScrollProgressBar();
    }, 100);
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScrollProgressBar;
}
