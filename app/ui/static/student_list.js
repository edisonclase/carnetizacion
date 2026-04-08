const alertBox = document.getElementById("alertBox");
const centerFilter = document.getElementById("centerFilter");
const schoolYearFilter = document.getElementById("schoolYearFilter");
const gradeFilter = document.getElementById("gradeFilter");
const sectionFilter = document.getElementById("sectionFilter");
const searchFilter = document.getElementById("searchFilter");
const clearFiltersBtn = document.getElementById("clearFiltersBtn");
const reloadStudentsBtn = document.getElementById("reloadStudentsBtn");
const studentsTableBody = document.getElementById("studentsTableBody");
const resultCount = document.getElementById("resultCount");

let centers = [];
let schoolYears = [];
let students = [];
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

function getCenterName(centerId) {
  const center = centers.find((item) => item.id === centerId);
  return center ? center.name : "-";
}

function getSchoolYearName(schoolYearId) {
  const schoolYear = schoolYears.find((item) => item.id === schoolYearId);
  return schoolYear ? schoolYear.name : "-";
}

function renderTable(rows) {
  if (!rows.length) {
    studentsTableBody.innerHTML = `
      <tr>
        <td colspan="10" class="empty-row">No se encontraron estudiantes con los filtros aplicados.</td>
      </tr>
    `;
    resultCount.textContent = "0 resultados";
    return;
  }

  studentsTableBody.innerHTML = rows.map((student) => {
    const fullName = `${student.first_name} ${student.last_name}`;
    const statusClass = student.is_active ? "status-active" : "status-inactive";
    const statusLabel = student.is_active ? "Activo" : "Inactivo";

    return `
      <tr>
        <td>${student.id}</td>
        <td>${student.student_code ?? "-"}</td>
        <td>${fullName}</td>
        <td>${student.minerd_id ?? "-"}</td>
        <td>${getCenterName(student.center_id)}</td>
        <td>${getSchoolYearName(student.school_year_id)}</td>
        <td>${student.grade ?? "-"}</td>
        <td>${student.section ?? "-"}</td>
        <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
        <td>
          <div class="action-stack">
            <a class="btn btn-primary" target="_blank" rel="noopener noreferrer" href="/students/${student.id}/card/front">Frontal</a>
            <a class="btn btn-secondary" target="_blank" rel="noopener noreferrer" href="/students/${student.id}/card/back">Reverso</a>
            <a class="btn btn-success" target="_blank" rel="noopener noreferrer" href="/admin/students/${student.id}/print">Imprimir</a>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  resultCount.textContent = `${rows.length} resultado(s)`;
}

function applyFilters() {
  const centerId = centerFilter.value;
  const schoolYearId = schoolYearFilter.value;
  const grade = gradeFilter.value.trim().toLowerCase();
  const section = sectionFilter.value.trim().toLowerCase();
  const search = searchFilter.value.trim().toLowerCase();

  const filtered = students.filter((student) => {
    const matchesCenter = !centerId || String(student.center_id) === String(centerId);
    const matchesSchoolYear = !schoolYearId || String(student.school_year_id) === String(schoolYearId);
    const matchesGrade = !grade || (student.grade || "").toLowerCase().includes(grade);
    const matchesSection = !section || (student.section || "").toLowerCase().includes(section);

    const fullName = `${student.first_name || ""} ${student.last_name || ""}`.toLowerCase();
    const code = (student.student_code || "").toLowerCase();
    const minerd = (student.minerd_id || "").toLowerCase();

    const matchesSearch =
      !search ||
      fullName.includes(search) ||
      code.includes(search) ||
      minerd.includes(search);

    return matchesCenter && matchesSchoolYear && matchesGrade && matchesSection && matchesSearch;
  });

  renderTable(filtered);
}

function populateFilters() {
  centerFilter.innerHTML = '<option value="">Todos los centros</option>';
  schoolYearFilter.innerHTML = '<option value="">Todos los años</option>';

  centers.forEach((center) => {
    const option = document.createElement("option");
    option.value = center.id;
    option.textContent = `${center.name} (${center.code})`;
    centerFilter.appendChild(option);
  });

  schoolYears.forEach((schoolYear) => {
    const option = document.createElement("option");
    option.value = schoolYear.id;
    option.textContent = schoolYear.name;
    schoolYearFilter.appendChild(option);
  });
}

async function loadData() {
  hideAlert();
  reloadStudentsBtn.disabled = true;
  reloadStudentsBtn.textContent = "Recargando...";

  try {
    const [centersRes, schoolYearsRes, studentsRes] = await Promise.all([
      fetch("/centers/"),
      fetch("/school-years/"),
      fetch("/students/"),
    ]);

    if (!centersRes.ok) throw new Error("No se pudieron cargar los centros.");
    if (!schoolYearsRes.ok) throw new Error("No se pudieron cargar los años escolares.");
    if (!studentsRes.ok) throw new Error("No se pudieron cargar los estudiantes.");

    centers = await centersRes.json();
    schoolYears = await schoolYearsRes.json();
    students = await studentsRes.json();

    populateFilters();
    applyFilters();
  } catch (error) {
    showAlert(error.message || "No se pudo cargar el listado.", "error");
  } finally {
    reloadStudentsBtn.disabled = false;
    reloadStudentsBtn.textContent = "Recargar listado";
  }
}

function clearFilters() {
  centerFilter.value = "";
  schoolYearFilter.value = "";
  gradeFilter.value = "";
  sectionFilter.value = "";
  searchFilter.value = "";
  applyFilters();
}

function bindEvents() {
  [centerFilter, schoolYearFilter, gradeFilter, sectionFilter, searchFilter].forEach((field) => {
    field.addEventListener("input", applyFilters);
    field.addEventListener("change", applyFilters);
  });

  clearFiltersBtn.addEventListener("click", clearFilters);
  reloadStudentsBtn.addEventListener("click", loadData);
}

bindEvents();
loadData();