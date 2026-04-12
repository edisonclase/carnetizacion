const loginForm = document.getElementById("loginForm");
const loginAlert = document.getElementById("loginAlert");
const loginBtn = document.getElementById("loginBtn");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

function showLoginError(message) {
    loginAlert.textContent = message;
    loginAlert.classList.remove("hidden");
}

function hideLoginError() {
    loginAlert.textContent = "";
    loginAlert.classList.add("hidden");
}

function getDashboardRouteForUser() {
    return "/dashboard";
}

document.addEventListener("DOMContentLoaded", () => {
    hideLoginError();

    clearSession();

    loginForm.reset();
    emailInput.value = "";
    passwordInput.value = "";

    window.setTimeout(() => {
        emailInput.value = "";
        passwordInput.value = "";
    }, 0);

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideLoginError();

        const email = emailInput.value.trim().toLowerCase();
        const password = passwordInput.value;

        if (!email || !password) {
            showLoginError("Debes completar correo y contraseña.");
            return;
        }

        loginBtn.disabled = true;
        loginBtn.textContent = "Ingresando...";

        try {
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email,
                    password,
                }),
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.detail || "No se pudo iniciar sesión.");
            }

            setAccessToken(data.access_token);
            setStoredUser(data.user);

            window.location.href = getDashboardRouteForUser();
        } catch (error) {
            showLoginError(error.message || "Credenciales inválidas.");
            passwordInput.value = "";
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = "Iniciar sesión";
        }
    });
});