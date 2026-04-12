let statusGenderChartInstance = null;
let enrollmentGenderChartInstance = null;
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
    const normalized = String(status || "").toLowerCase();

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

function setText(id, value) {
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

function normalizeGender(value) {
    const raw = String(value || "").trim().toLowerCase();

    if (raw === "m" || raw === "masculino" || raw === "male") return "M";
    if (raw === "f" || raw === "femenino" || raw === "female") return "F";
    return "O";
}

function mergedDailyRows(report) {
    const rows = [];
    (report.present_students || []).forEach(item => rows.push(item));
    (report.late_students || []).forEach(item => rows.push(item));
    (report.absent_students || []).forEach(item => rows.push(item));

    return rows.sort((a, b) => {
        if (a.grade !== b.grade) return String(a.grade).localeCompare(String(b.grade), "es");
        if (a.section !== b.section) return String(a.section).localeCompare(String(b.section), "es");
        return String(a.full_name || "").localeCompare(String(b.full_name || ""), "es");
    });
}

function computeAttendanceBreakdown(report) {
    const rows = mergedDailyRows(report);

    const result = {
        present: { M: 0, F: 0, T: 0 },
        late: { M: 0, F: 0, T: 0 },
        absent: { M: 0, F: 0, T: 0 },
        excuse: { M: 0, F: 0, T: 0 },
        general: { M: 0, F: 0, T: 0 },
    };

    rows.forEach((item) => {
        const gender = normalizeGender(item.gender);
        const status = String(item.status || "").toLowerCase();

        if (gender === "M" || gender === "F") {
            result.general[gender] += 1;
        }
        result.general.T += 1;

        if (status === "present") {
            if (gender === "M" || gender === "F") result.present[gender] += 1;
            result.present.T += 1;
        } else if (status === "late") {
            if (gender === "M" || gender === "F") result.late[gender] += 1;
            result.late.T += 1;
        } else if (status === "absent") {
            if (gender === "M" || gender === "F") result.absent[gender] += 1;
            result.absent.T += 1;
        }

        if (item.has_excuse) {
            if (gender === "M" || gender === "F") result.excuse[gender] += 1;
            result.excuse.T += 1;
        }
    });

    return result;
}

function computeEnrollmentBreakdown(summary) {
    const byGender = summary.by_gender || {};
    let male = 0;
    let female = 0;

    Object.entries(byGender).forEach(([key, value]) => {
        const normalized = normalizeGender(key);
        if (normalized === "M") male += Number(value || 0);
        if (normalized === "F") female += Number(value || 0);
    });

    return {
        M: male,
        F: female,
        T: Number(summary.total_students || 0),
    };
}

function computeCourseGenderSummary(report) {
    const rows = mergedDailyRows(report);
    const map = new Map();

    rows.forEach((item) => {
        const grade = item.grade || "-";
        const section = item.section || "-";
        const key = `${grade}|||${section}`;
        const gender = normalizeGender(item.gender);
        const status = String(item.status || "").toLowerCase();

        if (!map.has(key)) {
            map.set(key, {
                grade,
                section,
                enrollment_m: 0,
                enrollment_f: 0,
                enrollment_t: 0,
                present_m: 0,
                present_f: 0,
                present_t: 0,
                late_m: 0,
                late_f: 0,
                late_t: 0,
                absent_m: 0,
                absent_f: 0,
                absent_t: 0,
                excuse_m: 0,
                excuse_f: 0,
                excuse_t: 0,
            });
        }

        const row = map.get(key);

        if (gender === "M") row.enrollment_m += 1;
        if (gender === "F") row.enrollment_f += 1;
        row.enrollment_t += 1;

        if (status === "present") {
            if (gender === "M") row.present_m += 1;
            if (gender === "F") row.present_f += 1;
            row.present_t += 1;
        }

        if (status === "late") {
            if (gender === "M") row.late_m += 1;
            if (gender === "F") row.late_f += 1;
            row.late_t += 1;
        }

        if (status === "absent") {
            if (gender === "M") row.absent_m += 1;
            if (gender === "F") row.absent_f += 1;
            row.absent_t += 1;
        }

        if (item.has_excuse) {
            if (gender === "M") row.excuse_m += 1;
            if (gender === "F") row.excuse_f += 1;
            row.excuse_t += 1;
        }
    });

    return [...map.values()].sort((a, b) => {
        if (a.grade !== b.grade) return String(a.grade).localeCompare(String(b.grade), "es");
        return String(a.section).localeCompare(String(b.section), "es");
    });
}

function renderCourseTable(rows) {
    const tbody = document.getElementById("courseTableBody");
    if (!tbody) return;

    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="17" class="empty-row">Sin datos disponibles.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(item => `
        <tr>
            <td>${item.grade}</td>
            <td>${item.section}</td>
            <td>${item.enrollment_m}</td>
            <td>${item.enrollment_f}</td>
            <td>${item.enrollment_t}</td>
            <td>${item.present_m}</td>
            <td>${item.present_f}</td>
            <td>${item.present_t}</td>
            <td>${item.late_m}</td>
            <td>${item.late_f}</td>
            <td>${item.late_t}</td>
            <td>${item.absent_m}</td>
            <td>${item.absent_f}</td>
            <td>${item.absent_t}</td>
            <td>${item.excuse_m}</td>
            <td>${item.excuse_f}</td>
            <td>${item.excuse_t}</td>
        </tr>
    `).join("");
}

function renderDetailTable(report) {
    const tbody = document.getElementById("detailTableBody");
    if (!tbody) return;

    const rows = mergedDailyRows(report);

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

function renderStatusGenderChart(breakdown) {
    const ctx = document.getElementById("statusGenderChart");
    if (!ctx) return;

    if (statusGenderChartInstance) {
        statusGenderChartInstance.destroy();
    }

    statusGenderChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Presentes", "Tardanzas", "Ausentes", "Con excusa"],
            datasets: [
                {
                    label: "Masculino",
                    data: [
                        breakdown.present.M,
                        breakdown.late.M,
                        breakdown.absent.M,
                        breakdown.excuse.M,
                    ],
                    backgroundColor: "#2563eb",
                    borderRadius: 10,
                    maxBarThickness: 42,
                },
                {
                    label: "Femenino",
                    data: [
                        breakdown.present.F,
                        breakdown.late.F,
                        breakdown.absent.F,
                        breakdown.excuse.F,
                    ],
                    backgroundColor: "#ec4899",
                    borderRadius: 10,
                    maxBarThickness: 42,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                    },
                },
            },
        },
    });
}

