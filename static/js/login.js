        (() => {
            const passwordInput = document.getElementById("password");
            const toggleButton = document.getElementById("togglePassword");
            const eyeIcon = document.getElementById("passwordEyeIcon");

            if (!passwordInput || !toggleButton || !eyeIcon) {
                return;
            }

            const eyeOpen = `
                <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/>
                <circle cx="12" cy="12" r="3"/>
            `;

            const eyeClosed = `
                <path d="m3 3 18 18"/>
                <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/>
                <path d="M9.9 5.2A11 11 0 0 1 12 5c6.4 0 10 7 10 7a15.7 15.7 0 0 1-3.1 3.9"/>
                <path d="M6.6 6.6C3.7 8.5 2 12 2 12s3.6 7 10 7c1.4 0 2.7-.3 3.8-.8"/>
            `;

            toggleButton.addEventListener("click", () => {
                const showPassword = passwordInput.type === "password";

                passwordInput.type = showPassword ? "text" : "password";
                toggleButton.setAttribute(
                    "aria-label",
                    showPassword ? "Hide password" : "Show password"
                );
                toggleButton.setAttribute(
                    "aria-pressed",
                    String(showPassword)
                );

                eyeIcon.innerHTML = showPassword ? eyeClosed : eyeOpen;
            });
        })();
   