/**
 * Theme Switcher
 * 
 * Manages theme switching between light and dark modes
 */
class ThemeSwitcher {
    constructor() {
        this.themeKey = 'preferred-theme';
        this.themeMode = 'preferred-theme-mode'; // auto, manual, time-based
        this.darkThemeClass = 'dark-theme';
        this.init();
    }

    init() {
        // Apply saved theme or system preference
        this.applyTheme();
        
        // Set up event listeners
        document.addEventListener('DOMContentLoaded', () => {
            const toggleBtns = document.querySelectorAll('.theme-toggle');
            if (toggleBtns) {
                toggleBtns.forEach(btn => {
                    btn.addEventListener('click', () => this.toggleTheme());
                });
            }
        });

        // Schedule next theme check if time-based mode is active
        if (localStorage.getItem(this.themeMode) === 'time-based') {
            this.scheduleNextThemeCheck();
        }
    }

    applyTheme() {
        const savedThemeMode = localStorage.getItem(this.themeMode) || 'auto';
        const savedTheme = localStorage.getItem(this.themeKey);
        
        if (savedThemeMode === 'time-based') {
            this.applyTimeBasedTheme();
            return;
        }
        
        // If user has explicitly chosen a theme in manual mode
        if (savedThemeMode === 'manual' && savedTheme) {
            if (savedTheme === 'dark') {
                this.setDarkTheme(false); // Don't resave the preference
            } else {
                this.setLightTheme(false); // Don't resave the preference
            }
            return;
        }
        
        // Auto mode - follow system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.setDarkTheme(false); // Don't save, just follow system
        } else {
            this.setLightTheme(false); // Don't save, just follow system
        }
        
        // Add listener for system theme changes when in auto mode
        if (window.matchMedia && savedThemeMode === 'auto') {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (localStorage.getItem(this.themeMode) === 'auto') {
                    if (e.matches) {
                        this.setDarkTheme(false); // Don't save, just follow system
                    } else {
                        this.setLightTheme(false); // Don't save, just follow system
                    }
                }
            });
        }
    }

    applyTimeBasedTheme() {
        const now = new Date();
        const hour = now.getHours();
        
        // Default time ranges: dark theme from 18:00 to 6:00
        const startDarkHour = parseInt(localStorage.getItem('dark-theme-start') || '18');
        const endDarkHour = parseInt(localStorage.getItem('dark-theme-end') || '6');
        
        if (this.isNightTime(hour, startDarkHour, endDarkHour)) {
            this.setDarkTheme(false); // Don't resave the settings
        } else {
            this.setLightTheme(false); // Don't resave the settings
        }
        
        // Schedule next check
        this.scheduleNextThemeCheck();
    }
    
    isNightTime(currentHour, startHour, endHour) {
        // Handle cases where the night spans across midnight
        if (startHour >= endHour) {
            return currentHour >= startHour || currentHour < endHour;
        } else {
            // Simple case where dark period is within the same day
            return currentHour >= startHour && currentHour < endHour;
        }
    }
    
    scheduleNextThemeCheck() {
        // Check every hour for theme changes
        setTimeout(() => {
            if (localStorage.getItem(this.themeMode) === 'time-based') {
                this.applyTimeBasedTheme();
            }
        }, 60 * 60 * 1000); // Check every hour
    }

    toggleTheme() {
        // Always set to manual mode when user toggles manually
        localStorage.setItem(this.themeMode, 'manual');
        
        if (document.body.classList.contains(this.darkThemeClass)) {
            this.setLightTheme();
        } else {
            this.setDarkTheme();
        }
    }

    setDarkTheme(save = true) {
        document.body.classList.add(this.darkThemeClass);
        this.updateToggleIcons('sun');
        if (save) localStorage.setItem(this.themeKey, 'dark');
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: 'dark' }));
    }

    setLightTheme(save = true) {
        document.body.classList.remove(this.darkThemeClass);
        this.updateToggleIcons('moon');
        if (save) localStorage.setItem(this.themeKey, 'light');
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('themeChanged', { detail: 'light' }));
    }

    updateToggleIcons(icon) {
        const toggleBtns = document.querySelectorAll('.theme-toggle i');
        if (toggleBtns) {
            toggleBtns.forEach(btn => {
                btn.className = `fas fa-${icon}`;
            });
        }
    }

    // Set theme mode: 'auto', 'manual', 'time-based'
    setThemeMode(mode, startHour = 18, endHour = 6) {
        localStorage.setItem(this.themeMode, mode);
        
        if (mode === 'time-based') {
            localStorage.setItem('dark-theme-start', startHour);
            localStorage.setItem('dark-theme-end', endHour);
            this.applyTimeBasedTheme();
        } else if (mode === 'auto') {
            // Reset to system preference
            localStorage.removeItem(this.themeKey);
            this.applyTheme();
        }
        // For 'manual' mode, keep the current theme setting
    }
}

// Initialize theme switcher
const themeSwitcher = new ThemeSwitcher();

// Make themeSwitcher globally accessible
window.themeSwitcher = themeSwitcher;