function renderEnrollmentGenderChart(enrollment) {
    const ctx = document.getElementById("enrollmentGenderChart");
    if (!ctx) return;

    if (enrollmentGenderChartInstance) {
        enrollmentGenderChartInstance.destroy();
    }

    enrollmentGenderChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Masculino", "Femenino"],
            datasets: [
                {
                    data: [enrollment.M, enrollment.F],
                    backgroundColor: ["#2563eb", "#ec4899"],
                    borderWidth: 0,
                    hoverOffset: 8,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "62%",
            plugins: {
                legend: {
                    position: "top",
                },
            },
        },
    });
}

function fillAttendanceCards(breakdown) {
    setText("presentMale", breakdown.present.M);
    setText("presentFemale", breakdown.present.F);
    setText("presentTotal", breakdown.present.T);

    setText("lateMale", breakdown.late.M);
    setText("lateFemale", breakdown.late.F);
    setText("lateTotal", breakdown.late.T);

    setText("absentMale", breakdown.absent.M);
    setText("absentFemale", breakdown.absent.F);
    setText("absentTotal", breakdown.absent.T);

    setText("excuseMale", breakdown.excuse.M);
    setText("excuseFemale", breakdown.excuse.F);
    setText("excuseTotal", breakdown.excuse.T);

    setText("generalMale", breakdown.general.M);
    setText("generalFemale", breakdown.general.F);
    setText("generalTotal", breakdown.general.T);
}

