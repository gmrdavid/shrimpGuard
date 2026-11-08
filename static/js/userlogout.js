/**
 * ShrimpGuard - User Logout Handler
 * Robust modal confirmation and secure session termination.
 */
(function () {
    function initLogout() {
        const logoutForm = document.getElementById("logoutForm");
        const logoutButton = document.getElementById("logoutButton");
        const logoutModal = document.getElementById("logoutModal");
        const cancelLogout = document.getElementById("cancelLogout");
        const confirmLogout = document.getElementById("confirmLogout");

        if (!logoutForm || !logoutButton || !logoutModal || !cancelLogout || !confirmLogout) {
            return;
        }

        // Avoid duplicate event listener attachments
        if (logoutButton.dataset.logoutInitialized === "true") {
            return;
        }
        logoutButton.dataset.logoutInitialized = "true";

        // Always relocate modal to document.body so it isn't trapped or clipped by sidebar stacking contexts
        if (logoutModal.parentElement !== document.body) {
            document.body.appendChild(logoutModal);
        }

        function openLogoutModal(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            logoutModal.hidden = false;
            // Prevent body scroll behind modal
            document.body.classList.add("modal-open");
            cancelLogout.focus();
        }

        function closeLogoutModal() {
            logoutModal.hidden = true;
            document.body.classList.remove("modal-open");
            logoutButton.focus();
        }

        logoutButton.addEventListener("click", openLogoutModal);
        cancelLogout.addEventListener("click", closeLogoutModal);

        confirmLogout.addEventListener("click", function (event) {
            if (event) event.preventDefault();
            confirmLogout.disabled = true;
            confirmLogout.classList.add("loading");

            // Attempt standard form submission first
            try {
                if (typeof logoutForm.requestSubmit === "function") {
                    logoutForm.requestSubmit();
                    return;
                }
            } catch (err) {
                // requestSubmit failed, fall through to submit()
            }

            try {
                logoutForm.submit();
            } catch (err) {
                // Direct navigation fallback if form submission is completely blocked
                window.location.href = logoutForm.getAttribute("action") || "/logout";
            }
        });

        // Close on dark overlay click
        logoutModal.addEventListener("click", function (event) {
            if (event.target === logoutModal) {
                closeLogoutModal();
            }
        });

        // Close on Escape key
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !logoutModal.hidden) {
                closeLogoutModal();
            }
        });

        // Accessible trap
        logoutModal.addEventListener("keydown", function (event) {
            if (event.key !== "Tab" || logoutModal.hidden) return;

            const focusable = [cancelLogout, confirmLogout];
            const first = focusable[0];
            const last = focusable[1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initLogout);
    } else {
        initLogout();
    }
})();
