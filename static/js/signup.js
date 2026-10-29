 (() => {
            const form = document.getElementById("signupForm");
            const password = document.getElementById("password");
            const confirmPassword = document.getElementById("confirm-password");
            const matchMessage = document.getElementById("password-match-message");

            if (!form || !password || !confirmPassword || !matchMessage) {
                return;
            }

            // Show or hide either password field.
            document.querySelectorAll("[data-password-toggle]").forEach((button) => {
                button.addEventListener("click", () => {
                    const input = document.getElementById(
                        button.dataset.passwordToggle
                    );

                    if (!input) return;

                    const showPassword = input.type === "password";

                    input.type = showPassword ? "text" : "password";

                    button.setAttribute(
                        "aria-label",
                        showPassword
                            ? (input.id === "password"
                                ? "Hide password"
                                : "Hide confirm password")
                            : (input.id === "password"
                                ? "Show password"
                                : "Show confirm password")
                    );

                    button.setAttribute(
                        "aria-pressed",
                        String(showPassword)
                    );

                    button.innerHTML = showPassword
                        ? `
                            <svg viewBox="0 0 24 24" width="20" height="20"
                                 fill="none" stroke="currentColor"
                                 stroke-width="1.8" stroke-linecap="round"
                                 stroke-linejoin="round" aria-hidden="true">
                                <path d="m3 3 18 18"/>
                                <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/>
                                <path d="M9.9 5.2A11 11 0 0 1 12 5c6.4 0 10 7 10 7a15.7 15.7 0 0 1-3.1 3.9"/>
                                <path d="M6.6 6.6C3.7 8.5 2 12 2 12s3.6 7 10 7c1.4 0 2.7-.3 3.8-.8"/>
                            </svg>
                        `
                        : `
                            <svg viewBox="0 0 24 24" width="20" height="20"
                                 fill="none" stroke="currentColor"
                                 stroke-width="1.8" stroke-linecap="round"
                                 stroke-linejoin="round" aria-hidden="true">
                                <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                        `;
                });
            });

            // Check whether the passwords match.
            function checkPasswords() {
                confirmPassword.setCustomValidity("");

                if (!confirmPassword.value) {
                    matchMessage.textContent = "";
                    matchMessage.className = "signup-match-message";
                    return true;
                }

                if (password.value !== confirmPassword.value) {
                    matchMessage.textContent = "Passwords do not match.";
                    matchMessage.className =
                        "signup-match-message signup-match-error";

                    confirmPassword.setCustomValidity(
                        "The passwords do not match."
                    );

                    return false;
                }

                matchMessage.textContent = "Passwords match.";
                matchMessage.className =
                    "signup-match-message signup-match-success";

                return true;
            }

            password.addEventListener("input", checkPasswords);
            confirmPassword.addEventListener("input", checkPasswords);

            form.addEventListener("submit", (event) => {
                if (!checkPasswords()) {
                    event.preventDefault();
                    confirmPassword.reportValidity();
                }
            });
        })();