const bodyEl = document.body;
const centerId = bodyEl.dataset.centerId;

const form = document.getElementById("centerSettingsForm");
const alertBox = document.getElementById("alertBox");
const reloadBtn = document.getElementById("reloadBtn");
const saveBtn = document.getElementById("saveBtn");
const currentCenterName = document.getElementById("currentCenterName");

const fieldIds = [
  "name",
  "code",
  "logo_url",
  "letterhead_url",
  "primary_color",
  "secondary_color",
  "accent_color",
  "text_color",
  "background_color",
  "card_design_key",
  "show_full_card_identity",
  "philosophy",
  "mission",
  "vision",
  "values",
  "card_philosophy",
  "card_mission",
  "card_vision",
  "card_values",
  "card_footer_text",
  "motto",
  "address",
  "phone",
  "email",
  "district_name",
  "management_code",
  "is_active",
];

const pickerMap = [
  ["primary_color", "primary_color_picker"],
  ["secondary_color", "secondary_color_picker"],
  ["accent_color", "accent_color_picker"],
  ["text_color", "text_color_picker"],
  ["background_color", "background_color_picker"],
];

const defaultTheme = {
  primary_color: "#2563eb",
  secondary_color: "#1d4ed8",
  accent_color: "#e2e8f0",
  text_color: "#1e293b",
  background_color: "#ffffff",
  card_footer_text: "by Aula Nova",
  card_design_key: "classic_green_v1",
  show_full_card_identity: "true",
};

const designLabels = {
  classic_green_v1: "Carnet Estudiantil · Classic Green v1",
  prestige_clean_v1: "Carnet Estudiantil · Prestige Clean v1",
  nova_modern_v1: "Carnet Estudiantil · Nova Modern v1",
};

let alertTimeoutId = null;

function showAlert(message, type = "success") {
  if (alertTimeoutId) {
    clearTimeout(alertTimeoutId);
  }

  alertBox.textContent = message;
  alertBox.className = `alert-box ${type}`;

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });

  if (type === "success") {
    alertTimeoutId = window.setTimeout(() => {
      hideAlert();
    }, 3500);
  }
}

function hideAlert() {
  if (alertTimeoutId) {
    clearTimeout(alertTimeoutId);
    alertTimeoutId = null;
  }

  alertBox.textContent = "";
  alertBox.className = "alert-box hidden";
}

function getField(id) {
  return document.getElementById(id);
}

function normalizeValue(value) {
  if (value === undefined || value === null) return "";
  return String(value);
}

function isValidHexColor(value) {
  if (!value) return true;
  return /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(value);
}

function syncPickerFromText(inputId, pickerId) {
  const input = getField(inputId);
  const picker = getField(pickerId);

  if (!input || !picker) return;

  const value = input.value.trim();
  if (isValidHexColor(value)) {
    picker.value = value;
  }
}

function syncTextFromPicker(inputId, pickerId) {
  const input = getField(inputId);
  const picker = getField(pickerId);

  if (!input || !picker) return;

  input.value = picker.value;
  renderPreview();
}

function fillForm(data) {
  fieldIds.forEach((id) => {
    const field = getField(id);
    if (!field) return;

    if (id === "is_active") {
      field.value = String(data[id] ?? true);
      return;
    }

    if (id === "show_full_card_identity") {
      field.value = String(data[id] ?? true);
      return;
    }

    if (id === "card_design_key") {
      field.value = data[id] || defaultTheme.card_design_key;
      return;
    }

    field.value = normalizeValue(data[id]);
  });

  pickerMap.forEach(([inputId, pickerId]) => {
    const input = getField(inputId);
    const picker = getField(pickerId);
    if (!input || !picker) return;

    const value = input.value.trim() || defaultTheme[inputId] || "#ffffff";
    picker.value = isValidHexColor(value)
      ? value
      : (defaultTheme[inputId] || "#ffffff");
  });

  currentCenterName.textContent = data.name || "Centro educativo";
  renderPreview();
}

