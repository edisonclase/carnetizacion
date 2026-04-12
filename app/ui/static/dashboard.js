let courseChartInstance = null;
let genderChartInstance = null;
let currentUser = null;
let allSchoolYears = [];

function getTodayLocalDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function setDefaultDate() {
    const dateInput = document.getElementById("reportDate");
    if (dateInput && !dateInput.value) {
        dateInput.value = getTodayLocalDate();
    }
}

function statusBadge(status) {
    const normalized = (status || "").toLowerCase();

    if (normalized === "present") {
        return `<span class="badge badge-present">Presente</span>`;
    }
    if (normalized === "late") {
        return `<span class="badge badge-late">Tarde</span>`;
    }
    if (normalized === "absent") {
        return `<span class="badge badge-absent">Ausente</span>`;
    }

    return status || "-";
}

function fillMetric(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value ?? 0;
    }
}

function fillFlag(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value ? "Sí" : "No";
    }
}

function renderCourseTable(rows) {
    const tbody = document.getElementById("courseTableBody");
    if (!tbody) return;

    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Sin datos disponibles.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(item => `
        <tr>
            <td>${item.grade}</td>
            <td>${item.section}</td>
            <td>${item.total_students}</td>
            <td>${item.total_present}</td>
            <td>${item.total_late}</td>
            <td>${item.total_absent}</td>
            <td>${item.total_with_excuse}</td>
        </tr>
    `).join("");
}

function renderGenderTable(rows) {
    const tbody = document.getElementById("genderTableBody");
    if (!tbody) return;

    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Sin datos disponibles.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(item => `
        <tr>
            <td>${item.gender}</td>
            <td>${item.total_students}</td>
            <td>${item.total_present}</td>
            <td>${item.total_late}</td>
            <td>${item.total_absent}</td>
            <td>${item.total_with_excuse}</td>
        </tr>
    `).join("");
}

function mergeDetailRows(report) {
    const result = [];

    (report.present_students || []).forEach(item => result.push(item));
    (report.late_students || []).forEach(item => result.push(item));
    (report.absent_students || []).forEach(item => result.push(item));

    return result.sort((a, b) => {
        if (a.grade !== b.grade) return String(a.grade).localeCompare(String(b.grade));
        if (a.section !== b.section) return String(a.section).localeCompare(String(b.section));
        return String(a.full_name).localeCompare(String(b.full_name));
    });
}

function renderDetailTable(report) {
    const tbody = document.getElementById("detailTableBody");
    if (!tbody) return;

    const rows = mergeDetailRows(report);

    if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="empty-row">Sin datos disponibles.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(item => `
        <tr>
            <td>${statusBadge(item.status)}</td>
            <td>${item.full_name}</td>
            <td>${item.student_code ?? "-"}</td>
            <td>${item.minerd_id ?? "-"}</td>
            <td>${item.gender ?? "-"}</td>
            <td>${item.grade}</td>
            <td>${item.section}</td>
            <td>${item.first_entry_time ? new Date(item.first_entry_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-"}</td>
            <td>${item.minutes_late ?? 0}</td>
            <td>${item.has_excuse ? (item.excuse_note ?? "Sí") : "No"}</td>
        </tr>
    `).join("");
}

function renderCourseChart(data) {
    const ctx = document.getElementById("courseChart");
    if (!ctx) return;

    if (courseChartInstance) {
        courseChartInstance.destroy();
    }

    const labels = data.map(item => `${item.grade}-${item.section}`);
    const present = data.map(item => item.total_present);
    const absent = data.map(item => item.total_absent);
    const late = data.map(item => item.total_late);

    courseChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Presentes",
                    data: present,
                    backgroundColor: "#16a34a",
                },
                {
                    label: "Ausentes",
                    data: absent,
                    backgroundColor: "#dc2626",
                },
                {
                    label: "Tardes",
                    data: late,
                    backgroundColor: "#d97706",
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "top",
                },
            },
        },
    });
}

