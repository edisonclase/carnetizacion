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

function canAccessInstitutionalReports(role) {
    const normalized = String(role || "").toLowerCase();
    return normalized === "super_admin" || normalized === "admin_centro" || normalized === "consulta";
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
    const reportActionsCard = document.getElementById("reportActionsCard");

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

    if (canAccessInstitutionalReports(user.role)) {
        reportActionsCard.classList.remove("hidden");
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

function getSelectedFilters() {
    return {
        centerId: document.getElementById("centerId").value,
        schoolYearId: document.getElementById("schoolYearId").value,
        reportDate: document.getElementById("reportDate").value,
    };
}

function validateSelectedFilters() {
    const { centerId, schoolYearId, reportDate } = getSelectedFilters();

    if (!centerId || !schoolYearId || !reportDate) {
        alert("Debes completar centro, año escolar y fecha.");
        return false;
    }

    return true;
}

function buildReportBaseQuery() {
    const { centerId, schoolYearId, reportDate } = getSelectedFilters();
    return `center_id=${encodeURIComponent(centerId)}&school_year_id=${encodeURIComponent(schoolYearId)}&date=${encodeURIComponent(reportDate)}`;
}

function openPrintableJson(url) {
    window.open(url, "_blank", "noopener,noreferrer");
}

function handleViewCourseSummary() {
    if (!validateSelectedFilters()) return;

    const query = buildReportBaseQuery();
    openPrintableJson(`/reports/print/global-data?${query}`);
}

function handleViewDailyDetail() {
    if (!validateSelectedFilters()) return;

    const query = buildReportBaseQuery();
    openPrintableJson(`/reports/daily-institutional?${query}`);
}

function handlePrintGlobal() {
    if (!validateSelectedFilters()) return;

    const query = buildReportBaseQuery();
    openPrintableJson(`/reports/print/global-data?${query}`);
}

function handlePrintByCourse() {
    if (!validateSelectedFilters()) return;

    const grade = window.prompt("Escribe el curso que deseas imprimir. Ejemplo: 5to");
    if (!grade || !grade.trim()) return;

    const section = window.prompt("Escribe la sección si deseas filtrar por sección. Déjalo vacío para todas.");
    let query = `${buildReportBaseQuery()}&grade=${encodeURIComponent(grade.trim())}`;

    if (section && section.trim()) {
        query += `&section=${encodeURIComponent(section.trim())}`;
    }

    openPrintableJson(`/reports/print/by-course-data?${query}`);
}

function handlePrintMultiCourse() {
    if (!validateSelectedFilters()) return;

    const gradesInput = window.prompt(
        "Escribe varios cursos separados por coma. Ejemplo: 4to,5to,6to"
    );

    if (!gradesInput || !gradesInput.trim()) return;

    const grades = gradesInput
        .split(",")
        .map(item => item.trim())
        .filter(Boolean);

    if (!grades.length) return;

    const query = `${buildReportBaseQuery()}&${grades.map(grade => `grades=${encodeURIComponent(grade)}`).join("&")}`;
    openPrintableJson(`/reports/print/by-multi-course-data?${query}`);
}

function handlePrintExcuses() {
    if (!validateSelectedFilters()) return;

    const grade = window.prompt("Escribe el curso para filtrar excusas. Déjalo vacío para todos.");
    const section = window.prompt("Escribe la sección si deseas filtrar por sección. Déjalo vacío para todas.");

    let query = buildReportBaseQuery();

    if (grade && grade.trim()) {
        query += `&grade=${encodeURIComponent(grade.trim())}`;
    }

    if (section && section.trim()) {
        query += `&section=${encodeURIComponent(section.trim())}`;
    }

    openPrintableJson(`/reports/print/excuses-by-course-data?${query}`);
}

async function loadDashboard() {
    const { centerId, schoolYearId, reportDate } = getSelectedFilters();
    const generalMessage = document.getElementById("generalMessage");
    const loadButton = document.getElementById("loadDashboardBtn");

    if (!centerId || !schoolYearId || !reportDate) {
        alert("Debes completar centro, año escolar y fecha.");
        return;
    }

    generalMessage.textContent = "Cargando información...";
    if (loadButton) {
        loadButton.disabled = true;
        loadButton.textContent = "Cargando...";
    }

    try {
        const dailyUrl = `/reports/daily-institutional?center_id=${centerId}&school_year_id=${schoolYearId}&date=${reportDate}`;
        const summaryUrl = `/reports/students/summary?center_id=${centerId}&school_year_id=${schoolYearId}`;

        const [dailyReport, studentSummary] = await Promise.all([
            fetchJson(dailyUrl),
            fetchJson(summaryUrl),
        ]);

        const attendanceBreakdown = computeAttendanceBreakdown(dailyReport);
        const enrollmentBreakdown = computeEnrollmentBreakdown(studentSummary);

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

        const btnViewCourseSummary = document.getElementById("btnViewCourseSummary");
        if (btnViewCourseSummary) {
            btnViewCourseSummary.addEventListener("click", handleViewCourseSummary);
        }

        const btnViewDailyDetail = document.getElementById("btnViewDailyDetail");
        if (btnViewDailyDetail) {
            btnViewDailyDetail.addEventListener("click", handleViewDailyDetail);
        }

        const btnPrintGlobal = document.getElementById("btnPrintGlobal");
        if (btnPrintGlobal) {
            btnPrintGlobal.addEventListener("click", handlePrintGlobal);
        }

        const btnPrintByCourse = document.getElementById("btnPrintByCourse");
        if (btnPrintByCourse) {
            btnPrintByCourse.addEventListener("click", handlePrintByCourse);
        }

        const btnPrintMultiCourse = document.getElementById("btnPrintMultiCourse");
        if (btnPrintMultiCourse) {
            btnPrintMultiCourse.addEventListener("click", handlePrintMultiCourse);
        }

        const btnPrintExcuses = document.getElementById("btnPrintExcuses");
        if (btnPrintExcuses) {
            btnPrintExcuses.addEventListener("click", handlePrintExcuses);
        }
    } catch (error) {
        console.error(error);
    }
});