


class SVGPatternGenerator {
    constructor() {
        this.primaryColor = '#B595FF';
        this.primaryHover = '#9A7FE6';
        this.backgroundColor = '#1a1a1a';
        
        this.colorPalettes = {
            teal: ['#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#00695C', '#004D40', '#A7F3D0', '#6EE7B7', '#34D399', '#10B981', '#059669', '#047857', '#065F46', '#064E3B', '#B2F5EA', '#7DD3FC', '#38BDF8', '#0EA5E9', '#0284C7'],
            yellow: ['#FFFDE7', '#FFF9C4', '#FFF59D', '#FFF176', '#FFEE58', '#F57F17', '#FF8F00', '#FFC107', '#FFD54F', '#FFECB3', '#FFF8E1', '#F9A825', '#F59E0B', '#D97706', '#B45309', '#92400E', '#78350F', '#451A03', '#FEF3C7', '#FDE68A'],
            blue: ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#1976D2', '#0D47A1', '#81D4FA', '#4FC3F7', '#29B6F6', '#03A9F4', '#0288D1', '#0277BD', '#01579B', '#0F172A', '#1E293B', '#334155', '#475569', '#DBEAFE', '#BFDBFE'],
            pink: ['#FCE4EC', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#C2185B', '#880E4F', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#E91E63', '#DB2777', '#BE185D', '#9D174D', '#831843', '#500724', '#FDF2F8', '#FCE7F3', '#FBCFE8'],
            purple: ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#7B1FA2', '#4A148C', '#D1C4E9', '#B39DDB', '#9575CD', '#7E57C2', '#673AB7', '#5B21B6', '#4C1D95', '#581C87', '#3B0764', '#1E1B4B', '#312E81', '#F3E8FF', '#E9D5FF'],
            grey: ['#F5F5F5', '#EEEEEE', '#E0E0E0', '#BDBDBD', '#9E9E9E', '#616161', '#424242', '#FAFAFA', '#F0F0F0', '#E8E8E8', '#D0D0D0', '#A0A0A0', '#808080', '#606060', '#404040', '#202020', '#0F0F0F', '#F8FAFC', '#F1F5F9', '#E2E8F0'],
            mint: ['#E6FFFA', '#B2F5EA', '#81E6D9', '#4FD1C7', '#38B2AC', '#00695C', '#004D40', '#A7F3D0', '#6EE7B7', '#34D399', '#10B981', '#059669', '#047857', '#065F46', '#064E3B', '#B2F5EA', '#7DD3FC', '#38BDF8', '#0EA5E9', '#0284C7'],
            coral: ['#FFEBEE', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#D32F2F', '#B71C1C', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336', '#E11D48', '#BE123C', '#9F1239', '#881337', '#4C0519', '#FEF2F2', '#FEE2E2', '#FECACA'],
            emerald: ['#E8F5E8', '#C8E6C9', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#388E3C', '#2E7D32', '#1B5E20', '#E0F2E0', '#B8E6B8', '#90EE90', '#16A34A', '#15803D', '#166534', '#14532D', '#052E16', '#F0FDF4', '#DCFCE7', '#BBF7D0'],
            lavender: ['#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0', '#7B1FA2', '#6A1B9A', '#4A148C', '#E8DAEF', '#D1C4E9', '#B39DDB', '#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#4C1D95', '#F5F3FF', '#EDE9FE', '#DDD6FE'],
            peach: ['#FFF3E0', '#FFE0B2', '#FFCC80', '#FFB74D', '#FFA726', '#FF9800', '#F57C00', '#EF6C00', '#E65100', '#FFE0B2', '#FFCC80', '#FFB74D', '#F59E0B', '#D97706', '#B45309', '#92400E', '#78350F', '#FEF3C7', '#FDE68A', '#FCD34D'],
            aqua: ['#E0F7FA', '#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA', '#00BCD4', '#00ACC1', '#0097A7', '#00838F', '#B2EBF2', '#80DEEA', '#4DD0E1', '#06B6D4', '#0891B2', '#0E7490', '#155E75', '#164E63', '#F0FDFA', '#CCFBF1', '#99F6E4'],
            gold: ['#FFFBEB', '#FEF3C7', '#FDE68A', '#FCD34D', '#FBBF24', '#F59E0B', '#D97706', '#B45309', '#92400E', '#78350F', '#451A03', '#FFD700', '#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500', '#FFD700', '#FFA500', '#FF8C00'],
            silver: ['#F8FAFC', '#F1F5F9', '#E2E8F0', '#CBD5E1', '#94A3B8', '#64748B', '#475569', '#334155', '#1E293B', '#0F172A', '#C0C0C0', '#A8A8A8', '#909090', '#787878', '#606060', '#484848', '#303030', '#E5E7EB', '#D1D5DB', '#9CA3AF'],
            bronze: ['#FEF7ED', '#FED7AA', '#FDBA74', '#FB923C', '#F97316', '#EA580C', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D', '#CD7F32', '#B8860B', '#DAA520', '#B8860B', '#CD853F', '#D2691E', '#A0522D', '#8B4513', '#654321', '#3E2723'],
            neon: ['#00FF00', '#00FFFF', '#FF00FF', '#FFFF00', '#FF0080', '#8000FF', '#00FF80', '#FF8000', '#0080FF', '#80FF00', '#FF0080', '#8000FF', '#00FF80', '#FF8000', '#0080FF', '#80FF00', '#FF0080', '#8000FF', '#00FF80', '#FF8000'],
            pastel: ['#FFE4E1', '#FFD1DC', '#FFB6C1', '#FFA0B4', '#FF91A4', '#FFB6C1', '#FFC0CB', '#FFCCCB', '#FFD1DC', '#FFE4E1', '#E6E6FA', '#D8BFD8', '#DDA0DD', '#DA70D6', '#EE82EE', '#F0E68C', '#F5DEB3', '#FFE4B5', '#FFEFD5', '#FFF8DC'],
            dark: ['#1A1A1A', '#2D2D2D', '#404040', '#525252', '#666666', '#7A7A7A', '#8E8E8E', '#A2A2A2', '#B6B6B6', '#CACACA', '#0D1117', '#161B22', '#21262D', '#30363D', '#484F58', '#6E7681', '#8B949E', '#A8B2BF', '#C9D1D9', '#F0F6FC'],
            bright: ['#FF0000', '#FF4000', '#FF8000', '#FFBF00', '#FFFF00', '#BFFF00', '#80FF00', '#40FF00', '#00FF00', '#00FF40', '#00FF80', '#00FFBF', '#00FFFF', '#00BFFF', '#0080FF', '#0040FF', '#0000FF', '#4000FF', '#8000FF', '#BF00FF'],
            nature: ['#228B22', '#32CD32', '#00FF00', '#7CFC00', '#ADFF2F', '#9ACD32', '#6B8E23', '#556B2F', '#8FBC8F', '#90EE90', '#98FB98', '#8FBC8F', '#2E8B57', '#3CB371', '#20B2AA', '#48D1CC', '#40E0D0', '#00CED1', '#00BFFF', '#87CEEB']
        };
        
        this.colorPalette = [
            '#FFFFFF', '#F8F9FA', '#F1F3F4', '#E8EAED', '#DADCE0', '#F5F5F5', '#EEEEEE', '#E0E0E0', '#FAFAFA', '#F0F0F0',
            '#FFF8E1', '#FFF3E0', '#FFECB3', '#FFE0B2', '#FFCCBC', '#FFFDE7', '#FFF9C4', '#FFF59D', '#FFF176', '#FFEE58',
            '#FFC107', '#FFD54F', '#FFECB3', '#FFF8E1', '#F9A825', '#F59E0B', '#D97706', '#B45309', '#92400E', '#78350F',
            '#FCE4EC', '#F8BBD9', '#F48FB1', '#F06292', '#EC407A', '#FFEBEE', '#FFCDD2', '#EF9A9A', '#E57373', '#EF5350',
            '#F44336', '#E91E63', '#C2185B', '#880E4F', '#DB2777', '#BE185D', '#9F1239', '#881337', '#4C0519', '#FF0000',
            '#F3E5F5', '#E1BEE7', '#CE93D8', '#BA68C8', '#AB47BC', '#9C27B0', '#7B1FA2', '#6A1B9A', '#4A148C', '#673AB7',
            '#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#4C1D95', '#581C87', '#3B0764', '#1E1B4B', '#312E81', '#8000FF',
            '#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#1976D2', '#0D47A1', '#81D4FA', '#4FC3F7', '#29B6F6',
            '#03A9F4', '#0288D1', '#0277BD', '#01579B', '#0F172A', '#1E293B', '#334155', '#475569', '#0000FF', '#0080FF',
            '#E0F2F1', '#B2DFDB', '#80CBC4', '#4DB6AC', '#26A69A', '#00695C', '#004D40', '#E8F5E8', '#C8E6C9', '#A5D6A7',
            '#81C784', '#66BB6A', '#4CAF50', '#388E3C', '#2E7D32', '#1B5E20', '#16A34A', '#15803D', '#166534', '#00FF00',
            '#E6FFFA', '#B2F5EA', '#81E6D9', '#4FD1C7', '#38B2AC', '#E0F7FA', '#B2EBF2', '#80DEEA', '#4DD0E1', '#26C6DA',
            '#00BCD4', '#00ACC1', '#0097A7', '#00838F', '#06B6D4', '#0891B2', '#0E7490', '#155E75', '#164E63', '#00FFFF',
            '#F0F4F8', '#E2E8F0', '#CBD5E0', '#A0AEC0', '#718096', '#BDBDBD', '#9E9E9E', '#616161', '#424242', '#212121',
            '#F8FAFC', '#F1F5F9', '#E2E8F0', '#CBD5E1', '#94A3B8', '#64748B', '#475569', '#334155', '#1E293B', '#0F172A',
            '#FFFBEB', '#FEF3C7', '#FDE68A', '#FCD34D', '#FBBF24', '#FFD700', '#FFA500', '#FF8C00', '#FF7F50', '#FF6347',
            '#FEF7ED', '#FED7AA', '#FDBA74', '#FB923C', '#F97316', '#CD7F32', '#B8860B', '#DAA520', '#CD853F', '#D2691E',
            '#F8FAFC', '#F1F5F9', '#E2E8F0', '#CBD5E1', '#94A3B8', '#C0C0C0', '#A8A8A8', '#909090', '#787878', '#606060',
            '#E5E7EB', '#D1D5DB', '#9CA3AF', '#6B7280', '#4B5563', '#374151', '#1F2937', '#111827', '#0F172A', '#000000',
            '#00FF00', '#00FFFF', '#FF00FF', '#FFFF00', '#FF0080', '#8000FF', '#00FF80', '#FF8000', '#0080FF', '#80FF00',
            '#FF4000', '#FF8000', '#FFBF00', '#BFFF00', '#80FF00', '#40FF00', '#00FF40', '#00FF80', '#00FFBF', '#00BFFF',
            '#FFE4E1', '#FFD1DC', '#FFB6C1', '#FFA0B4', '#FF91A4', '#FFC0CB', '#FFCCCB', '#E6E6FA', '#D8BFD8', '#DDA0DD',
            '#DA70D6', '#EE82EE', '#F0E68C', '#F5DEB3', '#FFE4B5', '#FFEFD5', '#FFF8DC', '#F0FFF0', '#F5FFFA', '#F0F8FF'
        ];
        
        this.backgroundPalette = [
            '#0f0f0f', '#121212', '#141414', '#161616', '#181818', '#1a1a1a', '#1c1c1c', '#1e1e1e', '#202020', '#212121',
            '#242424', '#262626', '#282828', '#2a2a2a', '#2c2c2c', '#2d2d2d', '#2f2f2f', '#313131', '#333333', '#353535',
            '#373737', '#393939', '#3b3b3b', '#3d3d3d', '#3f3f3f', '#404040', '#424242', '#444444', '#464646', '#484848',
            '#0d1117', '#161b22', '#21262d', '#30363d', '#484f58', '#0f172a', '#1e293b', '#334155', '#475569', '#64748b',
            '#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6', '#0c4a6e', '#075985', '#0369a1', '#0284c7', '#0ea5e9',
            '#1a0d1a', '#2d1b2d', '#3d2a3d', '#4a2c4a', '#5a3a5a', '#581c87', '#6b21a8', '#7c2d12', '#7c3aed', '#8b5cf6',
            '#4c1d95', '#5b21b6', '#6d28d9', '#7c3aed', '#8b5cf6', '#1e1b4b', '#312e81', '#3730a3', '#4338ca', '#4f46e5',
            '#0d1a0d', '#1a2d1a', '#2a3d2a', '#3a4a3a', '#4a5a4a', '#14532d', '#166534', '#15803d', '#16a34a', '#22c55e',
            '#052e16', '#064e3b', '#065f46', '#047857', '#059669', '#0f172a', '#1e293b', '#334155', '#475569', '#64748b',
            '#1a0f0d', '#2d1a16', '#3d2a24', '#4a3a33', '#5a4a43', '#451a03', '#78350f', '#92400e', '#b45309', '#d97706',
            '#7c2d12', '#991b1b', '#b91c1c', '#dc2626', '#ef4444', '#3e2723', '#4e342e', '#5d4037', '#6d4c41', '#8d6e63',
            '#1a0d0d', '#2d1616', '#3d2424', '#4a3333', '#5a4343', '#7f1d1d', '#991b1b', '#b91c1b', '#dc2626', '#ef4444',
            '#881337', '#9f1239', '#be123c', '#e11d48', '#f43f5e', '#4c0519', '#7c2d12', '#991b1b', '#b91c1b', '#dc2626',
            '#451a03', '#78350f', '#92400e', '#b45309', '#d97706', '#ea580c', '#f97316', '#fb923c', '#fdba74', '#fed7aa',
            '#7c2d12', '#9a3412', '#c2410c', '#ea580c', '#f97316', '#1c1917', '#292524', '#44403c', '#57534e', '#78716c',
            '#0f172a', '#1e293b', '#334155', '#475569', '#64748b', '#0c4a6e', '#075985', '#0369a1', '#0284c7', '#0ea5e9',
            '#164e63', '#155e75', '#0e7490', '#0891b2', '#06b6d4', '#134e4a', '#115e59', '#0f766e', '#0d9488', '#14b8a6',
            '#500724', '#831843', '#9d174d', '#be185d', '#db2777', '#ec4899', '#f472b6', '#f9a8d4', '#fbcfe8', '#fce7f3',
            '#4c0519', '#7c2d12', '#991b1b', '#b91c1b', '#dc2626', '#881337', '#9f1239', '#be123c', '#e11d48', '#f43f5e'
        ];
        
    }

    setColors(primary, hover, background) {
        if (primary) this.primaryColor = primary;
        if (hover) this.primaryHover = hover;
        if (background) this.backgroundColor = background;
    }

    getRandomColor() {
        return this.colorPalette[Math.floor(Math.random() * this.colorPalette.length)];
    }
    
    getRandomPalette() {
        const paletteNames = Object.keys(this.colorPalettes);
        const randomPaletteName = paletteNames[Math.floor(Math.random() * paletteNames.length)];
        const selectedPalette = this.colorPalettes[randomPaletteName];
        
        const numColors = this.randomInt(4, 12);
        const paletteColors = [];
        for (let i = 0; i < numColors; i++) {
            const randomColor = selectedPalette[Math.floor(Math.random() * selectedPalette.length)];
            const randomOpacity = this.random(0.3, 0.8);
            paletteColors.push({ color: randomColor, opacity: randomOpacity });
        }
        
        return paletteColors;
    }
    
    getColorFromPalette(paletteName) {
        const palette = this.colorPalettes[paletteName];
        if (palette) {
            return palette[Math.floor(Math.random() * palette.length)];
        }
        return this.getRandomColor();
    }
    
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

    getRandomBackground() {
        return this.backgroundPalette[Math.floor(Math.random() * this.backgroundPalette.length)];
    }

    random(min, max) {
        if (window.crypto && window.crypto.getRandomValues) {
            const array = new Uint32Array(1);
            window.crypto.getRandomValues(array);
            return (array[0] / (0xffffffff + 1)) * (max - min) + min;
        }
        return Math.random() * (max - min) + min;
    }

    randomInt(min, max) {
        if (window.crypto && window.crypto.getRandomValues) {
            const array = new Uint32Array(1);
            window.crypto.getRandomValues(array);
            return Math.floor((array[0] / (0xffffffff + 1)) * (max - min + 1)) + min;
        }
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    getRandomSize() {
        return {
            width: 306,
            height: 147
        };
    }

    generatePattern(patternType) {
        try {
            return this.generateCirclesPattern();
        } catch (error) {
            return this.generateCirclesPattern();
        }
    }

    generateRandomPattern() {
        return this.generateCirclesPattern();
    }



    generateCirclesPattern() {
        const size = this.getRandomSize();
        const circles = [];
        
        const paletteNames = Object.keys(this.colorPalettes);
        const randomPaletteName = paletteNames[Math.floor(Math.random() * paletteNames.length)];
        const selectedPalette = this.colorPalettes[randomPaletteName];
        
        const numColors = this.randomInt(6, 10);
        const paletteColors = [];
        for (let i = 0; i < numColors; i++) {
            const randomColor = selectedPalette[Math.floor(Math.random() * selectedPalette.length)];
            const randomOpacity = this.random(0.2, 0.7);
            paletteColors.push({ color: randomColor, opacity: randomOpacity });
        }
        
        const numCircles = this.randomInt(25, 40);
        
        for (let i = 0; i < numCircles; i++) {
            const x = this.random(-20, size.width + 20);
            const y = this.random(-20, size.height + 20);
            const radius = this.random(20, 80);
            const colorObj = paletteColors[Math.floor(Math.random() * paletteColors.length)];
            const color = colorObj.color;
            const opacity = colorObj.opacity;
            
            const hasGradient = this.randomInt(0, 4) === 0;
            if (hasGradient) {
                const gradientId = `gradient_${i}`;
                const gradientColorObj = paletteColors[Math.floor(Math.random() * paletteColors.length)];
                const gradientColor = gradientColorObj.color;
                
                circles.push(`<defs>
                    <radialGradient id="${gradientId}" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:${color};stop-opacity:${opacity}"/>
                        <stop offset="100%" style="stop-color:${gradientColor};stop-opacity:${opacity * 0.3}"/>
                    </radialGradient>
                </defs>`);
                circles.push(`<circle cx="${x}" cy="${y}" r="${radius}" fill="url(#${gradientId})"/>`);
            } else {
                circles.push(`<circle cx="${x}" cy="${y}" r="${radius}" 
                    fill="${color}" opacity="${opacity}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, circles.join(''));
    }













    generateSpiralPattern() {

        const size = this.getRandomSize();
        const spirals = [];
        const numSpirals = this.randomInt(8, 18);
        const maxRadius = Math.min(size.width, size.height) * 0.4;
        const turns = this.randomInt(2, 5);
        const strokeWidth = this.randomInt(1, 3);
        
        for (let i = 0; i < numSpirals; i++) {
            const centerX = this.random(0, size.width);
            const centerY = this.random(0, size.height);
            const opacity = this.random(0.1, 0.6);
            const color = this.getRandomColor();
            
            const path = this.generateSpiralPath(centerX, centerY, maxRadius, turns);
            spirals.push(`<path d="${path}" fill="none" stroke="${color}" 
                stroke-width="${strokeWidth}" opacity="${opacity}"/>`);
        }
        
        return this.createSVG(size.width, size.height, spirals.join(''));
    }

    generateSpiralPath(centerX, centerY, maxRadius, turns) {
        const points = [];
        const steps = 50;
        
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





    generateFlowersPattern() {
        const size = this.getRandomSize();
        const flowers = [];
        const numFlowers = this.randomInt(8, 15);
        const flowerSize = this.randomInt(15, 25);
        const petalSize = this.randomInt(8, 12);
        
        for (let i = 0; i < numFlowers; i++) {
            const x = this.random(0, size.width);
            const y = this.random(0, size.height);
            const petals = this.randomInt(6, 10);
            const opacity = this.random(0.3, 0.8);
            const color = this.getRandomColor();
            
            flowers.push(`<circle cx="${x}" cy="${y}" r="${flowerSize * 0.4}" 
                fill="${this.getRandomColor()}" opacity="${opacity}"/>`);
            
            for (let j = 0; j < petals; j++) {
                const angle = (j * Math.PI * 2) / petals;
                const petalX = x + flowerSize * Math.cos(angle);
                const petalY = y + flowerSize * Math.sin(angle);
                
                flowers.push(`<ellipse cx="${petalX}" cy="${petalY}" 
                    rx="${petalSize}" ry="${petalSize * 0.7}" 
                    fill="${color}" opacity="${opacity}" 
                    transform="rotate(${angle * 180 / Math.PI} ${petalX} ${petalY})"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, flowers.join(''));
    }

    generateGeometricPattern() {
        const size = this.getRandomSize();
        const shapes = [];
        const palette = this.getRandomPalette();
        
        const cellSize = this.randomInt(30, 50);
        const cols = Math.ceil(size.width / cellSize);
        const rows = Math.ceil(size.height / cellSize);
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * cellSize;
                const y = row * cellSize;
                const opacity = this.random(0.4, 0.8);
                
                if ((row + col) % 2 === 0) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const squareSize = cellSize * 0.85;
                    const offset = (cellSize - squareSize) / 2;
                    shapes.push(`<rect x="${x + offset}" y="${y + offset}" 
                        width="${squareSize}" height="${squareSize}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else {
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

    generateDiamondsPattern() {
        const size = this.getRandomSize();
        const diamonds = [];
        const palette = this.getRandomPalette();
        
        const diamondSize = this.randomInt(25, 45);
        const cols = Math.ceil(size.width / diamondSize) + 1;
        const rows = Math.ceil(size.height / diamondSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * diamondSize;
                const y = row * diamondSize;
                
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



    generateChevronsPattern() {
        const size = this.getRandomSize();
        const chevrons = [];
        const palette = this.getRandomPalette();
        
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
                
                const points = `${x},${y} ${x + chevronWidth/2},${y + chevronHeight} ${x + chevronWidth},${y}`;
                
                chevrons.push(`<polygon points="${points}" 
                    fill="${color}" opacity="${opacity}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, chevrons.join(''));
    }



    generateQuiltPattern() {
        const size = this.getRandomSize();
        const quilt = [];
        
        const paletteNames = Object.keys(this.colorPalettes);
        const randomPaletteName = paletteNames[Math.floor(Math.random() * paletteNames.length)];
        const selectedPalette = this.colorPalettes[randomPaletteName];
        
        const numColors = this.randomInt(4, 12);
        const paletteColors = [];
        for (let i = 0; i < numColors; i++) {
            const randomColor = selectedPalette[Math.floor(Math.random() * selectedPalette.length)];
            const randomOpacity = this.random(0.3, 0.8);
            paletteColors.push({ color: randomColor, opacity: randomOpacity });
        }
        
        const basePatchSize = this.randomInt(15, 30);
        const cols = Math.ceil(size.width / basePatchSize) + 2;
        const rows = Math.ceil(size.height / basePatchSize) + 2;
        
        const layers = this.randomInt(2, 4);
        
        for (let layer = 0; layer < layers; layer++) {
            const layerOpacity = this.random(0.3, 0.7);
            const layerOffset = layer * 3;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                    const x = col * basePatchSize + layerOffset;
                    const y = row * basePatchSize + layerOffset;
                    
                    if (x < size.width && y < size.height) {
                        const patchSize = basePatchSize + this.randomInt(-5, 10);
                        const colorObj = paletteColors[Math.floor(Math.random() * paletteColors.length)];
                        const color = colorObj.color;
                        const colorOpacity = colorObj.opacity;
                        const secondaryColorObj = paletteColors[Math.floor(Math.random() * paletteColors.length)];
                        const secondaryColor = secondaryColorObj.color;
                        const secondaryOpacity = secondaryColorObj.opacity;
                        
                        const patchType = this.randomInt(0, 6);
                        
                        if (patchType === 0) {
                            const cornerRadius = patchSize * this.random(0.05, 0.2);
                            quilt.push(`<rect x="${x}" y="${y}" 
                                width="${patchSize}" height="${patchSize}" 
                                rx="${cornerRadius}" ry="${cornerRadius}"
                                fill="${color}" opacity="${colorOpacity}"/>`);
                        } else if (patchType === 1) {
                            const gradientId = `quilt_grad_${layer}_${row}_${col}`;
                            quilt.push(`<defs>
                                <linearGradient id="${gradientId}" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:${color};stop-opacity:${colorOpacity}"/>
                                    <stop offset="100%" style="stop-color:${secondaryColor};stop-opacity:${secondaryOpacity}"/>
                                </linearGradient>
                            </defs>`);
                            quilt.push(`<rect x="${x}" y="${y}" 
                                width="${patchSize}" height="${patchSize}" 
                                rx="${patchSize * 0.1}" ry="${patchSize * 0.1}"
                                fill="url(#${gradientId})"/>`);
                        } else if (patchType === 2) {
                const cornerRadius = patchSize * 0.1;
                                            quilt.push(`<rect x="${x}" y="${y}" 
                                width="${patchSize}" height="${patchSize}" 
                                rx="${cornerRadius}" ry="${cornerRadius}"
                                fill="${color}" opacity="${colorOpacity}"/>`);
                            
                            const innerSize = patchSize * 0.6;
                            const innerX = x + (patchSize - innerSize) / 2;
                            const innerY = y + (patchSize - innerSize) / 2;
                            quilt.push(`<rect x="${innerX}" y="${innerY}" 
                                width="${innerSize}" height="${innerSize}" 
                                rx="${cornerRadius * 0.5}" ry="${cornerRadius * 0.5}"
                                fill="${secondaryColor}" opacity="${secondaryOpacity}"/>`);
                        } else if (patchType === 3) {
                            const centerX = x + patchSize / 2;
                            const centerY = y + patchSize / 2;
                            const diamondSize = patchSize * 0.8;
                            const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                            quilt.push(`<polygon points="${points}" 
                                fill="${color}" opacity="${colorOpacity}"/>`);
                        } else if (patchType === 4) {
                            const cornerRadius = patchSize * 0.1;
                            quilt.push(`<rect x="${x}" y="${y}" 
                                width="${patchSize}" height="${patchSize}" 
                                rx="${cornerRadius}" ry="${cornerRadius}"
                                fill="${color}" opacity="${colorOpacity}"/>`);
                            
                            const centerX = x + patchSize / 2;
                            const centerY = y + patchSize / 2;
                            const circleRadius = patchSize * 0.3;
                            quilt.push(`<circle cx="${centerX}" cy="${centerY}" r="${circleRadius}" 
                                fill="${secondaryColor}" opacity="${secondaryOpacity}"/>`);
                        } else {
                            const cornerRadius = patchSize * 0.1;
                            quilt.push(`<rect x="${x}" y="${y}" 
                                width="${patchSize}" height="${patchSize}" 
                                rx="${cornerRadius}" ry="${cornerRadius}"
                                fill="${color}" opacity="${colorOpacity}"/>`);
                            
                            const centerX = x + patchSize / 2;
                            const centerY = y + patchSize / 2;
                            const starRadius = patchSize * 0.25;
                            const starPoints = this.generateStarPoints(centerX, centerY, starRadius, 5);
                            quilt.push(`<polygon points="${starPoints}" 
                                fill="${secondaryColor}" opacity="${secondaryOpacity}"/>`);
                        }
                        
                        if (this.randomInt(0, 4) === 0) {
                            const decorType = this.randomInt(0, 3);
                            const decorColorObj = paletteColors[Math.floor(Math.random() * paletteColors.length)];
                            const decorColor = decorColorObj.color;
                            const decorOpacity = decorColorObj.opacity;
                            
                            if (decorType === 0) {
                                for (let i = 0; i < 3; i++) {
                                    const dotX = x + this.random(5, patchSize - 5);
                                    const dotY = y + this.random(5, patchSize - 5);
                                    const dotRadius = this.random(1, 3);
                                    quilt.push(`<circle cx="${dotX}" cy="${dotY}" r="${dotRadius}" 
                                        fill="${decorColor}" opacity="${decorOpacity}"/>`);
                                }
                            } else if (decorType === 1) {
                                const lineX1 = x + this.random(0, patchSize);
                                const lineY1 = y + this.random(0, patchSize);
                                const lineX2 = x + this.random(0, patchSize);
                                const lineY2 = y + this.random(0, patchSize);
                                quilt.push(`<line x1="${lineX1}" y1="${lineY1}" x2="${lineX2}" y2="${lineY2}" 
                                    stroke="${decorColor}" stroke-width="${this.random(1, 3)}" opacity="${decorOpacity}"/>`);
                            } else {
                                const triX = x + patchSize / 2;
                                const triY = y + patchSize / 2;
                                const triSize = this.random(3, 8);
                                const triPoints = `${triX},${triY - triSize} ${triX + triSize},${triY + triSize} ${triX - triSize},${triY + triSize}`;
                                quilt.push(`<polygon points="${triPoints}" 
                                    fill="${decorColor}" opacity="${decorOpacity}"/>`);
                            }
                        }
                    }
                }
            }
        }
        
        return this.createSVG(size.width, size.height, quilt.join(''));
    }

    generateConcentricPattern() {
        const size = this.getRandomSize();
        const concentric = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
        const numRings = this.randomInt(6, 12);
        const ringSpacing = maxRadius / numRings;
        
        for (let ring = 0; ring < numRings; ring++) {
            const radius = ringSpacing * (ring + 1);
            const opacity = this.random(0.2, 0.6);
            const color = palette[Math.floor(Math.random() * palette.length)];
            
            concentric.push(`<circle cx="${centerX}" cy="${centerY}" r="${radius}" 
                fill="none" stroke="${color}" stroke-width="${this.randomInt(2, 5)}" opacity="${opacity}"/>`);
            
            if (ring % 2 === 0 && ring > 0) {
                const innerRadius = radius * 0.7;
                const innerColor = palette[Math.floor(Math.random() * palette.length)];
                concentric.push(`<circle cx="${centerX}" cy="${centerY}" r="${innerRadius}" 
                    fill="${innerColor}" opacity="${opacity * 0.5}"/>`);
            }
        }
        
        return this.createSVG(size.width, size.height, concentric.join(''));
    }



    generateBrickPattern() {
        const size = this.getRandomSize();
        const brick = [];
        const palette = this.getRandomPalette();
        
        const brickWidth = this.randomInt(30, 50);
        const brickHeight = this.randomInt(15, 25);
        const cols = Math.ceil(size.width / brickWidth) + 1;
        const rows = Math.ceil(size.height / brickHeight) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * brickWidth;
                const y = row * brickHeight;
                
                const offsetX = (row % 2) * brickWidth / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + brickWidth && y < size.height + brickHeight) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.4, 0.8);
                    
                    const cornerRadius = Math.min(brickWidth, brickHeight) * 0.1;
                    brick.push(`<rect x="${finalX}" y="${y}" 
                        width="${brickWidth}" height="${brickHeight}" 
                        rx="${cornerRadius}" ry="${cornerRadius}"
                        fill="${color}" opacity="${opacity}"/>`);
                    
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

    generateDiamondGridPattern() {
        const size = this.getRandomSize();
        const diamondGrid = [];
        const palette = this.getRandomPalette();
        
        const diamondSize = this.randomInt(25, 40);
        const cols = Math.ceil(size.width / diamondSize) + 1;
        const rows = Math.ceil(size.height / diamondSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * diamondSize;
                const y = row * diamondSize;
                
                const offsetX = (row % 2) * diamondSize / 2;
                const finalX = x + offsetX;
                
                if (finalX < size.width + diamondSize && y < size.height + diamondSize) {
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    const opacity = this.random(0.3, 0.7);
                    
                    const centerX = finalX + diamondSize / 2;
                    const centerY = y + diamondSize / 2;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    
                    diamondGrid.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                    
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

    generateMandalaPattern() {
        const size = this.getRandomSize();
        const mandala = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
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
                
                const elementType = this.randomInt(0, 3);
                
                if (elementType === 0) {
                    mandala.push(`<circle cx="${x}" cy="${y}" r="${elementSize}" 
                        fill="${color}" opacity="${opacity}"/>`);
                } else if (elementType === 1) {
                    mandala.push(`<rect x="${x - elementSize}" y="${y - elementSize}" 
                        width="${elementSize * 2}" height="${elementSize * 2}" 
                        fill="${color}" opacity="${opacity}" 
                        transform="rotate(${angle * 180 / Math.PI} ${x} ${y})"/>`);
                } else {
                    const points = `${x},${y - elementSize} ${x + elementSize},${y} ${x},${y + elementSize} ${x - elementSize},${y}`;
                    mandala.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, mandala.join(''));
    }

    generateTessellationPattern() {
        const size = this.getRandomSize();
        const tessellation = [];
        const palette = this.getRandomPalette();
        
        const cellSize = this.randomInt(20, 35);
        const cols = Math.ceil(size.width / cellSize) + 1;
        const rows = Math.ceil(size.height / cellSize) + 1;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * cellSize;
                const y = row * cellSize;
                
                const color = palette[Math.floor(Math.random() * palette.length)];
                const opacity = this.random(0.4, 0.8);
                
                const shapeType = this.randomInt(0, 4);
                
                if (shapeType === 0) {
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
                    const centerX = x + cellSize/2;
                    const centerY = y + cellSize/2;
                    const diamondSize = cellSize * 0.6;
                    const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                    tessellation.push(`<polygon points="${points}" 
                        fill="${color}" opacity="${opacity}"/>`);
                    
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    tessellation.push(`<circle cx="${centerX}" cy="${centerY}" r="${diamondSize/4}" 
                        fill="${innerColor}" opacity="${opacity * 0.7}"/>`);
                } else {
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

    generateFractalPattern() {
        const size = this.getRandomSize();
        const fractal = [];
        const palette = this.getRandomPalette();
        
        const centerX = size.width / 2;
        const centerY = size.height / 2;
        const maxRadius = Math.min(size.width, size.height) / 2;
        
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
                
                const elementType = this.randomInt(0, 4);
                
                if (elementType === 0) {
                    const spiralPoints = this.generateSpiralPoints(startX, startY, endX, endY, 3);
                    fractal.push(`<path d="${spiralPoints}" stroke="${color}" stroke-width="${2 + level}" fill="none" opacity="${opacity}"/>`);
                } else if (elementType === 1) {
                    const circleRadius = branchLength * 0.3;
                    fractal.push(`<circle cx="${endX}" cy="${endY}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                    
                    const innerColor = palette[Math.floor(Math.random() * palette.length)];
                    for (let i = 0; i < 4; i++) {
                        const innerAngle = (i * Math.PI) / 2;
                        const innerX = endX + circleRadius * 0.5 * Math.cos(innerAngle);
                        const innerY = endY + circleRadius * 0.5 * Math.sin(innerAngle);
                        fractal.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.3}" fill="${innerColor}" opacity="${opacity * 0.7}"/>`);
                    }
                } else if (elementType === 2) {
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
                    const starRadius = branchLength * 0.3;
                    const numPoints = this.randomInt(5, 8);
                    const starPoints = this.generateStarPoints(endX, endY, starRadius, numPoints);
                    fractal.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                }
            }
        }
        
        return this.createSVG(size.width, size.height, fractal.join(''));
    }

    generateOpticalPattern() {
        const size = this.getRandomSize();
        const optical = [];
        const palette = this.getRandomPalette();
        
        const numLayers = this.randomInt(3, 5);
        const layerSpacing = size.height / numLayers;
        
        for (let layer = 0; layer < numLayers; layer++) {
            const y = layer * layerSpacing;
            const layerHeight = layerSpacing;
            const opacity = this.random(0.3, 0.7);
            
            const effectType = this.randomInt(0, 3);
            
            if (effectType === 0) {
                const numWaves = this.randomInt(8, 15);
                const waveAmplitude = layerHeight * 0.3;
                const waveLength = size.width / numWaves;
                
                for (let i = 0; i < numWaves; i++) {
                    const x = i * waveLength;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    const wavePoints = [];
                    for (let j = 0; j < 20; j++) {
                        const waveX = x + (j * waveLength) / 20;
                        const waveY = y + layerHeight/2 + waveAmplitude * Math.sin((j * Math.PI) / 10);
                        wavePoints.push(`${waveX},${waveY}`);
                    }
                    
                    optical.push(`<polyline points="${wavePoints.join(' ')}" stroke="${color}" stroke-width="${3 + layer}" fill="none" opacity="${opacity}"/>`);
                }
            } else if (effectType === 1) {
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
                const numShapes = this.randomInt(6, 12);
                const shapeSize = Math.min(size.width, layerHeight) / numShapes;
                
                for (let i = 0; i < numShapes; i++) {
                    const x = i * shapeSize;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    const shapeType = this.randomInt(0, 3);
                    
                    if (shapeType === 0) {
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
                        const numPoints = this.randomInt(6, 10);
                        const starRadius = shapeSize * 0.4;
                        const starPoints = this.generateStarPoints(x + shapeSize/2, y + layerHeight/2, starRadius, numPoints);
                        optical.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                    } else {
                        const circleRadius = shapeSize * 0.4;
                        optical.push(`<circle cx="${x + shapeSize/2}" cy="${y + layerHeight/2}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                        
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

    generateMosaicPattern() {
        const size = this.getRandomSize();
        const mosaic = [];
        const palette = this.getRandomPalette();
        
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
                        
                        const elementType = this.randomInt(0, 4);
                        
                        if (elementType === 0) {
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
                            const numPoints = this.randomInt(5, 8);
                            const starRadius = cellSize * 0.4;
                            const starPoints = this.generateStarPoints(x + cellSize/2, y + cellSize/2, starRadius, numPoints);
                            mosaic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${layerOpacity}"/>`);
                        } else if (elementType === 2) {
                            const circleRadius = cellSize * 0.4;
                            mosaic.push(`<circle cx="${x + cellSize/2}" cy="${y + cellSize/2}" r="${circleRadius}" fill="${color}" opacity="${layerOpacity}"/>`);
                            
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            for (let k = 0; k < 4; k++) {
                                const innerAngle = (k * Math.PI) / 2;
                                const innerX = x + cellSize/2 + circleRadius * 0.6 * Math.cos(innerAngle);
                                const innerY = y + cellSize/2 + circleRadius * 0.6 * Math.sin(innerAngle);
                                mosaic.push(`<circle cx="${innerX}" cy="${innerY}" r="${circleRadius * 0.2}" fill="${innerColor}" opacity="${layerOpacity * 0.8}"/>`);
                            }
                        } else {
                            const centerX = x + cellSize/2;
                            const centerY = y + cellSize/2;
                            const diamondSize = cellSize * 0.6;
                            const points = `${centerX},${centerY - diamondSize/2} ${centerX + diamondSize/2},${centerY} ${centerX},${centerY + diamondSize/2} ${centerX - diamondSize/2},${centerY}`;
                            mosaic.push(`<polygon points="${points}" fill="${color}" opacity="${layerOpacity}"/>`);
                            
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            mosaic.push(`<circle cx="${centerX}" cy="${centerY}" r="${diamondSize/4}" fill="${innerColor}" opacity="${layerOpacity * 0.7}"/>`);
                        }
                    }
                }
            }
        }
        
        return this.createSVG(size.width, size.height, mosaic.join(''));
    }

    generateCelticPattern() {
        const size = this.getRandomSize();
        const celtic = [];
        const palette = this.getRandomPalette();
        
        const numKnots = this.randomInt(3, 6);
        const knotSize = Math.min(size.width, size.height) / numKnots;
        
        for (let knot = 0; knot < numKnots; knot++) {
            const centerX = (knot + 1) * (size.width / (numKnots + 1));
            const centerY = size.height / 2;
            const opacity = this.random(0.3, 0.7);
            
            const knotType = this.randomInt(0, 3);
            
            if (knotType === 0) {
                const numArms = this.randomInt(4, 8);
                for (let arm = 0; arm < numArms; arm++) {
                    const angle = (arm * 2 * Math.PI) / numArms;
                    const color = palette[Math.floor(Math.random() * palette.length)];
                    
                    const endX = centerX + knotSize * 0.8 * Math.cos(angle);
                    const endY = centerY + knotSize * 0.8 * Math.sin(angle);
                    const spiralPoints = this.generateSpiralPoints(centerX, centerY, endX, endY, 3);
                    celtic.push(`<path d="${spiralPoints}" stroke="${color}" stroke-width="${3}" fill="none" opacity="${opacity}"/>`);
                }
            } else if (knotType === 1) {
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
                        
                        const elementType = this.randomInt(0, 2);
                        
                        if (elementType === 0) {
                            celtic.push(`<circle cx="${x}" cy="${y}" r="${elementSize}" fill="${color}" opacity="${opacity}"/>`);
                            
                            const innerColor = palette[Math.floor(Math.random() * palette.length)];
                            for (let k = 0; k < 4; k++) {
                                const innerAngle = angle + (k * Math.PI) / 2;
                                const innerX = x + elementSize * 0.6 * Math.cos(innerAngle);
                                const innerY = y + elementSize * 0.6 * Math.sin(innerAngle);
                                celtic.push(`<circle cx="${innerX}" cy="${innerY}" r="${elementSize * 0.3}" fill="${innerColor}" opacity="${opacity * 0.8}"/>`);
                            }
                        } else {
                            const numPoints = this.randomInt(5, 8);
                            const starPoints = this.generateStarPoints(x, y, elementSize, numPoints);
                            celtic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                        }
                    }
                }
            } else {
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
                            
                            const shapeType = this.randomInt(0, 3);
                            
                            if (shapeType === 0) {
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
                                const numPoints = this.randomInt(5, 8);
                                const starRadius = cellSize * 0.4;
                                const starPoints = this.generateStarPoints(x + cellSize/2, y + cellSize/2, starRadius, numPoints);
                                celtic.push(`<polygon points="${starPoints}" fill="${color}" opacity="${opacity}"/>`);
                            } else {
                                const circleRadius = cellSize * 0.4;
                                celtic.push(`<circle cx="${x + cellSize/2}" cy="${y + cellSize/2}" r="${circleRadius}" fill="${color}" opacity="${opacity}"/>`);
                                
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
        return `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="100%" height="100%" fill="${randomBackground}"/>
            ${content}
        </svg>`;
    }

    getAllPatterns() {
        try {
            return [
                this.generateCirclesPattern(),
                this.generateCirclesPattern(),
                this.generateCirclesPattern()
            ];
        } catch (error) {
            return [this.generateCirclesPattern()];
        }
    }
}



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
                return true;
            }
        }
    }
    return false;
}

if (typeof window !== 'undefined') {
    try {
        window.patternGenerator = new SVGPatternGenerator();
    } catch (error) {
        window.patternGenerator = null;
    }
    
    window.SVGPatternGenerator = SVGPatternGenerator;
    window.getRandomPattern = getRandomPattern;
    window.getAllPatterns = getAllPatterns;
    window.setPatternColors = setPatternColors;
    window.generateNewPatternForCard = generateNewPatternForCard;
    
} else if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SVGPatternGenerator, getRandomPattern, getAllPatterns, setPatternColors };
}
