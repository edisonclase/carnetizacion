const body = document.body;
const staffId = body.dataset.staffId;

const form = document.getElementById("staffEditForm");
const alertBox = document.getElementById("alertBox");
const logoutBtn = document.getElementById("logoutBtn");
const reloadBtn = document.getElementById("reloadBtn");
const saveBtn = document.getElementById("saveBtn");
const uploadPhotoBtn = document.getElementById("uploadPhotoBtn");

const staffCodeChip = document.getElementById("staffCodeChip");

const firstNameInput = document.getElementById("first_name");
const lastNameInput = document.getElementById("last_name");
const staffCodeInput = document.getElementById("staff_code");
const nationalIdInput = document.getElementById("national_id");
const genderInput = document.getElementById("gender");
const departmentInput = document.getElementById("department");
const isActiveInput = document.getElementById("is_active");

const staffGroupSelect = document.getElementById("staff_group");
const staffPositionSelect = document.getElementById("staff_position");

const photoFileInput = document.getElementById("photo_file");
const photoPathInput = document.getElementById("photo_path");
const photoUploadStatus = document.getElementById("photoUploadStatus");
const photoPreviewWrap = document.getElementById("photoPreviewWrap");
const photoPreview = document.getElementById("photoPreview");

let currentUser = null;
let currentStaff = null;

const STAFF_POSITIONS_BY_GROUP = {
    administrativo: [
        { value: "secretaria", label: "Secretaria" },
        { value: "digitador", label: "Digitador" },
        { value: "administrativo_otro", label: "Administrativo / Otro" },
    ],
    apoyo: [
        { value: "conserje", label: "Conserje" },
        { value: "mayordomo", label: "Mayordomo" },
        { value: "jardinero", label: "Jardinero" },
        { value: "portero", label: "Portero" },
        { value: "sereno", label: "Sereno" },
        { value: "apoyo_otro", label: "Apoyo / Otro" },
    ],
    docente_tecnico: [
        { value: "docente", label: "Docente" },
        { value: "director", label: "Director" },
        { value: "subdirector", label: "Subdirector" },
        { value: "coordinador", label: "Coordinador" },
        { value: "psicologo", label: "Psicólogo" },
        { value: "psicologa", label: "Psicóloga" },
        { value: "orientador", label: "Orientador" },
        { value: "orientadora", label: "Orientadora" },
        { value: "tecnico_otro", label: "Técnico / Otro" },
    ],
};

function showAlert(message, type = "success") {
    alertBox.textContent = message;
    alertBox.className = `alert-box ${type}`;
}

function hideAlert() {
    alertBox.textContent = "";
    alertBox.className = "alert-box hidden";
}

function setLoading(isLoading) {
    saveBtn.disabled = isLoading;
    reloadBtn.disabled = isLoading;
    uploadPhotoBtn.disabled = isLoading;
}

function normalizeNullableText(value) {
    const text = String(value || "").trim();
    return text ? text : null;
}

function populatePositions(groupValue, selectedValue = "") {
    const positions = STAFF_POSITIONS_BY_GROUP[groupValue] || [];

    staffPositionSelect.innerHTML = `<option value="">Seleccione</option>`;

    positions.forEach((position) => {
        const option = document.createElement("option");
        option.value = position.value;
        option.textContent = position.label;
        staffPositionSelect.appendChild(option);
    });

    staffPositionSelect.disabled = positions.length === 0;

    if (selectedValue) {
        staffPositionSelect.value = selectedValue;
    }
}

function setPhotoPreview(path, statusText = "Foto lista.") {
    if (path) {
        photoPreview.src = path;
        photoPreviewWrap.classList.remove("hidden");
        photoUploadStatus.textContent = statusText;
    } else {
        photoPreview.removeAttribute("src");
        photoPreviewWrap.classList.add("hidden");
        photoUploadStatus.textContent = "Sin foto.";
    }
}

function previewSelectedPhoto() {
    const file = photoFileInput.files?.[0];

    if (!file) {
        setPhotoPreview(photoPathInput.value || null);
        return;
    }

    const previewUrl = URL.createObjectURL(file);
    photoPreview.src = previewUrl;
    photoPreviewWrap.classList.remove("hidden");
    photoUploadStatus.textContent = "Vista previa lista. Falta guardar para subirla.";
}