function fillEnrollmentCards(enrollment) {
    setText("enrollmentMale", enrollment.M);
    setText("enrollmentFemale", enrollment.F);
    setText("enrollmentTotal", enrollment.T);
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
        navCenterSettingsLink.classList.remove("hidden");
        moduleAccessCard.classList.remove("hidden");
        moduleCenterSettings.classList.remove("hidden");
    }

    if (String(user.role).toLowerCase() !== "super_admin") {
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
    const selectedCenterId = document.getElementById("centerId")?.value;
    const navCenterSettingsLink = document.getElementById("navCenterSettingsLink");
    const moduleCenterSettings = document.getElementById("moduleCenterSettings");
    const href = selectedCenterId ? `/admin/centers/${selectedCenterId}/settings` : "#";

    if (navCenterSettingsLink) navCenterSettingsLink.setAttribute("href", href);
    if (moduleCenterSettings) moduleCenterSettings.setAttribute("href", href);
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

        if (String(currentUser.role).toLowerCase() === "super_admin") {
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

function resetDashboardVisuals() {
    fillAttendanceCards({
        present: { M: 0, F: 0, T: 0 },
        late: { M: 0, F: 0, T: 0 },
        absent: { M: 0, F: 0, T: 0 },
        excuse: { M: 0, F: 0, T: 0 },
        general: { M: 0, F: 0, T: 0 },
    });

    fillEnrollmentCards({ M: 0, F: 0, T: 0 });
    setText("metricEntries", 0);
    setText("metricExits", 0);

    renderCourseTable([]);
    renderDetailTable({
        present_students: [],
        late_students: [],
        absent_students: [],
    });

    renderStatusGenderChart({
        present: { M: 0, F: 0, T: 0 },
        late: { M: 0, F: 0, T: 0 },
        absent: { M: 0, F: 0, T: 0 },
        excuse: { M: 0, F: 0, T: 0 },
    });

    renderEnrollmentGenderChart({ M: 0, F: 0, T: 0 });

    fillFlag("flagWorkday", false);
    fillFlag("flagActivity", false);
    fillFlag("flagNoSchool", false);
    fillFlag("flagEarlyDismissal", false);
}

async function loadDashboard() {
    const selectedCenterId = document.getElementById("centerId").value;
    const selectedSchoolYearId = document.getElementById("schoolYearId").value;
    const reportDate = document.getElementById("reportDate").value;
    const generalMessage = document.getElementById("generalMessage");
    const loadButton = document.getElementById("loadDashboardBtn");

    if (!selectedCenterId || !selectedSchoolYearId || !reportDate) {
        alert("Debes completar centro, año escolar y fecha.");
        return;
    }

    generalMessage.textContent = "Cargando información...";
    if (loadButton) {
        loadButton.disabled = true;
        loadButton.textContent = "Cargando...";
    }

    try {
        const dailyUrl = `/reports/daily-institutional?center_id=${selectedCenterId}&school_year_id=${selectedSchoolYearId}&date=${reportDate}`;
        const summaryUrl = `/reports/students/summary?center_id=${selectedCenterId}&school_year_id=${selectedSchoolYearId}`;

        const [dailyReport, studentSummary] = await Promise.all([
            fetchJson(dailyUrl),
            fetchJson(summaryUrl),
        ]);

        const attendanceBreakdown = computeAttendanceBreakdown(dailyReport);
        const enrollmentBreakdown = computeEnrollmentBreakdown(studentSummary);
        const courseRows = computeCourseGenderSummary(dailyReport);

        fillAttendanceCards(attendanceBreakdown);
        fillEnrollmentCards(enrollmentBreakdown);

        setText("metricEntries", dailyReport.total_entries);
        setText("metricExits", dailyReport.total_exits);

        fillFlag("flagWorkday", dailyReport.is_workday);
        fillFlag("flagActivity", dailyReport.had_attendance_activity);
        fillFlag("flagNoSchool", dailyReport.possible_no_school_day);
        fillFlag("flagEarlyDismissal", dailyReport.possible_early_dismissal);

        generalMessage.textContent =
            `Reporte cargado para ${dailyReport.date}. Total general: ${attendanceBreakdown.general.T}. Matrícula actual: ${enrollmentBreakdown.T}.`;

        renderCourseTable(courseRows);
        renderDetailTable(dailyReport);
        renderStatusGenderChart(attendanceBreakdown);
        renderEnrollmentGenderChart(enrollmentBreakdown);
    } catch (error) {
        generalMessage.textContent = error.message || "Ocurrió un error cargando el dashboard.";
        resetDashboardVisuals();
    } finally {
        if (loadButton) {
            loadButton.disabled = false;
            loadButton.textContent = "Cargar dashboard";
        }
    }
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

        const logoutBtn = document.getElementById("logoutBtn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", logout);
        }
    } catch (error) {
        console.error(error);
    }
});