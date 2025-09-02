/**
 * Генератор SVG паттернов для карточек предметов
 * Улучшенная версия с более интересными и рандомными паттернами
 */



// Простой класс для генерации паттернов
class SVGPatternGenerator {
    constructor() {
        this.primaryColor = '#B595FF';
        this.primaryHover = '#9A7FE6';
        this.backgroundColor = '#1a1a1a';
        
        // Светлая палитра цветов для фигур (от белого и светлых тонов)
        this.colorPalette = [
            '#FFFFFF', '#F8F9FA', '#E9ECEF', '#DEE2E6', '#CED4DA',
            '#ADB5BD', '#6C757D', '#495057', '#343A40', '#212529',
            '#FFF8E1', '#FFF3E0', '#FCE4EC', '#F3E5F5', '#E8EAF6',
            '#E3F2FD', '#E0F2F1', '#F1F8E9', '#FFFDE7', '#FFF3E0',
            '#FFEBEE', '#F3E5F5', '#E8EAF6', '#E3F2FD', '#E0F2F1',
            '#F1F8E9', '#FFFDE7', '#FFF8E1', '#FFF3E0', '#FCE4EC'
        ];
        
        // Темные фоновые цвета - черные и около черные
        this.backgroundPalette = [
            '#000000', '#0a0a0a', '#111111', '#1a1a1a', '#1e1e1e',
            '#212121', '#242424', '#2a2a2a', '#2d2d2d', '#333333',
            '#1a1a1a', '#0f0f0f', '#141414', '#181818', '#1c1c1c',
            '#202020', '#252525', '#2b2b2b', '#303030', '#353535'
        ];
        
    }

    setColors(primary, hover, background) {
        if (primary) this.primaryColor = primary;
        if (hover) this.primaryHover = hover;
        if (background) this.backgroundColor = background;
    }

    // Получить случайный цвет из палитры
    getRandomColor() {
        return this.colorPalette[Math.floor(Math.random() * this.colorPalette.length)];
    }

    // Получить случайный фоновый цвет
    getRandomBackground() {
        return this.backgroundPalette[Math.floor(Math.random() * this.backgroundPalette.length)];
    }

    // Получить случайное число в диапазоне
    random(min, max) {
        return Math.random() * (max - min) + min;
    }

    // Получить случайное целое число
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // Получить случайные размеры холста
    getRandomSize() {
        // Размеры карточки: 306x147, SVG должен занимать 80% места
        return {
            width: 306,
            height: 147
        };
    }

    generatePattern(patternType) {
        try {
            switch (patternType) {
                case 'dots':
                    return this.generateDotsPattern();
                case 'circles':
                    return this.generateCirclesPattern();
                case 'triangles':
                    return this.generateTrianglesPattern();
                case 'hexagons':
                    return this.generateHexagonsPattern();
                case 'waves':
                    return this.generateWavesPattern();
                case 'stars':
                    return this.generateStarsPattern();
                case 'spiral':
                    return this.generateSpiralPattern();
                default:
                    return this.generateDotsPattern();
            }
        } catch (error) {
            return this.generateDotsPattern();
        }
    }

    generateRandomPattern() {
        const patterns = ['dots', 'circles', 'triangles', 'hexagons', 'waves', 'stars', 'spiral'];
        const randomType = patterns[Math.floor(Math.random() * patterns.length)];
        console.log(`🎲 Случайный паттерн: ${randomType}`);
        return this.generatePattern(randomType);
    }

    // Улучшенный паттерн с точками - полностью рандомный
    generateDotsPattern() {

        const size = this.getRandomSize();
        const dots = [];
        const numDots = this.randomInt(80, 150);
        
        for (let i = 0; i < numDots; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const radius = this.random(1, 8); // Больше вариаций размеров
            const opacity = this.random(0.1, 0.9);
            const color = this.getRandomColor();
            
            // Случайные эффекты
            const hasStroke = Math.random() > 0.5; // Еще чаще обводки
            const strokeColor = this.getRandomColor();
            const strokeWidth = this.random(0.3, 2);
            
            let dot = `<circle cx="${x}" cy="${y}" r="${radius}" fill="${color}" opacity="${opacity}"`;
            if (hasStroke) {
                dot += ` stroke="${strokeColor}" stroke-width="${strokeWidth}"`;
            }
            dot += '/>';
            
            dots.push(dot);
        }
        
        return this.createSVG(size.width, size.height, dots.join(''));
    }

