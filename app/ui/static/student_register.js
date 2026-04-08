const form = document.getElementById("studentRegisterForm");
const alertBox = document.getElementById("alertBox");
const saveBtn = document.getElementById("saveBtn");
const resetBtn = document.getElementById("resetBtn");

const centerSelect = document.getElementById("center_id");
const schoolYearSelect = document.getElementById("school_year_id");

const resultPanel = document.getElementById("resultPanel");
const resultSummary = document.getElementById("resultSummary");
const resultStudentCode = document.getElementById("resultStudentCode");
const resultStudentId = document.getElementById("resultStudentId");
const resultCardId = document.getElementById("resultCardId");
const resultCardCode = document.getElementById("resultCardCode");
const openFrontBtn = document.getElementById("openFrontBtn");
const openBackBtn = document.getElementById("openBackBtn");
const openStudentBtn = document.getElementById("openStudentBtn");

let allSchoolYears = [];
let alertTimeoutId = null;

function showAlert(message, type = "success") {
  if (alertTimeoutId) {
    clearTimeout(alertTimeoutId);
  }

  alertBox.textContent = message;
  alertBox.className = `alert-box ${type}`;

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });

  if (type === "success") {
    alertTimeoutId = window.setTimeout(() => {
      hideAlert();
    }, 5000);
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

function hideResultPanel() {
  resultPanel.classList.add("hidden");

  resultSummary.textContent = "El estudiante fue registrado correctamente.";
  resultStudentCode.textContent = "---";
  resultStudentId.textContent = "-";
  resultCardId.textContent = "-";
  resultCardCode.textContent = "-";

  [openFrontBtn, openBackBtn, openStudentBtn].forEach((btn) => {
    btn.classList.add("hidden");
    btn.removeAttribute("href");
  });
}

function showResultPanel(result) {
  const student = result.student;
  const card = result.card;

  resultSummary.textContent = `El estudiante ${student.first_name} ${student.last_name} fue registrado con éxito y su carnet quedó generado.`;
  resultStudentCode.textContent = student.student_code || "---";
  resultStudentId.textContent = student.id ?? "-";
  resultCardId.textContent = card.id ?? "-";
  resultCardCode.textContent = card.card_code ?? "-";

  openFrontBtn.href = `/students/${student.id}/card/front`;
  openBackBtn.href = `/students/${student.id}/card/back`;
  openStudentBtn.href = `/students/${student.id}`;

  openFrontBtn.classList.remove("hidden");
  openBackBtn.classList.remove("hidden");
  openStudentBtn.classList.remove("hidden");

  resultPanel.classList.remove("hidden");
}

function getValue(id) {
  return document.getElementById(id).value.trim();
}

function setSchoolYearOptions(centerId) {
  schoolYearSelect.innerHTML = "";

  if (!centerId) {
    schoolYearSelect.disabled = true;
    schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
    return;
  }

  const filtered = allSchoolYears.filter(
    (item) => String(item.center_id) === String(centerId)
  );

  if (filtered.length === 0) {
    schoolYearSelect.disabled = true;
    schoolYearSelect.innerHTML = '<option value="">No hay años escolares para este centro</option>';
    return;
  }

  schoolYearSelect.disabled = false;
  schoolYearSelect.innerHTML = '<option value="">Seleccione un año escolar</option>';

  filtered.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name;
    schoolYearSelect.appendChild(option);
  });
}

async function loadCenters() {
  const response = await fetch("/centers/");
  if (!response.ok) {
    throw new Error("No se pudieron cargar los centros.");
  }

  const centers = await response.json();

  centerSelect.innerHTML = '<option value="">Seleccione un centro</option>';

  centers.forEach((center) => {
    const option = document.createElement("option");
    option.value = center.id;
    option.textContent = `${center.name} (${center.code})`;
    centerSelect.appendChild(option);
  });
}

async function loadSchoolYears() {
  const response = await fetch("/school-years/");
  if (!response.ok) {
    throw new Error("No se pudieron cargar los años escolares.");
  }

  allSchoolYears = await response.json();
}

function getRegisterPayload() {
  return {
    center_id: Number(centerSelect.value),
    school_year_id: Number(schoolYearSelect.value),
    student_code: getValue("student_code"),
    minerd_id: getValue("minerd_id") || null,
    first_name: getValue("first_name"),
    last_name: getValue("last_name"),
    birth_date: getValue("birth_date") || null,
    gender: getValue("gender") || null,
    grade: getValue("grade"),
    section: getValue("section"),
    photo_path: getValue("photo_path") || null,
    is_active: document.getElementById("is_active").value === "true",
    guardian: {
      full_name: getValue("guardian_full_name"),
      relationship_type: getValue("relationship_type"),
      phone: getValue("guardian_phone") || null,
      whatsapp: getValue("guardian_whatsapp") || null,
      email: getValue("guardian_email") || null,
    },
  };
}

function validateForm() {
  if (!centerSelect.value) return "Debes seleccionar un centro educativo.";
  if (!schoolYearSelect.value) return "Debes seleccionar un año escolar.";
  if (!getValue("student_code")) return "El código interno del estudiante es obligatorio.";
  if (!getValue("first_name")) return "Los nombres del estudiante son obligatorios.";
  if (!getValue("last_name")) return "Los apellidos del estudiante son obligatorios.";
  if (!getValue("grade")) return "El curso o grado es obligatorio.";
  if (!getValue("section")) return "La sección es obligatoria.";
  if (!getValue("guardian_full_name")) return "El nombre del tutor principal es obligatorio.";
  if (!getValue("relationship_type")) return "El parentesco del tutor principal es obligatorio.";

  return null;
}

async function submitForm(event) {
  event.preventDefault();
  hideAlert();
  hideResultPanel();

  const validationError = validateForm();
  if (validationError) {
    showAlert(validationError, "error");
    return;
  }

  const payload = getRegisterPayload();

  saveBtn.disabled = true;
  saveBtn.textContent = "Registrando...";

  try {
    const response = await fetch("/students/with-guardian-and-card", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok) {
      const detail = result?.detail || "No se pudo completar el registro del estudiante.";
      throw new Error(detail);
    }

    form.reset();
    schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
    schoolYearSelect.disabled = true;

    showAlert(
      `Registro completado correctamente. Estudiante ID: ${result.student.id}. Carnet ID: ${result.card.id}. Código del carnet: ${result.card.card_code}.`,
      "success"
    );

    showResultPanel(result);

    console.log("Registro completo:", result);
  } catch (error) {
    showAlert(error.message || "Ocurrió un error durante el registro.", "error");
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Registrar estudiante";
  }
}

function resetForm() {
  form.reset();
  schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
  schoolYearSelect.disabled = true;
  hideAlert();
  hideResultPanel();
}

function bindEvents() {
  form.addEventListener("submit", submitForm);
  resetBtn.addEventListener("click", resetForm);

  centerSelect.addEventListener("change", (event) => {
    setSchoolYearOptions(event.target.value);
  });
}

async function initPage() {
  hideAlert();
  hideResultPanel();

  try {
    await Promise.all([loadCenters(), loadSchoolYears()]);
    schoolYearSelect.disabled = true;
    schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
  } catch (error) {
    showAlert(error.message || "No se pudo inicializar el formulario.", "error");
  }
}

bindEvents();
initPage();