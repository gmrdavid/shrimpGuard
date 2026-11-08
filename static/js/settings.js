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
    const emailInput = document.getElementById("profile-email");
    const emailFeedback = document.getElementById("profile-email-feedback");

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

    function validateEmailInput(showSuccess = false) {
        if (!emailInput || !emailFeedback) return true;
        const val = emailInput.value.trim().toLowerCase();

        if (!val) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Please enter an email address.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (val.length < 6 || val.length > 254) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Email must be between 6 and 254 characters.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if ((val.match(/@/g) || []).length !== 1) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Email must contain exactly one '@' symbol.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        const parts = val.split("@");
        const localPart = parts[0];
        const domainPart = parts[1];

        if (!localPart || localPart.length > 64) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Username before '@' must be 1 to 64 characters.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (!domainPart || domainPart.length < 3) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Domain after '@' is incomplete.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (!EMAIL_REGEX.test(val)) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Enter a valid email address with a recognized domain (e.g., name@gmail.com).";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (DISPOSABLE_EMAIL_DOMAINS.has(domainPart)) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Temporary / disposable email addresses are not permitted.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (BLOCKED_PLACEHOLDER_DOMAINS.has(domainPart) || domainPart.endsWith(".invalid") || domainPart.endsWith(".localhost")) {
            emailFeedback.className = "settings-email-feedback is-invalid";
            emailFeedback.textContent = "Placeholder or dummy email domains are not allowed.";
            emailInput.style.borderColor = "#dc2626";
            return false;
        }

        if (COMMON_DOMAIN_TYPOS[domainPart]) {
            const suggested = COMMON_DOMAIN_TYPOS[domainPart];
            emailFeedback.className = "settings-email-feedback is-warning";
            emailFeedback.textContent = `Did you mean '${localPart}@${suggested}'? Please verify your domain spelling.`;
            emailInput.style.borderColor = "#d97706";
            return false;
        }

        // Valid!
        emailInput.style.borderColor = "";
        if (showSuccess) {
            emailFeedback.className = "settings-email-feedback is-valid";
            emailFeedback.textContent = "✓ Valid email address.";
        } else {
            emailFeedback.className = "settings-email-feedback";
            emailFeedback.textContent = "";
        }
        return true;
    }

    if (emailInput) {
        emailInput.addEventListener("input", () => validateEmailInput(false));
        emailInput.addEventListener("blur", () => validateEmailInput(true));
    }

    saveProfileButton.addEventListener("click", () => {
        const isEmailValid = validateEmailInput(true);
        if (!isEmailValid) {
            if (emailInput) {
                emailInput.focus();
                emailInput.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return;
        }

        if (typeof confirmationDialog.showModal === "function") {
            confirmationDialog.showModal();
        } else if (profileForm.reportValidity()) {
            profileForm.requestSubmit();
        }
    });

        // Generate secure unguessable ntfy topic
    const generateTopicBtn = document.getElementById("generate-topic-btn");
    if (generateTopicBtn) {
        generateTopicBtn.addEventListener("click", async () => {
            try {
                const resp = await fetch("/api/ntfy/generate-topic");
                const data = await resp.json();
                if (data.topic) {
                    const input = document.getElementById("profile-ntfy-topic");
                    if (input) {
                        input.value = data.topic;
                        input.focus();
                    }
                }
            } catch (err) {
                const randomHex = Math.random().toString(16).substring(2, 10);
                const input = document.getElementById("profile-ntfy-topic");
                if (input) {
                    input.value = `sg-pond-${randomHex}`;
                    input.focus();
                }
            }
        });
    }


    // ntfy.sh Setup & Guide Dialog
    const openGuideBtn = document.getElementById("open-ntfy-guide-btn");
    const openGuideLink = document.getElementById("open-ntfy-guide-link");
    const closeGuideBtn = document.getElementById("close-ntfy-guide-modal");
    const closeGuideActionBtn = document.getElementById("modal-close-ntfy-guide-btn");
    const guideModal = document.getElementById("ntfy-guide-modal");
    const guideTopicPreview = document.getElementById("guide-topic-preview");
    const guideCopyTopicBtn = document.getElementById("guide-copy-topic-btn");
    const guideCopyText = document.getElementById("guide-copy-text");

    function openNtfyGuide() {
        if (!guideModal) return;
        const topicInput = document.getElementById("profile-ntfy-topic");
        const currentTopic = topicInput && topicInput.value.trim() ? topicInput.value.trim() : "";
        if (guideTopicPreview) {
            guideTopicPreview.textContent = currentTopic || "(No topic entered yet - click Generate Secure Topic)";
        }
        guideModal.hidden = false;
        document.body.style.overflow = "hidden";
    }

    function closeNtfyGuide() {
        if (!guideModal) return;
        guideModal.hidden = true;
        document.body.style.overflow = "";
    }

    if (openGuideBtn) {
        openGuideBtn.addEventListener("click", openNtfyGuide);
    }

    if (openGuideLink) {
        openGuideLink.addEventListener("click", openNtfyGuide);
    }

    if (closeGuideBtn) {
        closeGuideBtn.addEventListener("click", closeNtfyGuide);
    }

    if (closeGuideActionBtn) {
        closeGuideActionBtn.addEventListener("click", closeNtfyGuide);
    }

    if (guideModal) {
        guideModal.addEventListener("click", (e) => {
            if (e.target === guideModal) {
                closeNtfyGuide();
            }
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && guideModal && !guideModal.hidden) {
            closeNtfyGuide();
        }
    });

    if (guideCopyTopicBtn) {
        guideCopyTopicBtn.addEventListener("click", async () => {
            const topicInput = document.getElementById("profile-ntfy-topic");
            const topic = topicInput && topicInput.value.trim() ? topicInput.value.trim() : "";
            if (!topic) {
                window.alert("Please enter or generate a topic first!");
                return;
            }
            try {
                await navigator.clipboard.writeText(topic);
                if (guideCopyText) guideCopyText.textContent = "Copied!";
                setTimeout(() => {
                    if (guideCopyText) guideCopyText.textContent = "Copy Topic";
                }, 2000);
            } catch (err) {
                // Fallback prompt
                window.prompt("Copy your topic name:", topic);
            }
        });
    }

    // Send Test ntfy Push Notification
    const testNtfyButton = document.getElementById("test-ntfy-button");
    if (testNtfyButton) {
        testNtfyButton.addEventListener("click", async () => {
            const topicInput = document.getElementById("profile-ntfy-topic");
            const topic = topicInput ? topicInput.value.trim() : "";
            if (!topic) {
                window.alert("Please enter or generate an ntfy topic first to test push notifications.\n\nTip: Click 'Generate Secure Topic' to create an unguessable private topic.");
                if (topicInput) topicInput.focus();
                return;
            }
            const originalHtml = testNtfyButton.innerHTML;
            testNtfyButton.disabled = true;
            testNtfyButton.textContent = "Sending Push Notification...";
            try {
                const resp = await fetch("/api/ntfy/test", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ntfy_topic: topic })
                });
                const res = await resp.json();
                if (res.success) {
                    window.alert(`Push Notification Dispatched Successfully!\n\nStatus: ${res.status}\nTopic: ${res.topic}\nServer: ${res.server || "ntfy.sh"}\n\nTo view on your phone or browser, open:\nhttps://ntfy.sh/${res.topic}`);
                } else {
                    window.alert(`Notification Delivery Notice: ${res.error || "Unable to send push notification."}`);
                }
            } catch (err) {
                window.alert(`Error sending test push notification: ${err.message}`);
            } finally {
                testNtfyButton.disabled = false;
                testNtfyButton.innerHTML = originalHtml;
            }
        });
    }

    confirmProfileButton.addEventListener("click", () => {
        if (!validateEmailInput(true)) {
            confirmationDialog.close();
            if (emailInput) {
                emailInput.focus();
                emailInput.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return;
        }
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