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

        // Open the confirmation popup.
        function openLogoutModal() {
            logoutModal.hidden = false;
            cancelLogout.focus();
        }

        // Close the popup without logging out.
        function closeLogoutModal() {
            logoutModal.hidden = true;
            logoutButton.focus();
        }

        // Click Log Out.
        logoutButton.addEventListener("click", openLogoutModal);

        // Click Cancel.
        cancelLogout.addEventListener("click", closeLogoutModal);

        // Confirm logout and submit the original POST form.
        confirmLogout.addEventListener("click", function () {
            logoutForm.requestSubmit();
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

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initLogout);
    } else {
        initLogout();
    }
})();
