const loginForm = document.getElementById("loginForm");
const loginAlert = document.getElementById("loginAlert");
const loginBtn = document.getElementById("loginBtn");

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

document.addEventListener("DOMContentLoaded", async () => {
    const token = getAccessToken();

    if (token) {
        try {
            await fetchCurrentUser();
            window.location.href = getDashboardRouteForUser();
            return;
        } catch (error) {
            clearSession();
        }
    }

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideLoginError();

        const email = document.getElementById("email").value.trim().toLowerCase();
        const password = document.getElementById("password").value;

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
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = "Iniciar sesión";
        }
    });
});