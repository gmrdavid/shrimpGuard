(() => {
    "use strict";

    const get = (id) => document.getElementById(id);

    // Safely open a dialog.
    function openDialog(id) {
        const dialog = get(id);
        if (dialog && !dialog.open) {
            dialog.showModal();
        }
    }

    // Close buttons shared by all dialogs.
    document.querySelectorAll("[data-close-dialog]").forEach((button) => {
        button.addEventListener("click", () => {
            const dialog = get(button.dataset.closeDialog);
            if (dialog && dialog.open) {
                dialog.close();
            }
        });
    });

    // Close a dialog when the user clicks the backdrop.
    document.querySelectorAll("dialog").forEach((dialog) => {
        dialog.addEventListener("click", (event) => {
            if (event.target !== dialog) {
                return;
            }

            const rect = dialog.getBoundingClientRect();
            const inside =
                event.clientX >= rect.left &&
                event.clientX <= rect.right &&
                event.clientY >= rect.top &&
                event.clientY <= rect.bottom;

            if (!inside) {
                dialog.close();
            }
        });
    });

    // ADD USER
    const openAddBtn = get("open-add-user");
    if (openAddBtn) {
        openAddBtn.addEventListener("click", () => {
            openDialog("add-user-dialog");
        });
    }

    // VIEW USER
    const viewDialog = get("view-user-dialog");
    document.querySelectorAll(".admin-view-user").forEach((button) => {
        button.addEventListener("click", () => {
            if (!viewDialog) return;
            const name = button.dataset.name || "Unknown";
            const role = button.dataset.role || "-";
            const status = button.dataset.status || "-";

            const nameEl = get("view-user-name");
            if (nameEl) nameEl.textContent = name;
            const emailEl = get("view-user-email");
            if (emailEl) emailEl.textContent = button.dataset.email || "-";
            const lastLoginEl = get("view-user-last-login");
            if (lastLoginEl) lastLoginEl.textContent = button.dataset.lastLogin || "Never";

            const avatarEl = get("view-user-avatar");
            if (avatarEl) {
                avatarEl.textContent = name.trim().charAt(0).toUpperCase() || "?";
            }

            const roleElement = get("view-user-role");
            if (roleElement) {
                roleElement.textContent = role;
                roleElement.className = "detail-badge " + role.toLowerCase();
            }

            const statusElement = get("view-user-status");
            if (statusElement) {
                statusElement.textContent = status;
                statusElement.className = "detail-badge " + status.toLowerCase();
            }

            viewDialog.showModal();
        });
    });

    // EDIT USER
    const editDialog = get("edit-user-dialog");
    document.querySelectorAll(".admin-edit-user").forEach((button) => {
        button.addEventListener("click", () => {
            if (!editDialog) return;
            const curEmail = get("edit-user-current-email");
            if (curEmail) curEmail.value = button.dataset.email || "";

            const nameEl = get("edit-user-name");
            if (nameEl) nameEl.value = button.dataset.name || "";

            const emailEl = get("edit-user-email");
            if (emailEl) emailEl.value = button.dataset.email || "";

            const roleEl = get("edit-user-role");
            if (roleEl) roleEl.value = button.dataset.role || "Client";

            const statusEl = get("edit-user-status");
            if (statusEl) statusEl.value = button.dataset.status || "Active";

            const newPassEl = get("edit-user-new-password");
            if (newPassEl) newPassEl.value = "";

            editDialog.showModal();
        });
    });

    // DELETE USER
    const deleteDialog = get("delete-user-dialog");
    document.querySelectorAll(".admin-delete-user").forEach((button) => {
        button.addEventListener("click", () => {
            if (button.disabled || !deleteDialog) {
                return;
            }

            const delEmail = get("delete-user-email");
            if (delEmail) delEmail.value = button.dataset.email || "";

            const targetNameEl = get("delete-user-target-name");
            if (targetNameEl) {
                targetNameEl.textContent = `${button.dataset.name || "Unknown"} (${button.dataset.email || ""})`;
            }

            deleteDialog.showModal();
        });
    });

    // PASSWORD VISIBILITY TOGGLE
    document.querySelectorAll(".admin-pw-toggle-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.targetInput;
            const input = get(targetId);
            if (!input) return;

            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";

            const iconUse = btn.querySelector("use");
            if (iconUse) {
                iconUse.setAttribute("href", isPassword ? "#icon-eye-off" : "#icon-eye");
            }
            btn.setAttribute("title", isPassword ? "Hide password" : "Show password");
            btn.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
        });
    });

    // SEARCH AND FILTER
    const search = get("user-search");
    const roleFilter = get("user-role-filter");
    const statusFilter = get("user-status-filter");
    const rows = Array.from(document.querySelectorAll("[data-user-row]"));

    const emptyRow = get("user-filter-empty");
    const userCount = get("user-count");
    const noUsersRow = get("no-users-row");

    function filterUsers() {
        const query = search ? search.value.trim().toLowerCase() : "";
        let visibleCount = 0;

        rows.forEach((row) => {
            const name = (row.dataset.name || "").toLowerCase();
            const email = (row.dataset.email || "").toLowerCase();
            const role = (row.dataset.role || "").toLowerCase();
            const status = (row.dataset.status || "").toLowerCase();

            const matchesText =
                !query ||
                name.includes(query) ||
                email.includes(query) ||
                role.includes(query);

            const matchesRole =
                !roleFilter ||
                roleFilter.value === "all" ||
                role === roleFilter.value.toLowerCase();

            const matchesStatus =
                !statusFilter ||
                statusFilter.value === "all" ||
                status === statusFilter.value.toLowerCase();

            const visible = matchesText && matchesRole && matchesStatus;
            row.hidden = !visible;

            if (visible) {
                visibleCount++;
            }
        });

        if (emptyRow) {
            emptyRow.hidden = rows.length === 0 || visibleCount > 0;
        }

        if (noUsersRow) {
            noUsersRow.hidden = rows.length > 0;
        }

        if (userCount) {
            userCount.innerHTML = `<strong>${visibleCount}</strong> account${visibleCount === 1 ? "" : "s"}`;
        }
    }

    if (search) {
        search.addEventListener("input", filterUsers);
    }
    if (roleFilter) {
        roleFilter.addEventListener("change", filterUsers);
    }
    if (statusFilter) {
        statusFilter.addEventListener("change", filterUsers);
    }

    filterUsers();
})();
