function novaRole(value) {
    return String(value || "").toLowerCase();
}

function novaCanViewStudents(role) {
    return ["super_admin", "admin_centro", "registro", "consulta", "digitador"].includes(novaRole(role));
}

function novaCanManageStudents(role) {
    return ["super_admin", "admin_centro", "registro", "digitador"].includes(novaRole(role));
}

function novaCanViewStaff(role) {
    return ["super_admin", "admin_centro", "registro", "consulta"].includes(novaRole(role));
}

function novaCanManageStaff(role) {
    return ["super_admin", "admin_centro", "registro"].includes(novaRole(role));
}

function novaCanManageCenterSettings(role) {
    return ["super_admin", "admin_centro"].includes(novaRole(role));
}

function novaCanAccessScanner(role) {
    return ["super_admin", "admin_centro", "registro", "digitador"].includes(novaRole(role));
}

function novaCanAccessBilling(role) {
    return novaRole(role) === "super_admin";
}

function novaShow(id) {
    document.getElementById(id)?.classList.remove("hidden");
}

function novaHide(id) {
    document.getElementById(id)?.classList.add("hidden");
}

function novaActivateCurrentLink() {
    const currentPath = window.location.pathname;

    document.querySelectorAll(".sidebar-nav a").forEach((link) => {
        link.classList.remove("active");

        const navPath = link.getAttribute("data-nav-path");

        if (!navPath) return;

        if (currentPath === navPath) {
            link.classList.add("active");
        }

        if (navPath !== "/dashboard" && currentPath.startsWith(navPath + "/")) {
            link.classList.add("active");
        }
    });
}

async function initializeNovaSidebar() {
    try {
        const response = await apiFetch("/auth/me");

        if (!response.ok) {
            window.location.href = "/login";
            return null;
        }

        const user = await response.json();
        const role = user.role;

        if (novaCanViewStudents(role)) {
            novaShow("navStudentsLink");
        }

        if (novaCanManageStudents(role)) {
            novaShow("navRegisterLink");
        }

        if (novaCanViewStaff(role)) {
            novaShow("navStaffListLink");
        }

        if (novaCanManageStaff(role)) {
            novaShow("navStaffRegisterLink");
        }

        if (novaCanManageCenterSettings(role)) {
            novaShow("navCenterSettingsLink");
        }

        if (novaCanAccessScanner(role)) {
            novaShow("navAttendanceScannerLink");
        }

        if (novaCanAccessBilling(role)) {
            novaShow("navBillingLink");
        }

        if (novaRole(role) !== "super_admin") {
            novaHide("navDocsLink");
        }

        const centerSettingsLink = document.getElementById("navCenterSettingsLink");
        if (centerSettingsLink) {
            const centerId = user.center_id || "";
            centerSettingsLink.href = centerId ? `/admin/centers/${centerId}/settings` : "#";
        }

        novaActivateCurrentLink();

        return user;
    } catch (error) {
        console.error("Error inicializando sidebar:", error);
        window.location.href = "/login";
        return null;
    }
}

document.addEventListener("DOMContentLoaded", initializeNovaSidebar);