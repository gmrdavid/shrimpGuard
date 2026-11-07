/**
 * ShrimpGuard Theme Manager (Dark / Light Mode)
 * Bulletproof persistent theme engine with immediate execution, debouncing,
 * and seamless cross-tab / cross-component synchronization.
 */
(function() {
    'use strict';

    const STORAGE_KEY = 'shrimp_theme';
    let lastToggleTimestamp = 0;

    function getSavedTheme() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved === 'dark' || saved === 'light') {
                return saved;
            }
        } catch (e) {}

        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    function applyTheme(theme, persist) {
        if (persist === undefined) persist = true;
        const isDark = theme === 'dark';
        const root = document.documentElement;

        // Apply attribute AND class to both <html> and <body>
        root.setAttribute('data-theme', theme);
        root.classList.remove('theme-dark', 'theme-light');
        root.classList.add(isDark ? 'theme-dark' : 'theme-light');

        if (document.body) {
            document.body.setAttribute('data-theme', theme);
            document.body.classList.remove('theme-dark', 'theme-light');
            document.body.classList.add(isDark ? 'theme-dark' : 'theme-light');
        }

        if (persist) {
            try {
                localStorage.setItem(STORAGE_KEY, theme);
            } catch (e) {
                console.warn('[ShrimpGuard Theme] localStorage unavailable', e);
            }
        }

        // Update mobile address bar meta theme color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', isDark ? '#0b1319' : '#126b4f');
        }

        // Update all toggle buttons accessible attributes
        const toggleButtons = document.querySelectorAll('.theme-toggle-btn, #theme-toggle-btn');
        toggleButtons.forEach(function(btn) {
            const nextMode = isDark ? 'light' : 'dark';
            btn.setAttribute('aria-label', 'Switch to ' + nextMode + ' mode');
            btn.setAttribute('title', 'Switch to ' + nextMode + ' mode');
            btn.setAttribute('data-active-theme', theme);
        });

        // Sync settings select dropdown if present
        const settingsSelect = document.getElementById('theme-preference-select');
        if (settingsSelect && settingsSelect.value !== theme) {
            settingsSelect.value = theme;
        }

        // Notify active charts and custom components to re-render
        window.dispatchEvent(new CustomEvent('shrimp-theme-change', { detail: { theme: theme, isDark: isDark } }));
    }

    function toggleTheme() {
        const now = Date.now();
        // 350ms debounce guard prevents duplicate rapid clicks / inline onclick + addEventListener dual dispatch
        if (now - lastToggleTimestamp < 350) {
            return document.documentElement.getAttribute('data-theme') || 'light';
        }
        lastToggleTimestamp = now;

        const cur = document.documentElement.getAttribute('data-theme') || 
                    (document.documentElement.classList.contains('theme-dark') ? 'dark' : 'light');
        const next = cur === 'dark' ? 'light' : 'dark';
        applyTheme(next, true);
        return next;
    }

    // Immediately synchronize theme
    const initial = getSavedTheme();
    applyTheme(initial, false);

    function initThemeListeners() {
        // Direct click bindings on all toggle buttons
        const buttons = document.querySelectorAll('#theme-toggle-btn, .theme-toggle-btn');
        buttons.forEach(function(btn) {
            if (!btn.__themeBound) {
                btn.__themeBound = true;
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    toggleTheme();
                });
            }
        });

        // Delegated fallback for dynamically inserted buttons
        document.addEventListener('click', function(event) {
            const target = event.target;
            if (!target) return;
            const btn = target.closest ? target.closest('#theme-toggle-btn, .theme-toggle-btn') : null;
            if (btn && !btn.__themeBound) {
                btn.__themeBound = true;
                event.preventDefault();
                toggleTheme();
            }
        });

        // Listen for changes from select dropdown if in settings
        document.addEventListener('change', function(event) {
            if (event.target && event.target.id === 'theme-preference-select') {
                applyTheme(event.target.value, true);
            }
        });

        // Listen for OS scheme change if user hasn't chosen manually
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                if (!localStorage.getItem(STORAGE_KEY)) {
                    applyTheme(e.matches ? 'dark' : 'light', false);
                }
            });
        }

        // Cross-tab storage sync
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

    // Expose global methods
    window.ShrimpTheme = {
        getTheme: function() { 
            return document.documentElement.getAttribute('data-theme') || getSavedTheme(); 
        },
        setTheme: applyTheme,
        toggleTheme: toggleTheme
    };
    window.toggleShrimpTheme = toggleTheme;
})();
