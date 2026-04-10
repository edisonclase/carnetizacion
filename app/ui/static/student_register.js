const form = document.getElementById("studentRegisterForm");
const alertBox = document.getElementById("alertBox");
const saveBtn = document.getElementById("saveBtn");
const resetBtn = document.getElementById("resetBtn");

const centerSelect = document.getElementById("center_id");
const schoolYearSelect = document.getElementById("school_year_id");

const photoFileInput = document.getElementById("photo_file");
const photoPathInput = document.getElementById("photo_path");
const uploadPhotoBtn = document.getElementById("uploadPhotoBtn");
const photoUploadStatus = document.getElementById("photoUploadStatus");
const photoPreviewWrap = document.getElementById("photoPreviewWrap");
const photoPreview = document.getElementById("photoPreview");

const resultPanel = document.getElementById("resultPanel");
const resultSummary = document.getElementById("resultSummary");
const resultStudentCode = document.getElementById("resultStudentCode");
const resultStudentId = document.getElementById("resultStudentId");
const resultCardId = document.getElementById("resultCardId");
const resultCardCode = document.getElementById("resultCardCode");
const openFrontBtn = document.getElementById("openFrontBtn");
const openBackBtn = document.getElementById("openBackBtn");
const openStudentBtn = document.getElementById("openStudentBtn");

const logoutBtn = document.getElementById("logoutBtn");
const headerUserChip = document.getElementById("headerUserChip");
const navDocsLink = document.getElementById("navDocsLink");

let allSchoolYears = [];
let allCenters = [];
let alertTimeoutId = null;
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
    openStudentBtn.href = `/admin/students/${student.id}/print`;

    openFrontBtn.textContent = "Ver frontal del carnet";
    openBackBtn.textContent = "Ver reverso del carnet";
    openStudentBtn.textContent = "Imprimir carnet";

    openFrontBtn.classList.remove("hidden");
    openBackBtn.classList.remove("hidden");
    openStudentBtn.classList.remove("hidden");

    resultPanel.classList.remove("hidden");
}

function getValue(id) {
    return document.getElementById(id).value.trim();
}

function configureRoleUI(user) {
    headerUserChip.textContent = `Nova ID · ${roleLabel(user.role)} · ${user.full_name}`;

    if (user.role !== "super_admin") {
        navDocsLink.style.display = "none";
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }
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

function setPhotoPreview(url) {
    if (!url) {
        photoPreviewWrap.classList.add("hidden");
        photoPreview.removeAttribute("src");
        return;
    }

    photoPreview.src = url;
    photoPreviewWrap.classList.remove("hidden");
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

async function loadCenters() {
    const response = await apiFetch("/centers/");
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudieron cargar los centros.");
    }

    const centers = await response.json();
    allCenters = centers;

    if (currentUser.role === "super_admin") {
        centerSelect.innerHTML = '<option value="">Seleccione un centro</option>';

        centers.forEach((center) => {
            const option = document.createElement("option");
            option.value = center.id;
            option.textContent = center.code ? `${center.name} (${center.code})` : center.name;
            centerSelect.appendChild(option);
        });
    } else {
        const ownCenter = centers.find(
            (center) => String(center.id) === String(currentUser.center_id)
        );

        if (!ownCenter) {
            centerSelect.innerHTML = '<option value="">Centro no disponible</option>';
            centerSelect.disabled = true;
            return;
        }

        centerSelect.innerHTML = "";
        const option = document.createElement("option");
        option.value = ownCenter.id;
        option.textContent = ownCenter.code ? `${ownCenter.name} (${ownCenter.code})` : ownCenter.name;
        centerSelect.appendChild(option);

        centerSelect.value = String(ownCenter.id);
        centerSelect.disabled = true;
    }
}

async function loadSchoolYears() {
    const response = await apiFetch("/school-years/");
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudieron cargar los años escolares.");
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

    if (photoFileInput.files?.length && !photoPathInput.value) {
        const uploadedPhoto = await uploadSelectedPhoto();
        if (!uploadedPhoto) {
            return;
        }
    }

    const payload = getRegisterPayload();

    saveBtn.disabled = true;
    saveBtn.textContent = "Registrando...";

    try {
        const response = await apiFetch("/students/with-guardian-and-card", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
            const detail = result?.detail || "No se pudo completar el registro del estudiante.";
            throw new Error(detail);
        }

        form.reset();
        photoPathInput.value = "";
        setPhotoPreview("");
        photoUploadStatus.textContent = "No se ha subido ninguna foto.";

        if (currentUser.role === "super_admin") {
            centerSelect.value = "";
            schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
            schoolYearSelect.disabled = true;
        } else {
            centerSelect.value = String(currentUser.center_id);
            setSchoolYearOptions(currentUser.center_id);
        }

        showAlert(
            `Registro completado correctamente. Estudiante ID: ${result.student.id}. Carnet ID: ${result.card.id}. Código del carnet: ${result.card.card_code}.`,
            "success"
        );

        showResultPanel(result);
    } catch (error) {
        showAlert(error.message || "Ocurrió un error durante el registro.", "error");
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Registrar estudiante";
    }
}

function resetForm() {
    form.reset();

    if (currentUser.role === "super_admin") {
        schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
        schoolYearSelect.disabled = true;
    } else {
        centerSelect.value = String(currentUser.center_id);
        setSchoolYearOptions(currentUser.center_id);
    }

    photoPathInput.value = "";
    setPhotoPreview("");
    photoUploadStatus.textContent = "No se ha subido ninguna foto.";

    hideAlert();
    hideResultPanel();
}

function bindEvents() {
    form.addEventListener("submit", submitForm);
    resetBtn.addEventListener("click", resetForm);
    uploadPhotoBtn.addEventListener("click", uploadSelectedPhoto);

    centerSelect.addEventListener("change", (event) => {
        setSchoolYearOptions(event.target.value);
    });

    photoFileInput.addEventListener("change", () => {
        const file = photoFileInput.files?.[0];

        if (!file) {
            photoUploadStatus.textContent = "No se ha subido ninguna foto.";
            setPhotoPreview("");
            photoPathInput.value = "";
            return;
        }

        photoUploadStatus.textContent = `Archivo seleccionado: ${file.name}. Falta subirlo.`;

        const previewUrl = URL.createObjectURL(file);
        setPhotoPreview(previewUrl);
        photoPathInput.value = "";
    });
}

async function initPage() {
    hideAlert();
    hideResultPanel();

    try {
        currentUser = await requireAuth(["super_admin", "registro"]);
        configureRoleUI(currentUser);

        await Promise.all([loadCenters(), loadSchoolYears()]);

        if (currentUser.role === "super_admin") {
            schoolYearSelect.disabled = true;
            schoolYearSelect.innerHTML = '<option value="">Seleccione primero un centro</option>';
        } else {
            centerSelect.value = String(currentUser.center_id);
            setSchoolYearOptions(currentUser.center_id);
        }
    } catch (error) {
        showAlert(error.message || "No se pudo inicializar el formulario.", "error");
    }
}

bindEvents();
initPage();