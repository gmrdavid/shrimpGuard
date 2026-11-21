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
    const newPwInput = get("new-user-password");
    const newPwHint = get("new-user-pw-hint");

    if (openAddBtn) {
        openAddBtn.addEventListener("click", () => {
            openDialog("add-user-dialog");
            const nameInput = get("new-user-name");
            if (nameInput) {
                setTimeout(() => nameInput.focus(), 80);
            }
        });
    }

    if (newPwInput && newPwHint) {
        const hintText = newPwHint.querySelector("span");
        newPwInput.addEventListener("input", () => {
            const len = newPwInput.value.length;
            if (len >= 8) {
                newPwHint.classList.add("valid");
                if (hintText) hintText.textContent = `Valid (${len} chars)`;
            } else if (len > 0) {
                newPwHint.classList.remove("valid");
                if (hintText) hintText.textContent = `${len}/8 chars (min. 8)`;
            } else {
                newPwHint.classList.remove("valid");
                if (hintText) hintText.textContent = "Min. 8 characters";
            }
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
            const avatarUrl = button.dataset.avatar || "";
            if (avatarEl) {
                if (avatarUrl) {
                    avatarEl.innerHTML = `<img src="${avatarUrl}" alt="${name}" class="view-user-avatar-img">`;
                } else {
                    avatarEl.textContent = name.trim().charAt(0).toUpperCase() || "?";
                }
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

            const exportBtn = get("view-user-export-btn");
            if (exportBtn) {
                const email = button.dataset.email || "";
                exportBtn.href = `/admin/logs/export?user=${encodeURIComponent(email)}`;
                exportBtn.title = `Export audit logs for ${email}`;
            }

            viewDialog.showModal();
        });
    });

    // EDIT USER
    const editDialog = get("edit-user-dialog");
    const editPwInput = get("edit-user-new-password");
    const editPwHint = get("edit-user-pw-hint");

    if (editPwInput && editPwHint) {
        const editHintText = editPwHint.querySelector("span");
        editPwInput.addEventListener("input", () => {
            const len = editPwInput.value.length;
            if (len >= 8) {
                editPwHint.classList.add("valid");
                if (editHintText) editHintText.textContent = `Valid (${len} chars)`;
            } else if (len > 0) {
                editPwHint.classList.remove("valid");
                if (editHintText) editHintText.textContent = `${len}/8 chars (min. 8)`;
            } else {
                editPwHint.classList.remove("valid");
                if (editHintText) editHintText.textContent = "Leave blank to keep unchanged";
            }
        });
    }

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
            if (roleEl) {
                roleEl.value = button.dataset.role || "Client";
                roleEl.dispatchEvent(new Event("change", { bubbles: true }));
            }

            const statusEl = get("edit-user-status");
            if (statusEl) {
                statusEl.value = button.dataset.status || "Active";
                statusEl.dispatchEvent(new Event("change", { bubbles: true }));
            }

            if (editPwInput) {
                editPwInput.value = "";
                editPwInput.dispatchEvent(new Event("input", { bubbles: true }));
            }

            editDialog.showModal();
            if (nameEl) {
                setTimeout(() => nameEl.focus(), 80);
            }
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

    // SEARCH, FILTER, SORT & 10-ITEM PAGINATION
    const search = get("user-search");
    const roleFilter = get("user-role-filter");
    const statusFilter = get("user-status-filter");
    const sortSelect = get("user-sort");
    const resetBtn = get("user-reset-btn");
    const tbody = document.querySelector(".admin-table tbody");
    const rows = Array.from(document.querySelectorAll("[data-user-row]"));

    const emptyRow = get("user-filter-empty");
    const userCount = get("user-count");
    const noUsersRow = get("no-users-row");

    const pageInfo = get("user-page-info");
    const currentPageLabel = get("user-current-page");
    const prevBtn = get("user-prev-btn");
    const nextBtn = get("user-next-btn");

    let currentPage = 1;
    const itemsPerPage = 10;
    let filteredUsers = rows.slice();

    function renderUserPagination() {
        const total = filteredUsers.length;
        const totalPages = Math.ceil(total / itemsPerPage) || 1;

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIdx = (currentPage - 1) * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;

        // Hide all rows first
        rows.forEach((r) => {
            r.hidden = true;
        });

        // Show only rows belonging to current page
        filteredUsers.forEach((r, idx) => {
            if (idx >= startIdx && idx < endIdx) {
                r.hidden = false;
            } else {
                r.hidden = true;
            }
        });

        if (pageInfo) {
            if (total === 0) {
                pageInfo.textContent = "Showing 0 users";
            } else {
                const actualEnd = Math.min(endIdx, total);
                pageInfo.textContent = `Showing ${startIdx + 1}–${actualEnd} of ${total} users`;
            }
        }

        if (currentPageLabel) {
            currentPageLabel.textContent = `${currentPage}`;
        }

        if (prevBtn) {
            prevBtn.disabled = currentPage <= 1;
        }
        if (nextBtn) {
            nextBtn.disabled = currentPage >= totalPages;
        }

        if (emptyRow) {
            emptyRow.hidden = rows.length === 0 || total > 0;
        }

        if (noUsersRow) {
            noUsersRow.hidden = rows.length > 0;
        }

        if (userCount) {
            userCount.innerHTML = `<strong>${total}</strong> account${total === 1 ? "" : "s"}`;
        }
    }

    function sortUsers() {
        if (!tbody || !sortSelect) return;
        const mode = sortSelect.value;

        filteredUsers.sort((a, b) => {
            const nameA = (a.dataset.name || "").toLowerCase();
            const nameB = (b.dataset.name || "").toLowerCase();
            const emailA = (a.dataset.email || "").toLowerCase();
            const emailB = (b.dataset.email || "").toLowerCase();
            const roleA = (a.dataset.role || "").toLowerCase();
            const roleB = (b.dataset.role || "").toLowerCase();
            const statusA = (a.dataset.status || "").toLowerCase();
            const statusB = (b.dataset.status || "").toLowerCase();

            if (mode === "name-asc") return nameA.localeCompare(nameB);
            if (mode === "name-desc") return nameB.localeCompare(nameA);
            if (mode === "email-asc") return emailA.localeCompare(emailB);
            if (mode === "role-admin") return roleB.localeCompare(roleA); // 'admin' before 'client'
            if (mode === "status-active") return statusA.localeCompare(statusB); // 'active' before 'inactive'
            return 0;
        });

        filteredUsers.forEach((r) => tbody.appendChild(r));
        if (emptyRow) tbody.appendChild(emptyRow);
        if (noUsersRow) tbody.appendChild(noUsersRow);
    }

    function filterUsers() {
        const query = search ? search.value.trim().toLowerCase() : "";

        filteredUsers = rows.filter((row) => {
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

            return matchesText && matchesRole && matchesStatus;
        });

        sortUsers();
        currentPage = 1;
        renderUserPagination();
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
    if (sortSelect) {
        sortSelect.addEventListener("change", () => {
            sortUsers();
            renderUserPagination();
        });
    }
    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                renderUserPagination();
            }
        });
    }
    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            const totalPages = Math.ceil(filteredUsers.length / itemsPerPage) || 1;
            if (currentPage < totalPages) {
                currentPage++;
                renderUserPagination();
            }
        });
    }
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            if (search) search.value = "";
            if (roleFilter) roleFilter.value = "all";
            if (statusFilter) statusFilter.value = "all";
            if (sortSelect) sortSelect.value = "name-asc";
            filterUsers();
        });
    }

    const selectAllCb = get("user-select-all");
    if (selectAllCb) {
        selectAllCb.addEventListener("change", () => {
            document.querySelectorAll(".user-row-checkbox").forEach((cb) => {
                cb.checked = selectAllCb.checked;
            });
        });
    }

    filterUsers();
})();
