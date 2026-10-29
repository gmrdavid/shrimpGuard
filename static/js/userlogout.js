document.addEventListener("DOMContentLoaded", function () {
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

        const focusableButtons = [
            cancelLogout,
            confirmLogout
        ];

        const firstButton = focusableButtons[0];
        const lastButton = focusableButtons[1];

        if (event.shiftKey && document.activeElement === firstButton) {
            event.preventDefault();
            lastButton.focus();
        } else if (
            !event.shiftKey &&
            document.activeElement === lastButton
        ) {
            event.preventDefault();
            firstButton.focus();
        }
    });
});

