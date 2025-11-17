/**
 * Color Theme Toggle System
 * Detects purple/violet colors and replaces them with peach/orange theme
 * Account-bound cookie persistence
 */

class ColorThemeManager {
    constructor() {
        this.originalColors = new Map();
        this.isPeachThemeActive = false;
        this.userId = this.getCurrentUserId();
        this.cookieName = `color_theme_${this.userId}`;

        // Only map the specific brand colors we target
        this.colorMappings = {
            '#B595FF': '#FF8C69',        // primary purple -> peach
            '#9A7FE6': '#FF7F50',        // primary hover -> coral
        };

        this.init();
    }

    init() {
        // Load saved theme preference
        this.loadThemePreference();

        // Create CSS custom properties for peach theme
        this.injectPeachCSS();

        // Add toggle button to navbar
        this.addToggleButton();

        // Apply theme if it was saved as active
        if (this.isPeachThemeActive) {
            this.applyPeachTheme();
        }

        console.log('Color Theme Manager initialized:', {
            userId: this.userId,
            isPeachThemeActive: this.isPeachThemeActive
        });
    }

    injectPeachCSS() {
        // CSS variables are now defined in style.css :root
        // This class simply defines identical fallback overrides using !important
        const css = `
            /* Emergency fallback - CSS variables should be defined in :root */
            .peach-theme-active {
                --primary-color: var(--peach-color) !important;
                --primary-hover: var(--peach-hover) !important;
            }

            .peach-theme-active .btn-primary {
                background-color: var(--peach-color) !important;
                border-color: var(--peach-color) !important;
            }

            .peach-theme-active .btn-primary:hover {
                background-color: var(--peach-hover) !important;
                border-color: var(--peach-hover) !important;
            }

            .peach-theme-active .text-primary {
                color: var(--peach-color) !important;
            }

            .peach-theme-active .navbar-brand {
                color: var(--peach-color) !important;
            }
        `;

        const style = document.createElement('style');
        style.id = 'peach-theme-styles';
        style.textContent = css;
        document.head.appendChild(style);
    }

    addToggleButton() {
        // Find the navbar collapse div
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (!navbarCollapse) return;

        // Create toggle button
        const toggleBtn = document.createElement('li');
        toggleBtn.className = 'nav-item me-2';
        toggleBtn.innerHTML = `
            <button id="colorThemeToggle" class="btn btn-outline-secondary btn-sm" title="Переключить цветовую тему (фиолетовая ↔ персиковая)">
                <i class="fas fa-palette"></i>
                <span class="d-lg-none ms-1">Тема</span>
            </button>
        `;

        // Insert before the profile link
        const profileLink = navbarCollapse.querySelector('a[href*="profile"]');
        if (profileLink && profileLink.closest('.nav-item')) {
            profileLink.closest('.nav-item').parentNode.insertBefore(toggleBtn, profileLink.closest('.nav-item'));
        } else {
            // Fallback: insert at the beginning
            const ul = navbarCollapse.querySelector('.navbar-nav');
            if (ul && ul.children.length > 0) {
                ul.insertBefore(toggleBtn, ul.children[0]);
            }
        }

        // Add click handler
        const btn = document.getElementById('colorThemeToggle');
        if (btn) {
            btn.addEventListener('click', () => this.toggleTheme());
            this.updateButtonState();
        }
    }

    toggleTheme() {
        this.isPeachThemeActive = !this.isPeachThemeActive;

        if (this.isPeachThemeActive) {
            this.applyPeachTheme();
            this.showNotification('Персиковая тема активирована! 🧡', 'success');
        } else {
            this.restoreOriginalTheme();
            this.showNotification('Стандартная тема активирована! 💜', 'info');
        }

        this.saveThemePreference();
        this.updateButtonState();
    }

    applyPeachTheme() {
        // Add peach theme class to body
        document.body.classList.add('peach-theme-active');

        // Find and replace purple/violet colors
        this.replaceColorsInDOM();

        // Replace CSS custom properties
        this.replaceCSSCustomProperties();

        console.log('Peach theme applied');
    }

    restoreOriginalTheme() {
        // Remove peach theme class
        document.body.classList.remove('peach-theme-active');

        // Restore original colors
        this.restoreColorsInDOM();

        // Restore CSS custom properties
        this.restoreCSSCustomProperties();

        console.log('Original theme restored');
    }

    replaceColorsInDOM() {
        // Process all elements
        const elements = document.querySelectorAll('*');

        elements.forEach(element => {
            const computedStyles = window.getComputedStyle(element);

            // Check background-color
            const bgColor = computedStyles.backgroundColor;
            if (this.isPurpleColor(bgColor)) {
                this.originalColors.set(element, {
                    ...this.originalColors.get(element),
                    backgroundColor: bgColor
                });
                element.style.backgroundColor = this.mapPurpleToPeach(bgColor);
            }

            // Check color
            const color = computedStyles.color;
            if (this.isPurpleColor(color)) {
                this.originalColors.set(element, {
                    ...this.originalColors.get(element),
                    color: color
                });
                element.style.color = this.mapPurpleToPeach(color);
            }

            // Check border colors
            const borderColor = computedStyles.borderColor;
            if (this.isPurpleColor(borderColor)) {
                this.originalColors.set(element, {
                    ...this.originalColors.get(element),
                    borderColor: borderColor
                });
                element.style.borderColor = this.mapPurpleToPeach(borderColor);
            }
        });
    }

