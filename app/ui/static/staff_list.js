const table = document.getElementById("staffTable");

function render(data) {
    table.innerHTML = "";

    if (!data.length) {
        table.innerHTML = "<tr><td colspan='5'>Sin registros</td></tr>";
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.staff_code}</td>
            <td>${item.first_name} ${item.last_name}</td>
            <td>${item.staff_group}</td>
            <td>${item.staff_position}</td>
            <td>${item.is_active ? "Activo" : "Inactivo"}</td>
        `;

        table.appendChild(row);
    });
}

async function loadStaff() {
    const res = await apiFetch("/staff/");
    const data = await res.json();
    render(data);
}

async function init() {
    await requireAuth(["super_admin", "registro", "consulta"]);
    loadStaff();
}

init();