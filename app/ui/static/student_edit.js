const bodyEl = document.body;
const studentId = bodyEl.dataset.studentId;

const form = document.getElementById("studentEditForm");
const alertBox = document.getElementById("alertBox");
const saveBtn = document.getElementById("saveBtn");
const reloadBtn = document.getElementById("reloadBtn");
const studentCodeChip = document.getElementById("studentCodeChip");

let alertTimeoutId = null;
let currentGuardianId = null;

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
    }, 4000);
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

function getField(id) {
  return document.getElementById(id);
}

function normalizeValue(value) {
  if (value === undefined || value === null) return "";
  return String(value);
}

function fillStudentForm(student) {
  getField("student_code").value = normalizeValue(student.student_code);
  getField("minerd_id").value = normalizeValue(student.minerd_id);
  getField("first_name").value = normalizeValue(student.first_name);
  getField("last_name").value = normalizeValue(student.last_name);
  getField("birth_date").value = normalizeValue(student.birth_date);
  getField("gender").value = normalizeValue(student.gender);
  getField("grade").value = normalizeValue(student.grade);
  getField("section").value = normalizeValue(student.section);
  getField("photo_path").value = normalizeValue(student.photo_path);
  getField("is_active").value = String(student.is_active);

  studentCodeChip.textContent = student.student_code || `Estudiante #${student.id}`;
}

function fillGuardianForm(guardian) {
  currentGuardianId = guardian?.id ?? null;
  getField("guardian_id").value = guardian?.id ?? "";
  getField("guardian_full_name").value = normalizeValue(guardian?.full_name);
  getField("relationship_type").value = normalizeValue(guardian?.relationship_type);
  getField("guardian_phone").value = normalizeValue(guardian?.phone);
  getField("guardian_whatsapp").value = normalizeValue(guardian?.whatsapp);
  getField("guardian_email").value = normalizeValue(guardian?.email);
}

async function loadStudentData() {
  hideAlert();

  try {
    reloadBtn.disabled = true;
    reloadBtn.textContent = "Recargando...";

    const studentResponse = await fetch(`/students/${studentId}`);
    if (!studentResponse.ok) {
      throw new Error("No se pudo cargar el estudiante.");
    }

    const student = await studentResponse.json();
    fillStudentForm(student);

    const guardiansResponse = await fetch("/guardians/");
    if (!guardiansResponse.ok) {
      throw new Error("No se pudieron cargar los tutores.");
    }

    const guardians = await guardiansResponse.json();
    const primaryGuardian =
      guardians.find(
        (guardian) =>
          guardian.student_id === Number(studentId) &&
          guardian.is_primary === true &&
          guardian.is_active === true
      ) ||
      guardians.find((guardian) => guardian.student_id === Number(studentId)) ||
      null;

    fillGuardianForm(primaryGuardian);
  } catch (error) {
    showAlert(error.message || "Ocurrió un error al cargar los datos.", "error");
  } finally {
    reloadBtn.disabled = false;
    reloadBtn.textContent = "Recargar";
  }
}

function getStudentPayload() {
  return {
    student_code: getField("student_code").value.trim(),
    minerd_id: getField("minerd_id").value.trim() || null,
    first_name: getField("first_name").value.trim(),
    last_name: getField("last_name").value.trim(),
    birth_date: getField("birth_date").value.trim() || null,
    gender: getField("gender").value.trim() || null,
    grade: getField("grade").value.trim(),
    section: getField("section").value.trim(),
    photo_path: getField("photo_path").value.trim() || null,
    is_active: getField("is_active").value === "true",
  };
}

function getGuardianPayload() {
  return {
    full_name: getField("guardian_full_name").value.trim(),
    relationship_type: getField("relationship_type").value.trim(),
    phone: getField("guardian_phone").value.trim() || null,
    whatsapp: getField("guardian_whatsapp").value.trim() || null,
    email: getField("guardian_email").value.trim() || null,
    is_primary: true,
    is_active: true,
  };
}

function validateForm() {
  if (!getField("student_code").value.trim()) {
    return "El código interno del estudiante es obligatorio.";
  }

  if (!getField("first_name").value.trim()) {
    return "Los nombres del estudiante son obligatorios.";
  }

  if (!getField("last_name").value.trim()) {
    return "Los apellidos del estudiante son obligatorios.";
  }

  if (!getField("grade").value.trim()) {
    return "El curso o grado es obligatorio.";
  }

  if (!getField("section").value.trim()) {
    return "La sección es obligatoria.";
  }

  if (!getField("guardian_full_name").value.trim()) {
    return "El nombre del tutor principal es obligatorio.";
  }

  if (!getField("relationship_type").value.trim()) {
    return "El parentesco del tutor principal es obligatorio.";
  }

  return null;
}

async function saveStudentAndGuardian(event) {
  event.preventDefault();
  hideAlert();

  const validationError = validateForm();
  if (validationError) {
    showAlert(validationError, "error");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.textContent = "Guardando...";

  try {
    const studentPayload = getStudentPayload();

    const studentResponse = await fetch(`/students/${studentId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(studentPayload),
    });

    const studentResult = await studentResponse.json();

    if (!studentResponse.ok) {
      throw new Error(studentResult?.detail || "No se pudo actualizar el estudiante.");
    }

    const guardianPayload = getGuardianPayload();

    if (currentGuardianId) {
      const guardianResponse = await fetch(`/guardians/${currentGuardianId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(guardianPayload),
      });

      const guardianResult = await guardianResponse.json();

      if (!guardianResponse.ok) {
        throw new Error(guardianResult?.detail || "El estudiante se actualizó, pero no se pudo actualizar el tutor principal.");
      }
    } else {
      const guardianCreatePayload = {
        student_id: Number(studentId),
        ...guardianPayload,
      };

      const guardianResponse = await fetch("/guardians/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(guardianCreatePayload),
      });

      const guardianResult = await guardianResponse.json();

      if (!guardianResponse.ok) {
        throw new Error(guardianResult?.detail || "El estudiante se actualizó, pero no se pudo crear el tutor principal.");
      }

      currentGuardianId = guardianResult.id;
      getField("guardian_id").value = guardianResult.id;
    }

    studentCodeChip.textContent = studentResult.student_code || `Estudiante #${studentResult.id}`;
    showAlert("Estudiante y tutor principal actualizados correctamente.", "success");
  } catch (error) {
    showAlert(error.message || "Ocurrió un error al guardar.", "error");
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Guardar cambios";
  }
}

function bindEvents() {
  form.addEventListener("submit", saveStudentAndGuardian);
  reloadBtn.addEventListener("click", loadStudentData);
}

bindEvents();
loadStudentData();