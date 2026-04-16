let currentUser = null;
let centersCache = [];
let selectedInvoiceId = null;

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value ?? "-";
    }
}

function formatCurrency(value) {
    const amount = Number(value || 0);
    return new Intl.NumberFormat("es-DO", {
        style: "currency",
        currency: "DOP",
        minimumFractionDigits: 2,
    }).format(amount);
}

function formatDate(value) {
    if (!value) return "-";
    return value;
}

function normalizeStatus(status) {
    const value = String(status || "").toLowerCase();
    if (value === "paid") return "Pagada";
    if (value === "partial") return "Parcial";
    if (value === "pending") return "Pendiente";
    if (value === "cancelled") return "Cancelada";
    return status || "-";
}

function statusBadge(status) {
    const value = String(status || "").toLowerCase();

    if (value === "paid") {
        return `<span class="badge badge-paid">Pagada</span>`;
    }
    if (value === "partial") {
        return `<span class="badge badge-partial">Parcial</span>`;
    }
    if (value === "pending") {
        return `<span class="badge badge-pending">Pendiente</span>`;
    }
    if (value === "cancelled") {
        return `<span class="badge badge-cancelled">Cancelada</span>`;
    }

    return `<span class="badge">${status || "-"}</span>`;
}

async function fetchJson(url, options = {}) {
    const response = await apiFetch(url, options);

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo completar la operación.");
    }

    return response.json();
}

function fillUserChip(user) {
    setText("currentUserName", user.full_name);
    setText("currentUserRole", roleLabel(user.role));
}

function getTodayLocalDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function setDefaultDates() {
    const issueDate = document.getElementById("issueDate");
    const dueDate = document.getElementById("dueDate");
    const paymentDate = document.getElementById("paymentDate");

    if (issueDate && !issueDate.value) {
        issueDate.value = getTodayLocalDate();
    }

    if (paymentDate && !paymentDate.value) {
        paymentDate.value = getTodayLocalDate();
    }

    if (dueDate && !dueDate.value) {
        const today = new Date();
        today.setDate(today.getDate() + 15);

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");
        dueDate.value = `${year}-${month}-${day}`;
    }
}

function renderCenters(selectId, includeAllOption = false) {
    const select = document.getElementById(selectId);
    if (!select) return;

    const options = [];

    if (includeAllOption) {
        options.push(`<option value="">Todos los centros</option>`);
    }

    options.push(
        ...centersCache.map(center => `<option value="${center.id}">${center.name}</option>`)
    );

    select.innerHTML = options.join("");
}

async function loadCenters() {
    centersCache = await fetchJson("/centers/");
    renderCenters("centerId", false);
    renderCenters("filterCenterId", true);
}

function getCenterName(centerId) {
    const center = centersCache.find(item => String(item.id) === String(centerId));
    return center ? center.name : `Centro ${centerId}`;
}

function calculateSummary(invoices) {
    const totals = invoices.reduce((acc, item) => {
        acc.totalBilled += Number(item.total_amount || 0);
        acc.totalPaid += Number(item.amount_paid || 0);
        acc.totalPending += Number(item.pending_amount || 0);
        return acc;
    }, {
        totalBilled: 0,
        totalPaid: 0,
        totalPending: 0,
    });

    setText("metricTotalBilled", formatCurrency(totals.totalBilled));
    setText("metricTotalPaid", formatCurrency(totals.totalPaid));
    setText("metricTotalPending", formatCurrency(totals.totalPending));
    setText("metricInvoiceCount", invoices.length);
}

