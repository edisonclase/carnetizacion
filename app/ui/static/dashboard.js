let courseChartInstance = null;
let genderChartInstance = null;

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
    const response = await fetch(url);
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo cargar la información.");
    }
    return response.json();
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

        centerSelect.innerHTML = centers.map(center => `
            <option value="${center.id}">${center.name}</option>
        `).join("");
    } catch (error) {
        centerSelect.innerHTML = `<option value="">Error cargando centros</option>`;
    }
}

async function loadSchoolYears() {
    const schoolYearSelect = document.getElementById("schoolYearId");
    if (!schoolYearSelect) return;

    try {
        const schoolYears = await fetchJson("/school-years/");
        if (!schoolYears.length) {
            schoolYearSelect.innerHTML = `<option value="">No hay años escolares registrados</option>`;
            return;
        }

        schoolYearSelect.innerHTML = schoolYears.map(item => `
            <option value="${item.id}">${item.name}</option>
        `).join("");
    } catch (error) {
        schoolYearSelect.innerHTML = `<option value="">Error cargando años escolares</option>`;
    }
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
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    setDefaultDate();
    await loadCenters();
    await loadSchoolYears();

    const button = document.getElementById("loadDashboardBtn");
    if (button) {
        button.addEventListener("click", loadDashboard);
    }
});