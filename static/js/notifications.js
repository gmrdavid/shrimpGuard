let cachedNotifications = [];
let lastUnreadCount = 0;

function formatNotificationTime(isoString) {
    if (!isoString) return "-";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function ensureBadgeElement() {
    const button = document.getElementById("notification-button");
    if (!button) return null;

    let badge = document.getElementById("notification-badge");
    if (!badge) {
        badge = document.createElement("span");
        badge.id = "notification-badge";
        badge.className = "notification-badge";
        badge.style.display = "none";
        badge.setAttribute("aria-hidden", "true");
        button.appendChild(badge);
    }
    return badge;
}

function updateNotificationBadge(unreadCount) {
    const badge = ensureBadgeElement();
    const button = document.getElementById("notification-button");
    lastUnreadCount = Number(unreadCount) || 0;

    if (badge) {
        if (lastUnreadCount > 0) {
            badge.textContent = lastUnreadCount > 9 ? "9+" : String(lastUnreadCount);
            badge.style.display = "inline-flex";
            if (button) {
                button.setAttribute("title", `${lastUnreadCount} unread notification(s)`);
                button.setAttribute("aria-label", `View notifications (${lastUnreadCount} unread)`);
            }
        } else {
            badge.style.display = "none";
            if (button) {
                button.setAttribute("title", "View notifications");
                button.setAttribute("aria-label", "View notifications");
            }
        }
    }

    const unreadCountEl = document.getElementById("unread-notifications-count");
    if (unreadCountEl) {
        unreadCountEl.textContent = String(lastUnreadCount);
    }
}

async function markAllNotificationsRead() {
    try {
        const response = await fetch("/api/alerts/mark-read", { method: "POST" });
        if (response.ok) {
            updateNotificationBadge(0);
            if (Array.isArray(cachedNotifications)) {
                cachedNotifications.forEach((n) => { n.is_read = true; });
            }
            const modalContent = document.getElementById("notification-content");
            if (modalContent) {
                renderNotificationsList(cachedNotifications, 0);
            }
            window.dispatchEvent(new Event("shrimpguard:notification-update"));
        }
    } catch (err) {
        console.error("Unable to mark notifications as read:", err);
    }
}

function renderNotificationsList(notifications, unreadCount) {
    const notificationContainer = document.getElementById("notification-content");
    if (!notificationContainer) return;

    const isAdminPage = window.location.pathname.startsWith("/admin");
    const alertsHref = isAdminPage ? "/admin/telemetry" : "/alerts";
    const alertsLabel = isAdminPage ? "View IoT & Telemetry Control &rarr;" : "View all alerts & history &rarr;";

    if (!Array.isArray(notifications) || notifications.length === 0) {
        notificationContainer.innerHTML = `
            <div class="notification-empty" style="padding: 28px 20px; text-align: center; color: #537260;">
                <svg class="ui-icon" style="width: 32px; height: 32px; margin-bottom: 8px; fill: #16a34a;"><use href="#icon-check-circle"></use></svg>
                <div style="font-weight: 700; font-size: 13px; color: #1e3a2b; margin-bottom: 4px;">Pond Parameters Optimal</div>
                <div style="font-size: 12px; color: #6a7c72;">All water parameters meet recommended standards for Penaeus vannamei.</div>
            </div>
            <div style="padding: 10px 16px; border-top: 1px solid #eef2f0; background: #fafcfb; text-align: center;">
                <a href="${alertsHref}" style="color: #16a34a; font-size: 12px; font-weight: 700; text-decoration: none;">${alertsLabel}</a>
            </div>
        `;
        return;
    }

    const countHeader = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: #fbfdfc; border-bottom: 1px solid #eef2f0;">
            <span style="font-size: 11px; font-weight: 750; color: #537260; text-transform: uppercase; letter-spacing: 0.5px;">
                ${unreadCount > 0 ? `${unreadCount} UNREAD NOTIFICATION${unreadCount > 1 ? "S" : ""}` : "ALL NOTIFICATIONS READ"}
            </span>
            ${unreadCount > 0 ? '<button id="modal-mark-read-btn" class="modal-mark-read-btn" type="button">Mark all read</button>' : ''}
        </div>
    `;

    const itemsHtml = notifications.map((item) => {
        const sev = (item.severity || "optimal").toLowerCase();
        const sevClass = sev === "critical" ? "severity-critical" : sev === "warning" ? "severity-warning" : "severity-optimal";
        const isUnread = !item.is_read;

        return `
            <li class="notification-item ${sev} ${isUnread ? "notification-item-unread" : ""}">
                <div class="notification-meta" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span class="notification-severity ${sevClass}">${item.severity || "Optimal"}</span>
                        ${isUnread ? '<span class="notification-badge-new">NEW</span>' : ''}
                    </div>
                    <small style="color: #6a7c72; font-size: 11px;">${formatNotificationTime(item.recorded_at)}</small>
                </div>
                <h3 style="margin: 0 0 4px 0; font-size: 13px; font-weight: 700; color: #1e3a2b;">${item.title}</h3>
                <p style="margin: 0; font-size: 12px; color: #3d5649; line-height: 1.45;">${item.message}</p>
                ${item.notification ? `<p style="margin-top: 6px; font-size: 11px; color: #537260;"><strong>Dispatch:</strong> ${item.notification}</p>` : ''}
            </li>
        `;
    }).join("");

    notificationContainer.innerHTML = `
        ${countHeader}
        <ul class="notification-list" style="margin: 0; padding: 0; list-style: none; max-height: calc(100vh - 220px); overflow-y: auto;">
            ${itemsHtml}
        </ul>
        <div style="padding: 10px 16px; border-top: 1px solid #eef2f0; background: #fafcfb; text-align: center;">
            <a href="${alertsHref}" style="color: #16a34a; font-size: 12px; font-weight: 700; text-decoration: none;">${alertsLabel}</a>
        </div>
    `;

    const markBtn = document.getElementById("modal-mark-read-btn");
    if (markBtn) {
        markBtn.addEventListener("click", async (e) => {
            e.stopPropagation();
            await markAllNotificationsRead();
        });
    }
}

async function renderNotifications() {
    const notificationContainer = document.getElementById("notification-content");
    if (!notificationContainer) return;

    notificationContainer.innerHTML = '<div class="notification-empty" style="padding: 24px; text-align: center; color: #6a7c72;">Loading notifications from database...</div>';

    try {
        const response = await fetch("/api/alerts");
        if (!response.ok) {
            throw new Error(`Alerts API request failed with status ${response.status}.`);
        }
        const data = await response.json();
        const notifications = (data && data.recent_notifications) ? data.recent_notifications : [];
        const unread = (data && data.summary && typeof data.summary.unread_notifications === "number")
            ? data.summary.unread_notifications
            : (notifications.filter(n => !n.is_read).length);

        cachedNotifications = notifications;
        updateNotificationBadge(unread);
        renderNotificationsList(notifications, unread);
    } catch (error) {
        console.error("Unable to load sensor notifications:", error);
        notificationContainer.innerHTML = '<div class="notification-empty" style="padding: 24px; text-align: center; color: #c53d48;">Unable to connect to alerts gateway. Please retry.</div>';
    }
}

async function pollNotificationBadge() {
    try {
        const response = await fetch("/api/alerts");
        if (!response.ok) return;
        const data = await response.json();
        if (data && data.summary) {
            const unread = Number(data.summary.unread_notifications) || 0;
            updateNotificationBadge(unread);

            const backdrop = document.getElementById("notification-modal-backdrop");
            if (backdrop && backdrop.classList.contains("visible")) {
                cachedNotifications = data.recent_notifications || [];
                renderNotificationsList(cachedNotifications, unread);
            }
        }
    } catch (err) {
        // Silent failure on background polling to avoid disturbing active user sessions
    }
}

function setupNotificationModal() {
    const button = document.getElementById("notification-button");
    const backdrop = document.getElementById("notification-modal-backdrop");
    const closeButton = document.getElementById("notification-modal-close");

    if (!button || !backdrop || !closeButton) {
        return;
    }

    button.setAttribute("aria-controls", backdrop.id);
    button.setAttribute("aria-expanded", "false");

    const closeNotifications = () => {
        backdrop.classList.remove("visible");
        button.setAttribute("aria-expanded", "false");
    };

    button.addEventListener("click", async () => {
        if (backdrop.classList.contains("visible")) {
            closeNotifications();
            return;
        }

        backdrop.classList.add("visible");
        button.setAttribute("aria-expanded", "true");
        await renderNotifications();
    });

    closeButton.addEventListener("click", () => {
        closeNotifications();
    });

    document.addEventListener("click", (event) => {
        if (!backdrop.contains(event.target) && !button.contains(event.target)) {
            closeNotifications();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && backdrop.classList.contains("visible")) {
            closeNotifications();
            button.focus();
        }
    });
}

function createNotificationModal() {
    if (document.getElementById("notification-modal-backdrop")) {
        return;
    }

    const modal = document.createElement("div");
    modal.className = "notification-modal-backdrop";
    modal.id = "notification-modal-backdrop";
    modal.innerHTML = `
        <div class="notification-modal" role="dialog" aria-labelledby="notification-modal-title">
            <div class="notification-header">
                <h2 id="notification-modal-title">Notifications</h2>
                <button id="notification-modal-close" class="notification-close" type="button" aria-label="Close notifications"><svg class="ui-icon"><use href="#icon-x"></use></svg></button>
            </div>
            <div id="notification-content" class="notification-content"></div>
        </div>
    `;

    document.body.appendChild(modal);
}

function initializeNotifications() {
    ensureBadgeElement();
    createNotificationModal();
    setupNotificationModal();
    pollNotificationBadge();
    setInterval(pollNotificationBadge, 8000);
    window.addEventListener("shrimpguard:notification-update", pollNotificationBadge);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeNotifications);
} else {
    initializeNotifications();
}
