/**
 * ShrimpGuard - Admin Custom Dropdowns
 * Replicates the Status Filter dropdown design from Historical Readings across all admin views.
 */
(function() {
    'use strict';

    function closeAllAdminDropdowns() {
        document.querySelectorAll('.admin-page .status-dropdown-menu, .admin-page .limit-dropdown-menu').forEach(function(menu) {
            menu.hidden = true;
            menu.style.display = 'none';
        });
        document.querySelectorAll('.admin-page .historical-toolbar-btn').forEach(function(btn) {
            btn.setAttribute('aria-expanded', 'false');
        });
    }

    function syncDropdownFromSelect(anchor) {
        var select = anchor.querySelector('select');
        var menu = anchor.querySelector('.status-dropdown-menu, .limit-dropdown-menu');
        var btn = anchor.querySelector('.historical-toolbar-btn');
        var textSpan = anchor.querySelector("[id$='-text'], span:not(.toolbar-arrow):not(.status-menu-dot):not(.limit-menu-dot)");

        if (!select || !menu) return;

        var prefix = btn ? (btn.getAttribute('data-prefix') || '') : '';
        var currentVal = (select.value || '').toLowerCase();
        var items = menu.querySelectorAll('.status-menu-item, .limit-menu-item');

        var matched = false;
        items.forEach(function(item) {
            var itemVal = (item.getAttribute('data-value') || item.getAttribute('data-status') || item.getAttribute('data-limit') || '').toLowerCase();
            if (itemVal === currentVal) {
                items.forEach(function(el) { el.classList.remove('active'); });
                item.classList.add('active');
                if (textSpan) {
                    var itemText = item.textContent.trim();
                    textSpan.textContent = prefix ? (prefix + itemText) : itemText;
                }
                matched = true;
            }
        });

        // Fallback if not matched: keep first item active
        if (!matched && items.length > 0) {
            var firstItem = items[0];
            items.forEach(function(el) { el.classList.remove('active'); });
            firstItem.classList.add('active');
            if (textSpan) {
                var firstText = firstItem.textContent.trim();
                textSpan.textContent = prefix ? (prefix + firstText) : firstText;
            }
        }
    }

    function initAdminDropdowns() {
        var anchors = document.querySelectorAll('.admin-page .status-picker-anchor, .admin-page .limit-picker-anchor');

        anchors.forEach(function(anchor) {
            if (anchor.dataset.dropdownInitialized === 'true') return;
            anchor.dataset.dropdownInitialized = 'true';

            var btn = anchor.querySelector('.historical-toolbar-btn');
            var menu = anchor.querySelector('.status-dropdown-menu, .limit-dropdown-menu');
            var select = anchor.querySelector('select');
            var textSpan = anchor.querySelector("[id$='-text'], span:not(.toolbar-arrow):not(.status-menu-dot):not(.limit-menu-dot)");

            if (!btn || !menu) return;

            var prefix = btn.getAttribute('data-prefix') || '';

            // Toggle dropdown open/close on button click
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                var isOpen = !menu.hidden && menu.style.display !== 'none';
                closeAllAdminDropdowns();

                if (!isOpen) {
                    menu.hidden = false;
                    menu.style.display = 'flex';
                    btn.setAttribute('aria-expanded', 'true');
                }
            });

            // Handle item clicks inside the menu
            var items = menu.querySelectorAll('.status-menu-item, .limit-menu-item');
            items.forEach(function(item) {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    var val = item.getAttribute('data-value') || item.getAttribute('data-status') || item.getAttribute('data-limit') || '';

                    // Set active class
                    items.forEach(function(el) { el.classList.remove('active'); });
                    item.classList.add('active');

                    // Update button text
                    var itemText = item.textContent.trim();
                    if (textSpan) {
                        textSpan.textContent = prefix ? (prefix + itemText) : itemText;
                    }

                    // Update hidden select if present and trigger change event
                    if (select) {
                        select.value = val;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    // Close menu
                    menu.hidden = true;
                    menu.style.display = 'none';
                    btn.setAttribute('aria-expanded', 'false');
                });
            });

            // Sync initial state from select if value is already set
            syncDropdownFromSelect(anchor);

            // Listen to select change (e.g. from reset buttons or other scripts)
            if (select) {
                select.addEventListener('change', function() {
                    syncDropdownFromSelect(anchor);
                });
            }
        });

        // Listen for reset button clicks to re-sync all dropdowns
        var resetBtns = document.querySelectorAll('#user-reset-btn, #log-reset-btn, #telemetry-reset-btn, .admin-filter-reset-btn');
        resetBtns.forEach(function(resetBtn) {
            if (resetBtn.dataset.resetSyncBound === 'true') return;
            resetBtn.dataset.resetSyncBound = 'true';

            resetBtn.addEventListener('click', function() {
                setTimeout(function() {
                    anchors.forEach(function(anchor) {
                        syncDropdownFromSelect(anchor);
                    });
                }, 20);
            });
        });
    }

    // Global click listener to close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.status-picker-anchor') && !e.target.closest('.limit-picker-anchor')) {
            closeAllAdminDropdowns();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllAdminDropdowns();
        }
    });

    // Auto-init on DOMContentLoaded or immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAdminDropdowns);
    } else {
        initAdminDropdowns();
    }

    window.initAdminDropdowns = initAdminDropdowns;
    window.closeAllAdminDropdowns = closeAllAdminDropdowns;
})();
