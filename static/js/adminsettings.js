/**
 * AERIS-V Admin Settings JavaScript
 * Handles local clock, asynchronous profile avatar updates, security toggles,
 * ntfy push notification testing, and live system diagnostics.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Live Local Clock
    function updateClock() {
        const timeEl = document.getElementById("time");
        if (timeEl) {
            timeEl.textContent = new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            });
        }
    }
    updateClock();
    setInterval(updateClock, 1000);

    // 2. CSRF Token Helper
    function getCsrfToken() {
        const tokenInput = document.querySelector('input[name="csrf_token"]');
        return tokenInput ? tokenInput.value : "";
    }

    // 3. Password Show/Hide Toggle
    const eyeButtons = document.querySelectorAll(".pwd-eye-btn");
    eyeButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) return;

            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";

            const showIcon = btn.querySelector(".eye-show");
            const hideIcon = btn.querySelector(".eye-hide");
            if (showIcon && hideIcon) {
                showIcon.style.display = isPassword ? "none" : "block";
                hideIcon.style.display = isPassword ? "block" : "none";
            }
        });
    });

    // 4. Admin Avatar Management (Async Upload & Remove)
    const fileInput = document.getElementById("admin-avatar-file-input");
    const changeBtn = document.getElementById("btn-admin-change-avatar");
    const removeBtn = document.getElementById("btn-admin-remove-avatar");
    const previewImg = document.getElementById("admin-avatar-preview-img");
    const previewInitials = document.getElementById("admin-avatar-preview-initials");
    const feedbackEl = document.getElementById("admin-avatar-feedback");
    const removeDialog = document.getElementById("admin-remove-avatar-dialog");
    const cancelRemoveBtn = document.getElementById("cancel-admin-remove-avatar");
    const confirmRemoveBtn = document.getElementById("confirm-admin-remove-avatar");

    function setAvatarFeedback(msg, isSuccess) {
        if (!feedbackEl) return;
        feedbackEl.className = "admin-avatar-feedback " + (isSuccess ? "is-success" : "is-error");
        feedbackEl.textContent = msg;
        setTimeout(() => {
            if (feedbackEl) {
                feedbackEl.textContent = "";
                feedbackEl.className = "admin-avatar-feedback";
            }
        }, 6000);
    }

    if (changeBtn && fileInput) {
        changeBtn.addEventListener("click", () => {
            fileInput.click();
        });

        fileInput.addEventListener("change", async () => {
            const file = fileInput.files[0];
            if (!file) return;

            // Validate format
            const validTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
            if (!validTypes.includes(file.type)) {
                setAvatarFeedback("Please select a JPG, PNG, WebP, or GIF image.", false);
                fileInput.value = "";
                return;
            }

            // Validate size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                setAvatarFeedback("Image exceeds the 5MB size limit.", false);
                fileInput.value = "";
                return;
            }

            changeBtn.disabled = true;
            changeBtn.innerHTML = `
                <svg class="ui-icon spin" aria-hidden="true"><use href="#icon-activity"></use></svg>
                <span>Uploading...</span>
            `;

            const formData = new FormData();
            formData.append("avatar", file);
            formData.append("action", "avatar_upload");
            const csrfToken = getCsrfToken();
            if (csrfToken) formData.append("csrf_token", csrfToken);

            try {
                const response = await fetch("/api/user/profile-picture", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                    body: formData,
                });

                const data = await response.json();
                if (response.ok && data.status === "success") {
                    const newUrl = data.avatar_url + "?t=" + Date.now();
                    if (previewImg) {
                        previewImg.src = newUrl;
                        previewImg.style.display = "block";
                    }
                    if (previewInitials) {
                        previewInitials.style.display = "none";
                    }
                    if (removeBtn) {
                        removeBtn.style.display = "inline-flex";
                    }
                    setAvatarFeedback("Profile picture updated successfully.", true);
                } else {
                    setAvatarFeedback(data.message || "Failed to update profile picture.", false);
                }
            } catch (err) {
                setAvatarFeedback("Network error. Please try uploading again.", false);
            } finally {
                fileInput.value = "";
                changeBtn.disabled = false;
                changeBtn.innerHTML = `
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-edit"></use></svg>
                    <span>Change Profile Picture</span>
                `;
            }
        });
    }

    if (removeBtn && removeDialog) {
        removeBtn.addEventListener("click", () => {
            if (typeof removeDialog.showModal === "function") {
                removeDialog.showModal();
            } else {
                removeDialog.setAttribute("open", "");
            }
        });

        if (cancelRemoveBtn) {
            cancelRemoveBtn.addEventListener("click", () => {
                if (typeof removeDialog.close === "function") {
                    removeDialog.close();
                } else {
                    removeDialog.removeAttribute("open");
                }
            });
        }

        if (confirmRemoveBtn) {
            confirmRemoveBtn.addEventListener("click", async () => {
                confirmRemoveBtn.disabled = true;
                confirmRemoveBtn.textContent = "Removing...";

                const csrfToken = getCsrfToken();
                try {
                    const response = await fetch("/api/user/profile-picture", {
                        method: "DELETE",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                        },
                        body: JSON.stringify({ csrf_token: csrfToken }),
                    });

                    const data = await response.json();
                    if (response.ok && data.status === "success") {
                        if (previewImg) {
                            previewImg.src = "";
                            previewImg.style.display = "none";
                        }
                        if (previewInitials) {
                            previewInitials.style.display = "flex";
                        }
                        removeBtn.style.display = "none";
                        setAvatarFeedback("Profile picture removed.", true);
                    } else {
                        setAvatarFeedback(data.message || "Could not remove profile picture.", false);
                    }
                } catch (err) {
                    setAvatarFeedback("Network error. Please try again.", false);
                } finally {
                    confirmRemoveBtn.disabled = false;
                    confirmRemoveBtn.textContent = "Remove Photo";
                    if (typeof removeDialog.close === "function") {
                        removeDialog.close();
                    } else {
                        removeDialog.removeAttribute("open");
                    }
                }
            });
        }
    }

    // 5. Generate Secure ntfy Topic Helper
    const generateTopicBtn = document.getElementById("admin-generate-topic-btn");
    const ntfyTopicInput = document.getElementById("admin-ntfy-topic");

    if (generateTopicBtn && ntfyTopicInput) {
        generateTopicBtn.addEventListener("click", () => {
            const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
            let randStr = "";
            for (let i = 0; i < 8; i++) {
                randStr += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            ntfyTopicInput.value = `aeris-admin-${randStr}`;
            ntfyTopicInput.focus();

            const origContent = generateTopicBtn.innerHTML;
            generateTopicBtn.innerHTML = `
                <svg class="ui-icon" aria-hidden="true"><use href="#icon-check"></use></svg>
                <span>Generated!</span>
            `;
            setTimeout(() => {
                generateTopicBtn.innerHTML = origContent;
            }, 1400);
        });
    }

    // 6. Test ntfy Push Notification
    const testNtfyBtn = document.getElementById("admin-test-ntfy-btn");
    const testNtfyDialog = document.getElementById("admin-test-ntfy-dialog");
    const testNtfyBody = document.getElementById("admin-test-ntfy-body");
    const closeTestNtfyBtn = document.getElementById("close-admin-test-ntfy");

    if (closeTestNtfyBtn && testNtfyDialog) {
        closeTestNtfyBtn.addEventListener("click", () => {
            if (typeof testNtfyDialog.close === "function") {
                testNtfyDialog.close();
            } else {
                testNtfyDialog.removeAttribute("open");
            }
        });
    }

    if (testNtfyBtn && ntfyTopicInput && testNtfyDialog) {
        testNtfyBtn.addEventListener("click", async () => {
            const topic = ntfyTopicInput.value.trim();
            if (!topic) {
                alert("Please enter or generate a push notification topic first.");
                ntfyTopicInput.focus();
                return;
            }

            testNtfyBtn.disabled = true;
            testNtfyBtn.innerHTML = `
                <svg class="ui-icon spin" aria-hidden="true"><use href="#icon-activity"></use></svg>
                <span>Dispatching...</span>
            `;

            try {
                const response = await fetch("/api/ntfy/test", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ntfy_topic: topic }),
                });

                const data = await response.json();
                if (typeof testNtfyDialog.showModal === "function") {
                    testNtfyDialog.showModal();
                } else {
                    testNtfyDialog.setAttribute("open", "");
                }

                if (response.ok && data.success) {
                    testNtfyBody.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <span class="status-indicator-dot dot-optimal" style="width: 14px; height: 14px;"></span>
                            <strong style="color: #126b4f; font-size: 16px;">Test Notification Dispatched!</strong>
                        </div>
                        <p style="color: #405468; line-height: 1.5;">
                            A test alert was sent to topic <code style="background: #eef2f5; padding: 2px 6px; border-radius: 4px;">${topic}</code> via the ntfy.sh gateway.
                        </p>
                        <p style="margin-top: 8px; font-size: 13px; color: #718184;">
                            Open your ntfy app or visit <a href="https://ntfy.sh/${topic}" target="_blank" rel="noopener noreferrer" style="color: #1769d2; text-decoration: underline;">ntfy.sh/${topic}</a> to confirm receipt.
                        </p>
                    `;
                } else {
                    testNtfyBody.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <span class="status-indicator-dot dot-critical" style="width: 14px; height: 14px;"></span>
                            <strong style="color: #dc2626; font-size: 16px;">Dispatch Notice</strong>
                        </div>
                        <p style="color: #405468; line-height: 1.5;">
                            ${data.error || "Unable to contact ntfy gateway. Please verify network access."}
                        </p>
                    `;
                }
            } catch (err) {
                if (typeof testNtfyDialog.showModal === "function") {
                    testNtfyDialog.showModal();
                } else {
                    testNtfyDialog.setAttribute("open", "");
                }
                testNtfyBody.innerHTML = `
                    <p style="color: #dc2626;">Network error communicating with the notification endpoint.</p>
                `;
            } finally {
                testNtfyBtn.disabled = false;
                testNtfyBtn.innerHTML = `
                    <svg class="ui-icon" aria-hidden="true"><use href="#icon-bell"></use></svg>
                    <span>Test Push</span>
                `;
            }
        });
    }

    // 7. Notification Channels Tab Switcher
    const notifTabs = document.querySelectorAll(".notif-channel-tab");
    notifTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            notifTabs.forEach((t) => {
                t.classList.remove("active");
                t.setAttribute("aria-selected", "false");
            });
            tab.classList.add("active");
            tab.setAttribute("aria-selected", "true");
        });
    });

    // 8. Dynamic Status Diagnostic Polling (Every 30 seconds)
    async function refreshDiagnostics() {
        try {
            const resp = await fetch("/api/admin/system-status");
            if (!resp.ok) return;
            const res = await resp.json();
            if (res.status === "success" && res.diagnostics) {
                const diag = res.diagnostics;
                // Live update LoRa status row if elements exist
                const loraRow = document.querySelector(".system-status-card .status-diag-row:nth-child(4)");
                if (loraRow) {
                    const dot = loraRow.querySelector(".status-indicator-dot");
                    const badge = loraRow.querySelector(".status-diag-badge");
                    if (dot && badge) {
                        dot.className = `status-indicator-dot ${diag.lora.online ? "dot-optimal" : "dot-standby"}`;
                        badge.className = `status-diag-badge ${diag.lora.online ? "badge-optimal" : "badge-standby"}`;
                        badge.textContent = diag.lora.text;
                    }
                }
            }
        } catch (e) {
            // Background polling failure, silent fallback
        }
    }
    setInterval(refreshDiagnostics, 30000);
});
