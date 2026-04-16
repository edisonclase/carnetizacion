document.addEventListener("DOMContentLoaded", async () => {

    // 🔐 SOLO SUPER ADMIN
    const user = await requireAuth(["super_admin"]);

    document.getElementById("userInfo").textContent =
        `${user.full_name} (${roleLabel(user.role)})`;

    const tableBody = document.getElementById("billingTableBody");

    async function loadInvoices() {
        try {
            const centerId = document.getElementById("filterCenterId").value;
            const status = document.getElementById("filterStatus").value;

            let url = "/billing/invoices?";

            if (centerId) url += `center_id=${centerId}&`;
            if (status) url += `status=${status}&`;

            const response = await apiFetch(url);

            if (!response.ok) {
                throw new Error("Error cargando facturas");
            }

            const data = await response.json();

            renderTable(data);

        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    }

    function renderTable(invoices) {
        tableBody.innerHTML = "";

        invoices.forEach(inv => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${inv.id}</td>
                <td>${inv.invoice_number}</td>
                <td>${inv.center_id}</td>
                <td>${inv.total_amount}</td>
                <td>${inv.amount_paid}</td>
                <td>${inv.pending_amount}</td>
                <td>${inv.status}</td>
                <td>
                    <button data-id="${inv.id}" class="btnVer">Ver</button>
                    <button data-id="${inv.id}" class="btnPagar">Pagar</button>
                </td>
            `;

            tableBody.appendChild(tr);
        });
    }

    // 📌 EVENTOS

    document.getElementById("btnFiltrar").addEventListener("click", loadInvoices);

    document.getElementById("btnRefrescar").addEventListener("click", loadInvoices);

    document.getElementById("btnNuevaFactura").addEventListener("click", () => {
        alert("Formulario de creación (próxima fase)");
    });

    // 💳 REGISTRAR PAGO
    tableBody.addEventListener("click", async (e) => {
        if (e.target.classList.contains("btnPagar")) {
            const invoiceId = e.target.dataset.id;

            const amount = prompt("Monto a pagar:");

            if (!amount) return;

            try {
                const response = await apiFetch("/billing/payments", {
                    method: "POST",
                    body: JSON.stringify({
                        invoice_id: Number(invoiceId),
                        amount: Number(amount)
                    })
                });

                if (!response.ok) {
                    throw new Error("Error registrando pago");
                }

                alert("Pago registrado correctamente");
                loadInvoices();

            } catch (error) {
                alert(error.message);
            }
        }
    });

    // 🚀 INIT
    loadInvoices();
});