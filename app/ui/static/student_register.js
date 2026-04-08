const form = document.getElementById("studentRegisterForm");
const alertBox = document.getElementById("alertBox");
const saveBtn = document.getElementById("saveBtn");
const resetBtn = document.getElementById("resetBtn");

const centerSelect = document.getElementById("center_id");
const schoolYearSelect = document.getElementById("school_year_id");

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

function getStudentPayload() {
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
  };
}

function getGuardianPayload(studentId) {
  return {
    student_id: studentId,
    full_name: getValue("guardian_full_name"),
    relationship_type: getValue("relationship_type"),
    phone: getValue("guardian_phone") || null,
    whatsapp: getValue("guardian_whatsapp") || null,
    email: getValue("guardian_email") || null,
    is_primary: true,
    is_active: true,
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

  const validationError = validateForm();
  if (validationError) {
    showAlert(validationError, "error");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.textContent = "Registrando...";

  try {
    const studentPayload = getStudentPayload();

    const studentResponse = await fetch("/students/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(studentPayload),
    });

    const studentResult = await studentResponse.json();

    if (!studentResponse.ok) {
      throw new Error(studentResult?.detail || "No se pudo registrar el estudiante.");
    }

    const guardianPayload = getGuardianPayload(studentResult.id);

    const guardianResponse = await fetch("/guardians/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(guardianPayload),
    });

    const guardianResult = await guardianResponse.json();

    if (!guardianResponse.ok) {
      throw new Error(guardianResult?.detail || "El estudiante fue creado, pero no se pudo registrar el tutor principal.");
    }

    form.reset();
    schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
    schoolYearSelect.disabled = true;

    showAlert(
      `Estudiante registrado correctamente. ID interno generado: ${studentResult.id}. Tutor principal registrado con éxito.`,
      "success"
    );
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