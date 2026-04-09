const tableBody = document.getElementById("studentsTable");

const centerFilter = document.getElementById("centerFilter");
const yearFilter = document.getElementById("yearFilter");
const gradeFilter = document.getElementById("gradeFilter");
const sectionFilter = document.getElementById("sectionFilter");

const filterBtn = document.getElementById("filterBtn");
const clearBtn = document.getElementById("clearBtn");

const selectAllCheckbox = document.getElementById("selectAll");
const printSelectedBtn = document.getElementById("printSelectedBtn");
const clearSelectedBtn = document.getElementById("clearSelectedBtn");
const resultCount = document.getElementById("resultCount");
const selectedCount = document.getElementById("selectedCount");
const alertBox = document.getElementById("alertBox");

const STORAGE_KEY = "nova_id_selected_students";

let students = [];
let filteredStudents = [];
let centers = [];
let schoolYears = [];
let alertTimeoutId = null;
let selectedStudents = new Set();

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

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function loadSelectionFromStorage() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            selectedStudents = new Set();
            return;
        }

        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) {
            selectedStudents = new Set();
            return;
        }

        selectedStudents = new Set(parsed.map(String));
    } catch (error) {
        console.error("No se pudo leer la selección guardada.", error);
        selectedStudents = new Set();
    }
}

function saveSelectionToStorage() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(selectedStudents)));
    } catch (error) {
        console.error("No se pudo guardar la selección.", error);
    }
}

function setFiltersFromUrl() {
    const params = new URLSearchParams(window.location.search);

    centerFilter.value = params.get("center_id") ?? "";
    yearFilter.value = params.get("school_year_id") ?? "";
    gradeFilter.value = params.get("grade") ?? "";
    sectionFilter.value = params.get("section") ?? "";
}