async function loadStaff() {
    hideAlert();

    const res = await apiFetch(`/staff/${staffId}`);

    if (!res.ok) {
        throw new Error("No se pudo cargar el personal.");
    }

    currentStaff = await res.json();

    firstNameInput.value = currentStaff.first_name || "";
    lastNameInput.value = currentStaff.last_name || "";
    staffCodeInput.value = currentStaff.staff_code || "";
    nationalIdInput.value = currentStaff.national_id || "";
    genderInput.value = currentStaff.gender || "";
    departmentInput.value = currentStaff.department || "";
    isActiveInput.value = String(Boolean(currentStaff.is_active));

    staffGroupSelect.value = currentStaff.staff_group || "";
    populatePositions(currentStaff.staff_group || "", currentStaff.staff_position || "");

    photoPathInput.value = currentStaff.photo_path || "";
    setPhotoPreview(currentStaff.photo_path);

    staffCodeChip.textContent = `Código: ${currentStaff.staff_code || "-"}`;
}

async function uploadPhoto() {
    const file = photoFileInput.files?.[0];

    if (!file) {
        showAlert("Selecciona una imagen.", "error");
        return null;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await apiFetch("/uploads/staff/photo", {
        method: "POST",
        body: formData,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        throw new Error(data.detail || "No se pudo subir la foto del personal.");
    }

    photoPathInput.value = data.file_url;
    setPhotoPreview(data.file_url, "Foto subida correctamente.");

    return data.file_url;
}

async function saveStaff(event) {
    event.preventDefault();
    hideAlert();
    setLoading(true);

    try {
        if (!firstNameInput.value.trim() || !lastNameInput.value.trim()) {
            throw new Error("Nombre y apellido son obligatorios.");
        }

        if (!staffCodeInput.value.trim()) {
            throw new Error("El código interno es obligatorio.");
        }

        if (!staffGroupSelect.value) {
            throw new Error("Selecciona el grupo del personal.");
        }

        if (!staffPositionSelect.value) {
            throw new Error("Selecciona el cargo del personal.");
        }

        if (photoFileInput.files?.length) {
            await uploadPhoto();
        }

        const payload = {
            first_name: firstNameInput.value.trim(),
            last_name: lastNameInput.value.trim(),
            staff_code: staffCodeInput.value.trim(),
            national_id: normalizeNullableText(nationalIdInput.value),
            gender: normalizeNullableText(genderInput.value),
            staff_group: staffGroupSelect.value,
            staff_position: staffPositionSelect.value,
            department: normalizeNullableText(departmentInput.value),
            photo_path: normalizeNullableText(photoPathInput.value),
            is_active: isActiveInput.value === "true",
        };

        const res = await apiFetch(`/staff/${staffId}`, {
            method: "PUT",
            body: JSON.stringify(payload),
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            const detail = Array.isArray(data.detail)
                ? data.detail.map((item) => item.msg).join(" | ")
                : data.detail;

            throw new Error(detail || "No se pudo actualizar el personal.");
        }

        currentStaff = data;
        photoFileInput.value = "";
        staffCodeChip.textContent = `Código: ${data.staff_code || "-"}`;

        showAlert("Personal actualizado correctamente.", "success");
    } catch (err) {
        showAlert(err.message || "Ocurrió un error al guardar.", "error");
    } finally {
        setLoading(false);
    }
}

async function init() {
    try {
        currentUser = await requireAuth(["super_admin", "registro", "admin_centro"]);
        await loadStaff();
    } catch (err) {
        console.error(err);
        showAlert(err.message || "Error cargando datos.", "error");
    }
}

staffGroupSelect.addEventListener("change", () => {
    populatePositions(staffGroupSelect.value);
});

photoFileInput.addEventListener("change", previewSelectedPhoto);

uploadPhotoBtn.addEventListener("click", async () => {
    try {
        hideAlert();
        setLoading(true);
        await uploadPhoto();
        showAlert("Foto subida correctamente. Recuerda guardar los cambios.", "success");
    } catch (err) {
        showAlert(err.message || "No se pudo subir la foto.", "error");
    } finally {
        setLoading(false);
    }
});

reloadBtn.addEventListener("click", loadStaff);
logoutBtn.addEventListener("click", logout);
form.addEventListener("submit", saveStaff);

init();