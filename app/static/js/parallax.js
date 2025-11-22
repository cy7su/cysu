// Parallax Scrolling - эффекты глубины и анимации при скролле
class ParallaxController {
    constructor() {
        this.elements = []
        this.isEnabled = true
        this.lastScrollY = 0
        this.ticking = false
        this.init()
    }

    init() {
        // Проверяем производительность устройства
        this.checkPerformance()

        if (this.isEnabled) {
            this.bindEvents()
            this.scanElements()
            this.update()
        }
    }

    checkPerformance() {
        // Отключаем на слабых устройствах
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection
        const isSlowConnection =
            connection && (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g')
        const isLowEnd = navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4

        if (isSlowConnection || isLowEnd || window.innerWidth < 768) {
            this.isEnabled = false
        }
    }

    bindEvents() {
        // Отслеживаем скролл
        window.addEventListener(
            'scroll',
            () => {
                this.requestTick()
            },
            { passive: true },
        )

        // Отслеживаем изменение размера окна
        window.addEventListener(
            'resize',
            () => {
                this.scanElements()
            },
            { passive: true },
        )

        // Отслеживаем изменение видимости
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pause()
            } else {
                this.resume()
            }
        })
    }

    scanElements() {
        this.elements = []

        // Ищем элементы с data-parallax атрибутом
        const parallaxElements = document.querySelectorAll('[data-parallax]')

        parallaxElements.forEach((element) => {
            const config = this.parseConfig(element)
            this.elements.push({
                element,
                config,
                originalTransform: element.style.transform || '',
            })
        })
    }

    parseConfig(element) {
        const parallaxAttr = element.getAttribute('data-parallax')
        const config = {
            speed: 0.5,
            direction: 'vertical',
            scale: 1,
            rotate: 0,
            opacity: 1,
            blur: 0,
            offset: 0,
        }

        if (parallaxAttr) {
            try {
                const parsed = JSON.parse(parallaxAttr)
                Object.assign(config, parsed)
            } catch (e) {
                // Простой парсинг для формата "speed:0.3,direction:horizontal"
                const pairs = parallaxAttr.split(',')
                pairs.forEach((pair) => {
                    const [key, value] = pair.split(':').map((s) => s.trim())
                    if (key && value !== undefined) {
                        if (key === 'speed') config.speed = parseFloat(value)
                        else if (key === 'direction') config.direction = value
                        else if (key === 'scale') config.scale = parseFloat(value)
                        else if (key === 'rotate') config.rotate = parseFloat(value)
                        else if (key === 'opacity') config.opacity = parseFloat(value)
                        else if (key === 'blur') config.blur = parseFloat(value)
                        else if (key === 'offset') config.offset = parseFloat(value)
                    }
                })
            }
        }

        return config
    }

    requestTick() {
        if (!this.ticking) {
            requestAnimationFrame(() => {
                this.update()
                this.ticking = false
            })
            this.ticking = true
        }
    }

    update() {
        if (!this.isEnabled) return

        const scrollY = window.pageYOffset || document.documentElement.scrollTop
        const windowHeight = window.innerHeight
        const documentHeight = document.documentElement.scrollHeight

        this.elements.forEach(({ element, config }) => {
            const rect = element.getBoundingClientRect()
            const elementTop = rect.top + scrollY
            const elementHeight = rect.height

            // Вычисляем прогресс скролла для элемента
            const scrollProgress = (scrollY - elementTop + windowHeight) / (windowHeight + elementHeight)
            const clampedProgress = Math.max(0, Math.min(1, scrollProgress))

            // Применяем эффекты
            this.applyEffects(element, config, scrollY, scrollProgress, clampedProgress)
        })

        this.lastScrollY = scrollY
    }

    applyEffects(element, config, scrollY, scrollProgress, clampedProgress) {
        let transform = ''
        let opacity = config.opacity
        let filter = ''

        // Вертикальное движение
        if (config.direction === 'vertical' || config.direction === 'both') {
            const yOffset = (scrollY - config.offset) * config.speed
            transform += ` translateY(${yOffset}px)`
        }

        // Горизонтальное движение
        if (config.direction === 'horizontal' || config.direction === 'both') {
            const xOffset = (scrollY - config.offset) * config.speed * 0.5
            transform += ` translateX(${xOffset}px)`
        }

        // Масштабирование
        if (config.scale !== 1) {
            const scale = 1 + (config.scale - 1) * clampedProgress
            transform += ` scale(${scale})`
        }

        // Поворот
        if (config.rotate !== 0) {
            const rotation = config.rotate * scrollProgress
            transform += ` rotate(${rotation}deg)`
        }

        // Прозрачность
        if (config.opacity !== 1) {
            opacity = config.opacity * clampedProgress
        }

        // Размытие
        if (config.blur > 0) {
            const blur = config.blur * (1 - clampedProgress)
            filter += ` blur(${blur}px)`
        }

        // Применяем стили
        element.style.transform = transform
        element.style.opacity = opacity
        if (filter) {
            element.style.filter = filter
        }
    }

    // Метод для добавления элемента вручную
    addElement(element, config = {}) {
        const parsedConfig = this.parseConfig(element)
        Object.assign(parsedConfig, config)

        this.elements.push({
            element,
            config: parsedConfig,
            originalTransform: element.style.transform || '',
        })
    }

    // Метод для удаления элемента
    removeElement(element) {
        this.elements = this.elements.filter((item) => item.element !== element)
    }

    // Метод для обновления конфигурации элемента
    updateElementConfig(element, newConfig) {
        const item = this.elements.find((item) => item.element === element)
        if (item) {
            Object.assign(item.config, newConfig)
        }
    }

    // Метод для паузы
    pause() {
        this.isEnabled = false
    }

    // Метод для возобновления
    resume() {
        this.isEnabled = true
        this.update()
    }

    // Метод для полного отключения
    disable() {
        this.isEnabled = false
        this.elements.forEach(({ element, originalTransform }) => {
            element.style.transform = originalTransform
            element.style.opacity = ''
            element.style.filter = ''
        })
    }

    // Метод для включения
    enable() {
        this.isEnabled = true
        this.scanElements()
        this.update()
    }

    // Метод для получения статистики
    getStats() {
        return {
            enabled: this.isEnabled,
            elementsCount: this.elements.length,
            lastScrollY: this.lastScrollY,
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Небольшая задержка для инициализации
    setTimeout(() => {
        window.parallaxController = new ParallaxController()
    }, 200)
})

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ParallaxController
}
