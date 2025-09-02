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
        
        // Расширенные структурированные цветовые палитры
        this.colorPalettes = {
            // Зелено-бирюзовая палитра (12 цветов)
            teal: ['#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#00695C', '#004D40', '#A7F3D0', '#6EE7B7', '#34D399', '#10B981', '#059669'],
            // Желто-оранжевая палитра (12 цветов)
            yellow: ['#FFFDE7', '#FFF9C4', '#FFF59D', '#FFF176', '#FFEE58', '#F57F17', '#FF8F00', '#FFC107', '#FFD54F', '#FFECB3', '#FFF8E1', '#F9A825'],
            // Голубая палитра (12 цветов)
            blue: ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#1976D2', '#0D47A1', '#81D4FA', '#4FC3F7', '#29B6F6', '#03A9F4', '#0288D1'],
            // Розовая палитра (12 цветов)
            pink: ['#FCE4EC', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#C2185B', '#880E4F', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#E91E63'],
            // Фиолетовая палитра (12 цветов)
            purple: ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#7B1FA2', '#4A148C', '#D1C4E9', '#B39DDB', '#9575CD', '#7E57C2', '#673AB7'],
            // Серая палитра (12 цветов)
            grey: ['#F5F5F5', '#EEEEEE', '#E0E0E0', '#BDBDBD', '#9E9E9E', '#616161', '#424242', '#FAFAFA', '#F0F0F0', '#E8E8E8', '#D0D0D0', '#A0A0A0'],
            // Мятная палитра (12 цветов)
            mint: ['#E6FFFA', '#B2F5EA', '#81E6D9', '#4FD1C7', '#38B2AC', '#00695C', '#004D40', '#A7F3D0', '#6EE7B7', '#34D399', '#10B981', '#059669'],
            // Коралловая палитра (12 цветов)
            coral: ['#FFEBEE', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#D32F2F', '#B71C1C', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336'],
            // Изумрудная палитра (12 цветов)
            emerald: ['#E8F5E8', '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#388E3C', '#2E7D32', '#1B5E20', '#E0F2E0', '#B8E6B8', '#90EE90'],
            // Лавандовая палитра (12 цветов)
            lavender: ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0', '#7B1FA2', '#6A1B9A', '#4A148C', '#E8DAEF', '#D1C4E9', '#B39DDB'],
            // Персиковая палитра (12 цветов)
            peach: ['#FFF3E0', '#FFE0B2', '#FFCC80', '#FFB74D', '#FFA726', '#FF9800', '#F57C00', '#EF6C00', '#E65100', '#FFE0B2', '#FFCC80', '#FFB74D'],
            // Аквамариновая палитра (12 цветов)
            aqua: ['#E0F7FA', '#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA', '#00BCD4', '#00ACC1', '#0097A7', '#00838F', '#B2EBF2', '#80DEEA', '#4DD0E1']
        };
        
        // Общая палитра для случайного выбора
        this.colorPalette = [
            '#FFFFFF', '#F8F9FA', '#F1F3F4', '#E8EAED', '#DADCE0',
            '#FFF8E1', '#FFF3E0', '#FFECB3', '#FFE0B2', '#FFCCBC',
            '#FCE4EC', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A',
            '#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC',
            '#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5',
            '#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A',
            '#F1F8E9', '#DCEDC8', '#C5E1A5', '#AED581', '#9CCC65',
            '#FFFDE7', '#FFF9C4', '#FFF59D', '#FFF176', '#FFEE58',
            '#FFF3E0', '#FFE0B2', '#FFCC80', '#FFB74D', '#FFA726',
            '#FFEBEE', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350',
            '#F0F4F8', '#E2E8F0', '#CBD5E0', '#A0AEC0', '#718096',
            '#E6FFFA', '#B2F5EA', '#81E6D9', '#4FD1C7', '#38B2AC'
        ];
        
        // Темные и около темные фоновые цвета с большей вариативностью
        this.backgroundPalette = [
            // Очень темные серые
            '#0f0f0f', '#121212', '#141414', '#161616', '#181818',
            '#1a1a1a', '#1c1c1c', '#1e1e1e', '#202020', '#212121',
            // Темные серые
            '#242424', '#262626', '#282828', '#2a2a2a', '#2c2c2c',
            '#2d2d2d', '#2f2f2f', '#313131', '#333333', '#353535',
            // Темно-синие
            '#0d1117', '#161b22', '#21262d', '#30363d', '#484f58',
            // Темно-фиолетовые
            '#1a0d1a', '#2d1b2d', '#3d2a3d', '#4a2c4a', '#5a3a5a',
            // Темно-зеленые
            '#0d1a0d', '#1a2d1a', '#2a3d2a', '#3a4a3a', '#4a5a4a',
            // Темно-коричневые
            '#1a0f0d', '#2d1a16', '#3d2a24', '#4a3a33', '#5a4a43',
            // Темно-красные
            '#1a0d0d', '#2d1616', '#3d2424', '#4a3333', '#5a4343'
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
    
    // Получить случайную палитру
    getRandomPalette() {
        const paletteNames = Object.keys(this.colorPalettes);
        const randomPaletteName = paletteNames[Math.floor(Math.random() * paletteNames.length)];
        return this.colorPalettes[randomPaletteName];
    }
    
    // Получить цвет из конкретной палитры
    getColorFromPalette(paletteName) {
        const palette = this.colorPalettes[paletteName];
        if (palette) {
            return palette[Math.floor(Math.random() * palette.length)];
        }
        return this.getRandomColor();
    }
    
    // Получить несколько цветов из одной палитры
    getColorsFromPalette(paletteName, count = 3) {
        const palette = this.colorPalettes[paletteName];
        if (palette) {
            const colors = [];
            for (let i = 0; i < count; i++) {
                colors.push(palette[Math.floor(Math.random() * palette.length)]);
            }
            return colors;
        }
        return [this.getRandomColor()];
    }

    // Получить случайный фоновый цвет
    getRandomBackground() {
        return this.backgroundPalette[Math.floor(Math.random() * this.backgroundPalette.length)];
    }

    // Улучшенный генератор случайных чисел с использованием crypto API
    random(min, max) {
        if (window.crypto && window.crypto.getRandomValues) {
            const array = new Uint32Array(1);
            window.crypto.getRandomValues(array);
            return (array[0] / (0xffffffff + 1)) * (max - min) + min;
        }
        return Math.random() * (max - min) + min;
    }

    // Получить случайное целое число
    randomInt(min, max) {
        if (window.crypto && window.crypto.getRandomValues) {
            const array = new Uint32Array(1);
            window.crypto.getRandomValues(array);
            return Math.floor((array[0] / (0xffffffff + 1)) * (max - min + 1)) + min;
        }
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
                case 'circles':
                    return this.generateCirclesPattern();
                case 'hexagons':
                    return this.generateHexagonsPattern();
                case 'grid':
                    return this.generateGridPattern();
                case 'octagons':
                    return this.generateOctagonsPattern();
                case 'herringbone':
                    return this.generateHerringbonePattern();
                case 'quilt':
                    return this.generateQuiltPattern();
                case 'honeycomb':
                    return this.generateHoneycombPattern();
                default:
                    return this.generateCirclesPattern();
            }
        } catch (error) {
            return this.generateCirclesPattern();
        }
    }

    generateRandomPattern() {
        const patterns = ['circles', 'hexagons', 'grid', 'octagons', 'herringbone', 'quilt', 'honeycomb'];
        const randomType = patterns[this.randomInt(0, patterns.length - 1)];
        console.log(`🎲 Случайный паттерн: ${randomType}`);
        return this.generatePattern(randomType);
    }

    // Крутой геометрический паттерн с точками - идеальная сетка
    generateDotsPattern() {
        const size = this.getRandomSize();
        const dots = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную геометрическую сетку
        const gridSize = this.randomInt(10, 16);
        const cellWidth = size.width / gridSize;
        const cellHeight = size.height / gridSize;
        
        // Создаем паттерн шахматной доски или диагональных линий
        const patternType = this.randomInt(0, 2);
        
        for (let row = 0; row < gridSize; row++) {
            for (let col = 0; col < gridSize; col++) {
                let shouldDraw = false;
                
                if (patternType === 0) {
                    // Шахматная доска
                    shouldDraw = (row + col) % 2 === 0;
                } else if (patternType === 1) {
                    // Диагональные линии
                    shouldDraw = (row + col) % 3 === 0;
                }
                
                if (shouldDraw) {
                    const x = col * cellWidth + cellWidth / 2;
                    const y = row * cellHeight + cellHeight / 2;
                    
                    // Размеры точек в зависимости от позиции в сетке
                    const baseRadius = Math.min(cellWidth, cellHeight) * 0.3;
                    const radius = baseRadius + this.random(-baseRadius * 0.3, baseRadius * 0.3);
                    const opacity = this.random(0.4, 0.9);
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    dots.push(`<circle cx="${x}" cy="${y}" r="${radius}" fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, dots.join(''));
    }

    // Крутой геометрический паттерн с кругами - идеальные перекрывающиеся круги
    generateCirclesPattern() {
        const size = this.getRandomSize();
        const circles = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную сетку кругов
        const gridSize = this.randomInt(4, 8);
        const cellWidth = size.width / gridSize;
        const cellHeight = size.height / gridSize;
        
        // Создаем несколько слоев для глубины
        const layers = this.randomInt(2, 3);
        
        for (let layer = 0; layer < layers; layer++) {
            const layerRadius = this.randomInt(20, 50);
            const layerOpacity = this.random(0.3, 0.7);
            
            for (let row = 0; row < gridSize; row++) {
                for (let col = 0; col < gridSize; col++) {
                    const x = col * cellWidth + cellWidth / 2;
                    const y = row * cellHeight + cellHeight / 2;
                    
                    // Добавляем небольшое смещение для каждого слоя
                    const offsetX = this.random(-cellWidth * 0.2, cellWidth * 0.2);
                    const offsetY = this.random(-cellHeight * 0.2, cellHeight * 0.2);
                    
                    const finalX = x + offsetX;
                    const finalY = y + offsetY;
                    
                    const radius = layerRadius + this.random(-layerRadius * 0.2, layerRadius * 0.2);
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    circles.push(`<circle cx="${finalX}" cy="${finalY}" r="${radius}" fill="${color}" opacity="${layerOpacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, circles.join(''));
    }

    // Крутой геометрический паттерн с треугольниками - идеальная мозаика
    generateTrianglesPattern() {
        const size = this.getRandomSize();
        const triangles = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из треугольников
        const triangleSize = this.randomInt(25, 40);
        const cols = Math.ceil(size.width / triangleSize);
        const rows = Math.ceil(size.height / triangleSize);
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * triangleSize;
                const y = row * triangleSize;
                
                // Создаем два треугольника в каждой ячейке (ромб)
                const color1 = palette[Math.floor(Math.random() * palette.length)];
                const color2 = palette[Math.floor(Math.random() * palette.length)];
                const opacity = this.random(0.4, 0.8);
                
                // Верхний треугольник
                const topTriangle = `${x},${y} ${x + triangleSize/2},${y + triangleSize/2} ${x + triangleSize},${y}`;
                triangles.push(`<polygon points="${topTriangle}" fill="${color1}" opacity="${opacity}"/>`);
                
                // Нижний треугольник
                const bottomTriangle = `${x},${y + triangleSize} ${x + triangleSize/2},${y + triangleSize/2} ${x + triangleSize},${y + triangleSize}`;
                triangles.push(`<polygon points="${bottomTriangle}" fill="${color2}" opacity="${opacity}"/>`);
            }
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
    // Крутой геометрический паттерн с шестиугольниками - идеальная мозаика
    generateHexagonsPattern() {
        const size = this.getRandomSize();
        const hexagons = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из шестиугольников
        const hexSize = this.randomInt(20, 35);
        const hexWidth = hexSize * Math.sqrt(3);
        const hexHeight = hexSize * 2;
        
        const cols = Math.ceil(size.width / (hexWidth * 0.75)) + 1;
        const rows = Math.ceil(size.height / (hexHeight * 0.5)) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * hexWidth * 0.75;
                const y = row * hexHeight * 0.5;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * hexWidth * 0.375;
                const finalX = x + offsetX;
                
                if (finalX < size.width + hexSize && y < size.height + hexSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    const points = this.generateHexagonPoints(finalX, y, hexSize);
                    
                    hexagons.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
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

    // Улучшенный паттерн с волнами - больше вариативности
    generateWavesPattern() {
        const size = this.getRandomSize();
        const waves = [];
        const numWaves = this.randomInt(8, 35); // Больше вариативности в количестве
        
        for (let i = 0; i < numWaves; i++) {
            const y = this.random(0, size.height); // Случайное расположение по Y
            const amplitude = this.random(5, 80); // Больше вариаций амплитуды
            const frequency = this.random(0.003, 0.05); // Больше вариаций частоты
            const phase = this.random(0, Math.PI * 2);
            
            // Случайные стили волн
            const waveStyle = this.randomInt(0, 3);
            const opacity = this.random(0.05, 0.8); // Больше вариативности прозрачности
            const color = this.getRandomColor();
            const strokeWidth = this.random(0.5, 6); // Больше вариаций толщины
            
            let wave;
            if (waveStyle === 0) {
                // Обычная волна
                const path = this.generateComplexWave(size.width, y, amplitude, frequency, phase);
                wave = `<path d="${path}" fill="none" stroke="${color}" 
                    style="opacity:${opacity};stroke-width:${strokeWidth}px;"/>`;
            } else if (waveStyle === 1) {
                // Волна с заливкой
                const path = this.generateComplexWave(size.width, y, amplitude, frequency, phase);
                const fillPath = path + ` L${size.width},${size.height} L0,${size.height} Z`;
                wave = `<path d="${fillPath}" fill="${color}" opacity="${opacity * 0.3}"/>`;
            } else {
                // Двойная волна
                const path1 = this.generateComplexWave(size.width, y, amplitude, frequency, phase);
                const path2 = this.generateComplexWave(size.width, y + 10, amplitude * 0.7, frequency * 1.5, phase + Math.PI);
                wave = `<path d="${path1}" fill="none" stroke="${color}" 
                    style="opacity:${opacity};stroke-width:${strokeWidth}px;"/>
                    <path d="${path2}" fill="none" stroke="${this.getRandomColor()}" 
                    style="opacity:${opacity * 0.6};stroke-width:${strokeWidth * 0.7}px;"/>`;
            }
            
            waves.push(wave);
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

    // Крутой геометрический паттерн с сеткой - идеальная сетка
    generateGridPattern() {
        const size = this.getRandomSize();
        const grid = [];
        const palette = this.getRandomPalette();
        const cellSize = this.randomInt(25, 45);
        const opacity = this.random(0.3, 0.6);
        const strokeWidth = this.random(1.5, 3);
        
        // Вертикальные линии
        for (let x = 0; x <= size.width; x += cellSize) {
            const color = palette[Math.floor(Math.random() * palette.length)];
            grid.push(`<line x1="${x}" y1="0" x2="${x}" y2="${size.height}" 
                stroke="${color}" stroke-width="${strokeWidth}" opacity="${opacity}"/>`);
        }
        
        // Горизонтальные линии
        for (let y = 0; y <= size.height; y += cellSize) {
            const color = palette[Math.floor(Math.random() * palette.length)];
            grid.push(`<line x1="0" y1="${y}" x2="${size.width}" y2="${y}" 
                stroke="${color}" stroke-width="${strokeWidth}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, grid.join(''));
    }



    // Новый паттерн с цветами (увеличенные)
    generateFlowersPattern() {
        const size = this.getRandomSize();
        const flowers = [];
        const numFlowers = this.randomInt(8, 20); // Меньше цветов, но больше размер
        
        for (let i = 0; i < numFlowers; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const flowerSize = this.random(20, 45); // Увеличенный размер цветов
            const petals = this.randomInt(6, 10);
            const opacity = this.random(0.3, 0.8);
            const color = this.getRandomColor();
            
            // Центр цветка (увеличенный)
            flowers.push(`<circle cx="${x}" cy="${y}" r="${flowerSize * 0.4}" 
                fill="${this.getRandomColor()}" opacity="${opacity}"/>`);
            
            // Лепестки (увеличенные)
            for (let j = 0; j < petals; j++) {
                const angle = (j * Math.PI * 2) / petals;
                const petalX = x + flowerSize * Math.cos(angle);
                const petalY = y + flowerSize * Math.sin(angle);
                const petalSize = this.random(flowerSize * 0.3, flowerSize * 0.5); // Увеличенные лепестки
                
                flowers.push(`<ellipse cx="${petalX}" cy="${petalY}" 
                    rx="${petalSize}" ry="${petalSize * 0.7}" 
                    fill="${color}" opacity="${opacity}" 
                    transform="rotate(${angle * 180 / Math.PI} ${petalX} ${petalY})"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, flowers.join(''));
    }

    // Крутой геометрический паттерн - идеальная мозаика из фигур
    generateGeometricPattern() {
        const size = this.getRandomSize();
        const shapes = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из квадратов и ромбов
        const cellSize = this.randomInt(30, 50);
        const cols = Math.ceil(size.width / cellSize);
        const rows = Math.ceil(size.height / cellSize);
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * cellSize;
                const y = row * cellSize;
                const opacity = this.random(0.4, 0.8);
                
                // Чередуем квадраты и ромбы
                if ((row + col) % 2 === 0) {
                    // Квадрат
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const squareSize = cellSize * 0.85;
                    const offset = (cellSize - squareSize) / 2;
                    shapes.push(`<rect x="${x + offset}" y="${y + offset}" 
                        width="${squareSize}" height="${squareSize}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else {
                    // Ромб
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const centerX = x + cellSize / 2;
                    const centerY = y + cellSize / 2;
                    const diamondSize = cellSize * 0.7;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    shapes.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, shapes.join(''));
    }

    // Крутой геометрический паттерн с ромбами - идеальная мозаика
    generateDiamondsPattern() {
        const size = this.getRandomSize();
        const diamonds = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из ромбов
        const diamondSize = this.randomInt(25, 45);
        const cols = Math.ceil(size.width / diamondSize) + 1;
        const rows = Math.ceil(size.height / diamondSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * diamondSize;
                const y = row * diamondSize;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * diamondSize / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + diamondSize && y < size.height + diamondSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    const centerX = finalX + diamondSize / 2;
                    const centerY = y + diamondSize / 2;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    
                    diamonds.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, diamonds.join(''));
    }

    // Крутой геометрический паттерн с восьмиугольниками - идеальная мозаика
    generateOctagonsPattern() {
        const size = this.getRandomSize();
        const octagons = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из восьмиугольников
        const octagonSize = this.randomInt(20, 35);
        const cols = Math.ceil(size.width / (octagonSize * 1.5)) + 1;
        const rows = Math.ceil(size.height / (octagonSize * 1.5)) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * octagonSize * 1.5;
                const y = row * octagonSize * 1.5;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * octagonSize * 0.75;
                const finalX = x + offsetX;
                
                if (finalX < size.width + octagonSize && y < size.height + octagonSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    const points = this.generateOctagonPoints(finalX + octagonSize/2, y + octagonSize/2, octagonSize);
                    
                    octagons.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, octagons.join(''));
    }

    // Крутой геометрический паттерн с шевронами - идеальная мозаика
    generateChevronsPattern() {
        const size = this.getRandomSize();
        const chevrons = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из шевронов
        const chevronWidth = this.randomInt(30, 50);
        const chevronHeight = this.randomInt(20, 35);
        const cols = Math.ceil(size.width / chevronWidth) + 1;
        const rows = Math.ceil(size.height / chevronHeight) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * chevronWidth;
                const y = row * chevronHeight;
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                const opacity = this.random(0.4, 0.8);
                
                // Создаем шеврон (V-образная форма)
                const points = `${x},${y} ${x + chevronWidth/2},${y + chevronHeight} ${x + chevronWidth},${y}`;
                
                chevrons.push(`<polygon points="${points}" 
                    fill="${color}" opacity="${opacity}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, chevrons.join(''));
    }

    // Крутой геометрический паттерн елочкой - идеальная мозаика
    generateHerringbonePattern() {
        const size = this.getRandomSize();
        const herringbone = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику елочкой
        const brickWidth = this.randomInt(25, 40);
        const brickHeight = this.randomInt(15, 25);
        const cols = Math.ceil(size.width / brickWidth) + 1;
        const rows = Math.ceil(size.height / brickHeight) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * brickWidth;
                const y = row * brickHeight;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * brickWidth / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + brickWidth && y < size.height + brickHeight) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    
                    // Создаем кирпич елочкой
                    herringbone.push(`<rect x="${finalX}" y="${y}" 
                        width="${brickWidth}" height="${brickHeight}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, herringbone.join(''));
    }

    // Крутой геометрический паттерн лоскутного одеяла - идеальная мозаика
    generateQuiltPattern() {
        const size = this.getRandomSize();
        const quilt = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику лоскутного одеяла
        const patchSize = this.randomInt(20, 35);
        const cols = Math.ceil(size.width / patchSize);
        const rows = Math.ceil(size.height / patchSize);
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * patchSize;
                const y = row * patchSize;
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                const opacity = this.random(0.4, 0.8);
                
                // Создаем лоскут (квадрат с закругленными углами)
                const cornerRadius = patchSize * 0.1;
                quilt.push(`<rect x="${x}" y="${y}" 
                    width="${patchSize}" height="${patchSize}" 
                    rx="${cornerRadius}" ry="${cornerRadius}"
                    fill="${color}" opacity="${opacity}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, quilt.join(''));
    }

    // Классный паттерн концентрические круги - идеальная симметрия
    generateConcentricPattern() {
        const size = this.getRandomSize();
        const concentric = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
        // Создаем концентрические круги
        const numRings = this.randomInt(6, 12);
        const ringSpacing = maxRadius / numRings;
        
        for (let ring = 0; ring < numRings; ring++) {
            const radius = ringSpacing * (ring + 1);
            const opacity = this.random(0.2, 0.6);
            const color = palette[Math.floor(Math.random() * palette.length)];
            
            // Создаем концентрический круг
            concentric.push(`<circle cx="${centerX}" cy="${centerY}" r="${radius}" 
                fill="none" stroke="${color}" stroke-width="${this.randomInt(2, 5)}" opacity="${opacity}"/>`);
            
            // Добавляем внутренние элементы для некоторых колец
            if (ring % 2 === 0 && ring > 0) {
                const innerRadius = radius * 0.7;
                const innerColor = palette[Math.floor(Math.random() * palette.length)];
                concentric.push(`<circle cx="${centerX}" cy="${centerY}" r="${innerRadius}" 
                    fill="${innerColor}" opacity="${opacity * 0.5}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, concentric.join(''));
    }

    // Классный паттерн соты - идеальная мозаика
    generateHoneycombPattern() {
        const size = this.getRandomSize();
        const honeycomb = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную мозаику из сот
        const hexSize = this.randomInt(18, 28);
        const hexWidth = hexSize * Math.sqrt(3);
        const hexHeight = hexSize * 2;
        
        const cols = Math.ceil(size.width / (hexWidth * 0.75)) + 2;
        const rows = Math.ceil(size.height / (hexHeight * 0.5)) + 2;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * hexWidth * 0.75;
                const y = row * hexHeight * 0.5;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * hexWidth * 0.375;
                const finalX = x + offsetX;
                
                if (finalX < size.width + hexSize && y < size.height + hexSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.3, 0.7);
                    const points = this.generateHexagonPoints(finalX + hexSize/2, y + hexSize/2, hexSize);
                    
                    // Создаем соту с внутренним элементом
                    honeycomb.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                    
                    // Добавляем внутренний элемент
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    const innerRadius = hexSize * 0.3;
                    honeycomb.push(`<circle cx="${finalX + hexSize/2}" cy="${y + hexSize/2}" r="${innerRadius}" 
                        fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, honeycomb.join(''));
    }

    // Классный паттерн кирпичная кладка - идеальная структура
    generateBrickPattern() {
        const size = this.getRandomSize();
        const brick = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную кирпичную кладку
        const brickWidth = this.randomInt(30, 50);
        const brickHeight = this.randomInt(15, 25);
        const cols = Math.ceil(size.width / brickWidth) + 1;
        const rows = Math.ceil(size.height / brickHeight) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * brickWidth;
                const y = row * brickHeight;
                
                // Смещение для четных рядов (кирпичная кладка)
                const offsetX = (row % 2) * brickWidth / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + brickWidth && y < size.height + brickHeight) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    
                    // Создаем кирпич с закругленными углами
                    const cornerRadius = Math.min(brickWidth, brickHeight) * 0.1;
                    brick.push(`<rect x="${finalX}" y="${y}" 
                        width="${brickWidth}" height="${brickHeight}" 
                        rx="${cornerRadius}" ry="${cornerRadius}"
                        fill="${color}" opacity="${opacity}"/>`);
                    
                    // Добавляем внутренний элемент
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    const innerWidth = brickWidth * 0.6;
                    const innerHeight = brickHeight * 0.6;
                    const innerX = finalX + (brickWidth - innerWidth) / 2;
                    const innerY = y + (brickHeight - innerHeight) / 2;
                    brick.push(`<rect x="${innerX}" y="${innerY}" 
                        width="${innerWidth}" height="${innerHeight}" 
                        rx="${cornerRadius * 0.5}" ry="${cornerRadius * 0.5}"
                        fill="${innerColor}" opacity="${opacity * 0.6}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, brick.join(''));
    }

    // Классный паттерн ромбовидная сетка - идеальная геометрия
    generateDiamondGridPattern() {
        const size = this.getRandomSize();
        const diamondGrid = [];
        const palette = this.getRandomPalette();
        
        // Создаем идеальную ромбовидную сетку
        const diamondSize = this.randomInt(25, 40);
        const cols = Math.ceil(size.width / diamondSize) + 1;
        const rows = Math.ceil(size.height / diamondSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * diamondSize;
                const y = row * diamondSize;
                
                // Смещение для четных рядов
                const offsetX = (row % 2) * diamondSize / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + diamondSize && y < size.height + diamondSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.3, 0.7);
                    
                    // Создаем ромб
                    const centerX = finalX + diamondSize / 2;
                    const centerY = y + diamondSize / 2;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    
                    diamondGrid.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                    
                    // Добавляем внутренний элемент
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    const innerSize = diamondSize * 0.4;
                    const innerPoints = `${centerX},${centerY - innerSize/2} ${centerX + innerSize/2},${centerY} ${centerX},${centerY + innerSize/2} ${centerX - innerSize/2},${centerY}`;
                    diamondGrid.push(`<polygon points="${innerPoints}" 
                        fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, diamondGrid.join(''));
    }

    // Крутой геометрический паттерн мандала - идеальная симметрия
    generateMandalaPattern() {
        const size = this.getRandomSize();
        const mandala = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
        // Создаем концентрические круги с геометрическими элементами
        const numRings = this.randomInt(4, 8);
        const ringSpacing = maxRadius / numRings;
        
        for (let ring = 0; ring < numRings; ring++) {
            const ringRadius = ringSpacing * (ring + 1);
            const numElements = this.randomInt(6, 16);
            const elementSize = ringSpacing * 0.3;
            const opacity = this.random(0.3, 0.7);
            
            for (let i = 0; i < numElements; i++) {
                const angle = (i * 2 * Math.PI) / numElements;
                const x = centerX + ringRadius * Math.cos(angle);
                const y = centerY + ringRadius * Math.sin(angle);
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                
                // Создаем геометрические элементы (круги, квадраты, ромбы)
                const elementType = this.randomInt(0, 3);
                
                if (elementType === 0) {
                    // Круг
                    mandala.push(`<circle cx="${x}" cy="${y}" r="${elementSize}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else if (elementType === 1) {
                    // Квадрат
                    mandala.push(`<rect x="${x - elementSize}" y="${y - elementSize}" 
                        width="${elementSize * 2}" height="${elementSize * 2}" 
                        fill="${color}" opacity="${opacity}" 
                        transform="rotate(${angle * 180 / Math.PI} ${x} ${y})"/>`);
                } else {
                    // Ромб
                    const points = `${x},${y - elementSize} ${x + elementSize},${y} ${x},${y + elementSize} ${x - elementSize},${y}`;
                    mandala.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, mandala.join(''));
    }

    // Крутой геометрический паттерн тесселяция - идеальная мозаика
    generateTessellationPattern() {
        const size = this.getRandomSize();
        const tessellation = [];
        const palette = this.getRandomPalette();
        
        // Создаем сложную тесселяцию из различных геометрических форм
        const cellSize = this.randomInt(20, 35);
        const cols = Math.ceil(size.width / cellSize) + 1;
        const rows = Math.ceil(size.height / cellSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * cellSize;
                const y = row * cellSize;
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                const opacity = this.random(0.4, 0.8);
                
                // Создаем сложные геометрические формы
                const shapeType = this.randomInt(0, 4);
                
                if (shapeType === 0) {
                    // Сложный многоугольник
                    const numSides = this.randomInt(5, 8);
                    const points = [];
                    for (let i = 0; i < numSides; i++) {
                        const angle = (i * 2 * Math.PI) / numSides;
                        const px = x + cellSize/2 + (cellSize/2 * 0.8) * Math.cos(angle);
                        const py = y + cellSize/2 + (cellSize/2 * 0.8) * Math.sin(angle);
                        points.push(`${px},${py}`);
                    }
                    tessellation.push(`<polygon points="${points.join(' ')}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else if (shapeType === 1) {
                    // Звезда
                    const numPoints = this.randomInt(5, 8);
                    const outerRadius = cellSize * 0.4;
                    const innerRadius = outerRadius * 0.5;
                    const points = [];
                    for (let i = 0; i < numPoints * 2; i++) {
                        const angle = (i * Math.PI) / numPoints;
                        const radius = i % 2 === 0 ? outerRadius : innerRadius;
                        const px = x + cellSize/2 + radius * Math.cos(angle);
                        const py = y + cellSize/2 + radius * Math.sin(angle);
                        points.push(`${px},${py}`);
                    }
                    tessellation.push(`<polygon points="${points.join(' ')}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else if (shapeType === 2) {
                    // Сложный ромб с внутренними элементами
                    const centerX = x + cellSize/2;
                    const centerY = y + cellSize/2;
                    const diamondSize = cellSize * 0.6;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    tessellation.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                    
                    // Добавляем внутренний элемент
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    tessellation.push(`<circle cx="${centerX}" cy="${centerY}" r="${diamondSize/4}" 
                        fill="${innerColor}" opacity="${opacity * 0.7}"/>`);
                } else {
                    // Сложный шестиугольник
                    const centerX = x + cellSize/2;
                    const centerY = y + cellSize/2;
                    const hexSize = cellSize * 0.4;
                    const points = this.generateHexagonPoints(centerX, centerY, hexSize);
                    tessellation.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, tessellation.join(''));
    }

    // Сложный фрактальный паттерн - рекурсивная геометрия
    generateFractalPattern() {
        const size = this.getRandomSize();
        const fractal = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
        // Создаем фрактальную структуру
        const numLevels = this.randomInt(4, 6);
        const baseRadius = maxRadius / numLevels;
        
        for (let level = 0; level < numLevels; level++) {
            const levelRadius = baseRadius * (level + 1);
            const numBranches = this.randomInt(6, 12);
            const branchLength = levelRadius * 0.8;
            const opacity = this.random(0.2, 0.6);
            
            for (let branch = 0; branch < numBranches; branch++) {
                const angle = (branch * 2 * Math.PI) / numBranches;
                const startX = centerX + levelRadius * Math.cos(angle);
                const startY = centerY + levelRadius * Math.sin(angle);
                const endX = centerX + (levelRadius + branchLength) * Math.cos(angle);
                const endY = centerY + (levelRadius + branchLength) * Math.sin(angle);
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                
                // Создаем сложные фрактальные элементы
                const elementType = this.randomInt(0, 4);
                
                if (elementType === 0) {
                    // Спиральная ветвь
                    const spiralPoints = this.generateSpiralPoints(startX, startY, endX, endY, 3);
                    fractal.push(`<path d="${spiralPoints}" stroke="${color}" stroke-width="${2 + level}" fill="none" opacity="${opacity}"/>`);
                } else if (elementType === 1) {
                    // Фрактальный круг с внутренними элементами
                    const circleRadius = branchLength * 0.3;
                    fractal.push(`<circle cx="${endX}" cy="${endY}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                    
                    // Внутренние элементы
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    for (let i = 0; i < 4; i++) {
                        const innerAngle = (i * Math.PI) / 2;
                        const innerX = endX + circleRadius * 0.5 * Math.cos(innerAngle);
                        const innerY = endY + circleRadius * 0.5 * Math.sin(innerAngle);
                        fractal.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.3}" fill="${innerColor}" opacity="${opacity * 0.7}"/>`);
                    }
                } else if (elementType === 2) {
                    // Фрактальный многоугольник
                    const numSides = this.randomInt(5, 8);
                    const polygonRadius = branchLength * 0.4;
                    const points = [];
                    for (let i = 0; i < numSides; i++) {
                        const polyAngle = angle + (i * 2 * Math.PI) / numSides;
                        const px = endX + polygonRadius * Math.cos(polyAngle);
                        const py = endY + polygonRadius * Math.sin(polyAngle);
                        points.push(`${px},${py}`);
                    }
                    fractal.push(`<polygon points="${points.join(' ')}" fill="${color}" opacity="${opacity}"/>`);
                } else {
                    // Фрактальная звезда
                    const starRadius = branchLength * 0.3;
                    const numPoints = this.randomInt(5, 8);
                    const starPoints = this.generateStarPoints(endX, endY, starRadius, numPoints);
                    fractal.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, fractal.join(''));
    }

    // Сложный оптический паттерн - иллюзии и глубины
    generateOpticalPattern() {
        const size = this.getRandomSize();
        const optical = [];
        const palette = this.getRandomPalette();
        
        // Создаем оптические иллюзии
        const numLayers = this.randomInt(3, 5);
        const layerSpacing = size.height / numLayers;
        
        for (let layer = 0; layer < numLayers; layer++) {
            const y = layer * layerSpacing;
            const layerHeight = layerSpacing;
            const opacity = this.random(0.3, 0.7);
            
            // Создаем разные типы оптических эффектов
            const effectType = this.randomInt(0, 3);
            
            if (effectType === 0) {
                // Волновой эффект
                const numWaves = this.randomInt(8, 15);
                const waveAmplitude = layerHeight * 0.3;
                const waveLength = size.width / numWaves;
                
                for (let i = 0; i < numWaves; i++) {
                    const x = i * waveLength;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    // Создаем сложную волну
                    const wavePoints = [];
                    for (let j = 0; j < 20; j++) {
                        const waveX = x + (j * waveLength) / 20;
                        const waveY = y + layerHeight/2 + waveAmplitude * Math.sin((j * Math.PI) / 10);
                        wavePoints.push(`${waveX},${waveY}`);
                    }
                    
                    optical.push(`<polyline points="${wavePoints.join(' ')}" stroke="${color}" stroke-width="${3 + layer}" fill="none" opacity="${opacity}"/>`);
                }
            } else if (effectType === 1) {
                // Спиральный эффект
                const centerX = size.width / 2;
                const centerY = y + layerHeight / 2;
                const maxRadius = Math.min(size.width, layerHeight) / 2;
                const numSpirals = this.randomInt(2, 4);
                
                for (let spiral = 0; spiral < numSpirals; spiral++) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const spiralRadius = maxRadius * (0.3 + spiral * 0.2);
                    const spiralPoints = this.generateSpiralPoints(centerX, centerY, centerX + spiralRadius, centerY, 5);
                    optical.push(`<path d="${spiralPoints}" stroke="${color}" stroke-width="${2 + layer}" fill="none" opacity="${opacity}"/>`);
                }
            } else {
                // Геометрический эффект
                const numShapes = this.randomInt(6, 12);
                const shapeSize = Math.min(size.width, layerHeight) / numShapes;
                
                for (let i = 0; i < numShapes; i++) {
                    const x = i * shapeSize;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    // Создаем сложные геометрические формы
                    const shapeType = this.randomInt(0, 3);
                    
                    if (shapeType === 0) {
                        // Сложный многоугольник
                        const numSides = this.randomInt(6, 10);
                        const points = [];
                        for (let j = 0; j < numSides; j++) {
                            const angle = (j * 2 * Math.PI) / numSides;
                            const px = x + shapeSize/2 + (shapeSize/2 * 0.8) * Math.cos(angle);
                            const py = y + layerHeight/2 + (shapeSize/2 * 0.8) * Math.sin(angle);
                            points.push(`${px},${py}`);
                        }
                        optical.push(`<polygon points="${points.join(' ')}" fill="${color}" opacity="${opacity}"/>`);
                    } else if (shapeType === 1) {
                        // Сложная звезда
                        const numPoints = this.randomInt(6, 10);
                        const starRadius = shapeSize * 0.4;
                        const starPoints = this.generateStarPoints(x + shapeSize/2, y + layerHeight/2, starRadius, numPoints);
                        optical.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                    } else {
                        // Сложный круг с внутренними элементами
                        const circleRadius = shapeSize * 0.4;
                        optical.push(`<circle cx="${x + shapeSize/2}" cy="${y + layerHeight/2}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                        
                        // Внутренние элементы
                        const innerColor = palette[Math.floor(Math.random() * palette.length)];
                        for (let k = 0; k < 6; k++) {
                            const innerAngle = (k * Math.PI) / 3;
                            const innerX = x + shapeSize/2 + circleRadius * 0.6 * Math.cos(innerAngle);
                            const innerY = y + layerHeight/2 + circleRadius * 0.6 * Math.sin(innerAngle);
                            optical.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.2}" fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                        }
                    }
                }
            }
        }
        
        return this.createSVG(size.width, size.height, optical.join(''));
    }

    // Сложная мозаика - многослойная геометрия
    generateMosaicPattern() {
        const size = this.getRandomSize();
        const mosaic = [];
        const palette = this.getRandomPalette();
        
        // Создаем многослойную мозаику
        const numLayers = this.randomInt(3, 5);
        const cellSize = this.randomInt(15, 25);
        const cols = Math.ceil(size.width / cellSize) + 1;
        const rows = Math.ceil(size.height / cellSize) + 1;
        
        for (let layer = 0; layer < numLayers; layer++) {
            const layerOpacity = this.random(0.2, 0.5);
            const layerOffset = layer * 2;
            
            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    const x = col * cellSize + layerOffset;
                    const y = row * cellSize + layerOffset;
                    
                    if (x < size.width && y < size.height) {
                        const color = palette[Math.floor(Math.random() * palette.length)];
                        
                        // Создаем сложные мозаичные элементы
                        const elementType = this.randomInt(0, 4);
                        
                        if (elementType === 0) {
                            // Сложный многоугольник
                            const numSides = this.randomInt(5, 8);
                            const points = [];
                            for (let i = 0; i < numSides; i++) {
                                const angle = (i * 2 * Math.PI) / numSides;
                                const px = x + cellSize/2 + (cellSize/2 * 0.8) * Math.cos(angle);
                                const py = y + cellSize/2 + (cellSize/2 * 0.8) * Math.sin(angle);
                                points.push(`${px},${py}`);
                            }
                            mosaic.push(`<polygon points="${points.join(' ')}" fill="${color}" opacity="${layerOpacity}"/>`);
                        } else if (elementType === 1) {
                            // Сложная звезда
                            const numPoints = this.randomInt(5, 8);
                            const starRadius = cellSize * 0.4;
                            const starPoints = this.generateStarPoints(x + cellSize/2, y + cellSize/2, starRadius, numPoints);
                            mosaic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${layerOpacity}"/>`);
                        } else if (elementType === 2) {
                            // Сложный круг с внутренними элементами
                            const circleRadius = cellSize * 0.4;
                            mosaic.push(`<circle cx="${x + cellSize/2}" cy="${y + cellSize/2}" r="${circleRadius}" fill="${color}" opacity="${layerOpacity}"/>`);
                            
                            // Внутренние элементы
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            for (let k = 0; k < 4; k++) {
                                const innerAngle = (k * Math.PI) / 2;
                                const innerX = x + cellSize/2 + circleRadius * 0.6 * Math.cos(innerAngle);
                                const innerY = y + cellSize/2 + circleRadius * 0.6 * Math.sin(innerAngle);
                                mosaic.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.2}" fill="${innerColor}" opacity="${layerOpacity * 0.8}"/>`);
                            }
                        } else {
                            // Сложный ромб с внутренними элементами
                            const centerX = x + cellSize/2;
                            const centerY = y + cellSize/2;
                            const diamondSize = cellSize * 0.6;
                            const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                            mosaic.push(`<polygon points="${points}" fill="${color}" opacity="${layerOpacity}"/>`);
                            
                            // Внутренний элемент
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            mosaic.push(`<circle cx="${centerX}" cy="${centerY}" r="${diamondSize/4}" fill="${innerColor}" opacity="${layerOpacity * 0.7}"/>`);
                        }
                    }
                }
            }
        }
        
        return this.createSVG(size.width, size.height, mosaic.join(''));
    }

    // Сложный кельтский паттерн - переплетающиеся узоры
    generateCelticPattern() {
        const size = this.getRandomSize();
        const celtic = [];
        const palette = this.getRandomPalette();
        
        // Создаем кельтские узоры
        const numKnots = this.randomInt(3, 6);
        const knotSize = Math.min(size.width, size.height) / numKnots;
        
        for (let knot = 0; knot < numKnots; knot++) {
            const centerX = (knot + 1) * (size.width / (numKnots + 1));
            const centerY = size.height / 2;
            const opacity = this.random(0.3, 0.7);
            
            // Создаем сложные кельтские узоры
            const knotType = this.randomInt(0, 3);
            
            if (knotType === 0) {
                // Сложный узел
                const numArms = this.randomInt(4, 8);
                for (let arm = 0; arm < numArms; arm++) {
                    const angle = (arm * 2 * Math.PI) / numArms;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    // Создаем спиральную ветвь
                    const endX = centerX + knotSize * 0.8 * Math.cos(angle);
                    const endY = centerY + knotSize * 0.8 * Math.sin(angle);
                    const spiralPoints = this.generateSpiralPoints(centerX, centerY, endX, endY, 3);
                    celtic.push(`<path d="${spiralPoints}" stroke="${color}" stroke-width="${3}" fill="none" opacity="${opacity}"/>`);
                }
            } else if (knotType === 1) {
                // Сложная мандала
                const numRings = this.randomInt(3, 5);
                const ringSpacing = knotSize / (numRings * 2);
                
                for (let ring = 0; ring < numRings; ring++) {
                    const ringRadius = ringSpacing * (ring + 1);
                    const numElements = this.randomInt(6, 12);
                    const elementSize = ringSpacing * 0.3;
                    
                    for (let i = 0; i < numElements; i++) {
                        const angle = (i * 2 * Math.PI) / numElements;
                        const x = centerX + ringRadius * Math.cos(angle);
                        const y = centerY + ringRadius * Math.sin(angle);
                        
                        const color = palette[Math.floor(Math.random() * palette.length)];
                        
                        // Создаем сложные элементы
                        const elementType = this.randomInt(0, 2);
                        
                        if (elementType === 0) {
                            // Сложный круг
                            celtic.push(`<circle cx="${x}" cy="${y}" r="${elementSize}" fill="${color}" opacity="${opacity}"/>`);
                            
                            // Внутренние элементы
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            for (let k = 0; k < 4; k++) {
                                const innerAngle = angle + (k * Math.PI) / 2;
                                const innerX = x + elementSize * 0.6 * Math.cos(innerAngle);
                                const innerY = y + elementSize * 0.6 * Math.sin(innerAngle);
                                celtic.push(`<circle cx="${innerX}" cy="${innerY}" r="${elementSize * 0.3}" fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                            }
                        } else {
                            // Сложная звезда
                            const numPoints = this.randomInt(5, 8);
                            const starPoints = this.generateStarPoints(x, y, elementSize, numPoints);
                            celtic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                        }
                    }
                }
            } else {
                // Сложная тесселяция
                const cellSize = knotSize * 0.3;
                const cols = Math.ceil(knotSize / cellSize);
                const rows = Math.ceil(knotSize / cellSize);
                
                for (let row = 0; row < rows; row++) {
                    for (let col = 0; col < cols; col++) {
                        const x = centerX - knotSize/2 + col * cellSize;
                        const y = centerY - knotSize/2 + row * cellSize;
                        
                        if (x >= centerX - knotSize/2 && x <= centerX + knotSize/2 && 
                            y >= centerY - knotSize/2 && y <= centerY + knotSize/2) {
                            
                            const color = palette[Math.floor(Math.random() * palette.length)];
                            
                            // Создаем сложные геометрические формы
                            const shapeType = this.randomInt(0, 3);
                            
                            if (shapeType === 0) {
                                // Сложный многоугольник
                                const numSides = this.randomInt(5, 8);
                                const points = [];
                                for (let i = 0; i < numSides; i++) {
                                    const angle = (i * 2 * Math.PI) / numSides;
                                    const px = x + cellSize/2 + (cellSize/2 * 0.8) * Math.cos(angle);
                                    const py = y + cellSize/2 + (cellSize/2 * 0.8) * Math.sin(angle);
                                    points.push(`${px},${py}`);
                                }
                                celtic.push(`<polygon points="${points.join(' ')}" fill="${color}" opacity="${opacity}"/>`);
                            } else if (shapeType === 1) {
                                // Сложная звезда
                                const numPoints = this.randomInt(5, 8);
                                const starRadius = cellSize * 0.4;
                                const starPoints = this.generateStarPoints(x + cellSize/2, y + cellSize/2, starRadius, numPoints);
                                celtic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                            } else {
                                // Сложный круг с внутренними элементами
                                const circleRadius = cellSize * 0.4;
                                celtic.push(`<circle cx="${x + cellSize/2}" cy="${y + cellSize/2}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                                
                                // Внутренние элементы
                                const innerColor = palette[Math.floor(Math.random() * palette.length)];
                                for (let k = 0; k < 6; k++) {
                                    const innerAngle = (k * Math.PI) / 3;
                                    const innerX = x + cellSize/2 + circleRadius * 0.6 * Math.cos(innerAngle);
                                    const innerY = y + cellSize/2 + circleRadius * 0.6 * Math.sin(innerAngle);
                                    celtic.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.2}" fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return this.createSVG(size.width, size.height, celtic.join(''));
    }

    // Вспомогательные функции для сложных паттернов
    generateSpiralPoints(startX, startY, endX, endY, turns) {
        const points = [];
        const numPoints = 50;
        const dx = endX - startX;
        const dy = endY - startY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        for (let i = 0; i <= numPoints; i++) {
            const t = i / numPoints;
            const angle = t * turns * 2 * Math.PI;
            const radius = t * distance * 0.3;
            const x = startX + t * dx + radius * Math.cos(angle);
            const y = startY + t * dy + radius * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        
        return `M ${points.join(' L ')}`;
    }

    generateStarPoints(centerX, centerY, radius, numPoints) {
        const points = [];
        const outerRadius = radius;
        const innerRadius = radius * 0.5;
        
        for (let i = 0; i < numPoints * 2; i++) {
            const angle = (i * Math.PI) / numPoints;
            const r = i % 2 === 0 ? outerRadius : innerRadius;
            const x = centerX + r * Math.cos(angle);
            const y = centerY + r * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        
        return points.join(' ');
    }

    generateOctagonPoints(centerX, centerY, size) {
        const points = [];
        for (let i = 0; i < 8; i++) {
            const angle = (i * Math.PI) / 4;
            const x = centerX + size * Math.cos(angle);
            const y = centerY + size * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        return points.join(' ');
    }

    generatePentagonPoints(centerX, centerY, size) {
        const points = [];
        for (let i = 0; i < 5; i++) {
            const angle = (i * Math.PI * 2) / 5 - Math.PI / 2;
            const x = centerX + size * Math.cos(angle);
            const y = centerY + size * Math.sin(angle);
            points.push(`${x},${y}`);
        }
        return points.join(' ');
    }

    generateStarPoints(centerX, centerY, size) {
        const points = [];
        const outerRadius = size;
        const innerRadius = size * 0.4;
        const numPoints = 5;
        
        for (let i = 0; i < numPoints * 2; i++) {
            const angle = (i * Math.PI) / numPoints - Math.PI / 2;
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            points.push(`${x},${y}`);
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
                this.generateCirclesPattern(),
                this.generateHexagonsPattern(),
                this.generateGridPattern(),
                this.generateOctagonsPattern(),
                this.generateHerringbonePattern(),
                this.generateQuiltPattern(),
                this.generateHoneycombPattern()
            ];
        } catch (error) {
            return [this.generateCirclesPattern()];
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

function generateNewPatternForCard(cardId) {
    if (typeof window !== 'undefined' && window.patternGenerator) {
        const newPattern = window.patternGenerator.generateRandomPattern();
        const card = document.getElementById(cardId);
        if (card) {
            const patternContainer = card.querySelector('.pattern-container');
            if (patternContainer) {
                patternContainer.innerHTML = newPattern;
                console.log(`🎨 Новый паттерн сгенерирован для карточки ${cardId}`);
                return true;
            }
        }
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
    window.generateNewPatternForCard = generateNewPatternForCard;
    
} else if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SVGPatternGenerator, getRandomPattern, getAllPatterns, setPatternColors };
}
