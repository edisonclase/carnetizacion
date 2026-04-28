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
    if (uploadPhotoBtn) uploadPhotoBtn.disabled = isLoading;
}

function setPhotoPreview(path) {
    if (path) {
        photoPreview.src = path;
        photoPreviewWrap.classList.remove("hidden");
        photoUploadStatus.textContent = "Foto lista.";
    } else {
        photoPreviewWrap.classList.add("hidden");
        photoUploadStatus.textContent = "Sin foto.";
    }
}

function normalizeNullableText(value) {
    const text = String(value || "").trim();
    return text ? text : null;
}

async function loadStaff() {
    const res = await apiFetch(`/staff/${staffId}`);

    if (!res.ok) {
        throw new Error("No se pudo cargar el personal.");
    }

    currentStaff = await res.json();

    firstNameInput.value = currentStaff.first_name || "";
    lastNameInput.value = currentStaff.last_name || "";
    staffCodeInput.value = currentStaff.staff_code || "";
    nationalIdInput.value = currentStaff.national_id || "";
    departmentInput.value = currentStaff.department || "";
    isActiveInput.value = String(Boolean(currentStaff.is_active));

    staffGroupSelect.value = currentStaff.staff_group || "";
    staffPositionSelect.value = currentStaff.staff_position || "";

    photoPathInput.value = currentStaff.photo_path || "";
    setPhotoPreview(currentStaff.photo_path);

    staffCodeChip.textContent = `Código: ${currentStaff.staff_code || "-"}`;
}

async function uploadPhoto() {
    if (!photoFileInput.files.length) {
        showAlert("Selecciona una imagen.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", photoFileInput.files[0]);

    try {
        const res = await apiFetch("/uploads/staff/photo", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail);

        photoPathInput.value = data.file_url;
        setPhotoPreview(data.file_url);

        showAlert("Foto actualizada.", "success");
    } catch (err) {
        showAlert(err.message, "error");
    }
}

async function saveStaff(e) {
    e.preventDefault();
    hideAlert();
    setLoading(true);

    try {
        if (!firstNameInput.value || !lastNameInput.value) {
            throw new Error("Nombre y apellido son obligatorios.");
        }

        const payload = {
            first_name: firstNameInput.value.trim(),
            last_name: lastNameInput.value.trim(),
            staff_code: staffCodeInput.value.trim(),
            national_id: normalizeNullableText(nationalIdInput.value),
            gender: document.getElementById("gender")?.value || null,
            staff_group: staffGroupSelect.value,
            staff_position: staffPositionSelect.value,
            department: normalizeNullableText(departmentInput.value),
            photo_path: normalizeNullableText(photoPathInput.value),
            is_active: isActiveInput.value === "true",
        };

        const res = await apiFetch(`/staff/${staffId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail);

        // 🔥 REGENERAR CARNET AUTOMÁTICAMENTE
        await apiFetch(`/staff-cards/auto/${staffId}`, { method: "POST" });

        showAlert("Personal actualizado y carnet renovado.", "success");

    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        setLoading(false);
    }
}

async function init() {
    try {
        currentUser = await requireAuth(["super_admin", "registro", "admin_centro"]);
        await loadStaff();
    } catch (err) {
        showAlert("Error cargando datos.", "error");
    }
}

uploadPhotoBtn.addEventListener("click", uploadPhoto);
reloadBtn.addEventListener("click", loadStaff);
logoutBtn.addEventListener("click", logout);
form.addEventListener("submit", saveStaff);

init();