    // Улучшенный паттерн с кругами - полностью рандомный
    generateCirclesPattern() {

        const size = this.getRandomSize();
        const circles = [];
        const numCircles = this.randomInt(40, 80);
        
        for (let i = 0; i < numCircles; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const radius = this.random(5, 40); // Больше вариаций размеров
            const opacity = this.random(0.1, 0.8);
            const color = this.getRandomColor();
            
            // Случайные эффекты
            const strokeColor = this.getRandomColor();
            const strokeWidth = this.random(0.5, 3);
            
            let circle = `<circle cx="${x}" cy="${y}" r="${radius}" fill="${color}" opacity="${opacity}"`;
            if (strokeWidth > 0.8) {
                circle += ` stroke="${strokeColor}" stroke-width="${strokeWidth}"`;
            }
            circle += '/>';
            
            circles.push(circle);
        }
        
        return this.createSVG(size.width, size.height, circles.join(''));
    }

    // Улучшенный паттерн с треугольниками - полностью рандомный
    generateTrianglesPattern() {

        const size = this.getRandomSize();
        const triangles = [];
        const numTriangles = this.randomInt(35, 70);
        
        for (let i = 0; i < numTriangles; i++) {
            const centerX = this.random(0, size.width);
            const centerY = this.random(0, size.height);
            const triangleSize = this.random(10, 35); // Больше вариаций размеров
            const rotation = this.random(0, Math.PI * 2);
            const opacity = this.random(0.1, 0.8);
            const color = this.getRandomColor();
            
            // Создаем треугольник с поворотом
            const points = this.generateRotatedTriangle(centerX, centerY, triangleSize, rotation);
            
            triangles.push(`<polygon points="${points}" fill="${color}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, triangles.join(''));
    }

    // Генерирует повернутый треугольник
    generateRotatedTriangle(centerX, centerY, size, rotation) {
        const points = [];
        for (let i = 0; i < 3; i++) {
            const angle = (i * Math.PI * 2 / 3) + rotation;
            const x = centerX + size * Math.cos(angle);
            const y = centerY + size * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        return points.join(' ');
    }



    // Улучшенный паттерн с шестигранниками - полностью рандомный
    generateHexagonsPattern() {

        const size = this.getRandomSize();
        const hexagons = [];
        const numHexagons = this.randomInt(20, 40);
        
        for (let i = 0; i < numHexagons; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const hexSize = this.random(10, 30); // Больше вариаций размеров
            const opacity = this.random(0.1, 0.7);
            const color = this.getRandomColor();
            
            const points = this.generateHexagonPoints(x, y, hexSize);
            hexagons.push(`<polygon points="${points}" fill="${color}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, hexagons.join(''));
    }

    generateHexagonPoints(centerX, centerY, size) {
        const points = [];
        for (let i = 0; i < 6; i++) {
            const angle = (i * Math.PI) / 3;
            const x = centerX + size * Math.cos(angle);
            const y = centerY + size * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        return points.join(' ');
    }

    // Улучшенный паттерн с волнами - полностью рандомный
    generateWavesPattern() {

        const size = this.getRandomSize();
        const waves = [];
        const numWaves = this.randomInt(12, 25);
        
        for (let i = 0; i < numWaves; i++) {
            const y = i * (size.height / numWaves);
            const amplitude = this.random(10, 50); // Больше вариаций амплитуды
            const frequency = this.random(0.005, 0.03); // Больше вариаций частоты
            const phase = this.random(0, Math.PI * 2);
            
            // Создаем более сложную волну
            const path = this.generateComplexWave(size.width, y, amplitude, frequency, phase);
            const opacity = this.random(0.1, 0.6);
            const color = this.getRandomColor();
            const strokeWidth = this.random(1, 5); // Больше вариаций толщины
            
            waves.push(`<path d="${path}" fill="none" stroke="${color}" 
                style="opacity:${opacity};stroke-width:${strokeWidth}px;"/>`);
        }
        
        return this.createSVG(size.width, size.height, waves.join(''));
    }

    // Генерирует сложную волну
    generateComplexWave(width, y, amplitude, frequency, phase) {
        const points = [];
        const steps = 60; // Больше точек для плавности
        
        for (let i = 0; i <= steps; i++) {
            const x = (i / steps) * width;
            const waveY = y + amplitude * Math.sin(frequency * x + phase);
            points.push(`${x},${waveY}`);
        }
        
        return `M${points.join(' L')}`;
    }



    // Улучшенный паттерн со звездами - полностью рандомный
    generateStarsPattern() {

        const size = this.getRandomSize();
        const stars = [];
        const numStars = this.randomInt(25, 50);
        
        for (let i = 0; i < numStars; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const starSize = this.random(5, 20); // Больше вариаций размеров
            const points = this.randomInt(5, 10); // Больше вариаций лучей
            const opacity = this.random(0.2, 0.9);
            const color = this.getRandomColor();
            
            const starPath = this.generateStarPath(x, y, starSize, points);
            stars.push(`<path d="${starPath}" fill="${color}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, stars.join(''));
    }

    generateStarPath(centerX, centerY, size, points) {
        const path = [];
        for (let i = 0; i < points * 2; i++) {
            const angle = (i * Math.PI) / points;
            const radius = i % 2 === 0 ? size : size * 0.5;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            if (i === 0) {
                path.push(`M${x},${y}`);
            } else {
                path.push(`L${x},${y}`);
            }
        }
        path.push('Z');
        return path.join(' ');
    }

    // Улучшенный паттерн со спиралями - полностью рандомный
    generateSpiralPattern() {

        const size = this.getRandomSize();
        const spirals = [];
        const numSpirals = this.randomInt(8, 18);
        
        for (let i = 0; i < numSpirals; i++) {
            const centerX = this.random(0, size.width);
            const centerY = this.random(0, size.height);
            const maxRadius = this.random(10, 60); // Больше вариаций радиуса
            const turns = this.random(1, 8); // Больше вариаций витков
            const opacity = this.random(0.1, 0.6);
            const color = this.getRandomColor();
            const strokeWidth = this.random(0.5, 3); // Больше вариаций толщины
            
            const path = this.generateSpiralPath(centerX, centerY, maxRadius, turns);
            spirals.push(`<path d="${path}" fill="none" stroke="${color}" 
                stroke-width="${strokeWidth}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, spirals.join(''));
    }

    generateSpiralPath(centerX, centerY, maxRadius, turns) {
        const points = [];
        const steps = 120; // Больше точек для плавности
        
        for (let i = 0; i <= steps; i++) {
            const t = (i / steps) * turns * Math.PI * 2;
            const radius = (i / steps) * maxRadius;
            const x = centerX + radius * Math.cos(t);
            const y = centerY + radius * Math.sin(t);
            
            if (i === 0) {
                points.push(`M${x},${y}`);
            } else {
                points.push(`L${x},${y}`);
            }
        }
        
        return points.join(' ');
    }

    createSVG(width, height, content) {
        const randomBackground = this.getRandomBackground();
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
            <rect x="0" y="0" width="100%" height="100%" fill="${randomBackground}"/>
            ${content}
        </svg>`;
    }

    getAllPatterns() {
        try {
            return [
                this.generateDotsPattern(),
                this.generateCirclesPattern(),
                this.generateTrianglesPattern(),
                this.generateHexagonsPattern(),
                this.generateWavesPattern(),
                this.generateStarsPattern(),
                this.generateSpiralPattern()
            ];
        } catch (error) {
            return [this.generateDotsPattern()];
        }
    }
}



// Глобальные функции
function getRandomPattern() {
    if (typeof window !== 'undefined' && window.patternGenerator) {
        return window.patternGenerator.generateRandomPattern();
    }
    return null;
}

function getAllPatterns() {
    if (typeof window !== 'undefined' && window.patternGenerator) {
        return window.patternGenerator.getAllPatterns();
    }
    return [];
}

function setPatternColors(primary, hover, background) {
    if (typeof window !== 'undefined' && window.patternGenerator) {
        window.patternGenerator.setColors(primary, hover, background);
        return true;
    }
    return false;
}

// Экспорт для браузера
if (typeof window !== 'undefined') {
    // Создаем глобальный экземпляр
    try {
        window.patternGenerator = new SVGPatternGenerator();
    } catch (error) {
        window.patternGenerator = null;
    }
    
    // Экспортируем класс и функции
    window.SVGPatternGenerator = SVGPatternGenerator;
    window.getRandomPattern = getRandomPattern;
    window.getAllPatterns = getAllPatterns;
    window.setPatternColors = setPatternColors;
    
} else if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SVGPatternGenerator, getRandomPattern, getAllPatterns, setPatternColors };
}
