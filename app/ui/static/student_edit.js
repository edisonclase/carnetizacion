const bodyEl = document.body;
const studentId = bodyEl.dataset.studentId;

const form = document.getElementById("studentEditForm");
const alertBox = document.getElementById("alertBox");
const saveBtn = document.getElementById("saveBtn");
const reloadBtn = document.getElementById("reloadBtn");
const studentCodeChip = document.getElementById("studentCodeChip");
const logoutBtn = document.getElementById("logoutBtn");
const navRegisterLink = document.getElementById("navRegisterLink");
const navDocsLink = document.getElementById("navDocsLink");

const photoFileInput = document.getElementById("photo_file");
const photoPathInput = document.getElementById("photo_path");
const uploadPhotoBtn = document.getElementById("uploadPhotoBtn");
const photoUploadStatus = document.getElementById("photoUploadStatus");
const photoPreviewWrap = document.getElementById("photoPreviewWrap");
const photoPreview = document.getElementById("photoPreview");

let alertTimeoutId = null;
let currentGuardianId = null;
let currentUser = null;

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

function configureRoleUI(user) {
    if (user.role !== "super_admin") {
        navDocsLink.style.display = "none";
    }

    if (!canManageStudents(user.role)) {
        navRegisterLink.style.display = "none";
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }
}

function setPhotoPreview(url) {
    if (!url) {
        photoPreviewWrap.classList.add("hidden");
        photoPreview.removeAttribute("src");
        return;
    }

    photoPreview.src = url;
    photoPreviewWrap.classList.remove("hidden");
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

    setPhotoPreview(student.photo_path || "");
    photoUploadStatus.textContent = student.photo_path
        ? "Foto actual cargada."
        : "No se ha actualizado la foto.";

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

async function uploadSelectedPhoto() {
    const file = photoFileInput.files?.[0];

    if (!file) {
        showAlert("Debes seleccionar una imagen antes de subirla.", "error");
        return null;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadPhotoBtn.disabled = true;
    uploadPhotoBtn.textContent = "Subiendo...";
    photoUploadStatus.textContent = "Subiendo foto...";

    try {
        const response = await apiFetch("/uploads/students/photo", {
            method: "POST",
            body: formData,
            headers: {},
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(result?.detail || "No se pudo subir la foto.");
        }

        photoPathInput.value = result.file_url || "";
        photoUploadStatus.textContent = "Foto subida correctamente.";
        setPhotoPreview(result.file_url || "");

        return result.file_url || "";
    } catch (error) {
        photoUploadStatus.textContent = "No se pudo subir la foto.";
        showAlert(error.message || "Error al subir la foto.", "error");
        return null;
    } finally {
        uploadPhotoBtn.disabled = false;
        uploadPhotoBtn.textContent = "Subir foto";
    }
}

async function loadStudentData() {
    hideAlert();

    try {
        reloadBtn.disabled = true;
        reloadBtn.textContent = "Recargando...";

        const studentResponse = await apiFetch(`/students/${studentId}`);
        if (!studentResponse.ok) {
            const data = await studentResponse.json().catch(() => ({}));
            throw new Error(data.detail || "No se pudo cargar el estudiante.");
        }

        const student = await studentResponse.json();
        fillStudentForm(student);

        const guardiansResponse = await apiFetch("/guardians/");
        if (!guardiansResponse.ok) {
            const data = await guardiansResponse.json().catch(() => ({}));
            throw new Error(data.detail || "No se pudieron cargar los tutores.");
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

    if (photoFileInput.files?.length && !photoPathInput.value.startsWith("/static/")) {
        const uploadedPhoto = await uploadSelectedPhoto();
        if (!uploadedPhoto) {
            return;
        }
    }

    saveBtn.disabled = true;
    saveBtn.textContent = "Guardando...";

    try {
        const studentPayload = getStudentPayload();

        const studentResponse = await apiFetch(`/students/${studentId}`, {
            method: "PUT",
            body: JSON.stringify(studentPayload),
        });

        const studentResult = await studentResponse.json().catch(() => ({}));

        if (!studentResponse.ok) {
            throw new Error(studentResult?.detail || "No se pudo actualizar el estudiante.");
        }

        const guardianPayload = getGuardianPayload();

        if (currentGuardianId) {
            const guardianResponse = await apiFetch(`/guardians/${currentGuardianId}`, {
                method: "PUT",
                body: JSON.stringify(guardianPayload),
            });

            const guardianResult = await guardianResponse.json().catch(() => ({}));

            if (!guardianResponse.ok) {
                throw new Error(
                    guardianResult?.detail ||
                    "El estudiante se actualizó, pero no se pudo actualizar el tutor principal."
                );
            }
        } else {
            const guardianCreatePayload = {
                student_id: Number(studentId),
                ...guardianPayload,
            };

            const guardianResponse = await apiFetch("/guardians/", {
                method: "POST",
                body: JSON.stringify(guardianCreatePayload),
            });

            const guardianResult = await guardianResponse.json().catch(() => ({}));

            if (!guardianResponse.ok) {
                throw new Error(
                    guardianResult?.detail ||
                    "El estudiante se actualizó, pero no se pudo crear el tutor principal."
                );
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
    uploadPhotoBtn.addEventListener("click", uploadSelectedPhoto);

    photoFileInput.addEventListener("change", () => {
        const file = photoFileInput.files?.[0];

        if (!file) {
            photoUploadStatus.textContent = getField("photo_path").value
                ? "Foto actual cargada."
                : "No se ha actualizado la foto.";
            setPhotoPreview(getField("photo_path").value || "");
            return;
        }

        photoUploadStatus.textContent = `Archivo seleccionado: ${file.name}. Falta subirlo.`;

        const previewUrl = URL.createObjectURL(file);
        setPhotoPreview(previewUrl);
    });
}

async function initPage() {
    try {
        currentUser = await requireAuth(["super_admin", "registro"]);
        configureRoleUI(currentUser);
        await loadStudentData();
    } catch (error) {
        showAlert(error.message || "No se pudo validar la sesión.", "error");
    }
}

bindEvents();
initPage();