function renderGenderChart(data) {
    const ctx = document.getElementById("genderChart");
    if (!ctx) return;

    if (genderChartInstance) {
        genderChartInstance.destroy();
    }

    const labels = data.map(item => item.gender);
    const present = data.map(item => item.total_present);

    genderChartInstance = new Chart(ctx, {
        type: "pie",
        data: {
            labels,
            datasets: [
                {
                    data: present,
                    backgroundColor: ["#2563eb", "#ec4899", "#10b981", "#f59e0b"],
                },
            ],
        },
    });
}

async function fetchJson(url) {
    const response = await apiFetch(url);

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo cargar la información.");
    }

    return response.json();
}

function canManageCenterCardSettings(role) {
    const normalized = String(role || "").toLowerCase();
    return normalized === "super_admin" || normalized === "admin_centro";
}

function canUsePrintActions(role) {
    const normalized = String(role || "").toLowerCase();
    return normalized === "super_admin" || normalized === "admin_centro" || normalized === "registro";
}

function configureRoleUI(user) {
    document.getElementById("currentUserName").textContent = user.full_name;
    document.getElementById("currentUserRole").textContent = roleLabel(user.role);

    const navStudentsLink = document.getElementById("navStudentsLink");
    const navRegisterLink = document.getElementById("navRegisterLink");
    const navCenterSettingsLink = document.getElementById("navCenterSettingsLink");
    const moduleAccessCard = document.getElementById("moduleAccessCard");
    const moduleStudentsList = document.getElementById("moduleStudentsList");
    const moduleStudentRegister = document.getElementById("moduleStudentRegister");
    const moduleCenterSettings = document.getElementById("moduleCenterSettings");
    const navDocsLink = document.getElementById("navDocsLink");
    const printActionsCard = document.getElementById("printActionsCard");

    if (canViewStudents(user.role)) {
        navStudentsLink.classList.remove("hidden");
        moduleAccessCard.classList.remove("hidden");
        moduleStudentsList.classList.remove("hidden");
    }

    if (canManageStudents(user.role)) {
        navRegisterLink.classList.remove("hidden");
        moduleAccessCard.classList.remove("hidden");
        moduleStudentRegister.classList.remove("hidden");
    }

    if (canManageCenterCardSettings(user.role)) {
        moduleAccessCard.classList.remove("hidden");
        navCenterSettingsLink.classList.remove("hidden");
        moduleCenterSettings.classList.remove("hidden");
    }

    if (!canUsePrintActions(user.role) && printActionsCard) {
        printActionsCard.style.display = "none";
    }

    if (user.role !== "super_admin") {
        navDocsLink.classList.add("hidden");
    }
}

function filterSchoolYearsByCenter(centerId) {
    const schoolYearSelect = document.getElementById("schoolYearId");
    if (!schoolYearSelect) return;

    const filtered = allSchoolYears.filter((item) => {
        return !centerId || String(item.center_id) === String(centerId);
    });

    if (!filtered.length) {
        schoolYearSelect.innerHTML = `<option value="">No hay años escolares disponibles</option>`;
        return;
    }

    schoolYearSelect.innerHTML = filtered.map(item => `
        <option value="${item.id}">${item.name}</option>
    `).join("");
}

function updateCenterSettingsLinks() {
    const centerId = document.getElementById("centerId")?.value;
    const navCenterSettingsLink = document.getElementById("navCenterSettingsLink");
    const moduleCenterSettings = document.getElementById("moduleCenterSettings");

    if (!centerId) {
        if (navCenterSettingsLink) navCenterSettingsLink.setAttribute("href", "#");
        if (moduleCenterSettings) moduleCenterSettings.setAttribute("href", "#");
        return;
    }

    const href = `/admin/centers/${centerId}/settings`;

    if (navCenterSettingsLink) navCenterSettingsLink.setAttribute("href", href);
    if (moduleCenterSettings) moduleCenterSettings.setAttribute("href", href);
}

