const form = document.getElementById("staffForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        center_id: 1, // luego lo hacemos dinámico
        first_name: document.getElementById("first_name").value,
        last_name: document.getElementById("last_name").value,
        staff_code: document.getElementById("staff_code").value,
        staff_group: document.getElementById("staff_group").value,
        staff_position: document.getElementById("staff_position").value,
        is_active: document.getElementById("is_active").value === "true"
    };

    const res = await apiFetch("/staff/", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        alert("Personal registrado correctamente");
        form.reset();
    } else {
        const data = await res.json();
        alert(data.detail || "Error");
    }
});

async function init() {
    await requireAuth(["super_admin", "registro"]);
}

init();