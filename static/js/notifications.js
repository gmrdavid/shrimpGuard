let cachedNotifications = [];

function formatNotificationTime(isoString) {
    if (!isoString) return "-";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

async function renderNotifications() {
    const notificationContainer = document.getElementById("notification-content");

    if (!notificationContainer) {
        return;
    }

    notificationContainer.innerHTML = '<div class="notification-empty">Loading notifications from database...</div>';

    try {
        const response = await fetch("/api/alerts");
        if (!response.ok) {
            throw new Error(`Alerts API request failed with status ${response.status}.`);
        }
        const data = await response.json();
        const notifications = (data && data.recent_notifications) ? data.recent_notifications : [];
        cachedNotifications = notifications;

        if (notifications.length === 0) {
            notificationContainer.innerHTML = `
                <div class="notification-empty">
                    <svg class="ui-icon"><use href="#icon-check-circle"></use></svg> All pond water parameters are currently optimal according to the ML model. No active alerts.
                </div>
            `;
            return;
        }

        notificationContainer.innerHTML = `
            <ul class="notification-list">
                ${notifications.map((item) => `
                    <li class="notification-item ${(item.severity || "").toLowerCase()}">
                        <div class="notification-meta">
                            <span class="notification-severity ${item.severity === "Critical" ? "severity-critical" : "severity-warning"}">${item.severity}</span>
                            <small>${formatNotificationTime(item.recorded_at)}</small>
                        </div>
                        <h3>${item.title}</h3>
                        <p>${item.message}</p>
                        <p style="margin-top: 6px; font-size: 11px; color: #537260;"><strong>Dispatch:</strong> ${item.notification}</p>
                    </li>
                `).join("")}
            </ul>
        `;
    } catch (error) {
        console.error("Unable to load sensor notifications:", error);
        notificationContainer.innerHTML = '<div class="notification-empty">Unable to load notifications from database. Please retry.</div>';
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
    createNotificationModal();
    setupNotificationModal();
}

initializeNotifications();