    restoreColorsInDOM() {
        // Restore all saved original colors
        this.originalColors.forEach((colors, element) => {
            if (colors.backgroundColor) {
                element.style.backgroundColor = colors.backgroundColor;
            }
            if (colors.color) {
                element.style.color = colors.color;
            }
            if (colors.borderColor) {
                element.style.borderColor = colors.borderColor;
            }
        });

        this.originalColors.clear();
    }

    replaceCSSCustomProperties() {
        // CSS custom properties are now handled by the injected CSS
        // with class-based overrides (.peach-theme-active)
        // No additional processing needed
    }

    restoreCSSCustomProperties() {
        // Note: CSS restoration is complex, so we rely on removing the peach-theme-active class
        // which overrides the colors via :root variables
    }

    isPurpleColor(color) {
        if (!color || color === 'transparent' || color === 'inherit') return false;

        // Check for CSS custom properties that are specifically brand colors
        if (color.includes('--primary-color') || color.includes('--primary-hover')) {
            return true;
        }

        // Only check specific known purple/violet color codes
        if (color.startsWith('#')) {
            return this.isKnownPurpleHex(color);
        }

        // Skip RGB detection entirely to avoid false positives with dark colors
        return false;
    }

    isKnownPurpleHex(color) {
        // Only target the specific brand colors used in the CSS
        // Avoid common dark/background colors by being very specific
        const knownBrandPurpleHex = [
            '#B595FF',    // main primary color (exact match only)
            '#9A7FE6'     // primary hover (exact match only)
        ];

        return knownBrandPurpleHex.some(purple =>
            color.toLowerCase() === purple.toLowerCase()
        );
    }

    mapPurpleToPeach(purpleColor) {
        // First check exact matches
        if (this.colorMappings[purpleColor]) {
            return this.colorMappings[purpleColor];
        }

        // Handle CSS custom properties
        if (purpleColor.includes('var(--primary-color')) {
            return 'var(--peach-color)';
        }
        if (purpleColor.includes('var(--primary-hover')) {
            return 'var(--peach-hover)';
        }

        // For hex colors, find approximate mappings
        if (purpleColor.startsWith('#')) {
            for (const [purple, peach] of Object.entries(this.colorMappings)) {
                if (purple.toLowerCase() === purpleColor.toLowerCase()) {
                    return peach;
                }
            }

            // Default fallback to main peach color
            return '#FF8C69';
        }

        // For RGB colors, default to peach
        return '#FF8C69';
    }

    updateButtonState() {
        const btn = document.getElementById('colorThemeToggle');
        if (!btn) return;

        const icon = btn.querySelector('i');

        if (this.isPeachThemeActive) {
            btn.className = 'btn btn-outline-warning btn-sm';
            btn.title = 'Переключить на фиолетовую тему';
            if (icon) {
                icon.className = 'fas fa-adjust';
            }
        } else {
            btn.className = 'btn btn-outline-primary btn-sm';
            btn.title = 'Переключить на персиковую тему';
            if (icon) {
                icon.className = 'fas fa-palette';
            }
        }
    }

    getCurrentUserId() {
        // Try to get user ID from Flask template context or session
        // Since we don't have direct access, we'll use a hash of the session or IP
        try {
            const sessionCookie = document.cookie.match(/session=([^;]+)/);
            if (sessionCookie && sessionCookie[1]) {
                // Simple hash of session ID for user identification
                let hash = 0;
                const str = sessionCookie[1];
                for (let i = 0; i < str.length; i++) {
                    hash = ((hash << 5) - hash) + str.charCodeAt(i);
                    hash = hash & hash; // Convert to 32-bit integer
                }
                return Math.abs(hash).toString();
            }
        } catch (e) { }

        // Fallback: use a more persistent identifier
        return this.getPersistentUserId();
    }

    getPersistentUserId() {
        // Use localStorage for user identification across sessions
        let userId = localStorage.getItem('userColorThemeId');
        if (!userId) {
            userId = Date.now().toString() + '-' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('userColorThemeId', userId);
        }
        return userId;
    }

    loadThemePreference() {
        try {
            const cookieValue = document.cookie.match(new RegExp(`${this.cookieName}=([^;]+)`));
            this.isPeachThemeActive = cookieValue ? (cookieValue[1] === 'true') : false;
        } catch (e) {
            console.warn('Failed to load color theme preference:', e);
            this.isPeachThemeActive = false;
        }
    }

    saveThemePreference() {
        try {
            const expiryDate = new Date();
            expiryDate.setFullYear(expiryDate.getFullYear() + 1); // Cookie expires in 1 year

            document.cookie = `${this.cookieName}=${this.isPeachThemeActive}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;

            // Also save to localStorage as backup
            localStorage.setItem(`color_theme_${this.userId}`, this.isPeachThemeActive.toString());
        } catch (e) {
            console.warn('Failed to save color theme preference:', e);
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type, duration);
        } else if (window.showSuccess && type === 'success') {
            window.showSuccess(message, duration);
        } else if (window.showError && type === 'error') {
            window.showError(message, duration);
        } else {
            // Fallback: simple alert (rarely used)
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// Initialize the color theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.colorThemeManager = new ColorThemeManager();
});

// Make it globally available for debugging
window.ColorThemeManager = ColorThemeManager;

/**
 * Usage examples:
 *
 * // Toggle theme programmatically
 * window.colorThemeManager.toggleTheme();
 *
 * // Apply peach theme
 * window.colorThemeManager.applyPeachTheme();
 *
 * // Restore original theme
 * window.colorThemeManager.restoreOriginalTheme();
 */
