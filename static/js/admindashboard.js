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
    get("open-add-user").addEventListener("click", () => {
        openDialog("add-user-dialog");
    });

    // VIEW USER
    const viewDialog = get("view-user-dialog");

    document.querySelectorAll(".admin-view-user").forEach((button) => {
        button.addEventListener("click", () => {
            const name = button.dataset.name || "Unknown";
            const role = button.dataset.role || "-";
            const status = button.dataset.status || "-";

            get("view-user-name").textContent = name;
            get("view-user-email").textContent = button.dataset.email || "-";
            get("view-user-last-login").textContent =
                button.dataset.lastLogin || "Never";

            get("view-user-avatar").textContent =
                name.trim().charAt(0).toUpperCase() || "?";

            const roleElement = get("view-user-role");
            roleElement.textContent = role;
            roleElement.className =
                "detail-badge " + role.toLowerCase();

            const statusElement = get("view-user-status");
            statusElement.textContent = status;
            statusElement.className =
                "detail-badge " + status.toLowerCase();

            viewDialog.showModal();
        });
    });

    // EDIT USER
    const editDialog = get("edit-user-dialog");
    const editForm = get("edit-user-form");

    document.querySelectorAll(".admin-edit-user").forEach((button) => {
        button.addEventListener("click", () => {
            get("edit-user-current-email").value =
                button.dataset.email || "";

            get("edit-user-name").value =
                button.dataset.name || "";

            get("edit-user-email").value =
                button.dataset.email || "";

            get("edit-user-role").value =
                button.dataset.role || "Client";

            get("edit-user-status").value =
                button.dataset.status || "Active";

            editDialog.showModal();
        });
    });

    // DELETE USER
    const deleteDialog = get("delete-user-dialog");

    document.querySelectorAll(".admin-delete-user").forEach((button) => {
        button.addEventListener("click", () => {
            if (button.disabled) {
                return;
            }

            get("delete-user-email").value =
                button.dataset.email || "";

            get("delete-user-target-name").textContent =
                `${button.dataset.name || "Unknown"} (${button.dataset.email || ""})`;

            deleteDialog.showModal();
        });
    });

    // SEARCH AND FILTER
    const search = get("user-search");
    const roleFilter = get("user-role-filter");
    const statusFilter = get("user-status-filter");
    const rows = Array.from(
        document.querySelectorAll("[data-user-row]")
    );

    const emptyRow = get("user-filter-empty");
    const userCount = get("user-count");
    const noUsersRow = get("no-users-row");

    function filterUsers() {
        const query = search ? search.value.trim().toLowerCase() : "";
        let visibleCount = 0;

        rows.forEach((row) => {
            const name = row.dataset.name || "";
            const email = row.dataset.email || "";
            const role = row.dataset.role || "";
            const status = row.dataset.status || "";

            const matchesText =
                name.includes(query) ||
                email.includes(query) ||
                role.includes(query);

            const matchesRole =
                !roleFilter ||
                roleFilter.value === "all" ||
                role === roleFilter.value;

            const matchesStatus =
                !statusFilter ||
                statusFilter.value === "all" ||
                status === statusFilter.value;

            const visible =
                matchesText && matchesRole && matchesStatus;

            row.hidden = !visible;

            if (visible) {
                visibleCount++;
            }
        });

        if (emptyRow) {
            emptyRow.hidden =
                rows.length === 0 || visibleCount > 0;
        }

        if (noUsersRow) {
            noUsersRow.hidden = rows.length > 0;
        }

        if (userCount) {
            userCount.innerHTML =
                `<strong>${visibleCount}</strong> account${visibleCount === 1 ? "" : "s"}`;
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