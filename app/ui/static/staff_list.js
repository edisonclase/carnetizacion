let staff = [];
let filteredStaff = [];

const table = document.getElementById("staffTable");

const groupFilter = document.getElementById("groupFilter");
const deptFilter = document.getElementById("deptFilter");
const activeFilter = document.getElementById("activeFilter");

async function loadStaff() {
    const res = await apiFetch(`/staff/?t=${Date.now()}`);
    staff = await res.json();
    filteredStaff = [...staff];

    render(filteredStaff);
}

function render(data) {
    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML = `<tr><td colspan="7">Sin registros</td></tr>`;
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.staff_code}</td>
            <td>${item.first_name} ${item.last_name}</td>
            <td>${item.staff_group}</td>
            <td>${item.staff_position}</td>
            <td>${item.department || "-"}</td>
            <td>
                <span class="status-badge ${item.is_active ? "status-active" : "status-inactive"}">
                    ${item.is_active ? "Activo" : "Inactivo"}
                </span>
            </td>
            <td>
                <div class="action-stack">
                    <button class="btn btn-primary" onclick="viewCard(${item.id})">Ver</button>
                    <button class="btn btn-success" onclick="printCard(${item.id})">Imprimir</button>
                    <button class="btn btn-neutral" onclick="editStaff(${item.id})">Editar</button>
                </div>
            </td>
        `;

        table.appendChild(row);
    });
}

// 🔍 FILTROS
function applyFilters() {
    const group = groupFilter.value;
    const dept = deptFilter.value.toLowerCase();
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
}

// 🔥 ACCIONES
function viewCard(id) {
    window.open(`/staff/${id}/card/front`, "_blank");
}

function printCard(id) {
    window.open(`/admin/staff/${id}/print`, "_blank");
}

function editStaff(id) {
    window.location.href = `/admin/staff/${id}/edit`;
}

// 🔄 INIT
async function init() {
    await requireAuth(["super_admin", "registro", "consulta"]);
    await loadStaff();
}

init();