/**
 * Карусель функций с автоматической прокруткой
 * Показывает 3 карточки одновременно, автоматически прокручивает каждые 4 секунды
 */

class FeaturesCarousel {
    constructor() {
        this.carousel = document.getElementById('featuresCarousel')
        this.indicators = document.querySelectorAll('.carousel-indicators .indicator')
        this.cards = document.querySelectorAll('.feature-card')

        this.currentSlide = 0
        this.totalSlides = Math.ceil(this.cards.length / 3) // 3 карточки на слайд
        this.autoSlideInterval = null
        this.slideDuration = 4000 // 4 секунды

        this.init()
    }

    init() {
        if (!this.carousel || this.cards.length === 0) {
            return
        }

        this.setupEventListeners()
        this.startAutoSlide()
        this.updateIndicators()

        // Пауза при наведении
        this.carousel.addEventListener('mouseenter', () => this.pauseAutoSlide())
        this.carousel.addEventListener('mouseleave', () => this.startAutoSlide())
    }

    setupEventListeners() {
        // Клики по индикаторам
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.goToSlide(index)
                this.pauseAutoSlide()
                // Перезапускаем автопрокрутку через 5 секунд после клика
                setTimeout(() => this.startAutoSlide(), 5000)
            })
        })

        // Touch события для мобильных устройств
        let startX = 0
        let startY = 0
        let isDragging = false

        this.carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX
            startY = e.touches[0].clientY
            isDragging = true
            this.pauseAutoSlide()
        })

        this.carousel.addEventListener('touchmove', (e) => {
            if (!isDragging) return

            const currentX = e.touches[0].clientX
            const currentY = e.touches[0].clientY
            const diffX = startX - currentX
            const diffY = startY - currentY

            // Если горизонтальный свайп больше вертикального
            if (Math.abs(diffX) > Math.abs(diffY)) {
                e.preventDefault()
            }
        })

        this.carousel.addEventListener('touchend', (e) => {
            if (!isDragging) return

            const endX = e.changedTouches[0].clientX
            const diffX = startX - endX
            const threshold = 50

            if (Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    this.nextSlide()
                } else {
                    this.prevSlide()
                }
            }

            isDragging = false
            // Перезапускаем автопрокрутку через 3 секунды после свайпа
            setTimeout(() => this.startAutoSlide(), 3000)
        })

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prevSlide()
                this.pauseAutoSlide()
                setTimeout(() => this.startAutoSlide(), 5000)
            } else if (e.key === 'ArrowRight') {
                this.nextSlide()
                this.pauseAutoSlide()
                setTimeout(() => this.startAutoSlide(), 5000)
            }
        })
    }

    goToSlide(slideIndex) {
        if (slideIndex < 0 || slideIndex >= this.totalSlides) {
            return
        }

        this.currentSlide = slideIndex
        const translateX = -slideIndex * 100
        this.carousel.style.transform = `translateX(${translateX}%)`
        this.updateIndicators()
    }

    nextSlide() {
        const nextSlide = (this.currentSlide + 1) % this.totalSlides
        this.goToSlide(nextSlide)
    }

    prevSlide() {
        const prevSlide = this.currentSlide === 0 ? this.totalSlides - 1 : this.currentSlide - 1
        this.goToSlide(prevSlide)
    }

    startAutoSlide() {
        this.pauseAutoSlide()
        this.autoSlideInterval = setInterval(() => {
            this.nextSlide()
        }, this.slideDuration)
    }

    pauseAutoSlide() {
        if (this.autoSlideInterval) {
            clearInterval(this.autoSlideInterval)
            this.autoSlideInterval = null
        }
    }

    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide)
        })
    }

    // Публичные методы для внешнего управления
    play() {
        this.startAutoSlide()
    }

    stop() {
        this.pauseAutoSlide()
    }

    reset() {
        this.goToSlide(0)
        this.startAutoSlide()
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function () {
    // Инициализируем карусель только на главной странице
    if (window.location.pathname === '/' || window.location.pathname === '') {
        new FeaturesCarousel()
    }
})

// Экспортируем для внешнего использования
window.FeaturesCarousel = FeaturesCarousel
