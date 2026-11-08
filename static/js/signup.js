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

            const emailInput = document.getElementById("email");
            const emailFeedback = document.getElementById("email-feedback");

            const DISPOSABLE_EMAIL_DOMAINS = new Set([
                "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
                "guerrillamail.block", "guerrillamail.net", "guerrillamail.org", "sharklasers.com",
                "yopmail.com", "yopmail.fr", "yopmail.net", "trashmail.com", "trashmail.net",
                "dispostable.com", "getairmail.com", "throwawaymail.com", "fakemailgenerator.com",
                "temp-mail.org", "tempmail.net", "generator.email", "mohmal.com", "nada.ltd",
                "crazymailing.com", "inboxkitten.com", "mytemp.email", "tempinbox.com",
                "burnermail.io", "maildrop.cc", "emailondeck.com", "zillamail.com"
            ]);

            const BLOCKED_PLACEHOLDER_DOMAINS = new Set([
                "example.com", "example.org", "example.net", "example.edu",
                "test.com", "testing.com", "test.test", "sample.com", "fake.com",
                "temp.com", "invalid", "localhost", "none.com", "null.com",
                "asdf.com", "qwerty.com", "xyz.com", "domain.com", "email.com"
            ]);

            const COMMON_DOMAIN_TYPOS = {
                "gmial.com": "gmail.com",
                "gmai.com": "gmail.com",
                "gamil.com": "gmail.com",
                "gmaill.com": "gmail.com",
                "yaho.com": "yahoo.com",
                "yahooo.com": "yahoo.com",
                "hotmial.com": "hotmail.com",
                "hotmaill.com": "hotmail.com",
                "outlok.com": "outlook.com",
                "outllok.com": "outlook.com",
                "iclud.com": "icloud.com"
            };

            const EMAIL_REGEX = /^(?![.])(?!.*[.]{2})[a-zA-Z0-9_.+-]+(?<![.])@(?![.-])(?!.*[.]{2})(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,24}$/;

            function checkEmail(showSuccess = false) {
                if (!emailInput) return true;
                emailInput.setCustomValidity("");
                const val = emailInput.value.trim().toLowerCase();

                if (!val) {
                    if (emailFeedback) {
                        emailFeedback.textContent = "";
                        emailFeedback.className = "settings-email-feedback";
                    }
                    return true;
                }

                let errMsg = "";
                let isWarning = false;

                if (val.length < 6 || val.length > 254) {
                    errMsg = "Email must be between 6 and 254 characters.";
                } else if ((val.match(/@/g) || []).length !== 1) {
                    errMsg = "Email must contain exactly one '@' symbol.";
                } else {
                    const parts = val.split("@");
                    const localPart = parts[0];
                    const domainPart = parts[1];

                    if (!localPart || localPart.length > 64) {
                        errMsg = "Username before '@' must be 1 to 64 characters.";
                    } else if (!domainPart || domainPart.length < 3) {
                        errMsg = "Domain after '@' is incomplete.";
                    } else if (!EMAIL_REGEX.test(val)) {
                        errMsg = "Enter a valid email address with a recognized domain (e.g., name@gmail.com).";
                    } else if (DISPOSABLE_EMAIL_DOMAINS.has(domainPart)) {
                        errMsg = "Temporary or disposable email addresses are not permitted.";
                    } else if (BLOCKED_PLACEHOLDER_DOMAINS.has(domainPart) || domainPart.endsWith(".invalid") || domainPart.endsWith(".localhost")) {
                        errMsg = "Placeholder or dummy email domains are not allowed.";
                    } else if (COMMON_DOMAIN_TYPOS[domainPart]) {
                        const suggested = COMMON_DOMAIN_TYPOS[domainPart];
                        errMsg = `Did you mean '${localPart}@${suggested}'? Please verify your domain spelling.`;
                        isWarning = true;
                    }
                }

                if (errMsg) {
                    emailInput.setCustomValidity(errMsg);
                    if (emailFeedback) {
                        emailFeedback.textContent = errMsg;
                        emailFeedback.className = isWarning
                            ? "settings-email-feedback is-warning"
                            : "settings-email-feedback is-invalid";
                    }
                    emailInput.style.borderColor = isWarning ? "#d97706" : "#dc2626";
                    return false;
                }

                emailInput.style.borderColor = "";
                if (emailFeedback) {
                    if (showSuccess) {
                        emailFeedback.textContent = "✓ Valid email address.";
                        emailFeedback.className = "settings-email-feedback is-valid";
                    } else {
                        emailFeedback.textContent = "";
                        emailFeedback.className = "settings-email-feedback";
                    }
                }
                return true;
            }

            if (emailInput) {
                emailInput.addEventListener("input", () => checkEmail(false));
                emailInput.addEventListener("blur", () => checkEmail(true));
            }

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
                const isEmailValid = checkEmail(true);
                const isPassValid = checkPasswords();

                if (!isEmailValid) {
                    event.preventDefault();
                    if (emailInput) {
                        emailInput.focus();
                        emailInput.reportValidity();
                    }
                    return;
                }

                if (!isPassValid) {
                    event.preventDefault();
                    confirmPassword.reportValidity();
                }
            });
        })();