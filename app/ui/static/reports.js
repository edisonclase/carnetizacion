document.addEventListener("DOMContentLoaded", async () => {
    const user = await requireAuth(["super_admin", "admin_centro", "registro", "consulta"]);

    const centerSelect = document.getElementById("centerId");
    const schoolYearSelect = document.getElementById("schoolYearId");
    const dateInput = document.getElementById("reportDate");

    dateInput.value = new Date().toISOString().split("T")[0];

    async function loadCenters() {
        const centers = await apiFetch("/centers/").then(r => r.json());
        centerSelect.innerHTML = centers.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    }

    async function loadYears() {
        const years = await apiFetch("/school-years/").then(r => r.json());
        schoolYearSelect.innerHTML = years.map(y => `<option value="${y.id}">${y.name}</option>`).join("");
    }

    async function loadReports() {
        const center = centerSelect.value;
        const year = schoolYearSelect.value;
        const date = dateInput.value;

        const res = await apiFetch(`/reports/daily-institutional?center_id=${center}&school_year_id=${year}&date=${date}`);
        const data = await res.json();

        renderDetail(data);
        renderCourse(data);
    }

    function renderDetail(data) {
        const tbody = document.getElementById("detailTableBody");

        const rows = [
            ...data.present_students,
            ...data.late_students,
            ...data.absent_students
        ];

        tbody.innerHTML = rows.map(r => `
            <tr>
                <td>${r.status}</td>
                <td>${r.full_name}</td>
                <td>${r.student_code}</td>
                <td>${r.grade}</td>
                <td>${r.section}</td>
            </tr>
        `).join("");
    }

    function renderCourse(data) {
        const tbody = document.getElementById("courseTableBody");

        const map = {};

        const rows = [
            ...data.present_students,
            ...data.late_students,
            ...data.absent_students
        ];

        rows.forEach(r => {
            const key = `${r.grade}-${r.section}`;
            if (!map[key]) {
                map[key] = { grade: r.grade, section: r.section, total: 0, present: 0, late: 0, absent: 0, excuse: 0 };
            }

            map[key].total++;

            if (r.status === "present") map[key].present++;
            if (r.status === "late") map[key].late++;
            if (r.status === "absent") map[key].absent++;
            if (r.has_excuse) map[key].excuse++;
        });

        tbody.innerHTML = Object.values(map).map(r => `
            <tr>
                <td>${r.grade}</td>
                <td>${r.section}</td>
                <td>${r.total}</td>
                <td>${r.present}</td>
                <td>${r.late}</td>
                <td>${r.absent}</td>
                <td>${r.excuse}</td>
            </tr>
        `).join("");
    }

    document.getElementById("loadReportsBtn").addEventListener("click", loadReports);

    await loadCenters();
    await loadYears();
});