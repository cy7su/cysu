// Индикатор прокрутки - заполняет полосу прокрутки фиолетовым цветом
document.addEventListener('DOMContentLoaded', function() {
    // Создаем стили для скролл-бара с прогрессом
    const style = document.createElement('style');
    style.id = 'scroll-indicator-styles';
    document.head.appendChild(style);
    
    // Функция обновления цвета скролл-бара
    function updateScrollIndicator() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100));
        
        // Вычисляем цвет на основе прогресса прокрутки
        // От темно-серого (0%) до фиолетового (100%)
        const r = Math.round(44 + (181 - 44) * (scrollPercent / 100));
        const g = Math.round(44 + (149 - 44) * (scrollPercent / 100));
        const b = Math.round(44 + (255 - 44) * (scrollPercent / 100));
        
        // Обновляем CSS для скролл-бара
        style.textContent = `
            ::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--dp-01);
                border-radius: 3px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, 
                    rgb(${r}, ${g}, ${b}) 0%, 
                    rgb(${Math.round(r * 0.8)}, ${Math.round(g * 0.8)}, ${Math.round(b * 0.8)}) 100%
                );
                border-radius: 3px;
                border: 1px solid var(--dp-01);
                transition: all 0.1s ease;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(180deg, 
                    var(--primary-color) 0%, 
                    var(--primary-hover) 100%
                );
                border-color: var(--dp-02);
            }
            
            ::-webkit-scrollbar-thumb:active {
                background: linear-gradient(180deg, 
                    var(--primary-hover) 0%, 
                    var(--primary-color) 100%
                );
            }
            
            /* Убираем стрелочки */
            ::-webkit-scrollbar-button {
                display: none;
            }
            
            ::-webkit-scrollbar-corner {
                background: var(--dp-01);
            }
            
            /* Для Firefox */
            * {
                scrollbar-width: thin;
                scrollbar-color: rgb(${r}, ${g}, ${b}) var(--dp-01);
            }
        `;
    }
    
    // Обработчики событий
    window.addEventListener('scroll', updateScrollIndicator, { passive: true });
    window.addEventListener('resize', updateScrollIndicator, { passive: true });
    
    // Инициализация
    updateScrollIndicator();
});
