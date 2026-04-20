let currentUser = null;
const form = document.getElementById("staffForm");

async function init() {
    currentUser = await requireAuth(["super_admin", "registro", "admin_centro"]);
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    try {
        const firstName = document.getElementById("first_name").value.trim();
        const lastName = document.getElementById("last_name").value.trim();
        const staffCode = document.getElementById("staff_code").value.trim();
        const nationalId = document.getElementById("national_id").value.trim();
        const gender = document.getElementById("gender").value;
        const staffGroup = document.getElementById("staff_group").value;
        const staffPosition = document.getElementById("staff_position").value.trim();
        const department = document.getElementById("department").value.trim();
        const isActive = document.getElementById("is_active").value === "true";
        const photoInput = document.getElementById("photo");

        if (!firstName || !lastName || !staffCode || !staffPosition) {
            alert("Completa los campos obligatorios.");
            return;
        }

        let photoPath = null;

        if (photoInput && photoInput.files && photoInput.files.length > 0) {
            const formData = new FormData();
            formData.append("file", photoInput.files[0]);

            const uploadRes = await apiFetch("/uploads/staff/photo", {
                method: "POST",
                body: formData,
            });

            const uploadData = await uploadRes.json().catch(() => ({}));

            if (!uploadRes.ok) {
                throw new Error(uploadData.detail || "No se pudo subir la foto del personal.");
            }

            photoPath = uploadData.file_url || null;
        }

        const payload = {
            center_id: currentUser?.center_id || 1,
            school_year_id: currentUser?.school_year_id || null,
            first_name: firstName,
            last_name: lastName,
            staff_code: staffCode,
            national_id: nationalId || null,
            photo_path: photoPath,
            gender: gender || null,
            staff_group: staffGroup,
            staff_position: staffPosition,
            department: department || null,
            is_active: isActive,
        };

        const res = await apiFetch("/staff/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const createdStaff = await res.json().catch(() => ({}));

        if (!res.ok) {
            throw new Error(createdStaff.detail || "Error registrando personal.");
        }

        const cardRes = await apiFetch(`/staff-cards/auto/${createdStaff.id}`, {
            method: "POST",
        });

        const cardData = await cardRes.json().catch(() => ({}));

        if (!cardRes.ok) {
            throw new Error(cardData.detail || "El personal se creó, pero no se pudo emitir el carnet.");
        }

        alert("Personal registrado correctamente y carnet emitido.");
        window.location.href = "/admin/staff";
    } catch (error) {
        alert(error.message || "Ocurrió un error inesperado.");
    }
});

init();