function updateUrlWithFilters() {
    const params = new URLSearchParams();

    if (centerFilter.value) params.set("center_id", centerFilter.value);
    if (yearFilter.value) params.set("school_year_id", yearFilter.value);
    if (gradeFilter.value) params.set("grade", gradeFilter.value);
    if (sectionFilter.value) params.set("section", sectionFilter.value);

    const newUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}`;
    window.history.replaceState({}, "", newUrl);
}

function getStudentsUrl() {
    const params = new URLSearchParams();

    if (centerFilter.value) params.set("center_id", centerFilter.value);
    if (yearFilter.value) params.set("school_year_id", yearFilter.value);
    if (gradeFilter.value) params.set("grade", gradeFilter.value);
    if (sectionFilter.value) params.set("section", sectionFilter.value);

    return `/students/${params.toString() ? `?${params.toString()}` : ""}`;
}

async function loadFilters() {
    const [centersResponse, schoolYearsResponse] = await Promise.all([
        fetch("/centers/"),
        fetch("/school-years/")
    ]);

    if (!centersResponse.ok || !schoolYearsResponse.ok) {
        throw new Error("No se pudieron cargar centros o años escolares.");
    }

    centers = await centersResponse.json();
    schoolYears = await schoolYearsResponse.json();

    centerFilter.innerHTML = `<option value="">Todos los centros</option>`;
    yearFilter.innerHTML = `<option value="">Todos los años</option>`;

    centers.forEach((c) => {
        centerFilter.innerHTML += `<option value="${c.id}">${escapeHtml(c.name)}</option>`;
    });

    schoolYears.forEach((y) => {
        yearFilter.innerHTML += `<option value="${y.id}">${escapeHtml(y.name)}</option>`;
    });

    setFiltersFromUrl();
}

async function loadStudents() {
    const response = await fetch(getStudentsUrl());

    if (!response.ok) {
        throw new Error("No se pudo cargar el listado de estudiantes.");
    }

    students = await response.json();
    filteredStudents = [...students];

    buildDynamicFiltersFromCurrentData();
    renderTable(filteredStudents);
    resultCount.textContent = `${filteredStudents.length} estudiante(s) encontrado(s)`;
    updateSelectedState();
}

function buildDynamicFiltersFromCurrentData() {
    const selectedGrade = gradeFilter.value;
    const selectedSection = sectionFilter.value;

    const grades = [...new Set(students.map((s) => s.grade).filter(Boolean))].sort((a, b) =>
        a.localeCompare(b, "es")
    );

    const sectionsBase = students.filter((s) => {
        return !selectedGrade || String(s.grade) === String(selectedGrade);
    });

    const sections = [...new Set(sectionsBase.map((s) => s.section).filter(Boolean))].sort((a, b) =>
        a.localeCompare(b, "es")
    );

    gradeFilter.innerHTML = `<option value="">Todos los cursos</option>`;
    sectionFilter.innerHTML = `<option value="">Todas las secciones</option>`;

    grades.forEach((grade) => {
        gradeFilter.innerHTML += `<option value="${escapeHtml(grade)}">${escapeHtml(grade)}</option>`;
    });

    sections.forEach((section) => {
        sectionFilter.innerHTML += `<option value="${escapeHtml(section)}">${escapeHtml(section)}</option>`;
    });

    if (grades.includes(selectedGrade)) {
        gradeFilter.value = selectedGrade;
    } else {
        gradeFilter.value = "";
    }

    if (sections.includes(selectedSection)) {
        sectionFilter.value = selectedSection;
    } else {
        sectionFilter.value = "";
    }
}

function renderTable(data) {
    tableBody.innerHTML = "";

    if (!data.length) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-row">No se encontraron estudiantes con esos filtros.</td>
            </tr>
        `;
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }

    data.forEach((student) => {
        const row = document.createElement("tr");
        const statusClass = student.is_active ? "status-active" : "status-inactive";
        const statusLabel = student.is_active ? "Activo" : "Inactivo";
        const fullName = `${student.first_name ?? ""} ${student.last_name ?? ""}`.trim();
        const isChecked = selectedStudents.has(String(student.id));

        row.innerHTML = `
            <td>
                <input
                    type="checkbox"
                    class="studentCheck"
                    value="${student.id}"
                    ${isChecked ? "checked" : ""}
                    aria-label="Seleccionar estudiante ${escapeHtml(fullName)}"
                >
            </td>
            <td>${escapeHtml(student.student_code ?? "-")}</td>
            <td>${escapeHtml(fullName || "-")}</td>
            <td>${escapeHtml(student.minerd_id ?? "-")}</td>
            <td>${escapeHtml(student.grade ?? "-")}</td>
            <td>${escapeHtml(student.section ?? "-")}</td>
            <td>
                <span class="status-badge ${statusClass}">${statusLabel}</span>
            </td>
            <td>
                <div class="action-stack">
                    <button type="button" class="btn btn-primary" onclick="viewFront(${student.id})">Ver</button>
                    <button type="button" class="btn btn-neutral" onclick="editStudent(${student.id})">Editar</button>
                    <button type="button" class="btn btn-success" onclick="printStudent(${student.id})">Imprimir</button>
                </div>
            </td>
        `;

        tableBody.appendChild(row);
    });

    document.querySelectorAll(".studentCheck").forEach((checkbox) => {
        checkbox.addEventListener("change", handleStudentCheckboxChange);
    });

    syncVisibleCheckboxesWithSelection();
    updateSelectedState();
}

function handleStudentCheckboxChange(event) {
    const id = String(event.target.value);

    if (event.target.checked) {
        selectedStudents.add(id);
    } else {
        selectedStudents.delete(id);
    }

    saveSelectionToStorage();
    updateSelectedState();
}

function syncVisibleCheckboxesWithSelection() {
    document.querySelectorAll(".studentCheck").forEach((checkbox) => {
        checkbox.checked = selectedStudents.has(String(checkbox.value));
    });
}

function getVisibleStudentIds() {
    return filteredStudents.map((student) => String(student.id));
}