function fillStudentSummary(summary) {
    fillMetric("metricStudentsTotal", summary.total_students ?? 0);

    const byGender = summary.by_gender || {};
    const male = byGender.M || byGender.Masculino || byGender.masculino || 0;
    const female = byGender.F || byGender.Femenino || byGender.femenino || 0;

    let other = 0;
    Object.entries(byGender).forEach(([key, value]) => {
        const normalized = String(key).toLowerCase();
        if (normalized !== "m" && normalized !== "masculino" && normalized !== "f" && normalized !== "femenino") {
            other += Number(value || 0);
        }
    });

    fillMetric("metricStudentsMale", male);
    fillMetric("metricStudentsFemale", female);
    fillMetric("metricStudentsOther", other);

    const printGradeSelect = document.getElementById("printGradeSelect");
    if (!printGradeSelect) return;

    const grades = Object.keys(summary.by_grade || {});
    printGradeSelect.innerHTML = `<option value="">Seleccione un curso</option>`;

    grades.forEach((grade) => {
        printGradeSelect.innerHTML += `<option value="${grade}">${grade}</option>`;
    });
}

async function loadCenters() {
    const centerSelect = document.getElementById("centerId");
    if (!centerSelect) return;

    try {
        const centers = await fetchJson("/centers/");

        if (!centers.length) {
            centerSelect.innerHTML = `<option value="">No hay centros registrados</option>`;
            return;
        }

        if (currentUser.role === "super_admin") {
            centerSelect.innerHTML = centers.map(center => `
                <option value="${center.id}">${center.name}</option>
            `).join("");
        } else {
            const ownCenter = centers.find((center) => String(center.id) === String(currentUser.center_id));

            if (!ownCenter) {
                centerSelect.innerHTML = `<option value="">Centro no disponible</option>`;
                return;
            }

            centerSelect.innerHTML = `<option value="${ownCenter.id}">${ownCenter.name}</option>`;
            centerSelect.value = String(ownCenter.id);
            centerSelect.disabled = true;
        }

        updateCenterSettingsLinks();
    } catch (error) {
        centerSelect.innerHTML = `<option value="">Error cargando centros</option>`;
    }
}

async function loadSchoolYears() {
    const schoolYearSelect = document.getElementById("schoolYearId");
    if (!schoolYearSelect) return;

    try {
        allSchoolYears = await fetchJson("/school-years/");

        if (!allSchoolYears.length) {
            schoolYearSelect.innerHTML = `<option value="">No hay años escolares registrados</option>`;
            return;
        }

        filterSchoolYearsByCenter(document.getElementById("centerId").value);
    } catch (error) {
        schoolYearSelect.innerHTML = `<option value="">Error cargando años escolares</option>`;
    }
}

async function loadStudentSummary(centerId, schoolYearId) {
    const params = new URLSearchParams();

    if (centerId) params.set("center_id", centerId);
    if (schoolYearId) params.set("school_year_id", schoolYearId);

    const summaryUrl = `/reports/students/summary?${params.toString()}`;
    const summary = await fetchJson(summaryUrl);
    fillStudentSummary(summary);
}