function renderTable(invoices) {
    const tbody = document.getElementById("billingTableBody");
    if (!tbody) return;

    if (!invoices.length) {
        tbody.innerHTML = `<tr><td colspan="11" class="empty-row">No hay facturas registradas con esos filtros.</td></tr>`;
        calculateSummary([]);
        return;
    }

    tbody.innerHTML = invoices.map(invoice => `
        <tr>
            <td>${invoice.invoice_number}</td>
            <td>${getCenterName(invoice.center_id)}</td>
            <td>${invoice.concept}</td>
            <td>${invoice.card_quantity}</td>
            <td>${formatCurrency(invoice.total_amount)}</td>
            <td>${formatCurrency(invoice.amount_paid)}</td>
            <td>${formatCurrency(invoice.pending_amount)}</td>
            <td>${statusBadge(invoice.status)}</td>
            <td>${formatDate(invoice.issue_date)}</td>
            <td>${formatDate(invoice.due_date)}</td>
            <td>
                <button
                    type="button"
                    class="table-action-btn"
                    data-invoice-id="${invoice.id}"
                >
                    Ver
                </button>
            </td>
        </tr>
    `).join("");

    calculateSummary(invoices);

    tbody.querySelectorAll("[data-invoice-id]").forEach(button => {
        button.addEventListener("click", () => {
            const invoiceId = button.getAttribute("data-invoice-id");
            loadInvoiceDetail(invoiceId);
        });
    });
}

function renderPaymentsTable(payments) {
    const tbody = document.getElementById("paymentsTableBody");
    if (!tbody) return;

    if (!payments || !payments.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-row">No hay pagos registrados.</td></tr>`;
        return;
    }

    tbody.innerHTML = payments.map(payment => `
        <tr>
            <td>${formatDate(payment.payment_date)}</td>
            <td>${formatCurrency(payment.amount)}</td>
            <td>${payment.payment_method || "-"}</td>
            <td>${payment.reference || "-"}</td>
            <td>${payment.recorded_by || "-"}</td>
        </tr>
    `).join("");
}

async function loadInvoices() {
    const filterCenterId = document.getElementById("filterCenterId")?.value || "";
    const filterStatus = document.getElementById("filterStatus")?.value || "";

    const params = new URLSearchParams();

    if (filterCenterId) params.append("center_id", filterCenterId);
    if (filterStatus) params.append("status", filterStatus);

    const url = params.toString()
        ? `/billing/invoices?${params.toString()}`
        : "/billing/invoices";

    const invoices = await fetchJson(url);
    renderTable(invoices);
}

function clearPaymentForm() {
    const paymentDate = document.getElementById("paymentDate");
    const paymentAmount = document.getElementById("paymentAmount");
    const paymentMethod = document.getElementById("paymentMethod");
    const paymentReference = document.getElementById("paymentReference");
    const paymentNotes = document.getElementById("paymentNotes");

    if (paymentDate) paymentDate.value = getTodayLocalDate();
    if (paymentAmount) paymentAmount.value = "";
    if (paymentMethod) paymentMethod.value = "transfer";
    if (paymentReference) paymentReference.value = "";
    if (paymentNotes) paymentNotes.value = "";
}

async function loadInvoiceDetail(invoiceId) {
    selectedInvoiceId = Number(invoiceId);

    const detail = await fetchJson(`/billing/invoices/${invoiceId}`);
    const payments = await fetchJson(`/billing/invoices/${invoiceId}/payments`);

    document.getElementById("invoiceDetailEmpty")?.classList.add("hidden");
    document.getElementById("invoiceDetailContent")?.classList.remove("hidden");

    setText("detailInvoiceNumber", detail.invoice_number);
    setText("detailCenterName", getCenterName(detail.center_id));
    setText("detailIssueDate", formatDate(detail.issue_date));
    setText("detailDueDate", formatDate(detail.due_date));
    setText("detailConcept", detail.concept);
    setText("detailCardQuantity", detail.card_quantity);
    setText("detailUnitPrice", formatCurrency(detail.unit_price));
    setText("detailTotalAmount", formatCurrency(detail.total_amount));
    setText("detailAmountPaid", formatCurrency(detail.amount_paid));
    setText("detailPendingAmount", formatCurrency(detail.pending_amount));
    setText("detailStatus", normalizeStatus(detail.status));
    setText("detailNotes", detail.notes || "-");

    renderPaymentsTable(payments);
    clearPaymentForm();
    showPaymentMessage("", "info", true);
}

