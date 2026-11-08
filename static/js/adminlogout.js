/**
 * ShrimpGuard - Admin Logout Handler
 * Robust modal confirmation and secure session termination.
 */
(() => {
    "use strict";

    function initLogout() {
        const logoutForm = document.getElementById("logoutForm");
        const logoutButton = document.getElementById("logoutButton");
        const logoutModal = document.getElementById("logoutModal");
        const cancelLogout = document.getElementById("cancelLogout");
        const confirmLogout = document.getElementById("confirmLogout");

        // Ensure all required elements exist.
        if (
            !logoutForm ||
            !logoutButton ||
            !logoutModal ||
            !cancelLogout ||
            !confirmLogout
        ) {
            return;
        }

        // Avoid duplicate initialization
        if (logoutButton.dataset.logoutInitialized === "true") {
            return;
        }
        logoutButton.dataset.logoutInitialized = "true";

        // Relocate modal to document.body if needed
        if (logoutModal.parentElement !== document.body) {
            document.body.appendChild(logoutModal);
        }

        // Open the confirmation popup.
        function openLogoutModal(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            logoutModal.removeAttribute("hidden");
            logoutModal.hidden = false;
            logoutModal.style.display = "flex";
            document.body.classList.add("modal-open");
            cancelLogout.focus();
        }

        // Close the popup without logging out.
        function closeLogoutModal() {
            logoutModal.setAttribute("hidden", "");
            logoutModal.hidden = true;
            logoutModal.style.display = "none";
            document.body.classList.remove("modal-open");
            logoutButton.focus();
        }

        // Click Log Out.
        logoutButton.addEventListener("click", openLogoutModal);

        // Click Cancel.
        cancelLogout.addEventListener("click", closeLogoutModal);

        // Confirm logout and submit.
        confirmLogout.addEventListener("click", function (event) {
            if (event) event.preventDefault();
            confirmLogout.disabled = true;
            confirmLogout.classList.add("loading");

            let submitted = false;
            try {
                if (logoutForm && typeof logoutForm.submit === "function") {
                    logoutForm.submit();
                    submitted = true;
                }
            } catch (err) {
                submitted = false;
            }

            if (!submitted) {
                window.location.href = logoutForm.getAttribute("action") || "/logout";
            } else {
                setTimeout(function () {
                    window.location.href = "/logout";
                }, 1200);
            }
        });

        // Close the popup when clicking the dark overlay.
        logoutModal.addEventListener("click", function (event) {
            if (event.target === logoutModal) {
                closeLogoutModal();
            }
        });

        // Close the popup by pressing Escape.
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !logoutModal.hidden) {
                closeLogoutModal();
            }
        });

        // Allow keyboard users to navigate within the dialog.
        logoutModal.addEventListener("keydown", function (event) {
            if (event.key !== "Tab" || logoutModal.hidden) {
                return;
            }

            const focusableElements = logoutModal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );

            if (focusableElements.length === 0) {
                return;
            }

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (event.shiftKey) {
                if (document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement.focus();
                }
            }
        });
    }

    if (document.getElementById("logoutButton")) {
        initLogout();
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initLogout);
    } else {
        initLogout();
    }
})();