function getFormData() {
  return {
    name: getField("name").value.trim(),
    code: getField("code").value.trim(),
    logo_url: getField("logo_url").value.trim() || null,
    letterhead_url: getField("letterhead_url").value.trim() || null,
    primary_color: getField("primary_color").value.trim() || null,
    secondary_color: getField("secondary_color").value.trim() || null,
    accent_color: getField("accent_color").value.trim() || null,
    text_color: getField("text_color").value.trim() || null,
    background_color: getField("background_color").value.trim() || null,
    card_design_key: getField("card_design_key").value || defaultTheme.card_design_key,
    show_full_card_identity: getField("show_full_card_identity").value === "true",
    philosophy: getField("philosophy").value.trim() || null,
    mission: getField("mission").value.trim() || null,
    vision: getField("vision").value.trim() || null,
    values: getField("values").value.trim() || null,
    card_philosophy: getField("card_philosophy").value.trim() || null,
    card_mission: getField("card_mission").value.trim() || null,
    card_vision: getField("card_vision").value.trim() || null,
    card_values: getField("card_values").value.trim() || null,
    card_footer_text: getField("card_footer_text").value.trim() || null,
    motto: getField("motto").value.trim() || null,
    address: getField("address").value.trim() || null,
    phone: getField("phone").value.trim() || null,
    email: getField("email").value.trim() || null,
    district_name: getField("district_name").value.trim() || null,
    management_code: getField("management_code").value.trim() || null,
    is_active: getField("is_active").value === "true",
  };
}

function validateForm(data) {
  if (!data.name) {
    return "El nombre del centro es obligatorio.";
  }

  if (!data.code) {
    return "El código del centro es obligatorio.";
  }

  const colorFields = [
    ["primary_color", "Color primario"],
    ["secondary_color", "Color secundario"],
    ["accent_color", "Color de acento"],
    ["text_color", "Color de texto"],
    ["background_color", "Color de fondo"],
  ];

  for (const [fieldName, label] of colorFields) {
    if (!isValidHexColor(data[fieldName])) {
      return `${label}: usa un formato HEX válido, por ejemplo #1f8f4a.`;
    }
  }

  return null;
}