async function loadDashboard() {
    const centerId = document.getElementById("centerId").value;
    const schoolYearId = document.getElementById("schoolYearId").value;
    const reportDate = document.getElementById("reportDate").value;
    const generalMessage = document.getElementById("generalMessage");

    if (!centerId || !schoolYearId || !reportDate) {
        alert("Debes completar centro, año escolar y fecha.");
        return;
    }

    generalMessage.textContent = "Cargando información...";

    try {
        const dailyUrl = `/reports/daily-institutional?center_id=${centerId}&school_year_id=${schoolYearId}&date=${reportDate}`;
        const groupedUrl = `/reports/daily-grouped?center_id=${centerId}&school_year_id=${schoolYearId}&date=${reportDate}`;

        const [dailyReport, groupedReport] = await Promise.all([
            fetchJson(dailyUrl),
            fetchJson(groupedUrl),
        ]);

        await loadStudentSummary(centerId, schoolYearId);

        fillMetric("metricPresent", dailyReport.total_present);
        fillMetric("metricLate", dailyReport.total_late);
        fillMetric("metricAbsent", dailyReport.total_absent);
        fillMetric("metricExcuse", dailyReport.total_with_excuse);
        fillMetric("metricEntries", dailyReport.total_entries);
        fillMetric("metricExits", dailyReport.total_exits);

        fillFlag("flagWorkday", dailyReport.is_workday);
        fillFlag("flagActivity", dailyReport.had_attendance_activity);
        fillFlag("flagNoSchool", dailyReport.possible_no_school_day);
        fillFlag("flagEarlyDismissal", dailyReport.possible_early_dismissal);

        generalMessage.textContent =
            `Reporte cargado para ${dailyReport.date}. Presentes: ${dailyReport.total_present}, Tardanzas: ${dailyReport.total_late}, Ausentes: ${dailyReport.total_absent}.`;

        renderCourseTable(groupedReport.by_course || []);
        renderGenderTable(groupedReport.by_gender || []);
        renderDetailTable(dailyReport);
        renderCourseChart(groupedReport.by_course || []);
        renderGenderChart(groupedReport.by_gender || []);
    } catch (error) {
        generalMessage.textContent = error.message || "Ocurrió un error cargando el dashboard.";
        renderCourseTable([]);
        renderGenderTable([]);
        renderDetailTable({
            present_students: [],
            late_students: [],
            absent_students: [],
        });
        renderCourseChart([]);
        renderGenderChart([]);
        fillStudentSummary({
            total_students: 0,
            by_gender: {},
            by_grade: {},
        });
    }
}

function printAllCards() {
    const centerId = document.getElementById("centerId").value;
    const schoolYearId = document.getElementById("schoolYearId").value;

    if (!centerId || !schoolYearId) {
        alert("Debes seleccionar centro y año escolar.");
        return;
    }

    window.open(
        `/students/cards/print-sheet?center_id=${centerId}&school_year_id=${schoolYearId}`,
        "_blank"
    );
}

function printCardsByGrade() {
    const centerId = document.getElementById("centerId").value;
    const schoolYearId = document.getElementById("schoolYearId").value;
    const grade = document.getElementById("printGradeSelect").value;

    if (!centerId || !schoolYearId || !grade) {
        alert("Debes seleccionar centro, año escolar y curso.");
        return;
    }

    window.open(
        `/students/cards/print-sheet?center_id=${centerId}&school_year_id=${schoolYearId}&grade=${encodeURIComponent(grade)}`,
        "_blank"
    );
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        currentUser = await requireAuth(["super_admin", "admin_centro", "registro", "consulta"]);
        configureRoleUI(currentUser);

        setDefaultDate();
        await loadCenters();
        await loadSchoolYears();

        const centerSelect = document.getElementById("centerId");
        if (centerSelect) {
            centerSelect.addEventListener("change", () => {
                filterSchoolYearsByCenter(centerSelect.value);
                updateCenterSettingsLinks();
            });
        }

        const button = document.getElementById("loadDashboardBtn");
        if (button) {
            button.addEventListener("click", loadDashboard);
        }

        const printAllBtn = document.getElementById("printAllBtn");
        if (printAllBtn) {
            printAllBtn.addEventListener("click", printAllCards);
        }

        const printByGradeBtn = document.getElementById("printByGradeBtn");
        if (printByGradeBtn) {
            printByGradeBtn.addEventListener("click", printCardsByGrade);
        }

        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", logout);
        }
    } catch (error) {
        console.error(error);
    }
});