function getSelectedVisibleStudentIds() {
    const visibleIds = new Set(getVisibleStudentIds());
    return Array.from(selectedStudents).filter((id) => visibleIds.has(String(id)));
}

function updateSelectedState() {
    const visibleIds = getVisibleStudentIds();
    const selectedVisibleIds = getSelectedVisibleStudentIds();

    selectedCount.textContent = `${selectedStudents.size} seleccionado(s)`;
    printSelectedBtn.disabled = selectedStudents.size === 0;
    clearSelectedBtn.disabled = selectedStudents.size === 0;

    if (visibleIds.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }

    if (selectedVisibleIds.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }

    if (selectedVisibleIds.length === visibleIds.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
        return;
    }

    selectAllCheckbox.checked = false;
    selectAllCheckbox.indeterminate = true;
}

function clearAllSelection() {
    selectedStudents.clear();
    saveSelectionToStorage();
    syncVisibleCheckboxesWithSelection();
    updateSelectedState();
}

async function applyServerFilters() {
    updateUrlWithFilters();
    await loadStudents();
}

selectAllCheckbox.addEventListener("change", () => {
    const visibleIds = getVisibleStudentIds();

    if (selectAllCheckbox.checked) {
        visibleIds.forEach((id) => selectedStudents.add(String(id)));
    } else {
        visibleIds.forEach((id) => selectedStudents.delete(String(id)));
    }

    saveSelectionToStorage();
    syncVisibleCheckboxesWithSelection();
    updateSelectedState();
});

printSelectedBtn.addEventListener("click", () => {
    const selected = Array.from(selectedStudents);

    if (selected.length === 0) {
        showAlert("Selecciona al menos un estudiante.", "error");
        return;
    }

    const params = new URLSearchParams();
    selected.forEach((id) => params.append("ids", id));

    window.open(`/students/cards/print-multiple?${params.toString()}`, "_blank");
});

clearSelectedBtn.addEventListener("click", () => {
    clearAllSelection();
    showAlert("La selección fue limpiada.", "success");
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

filterBtn.addEventListener("click", async () => {
    try {
        hideAlert();
        await applyServerFilters();
    } catch (error) {
        showAlert("No se pudieron aplicar los filtros.", "error");
        console.error(error);
    }
});

clearBtn.addEventListener("click", async () => {
    try {
        centerFilter.value = "";
        yearFilter.value = "";
        gradeFilter.value = "";
        sectionFilter.value = "";

        hideAlert();
        await applyServerFilters();
    } catch (error) {
        showAlert("No se pudieron limpiar los filtros.", "error");
        console.error(error);
    }
});

centerFilter.addEventListener("change", async () => {
    gradeFilter.value = "";
    sectionFilter.value = "";
});

yearFilter.addEventListener("change", async () => {
    gradeFilter.value = "";
    sectionFilter.value = "";
});

gradeFilter.addEventListener("change", () => {
    const selectedGrade = gradeFilter.value;
    const selectedSection = sectionFilter.value;

    const sectionsBase = students.filter((s) => {
        return !selectedGrade || String(s.grade) === String(selectedGrade);
    });

    const sections = [...new Set(sectionsBase.map((s) => s.section).filter(Boolean))].sort((a, b) =>
        a.localeCompare(b, "es")
    );

    sectionFilter.innerHTML = `<option value="">Todas las secciones</option>`;
    sections.forEach((section) => {
        sectionFilter.innerHTML += `<option value="${escapeHtml(section)}">${escapeHtml(section)}</option>`;
    });

    if (sections.includes(selectedSection)) {
        sectionFilter.value = selectedSection;
    } else {
        sectionFilter.value = "";
    }
});

async function init() {
    try {
        hideAlert();
        loadSelectionFromStorage();
        await loadFilters();
        await loadStudents();
    } catch (error) {
        showAlert("No se pudieron cargar los datos del listado.", "error");
        console.error(error);
    }
}

init();