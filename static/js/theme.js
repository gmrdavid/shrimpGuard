/**
 * ShrimpGuard Theme Manager (Dark / Light Mode)
 * Supports persistent localStorage, system preference fallback, and live event notifications.
 */
(function() {
    'use strict';

    const STORAGE_KEY = 'shrimp_theme';

    function getSavedTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'dark' || saved === 'light') {
            return saved;
        }
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    function applyTheme(theme, persist) {
        if (persist === undefined) persist = true;
        const root = document.documentElement;
        root.setAttribute('data-theme', theme);
        if (document.body) {
            document.body.setAttribute('data-theme', theme);
        }

        if (persist) {
            try {
                localStorage.setItem(STORAGE_KEY, theme);
            } catch (e) {
                console.warn('Unable to persist theme to localStorage', e);
            }
        }

        // Update meta theme-color for mobile address bar
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#0c151b' : '#126b4f');
        }

        // Update toggle button accessible labels
        const toggleButtons = document.querySelectorAll('.theme-toggle-btn, #theme-toggle-btn');
        toggleButtons.forEach(function(btn) {
            const nextMode = theme === 'dark' ? 'light' : 'dark';
            btn.setAttribute('aria-label', 'Switch to ' + nextMode + ' mode');
            btn.setAttribute('title', 'Switch to ' + nextMode + ' mode');
            btn.setAttribute('data-active-theme', theme);
        });

        // Sync settings select if present
        const settingsSelect = document.getElementById('theme-preference-select');
        if (settingsSelect && settingsSelect.value !== theme) {
            settingsSelect.value = theme;
        }

        // Dispatch custom event for charts and interactive components
        window.dispatchEvent(new CustomEvent('shrimp-theme-change', { detail: { theme: theme } }));
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || getSavedTheme();
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next, true);
    }

    // Apply immediately so pre-rendered or head-loaded DOM is synchronized
    const initialTheme = getSavedTheme();
    applyTheme(initialTheme, false);

    // Initialize toggle button listeners when DOM is ready
    function initThemeListeners() {
        document.addEventListener('click', function(event) {
            const btn = event.target.closest('#theme-toggle-btn, .theme-toggle-btn');
            if (btn) {
                event.preventDefault();
                toggleTheme();
            }
        });

        // Listen for changes from select dropdown if present in settings
        document.addEventListener('change', function(event) {
            if (event.target && event.target.id === 'theme-preference-select') {
                applyTheme(event.target.value, true);
            }
        });

        // Listen to system preference changes if user hasn't explicitly chosen
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                if (!localStorage.getItem(STORAGE_KEY)) {
                    applyTheme(e.matches ? 'dark' : 'light', false);
                }
            });
        }

        // Listen for storage changes across tabs
        window.addEventListener('storage', function(e) {
            if (e.key === STORAGE_KEY && e.newValue) {
                applyTheme(e.newValue, false);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeListeners);
    } else {
        initThemeListeners();
    }

    // Expose API globally
    window.ShrimpTheme = {
        getTheme: function() { return document.documentElement.getAttribute('data-theme') || getSavedTheme(); },
        setTheme: applyTheme,
        toggleTheme: toggleTheme
    };
})();
