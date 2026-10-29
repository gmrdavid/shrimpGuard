function updateDeviceTime() {
        const timeEl = document.getElementById("time");
        if (timeEl) {
            timeEl.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
        }
    }
    updateDeviceTime();
    setInterval(updateDeviceTime, 1000);

    const profileForm = document.getElementById("profile-update-form");
    const confirmationDialog = document.getElementById("profile-confirmation-dialog");
    const saveProfileButton = document.getElementById("save-profile-button");
    const cancelProfileButton = document.getElementById("cancel-profile-update");
    const confirmProfileButton = document.getElementById("confirm-profile-update");

    saveProfileButton.addEventListener("click", () => {
        if (typeof confirmationDialog.showModal === "function") {
            confirmationDialog.showModal();
        } else if (profileForm.reportValidity()) {
            profileForm.requestSubmit();
        }
    });

    confirmProfileButton.addEventListener("click", () => {
        if (profileForm.reportValidity()) {
            confirmationDialog.close();
            profileForm.requestSubmit();
        }
    });

    cancelProfileButton.addEventListener("click", () => {
        confirmationDialog.close();
        saveProfileButton.focus();
    });

    confirmationDialog.addEventListener("click", (event) => {
        if (event.target === confirmationDialog) {
            confirmationDialog.close();
            saveProfileButton.focus();
        }
    });

    // Show or hide password fields.
    document.querySelectorAll(".settings-password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.dataset.passwordTarget);
            if (!input) return;

            const showPassword = input.type === "password";
            input.type = showPassword ? "text" : "password";
            button.setAttribute("aria-pressed", String(showPassword));

            const labels = {
                "current-password": ["Show current password", "Hide current password"],
                "new-password": ["Show new password", "Hide new password"],
                "confirm-password": ["Show confirmation password", "Hide confirmation password"]
            };

            const labelPair = labels[input.id];
            if (labelPair) {
                button.setAttribute("aria-label", showPassword ? labelPair[1] : labelPair[0]);
            }

            const iconUse = button.querySelector("use");
            if (iconUse) {
                iconUse.setAttribute("href", showPassword ? "#icon-eye" : "#icon-eye");
            }
        });
    });

    // Check that the new password and confirmation match.
    const newPasswordInput = document.getElementById("new-password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const passwordMatchMessage = document.getElementById("confirm-password-help");
    const passwordForm = document.getElementById("password-update-form");

    function validatePasswordMatch() {
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        confirmPasswordInput.setCustomValidity("");

        if (!confirmPassword) {
            passwordMatchMessage.textContent = "Re-enter your new password to confirm it.";
            passwordMatchMessage.classList.remove("is-match", "is-mismatch");
            return;
        }

        if (newPassword !== confirmPassword) {
            confirmPasswordInput.setCustomValidity("The new passwords do not match.");
            passwordMatchMessage.textContent = "The passwords do not match.";
            passwordMatchMessage.classList.add("is-mismatch");
            passwordMatchMessage.classList.remove("is-match");
        } else {
            passwordMatchMessage.textContent = "The passwords match.";
            passwordMatchMessage.classList.add("is-match");
            passwordMatchMessage.classList.remove("is-mismatch");
        }
    }

    newPasswordInput.addEventListener("input", validatePasswordMatch);
    confirmPasswordInput.addEventListener("input", validatePasswordMatch);

    passwordForm.addEventListener("submit", (event) => {
        validatePasswordMatch();

        if (!passwordForm.reportValidity()) {
            event.preventDefault();
        }
    });