function clearForm() {
    document.getElementById("concept").value = "";
    document.getElementById("cardQuantity").value = "";
    document.getElementById("unitPrice").value = "";
    document.getElementById("amountPaid").value = "0";
    document.getElementById("notes").value = "";
    setDefaultDates();
}

function showFormMessage(message, type = "info", hidden = false) {
    const box = document.getElementById("formMessage");
    if (!box) return;

    if (hidden) {
        box.textContent = "";
        box.className = "form-message";
        return;
    }

    box.textContent = message;
    box.className = `form-message form-message-${type}`;
}

function showPaymentMessage(message, type = "info", hidden = false) {
    const box = document.getElementById("paymentMessage");
    if (!box) return;

    if (hidden) {
        box.textContent = "";
        box.className = "form-message";
        return;
    }

    box.textContent = message;
    box.className = `form-message form-message-${type}`;
}

async function handleCreateInvoice(event) {
    event.preventDefault();

    const saveButton = document.getElementById("saveInvoiceBtn");

    const payload = {
        center_id: Number(document.getElementById("centerId").value),
        issue_date: document.getElementById("issueDate").value,
        due_date: document.getElementById("dueDate").value,
        concept: document.getElementById("concept").value.trim(),
        card_quantity: Number(document.getElementById("cardQuantity").value),
        unit_price: Number(document.getElementById("unitPrice").value),
        amount_paid: Number(document.getElementById("amountPaid").value || 0),
        notes: document.getElementById("notes").value.trim() || null,
    };

    if (!payload.center_id || !payload.issue_date || !payload.due_date || !payload.concept) {
        showFormMessage("Completa los campos obligatorios.", "error");
        return;
    }

    saveButton.disabled = true;
    saveButton.textContent = "Registrando...";

    try {
        const created = await fetchJson("/billing/invoices", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        showFormMessage(`Factura registrada correctamente: ${created.invoice_number}`, "success");
        clearForm();
        await loadInvoices();
        await loadInvoiceDetail(created.id);
    } catch (error) {
        showFormMessage(error.message || "No se pudo registrar la factura.", "error");
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = "Registrar factura";
    }
}

async function handleRegisterPayment(event) {
    event.preventDefault();

    if (!selectedInvoiceId) {
        showPaymentMessage("Primero selecciona una factura.", "error");
        return;
    }

    const saveButton = document.getElementById("savePaymentBtn");

    const payload = {
        payment_date: document.getElementById("paymentDate").value,
        amount: Number(document.getElementById("paymentAmount").value),
        payment_method: document.getElementById("paymentMethod").value,
        reference: document.getElementById("paymentReference").value.trim() || null,
        notes: document.getElementById("paymentNotes").value.trim() || null,
        recorded_by: currentUser?.email || currentUser?.full_name || "super_admin",
    };

    if (!payload.payment_date || !payload.amount || payload.amount <= 0) {
        showPaymentMessage("Completa correctamente la fecha y el monto del pago.", "error");
        return;
    }

    saveButton.disabled = true;
    saveButton.textContent = "Registrando...";

    try {
        await fetchJson(`/billing/invoices/${selectedInvoiceId}/payments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        showPaymentMessage("Pago registrado correctamente.", "success");
        await loadInvoices();
        await loadInvoiceDetail(selectedInvoiceId);
    } catch (error) {
        showPaymentMessage(error.message || "No se pudo registrar el pago.", "error");
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = "Registrar pago";
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        currentUser = await requireAuth(["super_admin"]);

        if (String(currentUser.role || "").toLowerCase() !== "super_admin") {
            window.location.href = "/dashboard";
            return;
        }

        fillUserChip(currentUser);
        setDefaultDates();

        await loadCenters();
        await loadInvoices();

        document.getElementById("billingForm")?.addEventListener("submit", handleCreateInvoice);
        document.getElementById("paymentForm")?.addEventListener("submit", handleRegisterPayment);
        document.getElementById("filterInvoicesBtn")?.addEventListener("click", loadInvoices);
        document.getElementById("logoutBtn")?.addEventListener("click", logout);
    } catch (error) {
        console.error(error);
    }
});