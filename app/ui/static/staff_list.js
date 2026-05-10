let staff = [];
let filteredStaff = [];
let selectedStaff = new Set();

const table = document.getElementById("staffTable");

const groupFilter = document.getElementById("groupFilter");
const deptFilter = document.getElementById("deptFilter");
const activeFilter = document.getElementById("activeFilter");

const applyFiltersBtn = document.getElementById("applyFiltersBtn");
const clearFiltersBtn = document.getElementById("clearFiltersBtn");

const selectAllStaff = document.getElementById("selectAllStaff");
const selectedCount = document.getElementById("selectedCount");
const resultCount = document.getElementById("resultCount");
const clearSelectedBtn = document.getElementById("clearSelectedBtn");
const printSelectedBtn = document.getElementById("printSelectedBtn");
const printVisibleBtn = document.getElementById("printVisibleBtn");
const alertBox = document.getElementById("alertBox");

function showAlert(message, type = "success") {
    alertBox.textContent = message;
    alertBox.className = `alert-box ${type}`;
}

function hideAlert() {
    alertBox.textContent = "";
    alertBox.className = "alert-box hidden";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function loadStaff() {
    const res = await apiFetch(`/staff/?t=${Date.now()}`);

    if (!res.ok) {
        table.innerHTML = `<tr><td colspan="8" class="empty-row">No se pudo cargar el personal.</td></tr>`;
        return;
    }

    staff = await res.json();
    filteredStaff = [...staff];

    render(filteredStaff);
}

function render(data) {
    table.innerHTML = "";

    resultCount.textContent = `${data.length} miembro(s) del personal encontrado(s)`;
    printVisibleBtn.disabled = data.length === 0;

    if (!data.length) {
        table.innerHTML = `<tr><td colspan="8" class="empty-row">Sin registros</td></tr>`;
        updateSelectedState();
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");
        const isChecked = selectedStaff.has(String(item.id));

        row.innerHTML = `
            <td>
                <input
                    type="checkbox"
                    class="staffCheck"
                    value="${item.id}"
                    ${isChecked ? "checked" : ""}
                    aria-label="Seleccionar ${escapeHtml(item.first_name || "")} ${escapeHtml(item.last_name || "")}"
                />
            </td>
            <td>${escapeHtml(item.staff_code || "-")}</td>
            <td>${escapeHtml(item.first_name || "")} ${escapeHtml(item.last_name || "")}</td>
            <td>${escapeHtml(item.staff_group || "-")}</td>
            <td>${escapeHtml(item.staff_position || "-")}</td>
            <td>${escapeHtml(item.department || "-")}</td>
            <td>
                <span class="status-badge ${item.is_active ? "status-active" : "status-inactive"}">
                    ${item.is_active ? "Activo" : "Inactivo"}
                </span>
            </td>
            <td>
                <div class="action-stack">
                    <button class="btn btn-primary" type="button" onclick="viewCard(${item.id})">Ver</button>
                    <button class="btn btn-success" type="button" onclick="printCard(${item.id})">Imprimir</button>
                    <button class="btn btn-neutral" type="button" onclick="editStaff(${item.id})">Editar</button>
                </div>
            </td>
        `;

        table.appendChild(row);
    });

    document.querySelectorAll(".staffCheck").forEach((checkbox) => {
        checkbox.addEventListener("change", handleCheckboxChange);
    });

    updateSelectedState();
}

function handleCheckboxChange(event) {
    const id = String(event.target.value);

    if (event.target.checked) {
        selectedStaff.add(id);
    } else {
        selectedStaff.delete(id);
    }

    updateSelectedState();
}

function getVisibleIds() {
    return filteredStaff.map((item) => String(item.id));
}

function getSelectedVisibleIds() {
    const visible = new Set(getVisibleIds());
    return Array.from(selectedStaff).filter((id) => visible.has(id));
}

function updateSelectedState() {
    const visibleIds = getVisibleIds();
    const selectedVisibleIds = getSelectedVisibleIds();

    selectedCount.textContent = `${selectedVisibleIds.length} seleccionado(s)`;

    printSelectedBtn.disabled = selectedVisibleIds.length === 0;
    clearSelectedBtn.disabled = selectedVisibleIds.length === 0;

    if (visibleIds.length === 0) {
        selectAllStaff.checked = false;
        selectAllStaff.indeterminate = false;
        return;
    }

    if (selectedVisibleIds.length === 0) {
        selectAllStaff.checked = false;
        selectAllStaff.indeterminate = false;
        return;
    }

    if (selectedVisibleIds.length === visibleIds.length) {
        selectAllStaff.checked = true;
        selectAllStaff.indeterminate = false;
        return;
    }

    selectAllStaff.checked = false;
    selectAllStaff.indeterminate = true;
}

function applyFilters() {
    hideAlert();

    const group = groupFilter.value;
    const dept = deptFilter.value.toLowerCase().trim();
    const active = activeFilter.value;

    filteredStaff = staff.filter(s => {
        return (
            (!group || s.staff_group === group) &&
            (!dept || (s.department || "").toLowerCase().includes(dept)) &&
            (active === "" || String(s.is_active) === active)
        );
    });

    render(filteredStaff);
}

function clearFilters() {
    groupFilter.value = "";
    deptFilter.value = "";
    activeFilter.value = "";

    filteredStaff = [...staff];
    render(filteredStaff);
    hideAlert();
}

function clearSelection() {
    selectedStaff.clear();

    document.querySelectorAll(".staffCheck").forEach((checkbox) => {
        checkbox.checked = false;
    });

    updateSelectedState();
}

function viewCard(id) {
    window.open(`/staff/${id}/card/front`, "_blank");
}

function printCard(id) {
    window.open(`/admin/staff/${id}/print`, "_blank");
}

function editStaff(id) {
    window.location.href = `/admin/staff/${id}/edit`;
}

function printStaffIds(ids) {
    if (!ids.length) {
        showAlert("No hay personal seleccionado para imprimir.", "error");
        return;
    }

    ids.forEach((id) => {
        window.open(`/admin/staff/${id}/print`, "_blank");
    });
}

selectAllStaff.addEventListener("change", () => {
    const visibleIds = getVisibleIds();

    if (selectAllStaff.checked) {
        visibleIds.forEach((id) => selectedStaff.add(id));
    } else {
        visibleIds.forEach((id) => selectedStaff.delete(id));
    }

    document.querySelectorAll(".staffCheck").forEach((checkbox) => {
        checkbox.checked = selectedStaff.has(String(checkbox.value));
    });

    updateSelectedState();
});

printSelectedBtn.addEventListener("click", () => {
    const selectedIds = getSelectedVisibleIds();
    printStaffIds(selectedIds);
});

printVisibleBtn.addEventListener("click", () => {
    const visibleIds = getVisibleIds();
    printStaffIds(visibleIds);
});

clearSelectedBtn.addEventListener("click", () => {
    clearSelection();
    showAlert("Selección limpiada.", "success");
});

applyFiltersBtn.addEventListener("click", applyFilters);
clearFiltersBtn.addEventListener("click", clearFilters);

async function init() {
    try {
        await requireAuth(["super_admin", "admin_centro", "registro", "consulta"]);
        await loadStaff();
    } catch (error) {
        console.error(error);
        table.innerHTML = `<tr><td colspan="8" class="empty-row">No autorizado o sesión expirada.</td></tr>`;
    }
}

init();