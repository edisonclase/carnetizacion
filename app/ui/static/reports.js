document.addEventListener("DOMContentLoaded", async () => {
    await requireAuth(["super_admin", "admin_centro", "registro", "consulta"]);

    const centerSelect = document.getElementById("centerId");
    const schoolYearSelect = document.getElementById("schoolYearId");
    const dateInput = document.getElementById("reportDate");
    const courseTableBody = document.getElementById("courseTableBody");
    const detailTableBody = document.getElementById("detailTableBody");
    const executiveMessage = document.getElementById("executiveMessage");

    dateInput.value = new Date().toISOString().split("T")[0];

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

    async function fetchJson(url) {
        const response = await apiFetch(url);

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || "No se pudo cargar la información.");
        }

        return response.json();
    }

    async function loadCenters() {
        const centers = await fetchJson("/centers/");
        centerSelect.innerHTML = centers
            .map((c) => `<option value="${c.id}">${c.name}</option>`)
            .join("");
    }

    async function loadYears() {
        const years = await fetchJson("/school-years/");
        schoolYearSelect.innerHTML = years
            .map((y) => `<option value="${y.id}">${y.name}</option>`)
            .join("");
    }

    function getFilters() {
        return {
            centerId: centerSelect.value,
            schoolYearId: schoolYearSelect.value,
            reportDate: dateInput.value,
        };
    }

    function validateFilters() {
        const { centerId, schoolYearId, reportDate } = getFilters();

        if (!centerId || !schoolYearId || !reportDate) {
            alert("Debes completar centro, año escolar y fecha.");
            return false;
        }

        return true;
    }

    function buildBaseQuery() {
        const { centerId, schoolYearId, reportDate } = getFilters();
        return `center_id=${encodeURIComponent(centerId)}&school_year_id=${encodeURIComponent(schoolYearId)}&date=${encodeURIComponent(reportDate)}`;
    }

    function mergedRows(data) {
        const rows = [
            ...(data.present_students || []),
            ...(data.late_students || []),
            ...(data.absent_students || []),
        ];

        return rows.sort((a, b) => {
            if (a.grade !== b.grade) return String(a.grade).localeCompare(String(b.grade), "es");
            if (a.section !== b.section) return String(a.section).localeCompare(String(b.section), "es");
            return String(a.full_name || "").localeCompare(String(b.full_name || ""), "es");
        });
    }

    function computeAttendanceBreakdown(rows) {
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

    function computeEnrollmentFromRows(rows) {
        const result = { M: 0, F: 0, T: 0 };

        rows.forEach((item) => {
            const gender = normalizeGender(item.gender);
            if (gender === "M") result.M += 1;
            if (gender === "F") result.F += 1;
            result.T += 1;
        });

        return result;
    }

    function fillExecutiveCards(attendance, enrollment) {
        setText("presentMale", attendance.present.M);
        setText("presentFemale", attendance.present.F);
        setText("presentTotal", attendance.present.T);

        setText("lateMale", attendance.late.M);
        setText("lateFemale", attendance.late.F);
        setText("lateTotal", attendance.late.T);

        setText("absentMale", attendance.absent.M);
        setText("absentFemale", attendance.absent.F);
        setText("absentTotal", attendance.absent.T);

        setText("excuseMale", attendance.excuse.M);
        setText("excuseFemale", attendance.excuse.F);
        setText("excuseTotal", attendance.excuse.T);

        setText("generalMale", attendance.general.M);
        setText("generalFemale", attendance.general.F);
        setText("generalTotal", attendance.general.T);

        setText("enrollmentMale", enrollment.M);
        setText("enrollmentFemale", enrollment.F);
        setText("enrollmentTotal", enrollment.T);
    }

    function renderDetail(data) {
        const rows = mergedRows(data);

        if (!rows.length) {
            detailTableBody.innerHTML = `<tr><td colspan="9" class="empty-row">Sin datos disponibles.</td></tr>`;
            return;
        }

        detailTableBody.innerHTML = rows
            .map(
                (r) => `
            <tr>
                <td>${statusBadge(r.status)}</td>
                <td>${r.full_name}</td>
                <td>${r.student_code ?? "-"}</td>
                <td>${r.gender ?? "-"}</td>
                <td>${r.grade}</td>
                <td>${r.section}</td>
                <td>${r.first_entry_time ? new Date(r.first_entry_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-"}</td>
                <td>${r.minutes_late ?? 0}</td>
                <td>${r.has_excuse ? (r.excuse_note ?? "Sí") : "No"}</td>
            </tr>
        `
            )
            .join("");
    }

    function renderCourse(data) {
        const map = {};
        const rows = mergedRows(data);

        rows.forEach((r) => {
            const key = `${r.grade}-${r.section}`;
            const gender = normalizeGender(r.gender);

            if (!map[key]) {
                map[key] = {
                    grade: r.grade,
                    section: r.section,
                    enrollmentM: 0,
                    enrollmentF: 0,
                    enrollmentT: 0,
                    present: 0,
                    late: 0,
                    absent: 0,
                    excuse: 0,
                };
            }

            if (gender === "M") map[key].enrollmentM += 1;
            if (gender === "F") map[key].enrollmentF += 1;
            map[key].enrollmentT += 1;

            if (r.status === "present") map[key].present += 1;
            if (r.status === "late") map[key].late += 1;
            if (r.status === "absent") map[key].absent += 1;
            if (r.has_excuse) map[key].excuse += 1;
        });

        const values = Object.values(map);

        if (!values.length) {
            courseTableBody.innerHTML = `<tr><td colspan="9" class="empty-row">Sin datos disponibles.</td></tr>`;
            return;
        }

        courseTableBody.innerHTML = values
            .map(
                (r) => `
            <tr>
                <td>${r.grade}</td>
                <td>${r.section}</td>
                <td>${r.enrollmentM}</td>
                <td>${r.enrollmentF}</td>
                <td>${r.enrollmentT}</td>
                <td>${r.present}</td>
                <td>${r.late}</td>
                <td>${r.absent}</td>
                <td>${r.excuse}</td>
            </tr>
        `
            )
            .join("");
    }

    async function loadReports() {
        if (!validateFilters()) return;

        executiveMessage.textContent = "Cargando reporte institucional...";

        try {
            const query = buildBaseQuery();
            const data = await fetchJson(`/reports/daily-institutional?${query}`);
            const rows = mergedRows(data);
            const attendance = computeAttendanceBreakdown(rows);
            const enrollment = computeEnrollmentFromRows(rows);

            fillExecutiveCards(attendance, enrollment);
            renderDetail(data);
            renderCourse(data);

            fillFlag("flagWorkday", data.is_workday);
            fillFlag("flagActivity", data.had_attendance_activity);
            fillFlag("flagNoSchool", data.possible_no_school_day);
            fillFlag("flagEarlyDismissal", data.possible_early_dismissal);

            executiveMessage.textContent =
                `Reporte cargado para ${data.date}. Presentes: ${data.total_present}, tardanzas: ${data.total_late}, ausentes: ${data.total_absent}, excusas: ${data.total_with_excuse}.`;
        } catch (error) {
            executiveMessage.textContent = error.message || "No se pudo cargar el reporte.";
            courseTableBody.innerHTML = `<tr><td colspan="9" class="empty-row">Sin datos disponibles.</td></tr>`;
            detailTableBody.innerHTML = `<tr><td colspan="9" class="empty-row">Sin datos disponibles.</td></tr>`;
        }
    }

    function openPdf(url) {
        window.open(url, "_blank", "noopener,noreferrer");
    }

    function handlePdfGlobal() {
        if (!validateFilters()) return;
        openPdf(`/reports/print/global.pdf?${buildBaseQuery()}`);
    }

    function handlePdfCourse() {
        if (!validateFilters()) return;

        const grade = window.prompt("Escribe el curso. Ejemplo: 5to");
        if (!grade || !grade.trim()) return;

        const section = window.prompt("Escribe la sección si deseas filtrar. Déjalo vacío para todas.");

        let query = `${buildBaseQuery()}&grade=${encodeURIComponent(grade.trim())}`;
        if (section && section.trim()) {
            query += `&section=${encodeURIComponent(section.trim())}`;
        }

        openPdf(`/reports/print/by-course.pdf?${query}`);
    }

    function handlePdfSection() {
        if (!validateFilters()) return;

        const section = window.prompt("Escribe la sección. Ejemplo: A");
        if (!section || !section.trim()) return;

        const query = `${buildBaseQuery()}&section=${encodeURIComponent(section.trim())}`;
        openPdf(`/reports/print/by-section.pdf?${query}`);
    }

    function handlePdfMultiCourse() {
        if (!validateFilters()) return;

        const gradesInput = window.prompt("Escribe varios cursos separados por coma. Ejemplo: 4to,5to,6to");
        if (!gradesInput || !gradesInput.trim()) return;

        const grades = gradesInput
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);

        if (!grades.length) return;

        const query = `${buildBaseQuery()}&${grades.map((grade) => `grades=${encodeURIComponent(grade)}`).join("&")}`;
        openPdf(`/reports/print/by-multi-course.pdf?${query}`);
    }

    function handlePdfExcuses() {
        if (!validateFilters()) return;

        const grade = window.prompt("Escribe el curso para filtrar excusas. Déjalo vacío para todos.");
        const section = window.prompt("Escribe la sección si deseas filtrar. Déjalo vacío para todas.");

        let query = buildBaseQuery();

        if (grade && grade.trim()) {
            query += `&grade=${encodeURIComponent(grade.trim())}`;
        }

        if (section && section.trim()) {
            query += `&section=${encodeURIComponent(section.trim())}`;
        }

        openPdf(`/reports/print/excuses.pdf?${query}`);
    }

    document.getElementById("loadReportsBtn").addEventListener("click", loadReports);
    document.getElementById("btnPdfGlobal").addEventListener("click", handlePdfGlobal);
    document.getElementById("btnPdfCourse").addEventListener("click", handlePdfCourse);
    document.getElementById("btnPdfSection").addEventListener("click", handlePdfSection);
    document.getElementById("btnPdfMultiCourse").addEventListener("click", handlePdfMultiCourse);
    document.getElementById("btnPdfExcuses").addEventListener("click", handlePdfExcuses);

    await loadCenters();
    await loadYears();
});