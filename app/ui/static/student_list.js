const tableBody = document.getElementById("studentsTable");

const centerFilter = document.getElementById("centerFilter");
const yearFilter = document.getElementById("yearFilter");
const gradeFilter = document.getElementById("gradeFilter");
const sectionFilter = document.getElementById("sectionFilter");

const filterBtn = document.getElementById("filterBtn");
const clearBtn = document.getElementById("clearBtn");

const selectAllCheckbox = document.getElementById("selectAll");
const printSelectedBtn = document.getElementById("printSelectedBtn");
const resultCount = document.getElementById("resultCount");
const alertBox = document.getElementById("alertBox");

let students = [];
let filteredStudents = [];
let centers = [];
let schoolYears = [];
let alertTimeoutId = null;

function showAlert(message, type = "success") {
    if (alertTimeoutId) {
        clearTimeout(alertTimeoutId);
    }

    alertBox.textContent = message;
    alertBox.className = `alert-box ${type}`;

    if (type === "success") {
        alertTimeoutId = window.setTimeout(() => {
            hideAlert();
        }, 3500);
    }
}

function hideAlert() {
    if (alertTimeoutId) {
        clearTimeout(alertTimeoutId);
        alertTimeoutId = null;
    }

    alertBox.textContent = "";
    alertBox.className = "alert-box hidden";
}

async function loadFilters() {
    centers = await fetch("/centers/").then((r) => r.json());
    schoolYears = await fetch("/school-years/").then((r) => r.json());

    centerFilter.innerHTML = `<option value="">Todos los centros</option>`;
    yearFilter.innerHTML = `<option value="">Todos los años</option>`;

    centers.forEach((c) => {
        centerFilter.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });

    schoolYears.forEach((y) => {
        yearFilter.innerHTML += `<option value="${y.id}">${y.name}</option>`;
    });
}

async function loadStudents() {
    students = await fetch("/students/").then((r) => r.json());
    filteredStudents = [...students];

    buildDynamicFilters(filteredStudents);
    renderTable(filteredStudents);
}

function buildDynamicFilters(data) {
    const selectedGrade = gradeFilter.value;
    const selectedSection = sectionFilter.value;

    const grades = [...new Set(data.map((s) => s.grade).filter(Boolean))].sort();
    const sections = [...new Set(data.map((s) => s.section).filter(Boolean))].sort();

    gradeFilter.innerHTML = `<option value="">Todos los cursos</option>`;
    sectionFilter.innerHTML = `<option value="">Todas las secciones</option>`;

    grades.forEach((g) => {
        gradeFilter.innerHTML += `<option value="${g}">${g}</option>`;
    });

    sections.forEach((s) => {
        sectionFilter.innerHTML += `<option value="${s}">${s}</option>`;
    });

    if (grades.includes(selectedGrade)) {
        gradeFilter.value = selectedGrade;
    }

    if (sections.includes(selectedSection)) {
        sectionFilter.value = selectedSection;
    }
}

function applyFilters() {
    const centerValue = centerFilter.value;
    const yearValue = yearFilter.value;
    const gradeValue = gradeFilter.value;
    const sectionValue = sectionFilter.value;

    filteredStudents = students.filter((s) => {
        return (
            (!centerValue || String(s.center_id) === String(centerValue)) &&
            (!yearValue || String(s.school_year_id) === String(yearValue)) &&
            (!gradeValue || s.grade === gradeValue) &&
            (!sectionValue || s.section === sectionValue)
        );
    });

    renderTable(filteredStudents);
    resultCount.textContent = `${filteredStudents.length} estudiante(s) encontrado(s)`;
}

function renderTable(data) {
    tableBody.innerHTML = "";

    if (!data.length) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">No se encontraron estudiantes con esos filtros.</td>
            </tr>
        `;
        return;
    }

    data.forEach((student) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>
                <input type="checkbox" class="studentCheck" value="${student.id}">
            </td>
            <td>${student.student_code ?? "-"}</td>
            <td>${student.first_name} ${student.last_name}</td>
            <td>${student.grade ?? "-"}</td>
            <td>${student.section ?? "-"}</td>
            <td>
                <div class="action-stack">
                    <button class="btn btn-primary" onclick="viewFront(${student.id})">Ver</button>
                    <button class="btn btn-neutral" onclick="editStudent(${student.id})">Editar</button>
                    <button class="btn btn-success" onclick="printStudent(${student.id})">Imprimir</button>
                </div>
            </td>
        `;

        tableBody.appendChild(row);
    });

    selectAllCheckbox.checked = false;
}

function getSelectedStudents() {
    const checks = document.querySelectorAll(".studentCheck:checked");
    return Array.from(checks).map((c) => c.value);
}

selectAllCheckbox.addEventListener("change", () => {
    document.querySelectorAll(".studentCheck").forEach((cb) => {
        cb.checked = selectAllCheckbox.checked;
    });
});

printSelectedBtn.addEventListener("click", () => {
    const selected = getSelectedStudents();

    if (selected.length === 0) {
        showAlert("Selecciona al menos un estudiante.", "error");
        return;
    }

    const params = new URLSearchParams();
    selected.forEach((id) => params.append("ids", id));

    window.open(`/students/cards/print-multiple?${params.toString()}`, "_blank");
});

function printStudent(id) {
    window.open(`/admin/students/${id}/print`, "_blank");
}

function viewFront(id) {
    window.open(`/students/${id}/card/front`, "_blank");
}

function editStudent(id) {
    window.location.href = `/admin/students/${id}/edit`;
}

filterBtn.addEventListener("click", () => {
    applyFilters();
});

clearBtn.addEventListener("click", () => {
    centerFilter.value = "";
    yearFilter.value = "";
    filteredStudents = [...students];
    buildDynamicFilters(filteredStudents);
    renderTable(filteredStudents);
    resultCount.textContent = `${filteredStudents.length} estudiante(s) encontrado(s)`;
    hideAlert();
});

centerFilter.addEventListener("change", () => {
    const centerValue = centerFilter.value;
    const yearValue = yearFilter.value;

    const preFiltered = students.filter((s) => {
        return (
            (!centerValue || String(s.center_id) === String(centerValue)) &&
            (!yearValue || String(s.school_year_id) === String(yearValue))
        );
    });

    buildDynamicFilters(preFiltered);
});

yearFilter.addEventListener("change", () => {
    const centerValue = centerFilter.value;
    const yearValue = yearFilter.value;

    const preFiltered = students.filter((s) => {
        return (
            (!centerValue || String(s.center_id) === String(centerValue)) &&
            (!yearValue || String(s.school_year_id) === String(yearValue))
        );
    });

    buildDynamicFilters(preFiltered);
});

async function init() {
    try {
        hideAlert();
        await loadFilters();
        await loadStudents();
        resultCount.textContent = `${filteredStudents.length} estudiante(s) encontrado(s)`;
    } catch (error) {
        showAlert("No se pudieron cargar los datos del listado.", "error");
        console.error(error);
    }
}

init();