function renderPreview() {
  const data = getFormData();

  const primaryColor = data.primary_color || defaultTheme.primary_color;
  const accentColor = data.accent_color || defaultTheme.accent_color;
  const textColor = data.text_color || defaultTheme.text_color;
  const backgroundColor = data.background_color || defaultTheme.background_color;
  const footerText = data.card_footer_text || defaultTheme.card_footer_text;
  const useFullIdentity = data.show_full_card_identity === true;

  const frontCard = document.getElementById("previewFrontCard");
  const backCard = document.getElementById("previewBackCard");
  const frontHeader = document.getElementById("previewFrontHeader");
  const backHeader = document.getElementById("previewBackHeader");
  const frontFooter = document.getElementById("previewFrontFooter");
  const backFooter = document.getElementById("previewBackFooter");
  const previewDesignName = document.getElementById("previewDesignName");

  frontCard.style.background = backgroundColor;
  frontCard.style.color = textColor;
  frontCard.style.borderColor = accentColor;

  backCard.style.background = backgroundColor;
  backCard.style.color = textColor;
  backCard.style.borderColor = accentColor;

  frontHeader.style.background = primaryColor;
  backHeader.style.background = primaryColor;

  frontFooter.style.borderTopColor = accentColor;
  frontFooter.style.background = backgroundColor;
  frontFooter.style.color = textColor;
  frontFooter.textContent = footerText;

  backFooter.style.borderTopColor = accentColor;
  backFooter.style.background = backgroundColor;
  backFooter.style.color = textColor;
  backFooter.textContent = footerText;

  document.getElementById("previewCenterNameFront").textContent =
    data.name || "Centro educativo";
  document.getElementById("previewCenterNameBack").textContent =
    data.name || "Centro educativo";
  currentCenterName.textContent = data.name || "Centro educativo";

  const contactParts = [data.phone, data.email].filter(Boolean);
  document.getElementById("previewContactLine").textContent =
    contactParts.length > 0 ? contactParts.join(" · ") : "Teléfono · correo";

  previewDesignName.textContent =
    designLabels[data.card_design_key] || "Carnet Estudiantil";

  document.getElementById("previewPhilosophy").textContent =
    useFullIdentity
      ? (data.philosophy || "Texto institucional completo.")
      : (data.card_philosophy || data.philosophy || "Texto corto de filosofía.");

  document.getElementById("previewMission").textContent =
    useFullIdentity
      ? (data.mission || "Texto institucional completo.")
      : (data.card_mission || data.mission || "Texto corto de misión.");

  document.getElementById("previewVision").textContent =
    useFullIdentity
      ? (data.vision || "Texto institucional completo.")
      : (data.card_vision || data.vision || "Texto corto de visión.");

  document.getElementById("previewValues").textContent =
    useFullIdentity
      ? (data.values || "Texto institucional completo.")
      : (data.card_values || data.values || "Texto corto de valores.");

  const logo = document.getElementById("previewLogo");
  const logoPlaceholder = document.getElementById("previewLogoPlaceholder");

  if (data.logo_url) {
    logo.src = data.logo_url;
    logo.classList.remove("hidden");
    logoPlaceholder.style.display = "none";
  } else {
    logo.removeAttribute("src");
    logo.classList.add("hidden");
    logoPlaceholder.style.display = "block";
  }
}

async function loadCenterData() {
  hideAlert();

  try {
    reloadBtn.disabled = true;
    reloadBtn.textContent = "Recargando...";

    const response = await fetch(`/centers/${centerId}`);

    if (!response.ok) {
      throw new Error("No se pudo cargar la configuración del centro.");
    }

    const data = await response.json();
    fillForm(data);
  } catch (error) {
    showAlert(error.message || "Ocurrió un error al cargar los datos.", "error");
  } finally {
    reloadBtn.disabled = false;
    reloadBtn.textContent = "Recargar";
  }
}

async function saveCenterData(event) {
  event.preventDefault();
  hideAlert();

  const payload = getFormData();
  const validationError = validateForm(payload);

  if (validationError) {
    showAlert(validationError, "error");
    return;
  }

  saveBtn.disabled = true;
  saveBtn.textContent = "Guardando...";

  try {
    const response = await fetch(`/centers/${centerId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();

    if (!response.ok) {
      const detail = result?.detail || "No se pudieron guardar los cambios.";
      throw new Error(detail);
    }

    fillForm(result);
    showAlert("Configuración del centro actualizada correctamente.", "success");
  } catch (error) {
    showAlert(error.message || "Ocurrió un error al guardar.", "error");
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Guardar cambios";
  }
}

function bindEvents() {
  form.addEventListener("submit", saveCenterData);
  reloadBtn.addEventListener("click", loadCenterData);

  fieldIds.forEach((id) => {
    const field = getField(id);
    if (!field) return;

    field.addEventListener("input", renderPreview);
    field.addEventListener("change", renderPreview);
  });

  pickerMap.forEach(([inputId, pickerId]) => {
    const input = getField(inputId);
    const picker = getField(pickerId);

    if (input) {
      input.addEventListener("input", () => {
        syncPickerFromText(inputId, pickerId);
        renderPreview();
      });

      input.addEventListener("change", () => {
        syncPickerFromText(inputId, pickerId);
        renderPreview();
      });
    }

    if (picker) {
      picker.addEventListener("input", () => syncTextFromPicker(inputId, pickerId));
      picker.addEventListener("change", () => syncTextFromPicker(inputId, pickerId));
    }
  });
}

bindEvents();
loadCenterData();