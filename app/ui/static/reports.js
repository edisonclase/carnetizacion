document.addEventListener("DOMContentLoaded", async () => {
    await requireAuth(["super_admin", "admin_centro", "registro", "consulta"]);

    const centerSelect = document.getElementById("centerId");
    const schoolYearSelect = document.getElementById("schoolYearId");
    const dateInput = document.getElementById("reportDate");
    const courseTableBody = document.getElementById("courseTableBody");
    const detailTableBody = document.getElementById("detailTableBody");

    dateInput.value = new Date().toISOString().split("T")[0];

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

    function renderDetail(data) {
        const rows = [
            ...(data.present_students || []),
            ...(data.late_students || []),
            ...(data.absent_students || []),
        ];

        if (!rows.length) {
            detailTableBody.innerHTML = `<tr><td colspan="5" class="empty-row">Sin datos disponibles.</td></tr>`;
            return;
        }

        detailTableBody.innerHTML = rows
            .map(
                (r) => `
            <tr>
                <td>${r.status}</td>
                <td>${r.full_name}</td>
                <td>${r.student_code ?? "-"}</td>
                <td>${r.grade}</td>
                <td>${r.section}</td>
            </tr>
        `
            )
            .join("");
    }

    function renderCourse(data) {
        const map = {};
        const rows = [
            ...(data.present_students || []),
            ...(data.late_students || []),
            ...(data.absent_students || []),
        ];

        rows.forEach((r) => {
            const key = `${r.grade}-${r.section}`;
            if (!map[key]) {
                map[key] = {
                    grade: r.grade,
                    section: r.section,
                    total: 0,
                    present: 0,
                    late: 0,
                    absent: 0,
                    excuse: 0,
                };
            }

            map[key].total += 1;

            if (r.status === "present") map[key].present += 1;
            if (r.status === "late") map[key].late += 1;
            if (r.status === "absent") map[key].absent += 1;
            if (r.has_excuse) map[key].excuse += 1;
        });

        const values = Object.values(map);

        if (!values.length) {
            courseTableBody.innerHTML = `<tr><td colspan="7" class="empty-row">Sin datos disponibles.</td></tr>`;
            return;
        }

        courseTableBody.innerHTML = values
            .map(
                (r) => `
            <tr>
                <td>${r.grade}</td>
                <td>${r.section}</td>
                <td>${r.total}</td>
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

        const query = buildBaseQuery();
        const data = await fetchJson(`/reports/daily-institutional?${query}`);

        renderDetail(data);
        renderCourse(data);
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