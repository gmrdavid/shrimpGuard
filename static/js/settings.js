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
                const warnDialog = document.getElementById("test-ntfy-warning-dialog");
                if (warnDialog && typeof warnDialog.showModal === "function") {
                    warnDialog.showModal();
                } else if (warnDialog) {
                    warnDialog.setAttribute("open", "");
                }
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

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Send Test ntfy Push Notification
    const testNtfyButton = document.getElementById("test-ntfy-button");
    const testNtfyWarnDialog = document.getElementById("test-ntfy-warning-dialog");
    const closeTestNtfyWarnBtn = document.getElementById("close-test-ntfy-warning");
    const actionGenTopicBtn = document.getElementById("action-generate-topic");

    const testNtfyResultDialog = document.getElementById("test-ntfy-result-dialog");
    const closeTestNtfyResultBtn = document.getElementById("close-test-ntfy-result");
    const testNtfyResultTitle = document.getElementById("test-ntfy-result-title");
    const testNtfyResultSubtitle = document.getElementById("test-ntfy-result-subtitle");
    const testNtfyResultIcon = document.getElementById("test-ntfy-result-icon");
    const testNtfyResultBody = document.getElementById("test-ntfy-result-body");
    const testNtfyOpenLink = document.getElementById("test-ntfy-open-link");

    if (closeTestNtfyWarnBtn && testNtfyWarnDialog) {
        closeTestNtfyWarnBtn.addEventListener("click", () => testNtfyWarnDialog.close());
    }
    if (actionGenTopicBtn && testNtfyWarnDialog) {
        actionGenTopicBtn.addEventListener("click", () => {
            testNtfyWarnDialog.close();
            if (generateTopicBtn) generateTopicBtn.click();
        });
    }
    if (closeTestNtfyResultBtn && testNtfyResultDialog) {
        closeTestNtfyResultBtn.addEventListener("click", () => testNtfyResultDialog.close());
    }

    [testNtfyWarnDialog, testNtfyResultDialog].forEach(dlg => {
        if (dlg) {
            dlg.addEventListener("click", (e) => {
                if (e.target === dlg) dlg.close();
            });
        }
    });

    if (testNtfyButton) {
        testNtfyButton.addEventListener("click", async () => {
            const topicInput = document.getElementById("profile-ntfy-topic");
            const topic = topicInput ? topicInput.value.trim() : "";
            if (!topic) {
                if (testNtfyWarnDialog && typeof testNtfyWarnDialog.showModal === "function") {
                    testNtfyWarnDialog.showModal();
                } else if (testNtfyWarnDialog) {
                    testNtfyWarnDialog.setAttribute("open", "");
                }
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

                let res;
                const contentType = resp.headers.get("content-type") || "";
                if (contentType.includes("application/json")) {
                    try {
                        res = await resp.json();
                    } catch (parseErr) {
                        res = { success: false, error: "The notification gateway returned an invalid JSON response." };
                    }
                } else {
                    const text = await resp.text();
                    if (resp.status === 401) {
                        res = { success: false, error: "Authentication required. Please refresh the page and log in." };
                    } else if (resp.status === 404) {
                        res = { success: false, error: "The notification endpoint was not found (404). Please ensure the Flask app is restarted." };
                    } else {
                        res = { success: false, error: `Notification gateway returned HTTP ${resp.status}. Please check server logs.` };
                    }
                }

                if (res.success) {
                    if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Test Notification Dispatched!";
                    if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Alert successfully transmitted via ntfy.sh gateway";
                    if (testNtfyResultIcon) {
                        testNtfyResultIcon.style.background = "#ecfdf5";
                        testNtfyResultIcon.style.color = "#059669";
                        testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-check-circle"></use></svg>`;
                    }
                    if (testNtfyResultBody) {
                        testNtfyResultBody.innerHTML = `
                            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; font-size: 13px; line-height: 1.6; color: #334155;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span style="color: #64748b;">Status:</span>
                                    <strong style="color: #059669;">Dispatched (200 OK)</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span style="color: #64748b;">Topic:</span>
                                    <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: 700; color: #0f172a;">${escapeHtml(res.topic || topic)}</code>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: #64748b;">Server Gateway:</span>
                                    <span>${escapeHtml(res.server || "ntfy.sh")}</span>
                                </div>
                            </div>
                            <p style="margin: 12px 0 0; font-size: 12px; color: #64748b; line-height: 1.5;">
                                A test water quality notification has been sent. If you are subscribed to this topic on your mobile phone or browser, you will receive an alert chime now.
                            </p>
                        `;
                    }
                    if (testNtfyOpenLink) {
                        testNtfyOpenLink.href = `https://ntfy.sh/${encodeURIComponent(res.topic || topic)}`;
                        testNtfyOpenLink.style.display = "inline-flex";
                    }
                } else {
                    if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Delivery Notice";
                    if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Unable to dispatch notification";
                    if (testNtfyResultIcon) {
                        testNtfyResultIcon.style.background = "#fee2e2";
                        testNtfyResultIcon.style.color = "#dc2626";
                        testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-alert"></use></svg>`;
                    }
                    if (testNtfyResultBody) {
                        testNtfyResultBody.innerHTML = `
                            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px 16px; font-size: 13px; color: #991b1b; line-height: 1.5;">
                                ${escapeHtml(res.error || "Unable to dispatch push notification. Please check your network connection.")}
                            </div>
                        `;
                    }
                    if (testNtfyOpenLink) testNtfyOpenLink.style.display = "none";
                }
                if (testNtfyResultDialog && typeof testNtfyResultDialog.showModal === "function") {
                    testNtfyResultDialog.showModal();
                } else if (testNtfyResultDialog) {
                    testNtfyResultDialog.setAttribute("open", "");
                }
            } catch (err) {
                if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Delivery Error";
                if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Network request failed";
                if (testNtfyResultIcon) {
                    testNtfyResultIcon.style.background = "#fee2e2";
                    testNtfyResultIcon.style.color = "#dc2626";
                    testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-alert"></use></svg>`;
                }
                if (testNtfyResultBody) {
                    testNtfyResultBody.innerHTML = `
                        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px 16px; font-size: 13px; color: #991b1b;">
                            Error communicating with notification server: ${escapeHtml(err.message)}
                        </div>
                    `;
                }
                if (testNtfyOpenLink) testNtfyOpenLink.style.display = "none";
                if (testNtfyResultDialog && typeof testNtfyResultDialog.showModal === "function") {
                    testNtfyResultDialog.showModal();
                } else if (testNtfyResultDialog) {
                    testNtfyResultDialog.setAttribute("open", "");
                }
            } finally {
                testNtfyButton.disabled = false;
                testNtfyButton.innerHTML = originalHtml;
            }
        });
    }

    // Send Test Sensor Maintenance Notice via ntfy.sh
    const testNtfyMaintButton = document.getElementById("test-ntfy-maint-button");
    if (testNtfyMaintButton) {
        testNtfyMaintButton.addEventListener("click", async () => {
            const topicInput = document.getElementById("profile-ntfy-topic");
            const topic = topicInput ? topicInput.value.trim() : "";
            if (!topic) {
                if (testNtfyWarnDialog && typeof testNtfyWarnDialog.showModal === "function") {
                    testNtfyWarnDialog.showModal();
                } else if (testNtfyWarnDialog) {
                    testNtfyWarnDialog.setAttribute("open", "");
                }
                return;
            }
            const originalHtml = testNtfyMaintButton.innerHTML;
            testNtfyMaintButton.disabled = true;
            testNtfyMaintButton.textContent = "Sending Maintenance Alert...";
            try {
                // Primary: call /api/ntfy/test with alert_type "maintenance"
                let resp = await fetch("/api/ntfy/test", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ntfy_topic: topic, alert_type: "maintenance", is_test: true })
                });

                // Fallback: if /api/ntfy/test returned 404, try /api/ntfy/test-maintenance
                if (resp.status === 404) {
                    resp = await fetch("/api/ntfy/test-maintenance", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ ntfy_topic: topic, alert_type: "maintenance", is_test: true })
                    });
                }

                let res;
                const contentType = resp.headers.get("content-type") || "";
                if (contentType.includes("application/json")) {
                    try {
                        res = await resp.json();
                    } catch (parseErr) {
                        res = { success: false, error: "The notification gateway returned an invalid JSON response." };
                    }
                } else {
                    const text = await resp.text();
                    if (resp.status === 401) {
                        res = { success: false, error: "Authentication required. Please refresh the page and log in." };
                    } else if (resp.status === 404) {
                        res = { success: false, error: "The notification endpoint was not found on the server (404). Please ensure the Flask app is restarted." };
                    } else {
                        res = { success: false, error: `Notification gateway returned HTTP ${resp.status}. Please check server logs.` };
                    }
                }

                if (res.success) {
                    if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Sensor Maintenance Notice Dispatched!";
                    if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Probe cleaning & calibration alert sent via ntfy.sh";
                    if (testNtfyResultIcon) {
                        testNtfyResultIcon.style.background = "#fef3c7";
                        testNtfyResultIcon.style.color = "#d97706";
                        testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-clock"></use></svg>`;
                    }
                    if (testNtfyResultBody) {
                        testNtfyResultBody.innerHTML = `
                            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 14px 16px; font-size: 13px; line-height: 1.6; color: #78350f;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span style="color: #92400e;">Status:</span>
                                    <strong style="color: #d97706;">Transmitted (200 OK)</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                    <span style="color: #92400e;">Target Topic:</span>
                                    <code style="background: #fef3c7; padding: 2px 6px; border-radius: 4px; font-weight: 700; color: #78350f;">${escapeHtml(res.topic || topic)}</code>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: #92400e;">Cycles Alerted:</span>
                                    <strong>7d Biofilm Scrub &bull; 14d 2-Pt pH Calibration</strong>
                                </div>
                            </div>
                            <p style="margin: 12px 0 0; font-size: 12px; color: #64748b; line-height: 1.5;">
                                A Scheduled Sensor Maintenance Notice has been pushed to your device. Check your ntfy app to view the complete anti-drift protocol and SOP guidance!
                            </p>
                        `;
                    }
                    if (testNtfyOpenLink) {
                        testNtfyOpenLink.href = `https://ntfy.sh/${encodeURIComponent(res.topic || topic)}`;
                        testNtfyOpenLink.style.display = "inline-flex";
                    }
                } else {
                    if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Delivery Notice";
                    if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Unable to dispatch maintenance alert";
                    if (testNtfyResultIcon) {
                        testNtfyResultIcon.style.background = "#fee2e2";
                        testNtfyResultIcon.style.color = "#dc2626";
                        testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-alert"></use></svg>`;
                    }
                    if (testNtfyResultBody) {
                        testNtfyResultBody.innerHTML = `<p style="color: #dc2626; font-size: 13px;">${escapeHtml(res.error || "Failed to publish maintenance push alert.")}</p>`;
                    }
                    if (testNtfyOpenLink) testNtfyOpenLink.style.display = "none";
                }
                if (testNtfyResultDialog && typeof testNtfyResultDialog.showModal === "function") {
                    testNtfyResultDialog.showModal();
                } else if (testNtfyResultDialog) {
                    testNtfyResultDialog.setAttribute("open", "");
                }
            } catch (err) {
                if (testNtfyResultTitle) testNtfyResultTitle.textContent = "Delivery Error";
                if (testNtfyResultSubtitle) testNtfyResultSubtitle.textContent = "Network request failed";
                if (testNtfyResultIcon) {
                    testNtfyResultIcon.style.background = "#fee2e2";
                    testNtfyResultIcon.style.color = "#dc2626";
                    testNtfyResultIcon.innerHTML = `<svg class="ui-icon" aria-hidden="true"><use href="#icon-alert"></use></svg>`;
                }
                if (testNtfyResultBody) {
                    testNtfyResultBody.innerHTML = `
                        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 14px 16px; font-size: 13px; color: #991b1b;">
                            Error communicating with notification server: ${escapeHtml(err.message)}
                        </div>
                    `;
                }
                if (testNtfyOpenLink) testNtfyOpenLink.style.display = "none";
                if (testNtfyResultDialog && typeof testNtfyResultDialog.showModal === "function") {
                    testNtfyResultDialog.showModal();
                } else if (testNtfyResultDialog) {
                    testNtfyResultDialog.setAttribute("open", "");
                }
            } finally {
                testNtfyMaintButton.disabled = false;
                testNtfyMaintButton.innerHTML = originalHtml;
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

    // --- ADAPTIVE SYSTEM SETTINGS LOGIC ---
    function initAdaptiveSettings() {
        const adaptive = window.AerisVAdaptive || window.ShrimpGuardAdaptive;
        if (!adaptive) return;

        const model = adaptive.getModel();
        const persona = adaptive.getPersona();
        const device = adaptive.getDevice();

        const badgeEl = document.getElementById("adaptive-persona-badge");
        const descEl = document.getElementById("adaptive-persona-desc");
        const deviceTypeEl = document.getElementById("adaptive-device-type");
        const modalityEl = document.getElementById("adaptive-input-modality");

        const titles = {
            evaluating: "Evaluating Usage",
            field_inspector: "Real-time Telemetry Monitor",
            farm_planner: "Aquaculture Farm Planner",
            data_analyst: "Pond Data Analyst",
            balanced_operator: "Balanced Farm Operator"
        };

        const descs = {
            evaluating: "No interaction history recorded yet for this new account. Navigate across monitoring, calculators, and analytics to train your behavioral profile.",
            field_inspector: "High engagement with real-time pond telemetry and alarms. System prioritizes live sensor metrics and responsive telemetry views.",
            farm_planner: "High engagement with bio-mass formulas, feeding rates, liming, and molasses dosing. System prioritizes calculator toolbars and dosage recommendations.",
            data_analyst: "High engagement with 24-hour trends, historical logs, and data exports. System prioritizes dense information grids and multi-variable analytical views.",
            balanced_operator: "Even distribution of activity across monitoring, calculators, and system notifications."
        };

        if (badgeEl) {
            badgeEl.querySelector("span").textContent = titles[persona.persona_id] || "Evaluating...";
        }
        if (descEl) {
            descEl.textContent = descs[persona.persona_id] || descs.balanced_operator;
        }
        if (deviceTypeEl) {
            deviceTypeEl.textContent = device.is_mobile ? "Mobile Field Device" : (device.is_tablet ? "Tablet Hybrid" : "Desktop Workstation");
        }
        if (modalityEl) {
            modalityEl.textContent = device.is_touch ? "Touch Screen (Thumb-Zone Enabled)" : "Pointer / Mouse";
        }

        // Fill meters
        const percentages = persona.percentages || {};
        for (const [key, val] of Object.entries(percentages)) {
            const valEl = document.getElementById(`meter-val-${key}`);
            const barEl = document.getElementById(`meter-bar-${key}`);
            if (valEl) valEl.textContent = `${val}%`;
            if (barEl) barEl.style.width = `${val}%`;
        }

        // Preference controls
        const autoAdaptCheck = document.getElementById("adaptive-pref-autoadapt");
        const sunlightSelect = document.getElementById("adaptive-pref-sunlight");
        const densitySelect = document.getElementById("adaptive-pref-density");
        const dataSaverSelect = document.getElementById("adaptive-pref-datasaver");
        const resetBtn = document.getElementById("reset-adaptive-btn");

        const prefs = model.preferences || {};
        if (autoAdaptCheck) autoAdaptCheck.checked = prefs.auto_adapt !== false;
        if (sunlightSelect) sunlightSelect.value = prefs.sunlight_mode || "auto";
        if (densitySelect) densitySelect.value = prefs.density || "auto";
        if (dataSaverSelect) dataSaverSelect.value = prefs.data_saver || "auto";

        function showPresentationNotice(message) {
            let noticeBox = document.getElementById("presentation-notice-toast");
            if (!noticeBox) {
                noticeBox = document.createElement("div");
                noticeBox.id = "presentation-notice-toast";
                noticeBox.style.cssText = "position: fixed; top: 24px; right: 24px; z-index: 100000; background: #ecfdf5; color: #065f46; border: 1.5px solid #a7f3d0; border-left: 5px solid #10b981; padding: 13px 20px; border-radius: 10px; font-size: 13.5px; font-weight: 700; box-shadow: 0 8px 26px rgba(16, 185, 129, 0.18); display: flex; align-items: center; gap: 10px; transition: opacity 250ms ease, transform 250ms ease; opacity: 0; transform: translateY(-10px);";
                document.body.appendChild(noticeBox);
            }
            noticeBox.innerHTML = `
                <svg class="ui-icon" style="width:18px;height:18px;color:#059669;flex-shrink:0;"><use href="#icon-check-circle"></use></svg>
                <span>${message}</span>
            `;
            noticeBox.style.display = "flex";
            requestAnimationFrame(() => {
                noticeBox.style.opacity = "1";
                noticeBox.style.transform = "translateY(0)";
            });

            clearTimeout(noticeBox._timer);
            noticeBox._timer = setTimeout(() => {
                noticeBox.style.opacity = "0";
                noticeBox.style.transform = "translateY(-10px)";
                setTimeout(() => {
                    if (noticeBox.style.opacity === "0") {
                        noticeBox.style.display = "none";
                    }
                }, 300);
            }, 3500);
        }

        function savePrefs() {
            const adaptive = window.AerisVAdaptive || window.ShrimpGuardAdaptive;
            if (!adaptive || typeof adaptive.updatePreferences !== "function") return;
            adaptive.updatePreferences({
                auto_adapt: autoAdaptCheck ? autoAdaptCheck.checked : true,
                sunlight_mode: sunlightSelect ? sunlightSelect.value : "auto",
                density: densitySelect ? densitySelect.value : "auto",
                data_saver: dataSaverSelect ? dataSaverSelect.value : "auto"
            });
            if (typeof adaptive.applyAdaptations === "function") {
                adaptive.applyAdaptations();
            }
        }

        if (autoAdaptCheck) {
            autoAdaptCheck.addEventListener("change", () => {
                savePrefs();
                showPresentationNotice(`Automatic UI Adaptation ${autoAdaptCheck.checked ? "enabled" : "disabled"}.`);
            });
        }
        if (sunlightSelect) {
            sunlightSelect.addEventListener("change", () => {
                savePrefs();
                const txt = sunlightSelect.options[sunlightSelect.selectedIndex].text;
                showPresentationNotice(`Field Sunlight Mode set to: ${txt}`);
            });
        }
        if (densitySelect) {
            densitySelect.addEventListener("change", () => {
                savePrefs();
                const txt = densitySelect.options[densitySelect.selectedIndex].text;
                showPresentationNotice(`Layout Density set to: ${txt}`);
            });
        }
        if (dataSaverSelect) {
            dataSaverSelect.addEventListener("change", () => {
                savePrefs();
                const txt = dataSaverSelect.options[dataSaverSelect.selectedIndex].text;
                showPresentationNotice(`Network Data-Saver set to: ${txt}`);
            });
        }

        const resetAdaptiveDialog = document.getElementById("reset-adaptive-dialog");
        const cancelResetAdaptiveBtn = document.getElementById("cancel-reset-adaptive");
        const confirmResetAdaptiveBtn = document.getElementById("confirm-reset-adaptive");

        if (resetAdaptiveDialog) {
            resetAdaptiveDialog.addEventListener("click", (e) => {
                if (e.target === resetAdaptiveDialog) resetAdaptiveDialog.close();
            });
        }

        if (cancelResetAdaptiveBtn && resetAdaptiveDialog) {
            cancelResetAdaptiveBtn.addEventListener("click", () => {
                resetAdaptiveDialog.close();
            });
        }

        if (confirmResetAdaptiveBtn && resetAdaptiveDialog) {
            confirmResetAdaptiveBtn.addEventListener("click", () => {
                resetAdaptiveDialog.close();
                const adaptive = window.AerisVAdaptive || window.ShrimpGuardAdaptive;
                if (adaptive && typeof adaptive.resetModel === "function") {
                    adaptive.resetModel();
                }
                initAdaptiveSettings();
                showPresentationNotice("Learned profile and presentation reset to factory defaults.");
            });
        }

        if (resetBtn && resetAdaptiveDialog) {
            resetBtn.addEventListener("click", () => {
                if (typeof resetAdaptiveDialog.showModal === "function") {
                    resetAdaptiveDialog.showModal();
                } else {
                    resetAdaptiveDialog.setAttribute("open", "");
                }
            });
        }
    }

    function initAvatarManager() {
        const fileInput = document.getElementById("avatar-file-input");
        const changeBtn = document.getElementById("btn-change-avatar");
        const quickTrigger = document.getElementById("avatar-quick-trigger");
        const removeBtn = document.getElementById("btn-remove-avatar");
        const previewImg = document.getElementById("avatar-preview-img");
        const previewInitials = document.getElementById("avatar-preview-initials");
        const feedbackEl = document.getElementById("avatar-action-feedback");
        const headerImg = document.getElementById("header-avatar-img");
        const headerInitials = document.getElementById("header-avatar-initials");

        const removeDialog = document.getElementById("remove-avatar-dialog");
        const cancelRemoveBtn = document.getElementById("cancel-remove-avatar");
        const confirmRemoveBtn = document.getElementById("confirm-remove-avatar");

        const ALLOWED_EXTENSIONS = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"];
        const MAX_BYTES = 5 * 1024 * 1024; // 5MB

        function getCsrfToken() {
            const avatarForm = document.getElementById("avatar-upload-form");
            if (avatarForm) {
                const inp = avatarForm.querySelector('input[name="csrf_token"]');
                if (inp && inp.value) return inp.value;
            }
            const profileForm = document.getElementById("profile-update-form");
            if (profileForm) {
                const inp = profileForm.querySelector('input[name="csrf_token"]');
                if (inp && inp.value) return inp.value;
            }
            const anyInp = document.querySelector('input[name="csrf_token"]');
            return anyInp ? anyInp.value : "";
        }

        function showFeedback(msg, isSuccess = true) {
            if (!feedbackEl) return;
            feedbackEl.className = "settings-avatar-feedback " + (isSuccess ? "is-success" : "is-error");
            feedbackEl.textContent = msg;
            feedbackEl.style.display = "block";
            feedbackEl.style.opacity = "1";
            setTimeout(() => {
                feedbackEl.style.opacity = "0";
                setTimeout(() => {
                    feedbackEl.style.display = "none";
                    feedbackEl.style.opacity = "1";
                }, 300);
            }, 4500);
        }

        function triggerFileInput() {
            if (fileInput) fileInput.click();
        }

        if (changeBtn) changeBtn.addEventListener("click", triggerFileInput);
        if (quickTrigger) quickTrigger.addEventListener("click", triggerFileInput);

        if (fileInput) {
            fileInput.addEventListener("change", async () => {
                const file = fileInput.files && fileInput.files[0];
                if (!file) return;

                const fileType = (file.type || "").toLowerCase();
                const fileName = (file.name || "").toLowerCase();
                const isExtValid = ALLOWED_EXTENSIONS.includes(fileType) ||
                    /\.(jpe?g|png|webp|gif)$/i.test(fileName);

                if (!isExtValid) {
                    showFeedback("Unsupported file format. Please choose a JPG, PNG, GIF, or WebP image.", false);
                    fileInput.value = "";
                    return;
                }

                if (file.size > MAX_BYTES) {
                    showFeedback("File size exceeds 5MB. Please choose a smaller photo.", false);
                    fileInput.value = "";
                    return;
                }

                // Instant preview via FileReader
                const reader = new FileReader();
                reader.onload = (e) => {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = "block";
                    }
                    if (previewInitials) {
                        previewInitials.style.display = "none";
                    }
                };
                reader.readAsDataURL(file);

                // Set loading state
                const originalHtml = changeBtn ? changeBtn.innerHTML : "";
                if (changeBtn) {
                    changeBtn.disabled = true;
                    changeBtn.innerHTML = `
                        <svg class="ui-icon spin" aria-hidden="true" style="animation: spin 1s linear infinite;"><use href="#icon-clock"></use></svg>
                        <span>Uploading...</span>
                    `;
                }

                const csrfToken = getCsrfToken();
                const formData = new FormData();
                formData.append("avatar", file);
                formData.append("action", "avatar_upload");
                if (csrfToken) {
                    formData.append("csrf_token", csrfToken);
                }

                const headers = {};
                if (csrfToken) {
                    headers["X-CSRFToken"] = csrfToken;
                }

                let response;
                let usedFallback = false;

                try {
                    response = await fetch("/api/user/profile-picture", {
                        method: "POST",
                        headers: headers,
                        body: formData
                    });
                } catch (fetchErr) {
                    console.warn("Direct API upload fetch error, trying /settings fallback:", fetchErr);
                    // Fallback to /settings form endpoint
                    try {
                        response = await fetch("/settings", {
                            method: "POST",
                            body: formData
                        });
                        usedFallback = true;
                    } catch (fallbackErr) {
                        console.error("Upload fallback also failed:", fallbackErr);
                        showFeedback("Network error. Please verify your connection and try again.", false);
                        if (changeBtn) {
                            changeBtn.disabled = false;
                            changeBtn.innerHTML = originalHtml;
                        }
                        fileInput.value = "";
                        return;
                    }
                }

                if (response && response.status === 404 && !usedFallback) {
                    // Endpoint not found on running server, fallback to /settings
                    try {
                        response = await fetch("/settings", {
                            method: "POST",
                            body: formData
                        });
                        usedFallback = true;
                    } catch (fallbackErr) {
                        console.error("404 fallback failed:", fallbackErr);
                    }
                }

                if (usedFallback) {
                    if (response && response.ok) {
                        showFeedback("Profile picture updated successfully! Reloading...", true);
                        setTimeout(() => window.location.reload(), 1000);
                        return;
                    } else {
                        showFeedback("Upload could not be processed. Please try again.", false);
                        if (changeBtn) {
                            changeBtn.disabled = false;
                            changeBtn.innerHTML = originalHtml;
                        }
                        fileInput.value = "";
                        return;
                    }
                }

                let data;
                const contentType = (response && response.headers.get("content-type")) || "";
                if (contentType.includes("application/json")) {
                    try {
                        data = await response.json();
                    } catch (parseErr) {
                        console.error("JSON parse error:", parseErr);
                        data = { status: "error", message: `Server error (${response.status}).` };
                    }
                } else {
                    const textResp = await response.text();
                    console.warn("Server responded with non-JSON:", textResp.slice(0, 150));
                    data = { status: "error", message: response.ok ? "Upload completed." : `Server returned error (${response.status}).` };
                }

                if (response && response.ok && data.status === "success") {
                    const newUrl = data.avatar_url + "?t=" + Date.now();
                    if (previewImg) {
                        previewImg.src = newUrl;
                        previewImg.style.display = "block";
                    }
                    if (previewInitials) previewInitials.style.display = "none";
                    if (removeBtn) removeBtn.style.display = "inline-flex";

                    if (headerImg) {
                        headerImg.src = newUrl;
                        headerImg.style.display = "block";
                    }
                    if (headerInitials) headerInitials.style.display = "none";

                    showFeedback("Profile picture updated successfully!", true);
                } else {
                    showFeedback((data && (data.message || data.error)) || "Failed to upload profile picture.", false);
                }

                if (changeBtn) {
                    changeBtn.disabled = false;
                    changeBtn.innerHTML = originalHtml;
                }
                fileInput.value = "";
            });
        }

        // Remove Avatar Modal & Actions
        if (removeBtn && removeDialog) {
            removeBtn.addEventListener("click", () => {
                if (typeof removeDialog.showModal === "function") {
                    removeDialog.showModal();
                } else {
                    removeDialog.setAttribute("open", "");
                }
            });
        }

        if (cancelRemoveBtn && removeDialog) {
            cancelRemoveBtn.addEventListener("click", () => {
                removeDialog.close();
            });
        }

        if (removeDialog) {
            removeDialog.addEventListener("click", (e) => {
                if (e.target === removeDialog) removeDialog.close();
            });
        }

        if (confirmRemoveBtn) {
            confirmRemoveBtn.addEventListener("click", async () => {
                if (removeDialog) removeDialog.close();

                const originalRemoveHtml = removeBtn ? removeBtn.innerHTML : "";
                if (removeBtn) {
                    removeBtn.disabled = true;
                    removeBtn.innerHTML = `
                        <svg class="ui-icon spin" aria-hidden="true" style="animation: spin 1s linear infinite;"><use href="#icon-clock"></use></svg>
                        <span>Removing...</span>
                    `;
                }

                const csrfToken = getCsrfToken();
                const headers = {};
                if (csrfToken) {
                    headers["X-CSRFToken"] = csrfToken;
                }

                let response;
                let usedFallback = false;

                try {
                    response = await fetch("/api/user/profile-picture", {
                        method: "DELETE",
                        headers: {
                            ...headers,
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ csrf_token: csrfToken })
                    });
                } catch (fetchErr) {
                    console.warn("Direct delete API error, using /settings fallback:", fetchErr);
                    try {
                        const fd = new FormData();
                        fd.append("action", "avatar_remove");
                        if (csrfToken) fd.append("csrf_token", csrfToken);
                        response = await fetch("/settings", {
                            method: "POST",
                            body: fd
                        });
                        usedFallback = true;
                    } catch (fallbackErr) {
                        console.error("Delete fallback also failed:", fallbackErr);
                    }
                }

                if (response && response.status === 404 && !usedFallback) {
                    try {
                        const fd = new FormData();
                        fd.append("action", "avatar_remove");
                        if (csrfToken) fd.append("csrf_token", csrfToken);
                        response = await fetch("/settings", {
                            method: "POST",
                            body: fd
                        });
                        usedFallback = true;
                    } catch (fallbackErr) {
                        console.error("404 delete fallback failed:", fallbackErr);
                    }
                }

                if (usedFallback) {
                    if (response && response.ok) {
                        showFeedback("Profile picture removed. Reloading...", true);
                        setTimeout(() => window.location.reload(), 1000);
                        return;
                    } else {
                        showFeedback("Could not remove profile picture.", false);
                        if (removeBtn) {
                            removeBtn.disabled = false;
                            removeBtn.innerHTML = originalRemoveHtml;
                        }
                        return;
                    }
                }

                let data;
                const contentType = (response && response.headers.get("content-type")) || "";
                if (contentType.includes("application/json")) {
                    try {
                        data = await response.json();
                    } catch (parseErr) {
                        data = { status: "error", message: `Server error (${response.status}).` };
                    }
                } else {
                    data = { status: "error", message: response && response.ok ? "Removed." : "Server error." };
                }

                if (response && response.ok && data.status === "success") {
                    if (previewImg) {
                        previewImg.src = "";
                        previewImg.style.display = "none";
                    }
                    if (previewInitials) previewInitials.style.display = "flex";
                    if (removeBtn) removeBtn.style.display = "none";

                    if (headerImg) {
                        headerImg.src = "";
                        headerImg.style.display = "none";
                    }
                    if (headerInitials) headerInitials.style.display = "flex";

                    showFeedback("Profile picture removed successfully.", true);
                } else {
                    showFeedback((data && (data.message || data.error)) || "Could not remove profile picture.", false);
                }

                if (removeBtn) {
                    removeBtn.disabled = false;
                    removeBtn.innerHTML = originalRemoveHtml;
                }
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            initAdaptiveSettings();
            initAvatarManager();
        });
    } else {
        initAdaptiveSettings();
        initAvatarManager();
    }