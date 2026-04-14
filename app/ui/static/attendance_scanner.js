function getNowForDatetimeLocal() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function setResultState(message, variant = "success") {
    const resultPanel = document.getElementById("resultPanel");
    const resultState = document.getElementById("resultState");

    resultPanel.classList.remove("hidden");
    resultState.className = `result-state ${variant}`;
    resultState.textContent = message;
}

function fillResult(result) {
    const student = result.student || {};
    const event = result.event || {};
    const dailySummary = result.daily_summary || {};
    const centerDay = result.center_day || {};

    document.getElementById("resultStudentName").textContent = student.full_name || "-";
    document.getElementById("resultStudentMeta").textContent =
        `${student.student_code || "-"} · ${student.grade || "-"} · Sección ${student.section || "-"}`;

    document.getElementById("resultEventStatus").textContent = event.status || "-";
    document.getElementById("resultEventTime").textContent = event.event_time || "-";

    document.getElementById("resultDailyStatus").textContent = dailySummary.status || "-";
    document.getElementById("resultDailyMeta").textContent =
        `Entrada: ${dailySummary.first_entry_time || "-"} · Min. tarde: ${dailySummary.minutes_late ?? 0}`;

    document.getElementById("resultCenterTotals").textContent =
        `Entradas: ${centerDay.total_entries ?? 0} · Tardanzas: ${centerDay.total_late ?? 0}`;
    document.getElementById("resultCenterMeta").textContent =
        `Presentes: ${centerDay.total_present ?? 0} · Ausentes: ${centerDay.total_absent ?? 0} · Excusas: ${centerDay.total_with_excuse ?? 0}`;
}

function clearFormAndResult() {
    document.getElementById("qrToken").value = "";
    document.getElementById("notes").value = "";
    document.getElementById("eventTime").value = getNowForDatetimeLocal();

    document.getElementById("resultPanel").classList.add("hidden");
    document.getElementById("resultState").textContent = "";
}

async function submitScan(event) {
    event.preventDefault();

    const submitBtn = document.getElementById("submitScanBtn");
    const qrToken = document.getElementById("qrToken").value.trim();
    const eventTime = document.getElementById("eventTime").value;
    const source = document.getElementById("source").value.trim() || "scanner";
    const recordedBy = document.getElementById("recordedBy").value.trim() || "super_admin";
    const notes = document.getElementById("notes").value.trim();

    if (!qrToken || !eventTime) {
        setResultState("Debes completar el QR token y la fecha/hora.", "error");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Registrando...";

    try {
        const response = await apiFetch("/attendance-events/scan-qr-entry", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                qr_token: qrToken,
                event_time: new Date(eventTime).toISOString(),
                source,
                notes: notes || null,
                recorded_by: recordedBy,
            }),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "No se pudo registrar la entrada.");
        }

        fillResult(data);

        const eventStatus = String(data?.event?.status || "").toLowerCase();
        if (eventStatus === "late") {
            setResultState("Entrada registrada con tardanza.", "warning");
        } else {
            setResultState("Entrada registrada correctamente.", "success");
        }

        document.getElementById("qrToken").value = "";
        document.getElementById("qrToken").focus();
    } catch (error) {
        setResultState(error.message || "Ocurrió un error registrando la entrada.", "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Registrar entrada";
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const currentUser = await requireAuth(["super_admin"]);

        document.getElementById("currentUserName").textContent = currentUser.full_name;
        document.getElementById("currentUserRole").textContent = roleLabel(currentUser.role);

        document.getElementById("eventTime").value = getNowForDatetimeLocal();
        document.getElementById("recordedBy").value = currentUser.email || "super_admin";

        document.getElementById("scannerForm")?.addEventListener("submit", submitScan);
        document.getElementById("clearScanBtn")?.addEventListener("click", clearFormAndResult);
        document.getElementById("logoutBtn")?.addEventListener("click", logout);

        document.getElementById("qrToken").focus();
    } catch (error) {
        console.error(error);
    }
});