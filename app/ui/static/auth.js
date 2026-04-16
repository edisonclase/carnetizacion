const AUTH_STORAGE_KEY = "nova_id_access_token";
const AUTH_USER_STORAGE_KEY = "nova_id_current_user";

function getAccessToken() {
    return localStorage.getItem(AUTH_STORAGE_KEY);
}

function setAccessToken(token) {
    localStorage.setItem(AUTH_STORAGE_KEY, token);
}

function clearAccessToken() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
}

function getStoredUser() {
    const raw = localStorage.getItem(AUTH_USER_STORAGE_KEY);
    if (!raw) return null;

    try {
        return JSON.parse(raw);
    } catch (error) {
        return null;
    }
}

function setStoredUser(user) {
    localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
}

function clearStoredUser() {
    localStorage.removeItem(AUTH_USER_STORAGE_KEY);
}

function clearSession() {
    clearAccessToken();
    clearStoredUser();
}

function goToLogin() {
    if (window.location.pathname !== "/login") {
        window.location.href = "/login";
    }
}

async function apiFetch(url, options = {}) {
    const token = getAccessToken();
    const headers = new Headers(options.headers || {});

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearSession();
        goToLogin();
        throw new Error("Sesión expirada o no válida.");
    }

    return response;
}

async function fetchCurrentUser() {
    const response = await apiFetch("/auth/me");

    if (!response.ok) {
        clearSession();
        goToLogin();
        throw new Error("No se pudo validar la sesión.");
    }

    const user = await response.json();
    setStoredUser(user);
    return user;
}

function roleLabel(role) {
    const labels = {
        super_admin: "Super Administrador",
        admin_centro: "Administrador del centro",
        registro: "Registro",
        consulta: "Consulta",
        digitador: "Digitador",
    };

    return labels[role] || role || "-";
}

function canManageStudents(role) {
    return ["super_admin", "admin_centro", "registro"].includes(role);
}

function canViewStudents(role) {
    return ["super_admin", "admin_centro", "registro", "consulta"].includes(role);
}

function canPrint(role) {
    return ["super_admin", "admin_centro", "registro"].includes(role);
}

function canEdit(role) {
    return ["super_admin", "admin_centro", "registro"].includes(role);
}

async function requireAuth(allowedRoles = []) {
    const token = getAccessToken();

    if (!token) {
        goToLogin();
        throw new Error("No autenticado.");
    }

    const user = await fetchCurrentUser();

    if (allowedRoles.length && !allowedRoles.includes(user.role)) {
        throw new Error("No autorizado.");
    }

    return user;
}

function logout() {
    clearSession();
    goToLogin();
}