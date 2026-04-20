let allData = [];
const table = document.getElementById("staffTable");

function render(data) {
    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML = "<tr><td colspan='7'>Sin registros</td></tr>";
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
                <span class="status-badge ${item.is_active ? 'status-active' : 'status-inactive'}">
                    ${item.is_active ? "Activo" : "Inactivo"}
                </span>
            </td>
            <td class="action-stack">
                <button onclick="viewCard(${item.id})">Carnet</button>
                <button onclick="printCard(${item.id})">Imprimir</button>
                <button onclick="editStaff(${item.id})">Editar</button>
            </td>
        `;

        table.appendChild(row);
    });
}

// 🔥 ACCIONES

function viewCard(id) {
    window.open(`/staff/${id}/card/front`, "_blank");
}

function printCard(id) {
    window.open(`/admin/staff/${id}/print`, "_blank");
}

function editStaff(id) {
    alert("Edición en construcción.");
}

// 🔄 LOAD

async function loadStaff() {
    const res = await apiFetch(`/staff/?t=${Date.now()}`);
    const data = await res.json();

    allData = data;
    render(allData);
}

async function init() {
    await requireAuth(["super_admin", "registro", "consulta"]);
    await loadStaff();
}

init();