/**
 * AERIS-V Admin Settings JavaScript
 * Handles local clock, asynchronous profile avatar updates, password toggles,
 * ntfy push topic generation, test notifications, and live system diagnostics.
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

    // 4. Admin Avatar Management (Async Upload)
    const fileInput = document.getElementById("admin-avatar-file-input");
    const changeBtn = document.getElementById("btn-admin-change-avatar");
    const avatarDisplay = document.getElementById("admin-avatar-display");

    if (changeBtn && fileInput) {
        changeBtn.addEventListener("click", () => {
            fileInput.click();
        });

        fileInput.addEventListener("change", async () => {
            const file = fileInput.files[0];
            if (!file) return;

            const validTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
            if (!validTypes.includes(file.type)) {
                alert("Please select a JPG, PNG, WebP, or GIF image.");
                fileInput.value = "";
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                alert("Image exceeds the 5MB size limit.");
                fileInput.value = "";
                return;
            }

            const origContent = changeBtn.innerHTML;
            changeBtn.disabled = true;
            changeBtn.innerHTML = `<span>Uploading...</span>`;

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
                    let previewImg = document.getElementById("admin-avatar-preview-img");
                    const previewInitials = document.getElementById("admin-avatar-preview-initials");

                    if (!previewImg && avatarDisplay) {
                        previewImg = document.createElement("img");
                        previewImg.id = "admin-avatar-preview-img";
                        avatarDisplay.appendChild(previewImg);
                    }

                    if (previewImg) {
                        previewImg.src = newUrl;
                        previewImg.style.display = "block";
                    }
                    if (previewInitials) {
                        previewInitials.style.display = "none";
                    }
                } else {
                    alert(data.message || "Failed to update profile picture.");
                }
            } catch (err) {
                console.error("Avatar upload error:", err);
                alert("Network error while uploading photo. Please try again.");
            } finally {
                changeBtn.disabled = false;
                changeBtn.innerHTML = origContent;
                fileInput.value = "";
            }
        });
    }

    // 5. Generate Secure Topic Handler
    const genTopicBtn = document.getElementById("admin-generate-topic-btn");
    const ntfyTopicInput = document.getElementById("admin-ntfy-topic");

    if (genTopicBtn && ntfyTopicInput) {
        genTopicBtn.addEventListener("click", async () => {
            const origContent = genTopicBtn.innerHTML;
            genTopicBtn.disabled = true;
            genTopicBtn.innerHTML = `<span>Generating...</span>`;

            try {
                const resp = await fetch("/api/ntfy/generate-topic");
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.topic) {
                        ntfyTopicInput.value = data.topic;
                    }
                } else {
                    const randomHex = Array.from(crypto.getRandomValues(new Uint8Array(6)))
                        .map(b => b.toString(16).padStart(2, '0'))
                        .join('');
                    ntfyTopicInput.value = "sg-pond-" + randomHex;
                }
            } catch (e) {
                const randomHex = Array.from(crypto.getRandomValues(new Uint8Array(6)))
                    .map(b => b.toString(16).padStart(2, '0'))
                    .join('');
                ntfyTopicInput.value = "sg-pond-" + randomHex;
            } finally {
                genTopicBtn.disabled = false;
                genTopicBtn.innerHTML = origContent;
                ntfyTopicInput.focus();
            }
        });
    }

    // 6. Test Push Notification Handler
    const testPushBtn = document.getElementById("admin-test-ntfy-btn");
    if (testPushBtn && ntfyTopicInput) {
        testPushBtn.addEventListener("click", async () => {
            const topic = ntfyTopicInput.value.trim();
            if (!topic) {
                alert("Please enter or generate a push notification topic first.");
                ntfyTopicInput.focus();
                return;
            }

            const origContent = testPushBtn.innerHTML;
            testPushBtn.disabled = true;
            testPushBtn.innerHTML = `<span>Sending...</span>`;

            try {
                const resp = await fetch("/api/ntfy/test", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify({ ntfy_topic: topic }),
                });

                const data = await resp.json();
                if (resp.ok && !data.error) {
                    testPushBtn.innerHTML = `<span>✓ Sent!</span>`;
                    setTimeout(() => {
                        testPushBtn.innerHTML = origContent;
                        testPushBtn.disabled = false;
                    }, 3000);
                } else {
                    alert(data.error || "Failed to dispatch test notification. Please verify your topic.");
                    testPushBtn.disabled = false;
                    testPushBtn.innerHTML = origContent;
                }
            } catch (err) {
                alert("Network error dispatching test push notification.");
                testPushBtn.disabled = false;
                testPushBtn.innerHTML = origContent;
            }
        });
    }

    // 7. Dynamic System Diagnostics Polling (Every 30 seconds)
    async function refreshDiagnostics() {
        try {
            await fetch("/api/admin/system-status");
        } catch (e) {
            // Silently continue
        }
    }
    setInterval(refreshDiagnostics, 30000);
});
