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
  "mission",
  "vision",
  "values",
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
  primary_color: "#1f8f4a",
  secondary_color: "#0b3d24",
  accent_color: "#f4c95d",
  text_color: "#1e1e1e",
  background_color: "#ffffff",
  card_footer_text: "Nova ID by Aula Nova",
  card_design_key: "classic_green_v1",
  show_full_card_identity: "true",
};

const designLabels = {
  classic_green_v1: "Classic Green v1",
  prestige_clean_v1: "Prestige Clean v1",
  nova_modern_v1: "Nova Modern v1",
};

let alertTimeoutId = null;

function showAlert(message, type = "success") {
  if (alertTimeoutId) clearTimeout(alertTimeoutId);

  alertBox.textContent = message;
  alertBox.className = `alert-box ${type}`;

  window.scrollTo({ top: 0, behavior: "smooth" });

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
    philosophy: null,
    mission: getField("mission").value.trim() || null,
    vision: getField("vision").value.trim() || null,
    values: getField("values").value.trim() || null,
    card_philosophy: null,
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
  if (!data.name) return "El nombre del centro es obligatorio.";
  if (!data.code) return "El código del centro es obligatorio.";

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

function setBaseCardTheme(card, { backgroundColor, textColor, accentColor }) {
  if (!card) return;
  card.style.background = backgroundColor;
  card.style.color = textColor;
  card.style.border = `1.5px solid ${accentColor}`;
  card.style.borderRadius = "18px";
  card.style.position = "relative";
  card.style.overflow = "hidden";
}

function setTopBand(band, secondaryColor, primaryColor, accentColor) {
  if (!band) return;
  band.style.position = "absolute";
  band.style.inset = "0 0 auto 0";
  band.style.height = "12px";
  band.style.background = `linear-gradient(90deg, ${secondaryColor}, ${primaryColor}, ${accentColor})`;
}

function styleClassicPreview(elements, theme) {
  const {
    frontCard, backCard, frontHeader, backHeader, frontDecor, backDecor,
    frontBody, photo, studentName, infoGrid, qrWrap,
    missionSection, visionSection, valuesSection
  } = elements;

  frontCard.style.width = "255px";
  frontCard.style.height = "375px";
  backCard.style.width = "255px";
  backCard.style.height = "300px";

  frontCard.style.boxShadow = "0 12px 24px rgba(15, 23, 42, 0.10)";
  backCard.style.boxShadow = "0 12px 24px rgba(15, 23, 42, 0.10)";

  frontDecor.style.display = "block";
  backDecor.style.display = "block";

  frontDecor.style.position = "absolute";
  frontDecor.style.right = "-50px";
  frontDecor.style.bottom = "-20px";
  frontDecor.style.width = "170px";
  frontDecor.style.height = "120px";
  frontDecor.style.background = `linear-gradient(135deg, rgba(31,143,74,0.08), rgba(11,61,36,0.16))`;
  frontDecor.style.transform = "rotate(-18deg)";
  frontDecor.style.borderRadius = "26px";

  backDecor.style.position = "absolute";
  backDecor.style.right = "-50px";
  backDecor.style.bottom = "-10px";
  backDecor.style.width = "170px";
  backDecor.style.height = "110px";
  backDecor.style.background = `linear-gradient(135deg, rgba(31,143,74,0.08), rgba(11,61,36,0.16))`;
  backDecor.style.transform = "rotate(-18deg)";
  backDecor.style.borderRadius = "26px";

  frontHeader.style.position = "relative";
  frontHeader.style.zIndex = "2";
  frontHeader.style.padding = "18px 14px 6px";
  frontHeader.style.display = "flex";
  frontHeader.style.alignItems = "center";
  frontHeader.style.gap = "10px";

  backHeader.style.position = "relative";
  backHeader.style.zIndex = "2";
  backHeader.style.padding = "18px 14px 6px";
  backHeader.style.textAlign = "center";

  frontBody.style.position = "relative";
  frontBody.style.zIndex = "2";
  frontBody.style.padding = "8px 14px 12px";
  frontBody.style.display = "flex";
  frontBody.style.flexDirection = "column";
  frontBody.style.alignItems = "center";
  frontBody.style.gap = "10px";

  photo.style.width = "86px";
  photo.style.height = "86px";
  photo.style.borderRadius = "50%";
  photo.style.border = `4px solid ${theme.primaryColor}`;
  photo.style.background = "#dfe7f1";
  photo.style.display = "flex";
  photo.style.alignItems = "center";
  photo.style.justifyContent = "center";
  photo.style.color = "#64748b";
  photo.style.fontSize = "13px";
  photo.style.fontWeight = "700";

  studentName.style.textAlign = "center";
  studentName.style.fontWeight = "800";
  studentName.style.fontSize = "16px";
  studentName.style.lineHeight = "1.1";
  studentName.style.color = "#0f172a";

  infoGrid.style.width = "100%";
  infoGrid.style.background = "rgba(248,250,252,0.92)";
  infoGrid.style.border = "1px solid rgba(15,23,42,0.08)";
  infoGrid.style.borderRadius = "14px";
  infoGrid.style.padding = "10px 12px";
  infoGrid.style.fontSize = "11px";
  infoGrid.style.lineHeight = "1.55";
  infoGrid.style.color = "#334155";

  qrWrap.style.display = "flex";
  qrWrap.style.flexDirection = "column";
  qrWrap.style.alignItems = "center";
  qrWrap.style.gap = "4px";

  [missionSection, visionSection, valuesSection].forEach((section) => {
    section.style.background = "rgba(255,255,255,0.90)";
    section.style.border = "1px solid rgba(15,23,42,0.08)";
    section.style.borderRadius = "12px";
    section.style.padding = "10px";
    section.style.marginBottom = "8px";
  });
}

function stylePrestigePreview(elements, theme) {
  const {
    frontCard, backCard, frontHeader, backHeader, frontDecor, backDecor,
    frontBody, photo, studentName, infoGrid, qrWrap,
    missionSection, visionSection, valuesSection
  } = elements;

  frontCard.style.width = "255px";
  frontCard.style.height = "375px";
  backCard.style.width = "255px";
  backCard.style.height = "300px";

  frontCard.style.boxShadow = "0 16px 30px rgba(15, 23, 42, 0.08)";
  backCard.style.boxShadow = "0 16px 30px rgba(15, 23, 42, 0.08)";

  frontDecor.style.display = "none";
  backDecor.style.display = "none";

  frontHeader.style.position = "relative";
  frontHeader.style.zIndex = "2";
  frontHeader.style.padding = "18px 14px 10px";
  frontHeader.style.display = "flex";
  frontHeader.style.alignItems = "center";
  frontHeader.style.gap = "10px";
  frontHeader.style.borderBottom = "1px solid rgba(15,23,42,0.08)";

  backHeader.style.position = "relative";
  backHeader.style.zIndex = "2";
  backHeader.style.padding = "18px 14px 10px";
  backHeader.style.textAlign = "center";
  backHeader.style.borderBottom = "1px solid rgba(15,23,42,0.08)";

  frontBody.style.position = "relative";
  frontBody.style.zIndex = "2";
  frontBody.style.padding = "10px 16px 12px";
  frontBody.style.display = "flex";
  frontBody.style.flexDirection = "column";
  frontBody.style.alignItems = "center";
  frontBody.style.gap = "12px";

  photo.style.width = "80px";
  photo.style.height = "80px";
  photo.style.borderRadius = "18px";
  photo.style.border = `2px solid ${theme.primaryColor}`;
  photo.style.background = "#eef2f8";
  photo.style.display = "flex";
  photo.style.alignItems = "center";
  photo.style.justifyContent = "center";
  photo.style.color = "#64748b";
  photo.style.fontSize = "13px";
  photo.style.fontWeight = "700";

  studentName.style.textAlign = "center";
  studentName.style.fontWeight = "800";
  studentName.style.fontSize = "15px";
  studentName.style.lineHeight = "1.1";
  studentName.style.color = "#0f172a";
  studentName.style.letterSpacing = "0.01em";

  infoGrid.style.width = "100%";
  infoGrid.style.background = "rgba(255,255,255,0.96)";
  infoGrid.style.border = "1px solid rgba(15,23,42,0.06)";
  infoGrid.style.borderRadius = "10px";
  infoGrid.style.padding = "10px 12px";
  infoGrid.style.fontSize = "10.5px";
  infoGrid.style.lineHeight = "1.5";
  infoGrid.style.color = "#334155";

  qrWrap.style.display = "flex";
  qrWrap.style.flexDirection = "column";
  qrWrap.style.alignItems = "center";
  qrWrap.style.gap = "4px";

  [missionSection, visionSection, valuesSection].forEach((section) => {
    section.style.background = "rgba(255,255,255,0.98)";
    section.style.border = "1px solid rgba(15,23,42,0.06)";
    section.style.borderRadius = "10px";
    section.style.padding = "9px 10px";
    section.style.marginBottom = "8px";
  });
}

function styleModernPreview(elements, theme) {
  const {
    frontCard, backCard, frontHeader, backHeader, frontDecor, backDecor,
    frontBody, photo, studentName, infoGrid, qrWrap,
    missionSection, visionSection, valuesSection
  } = elements;

  frontCard.style.width = "255px";
  frontCard.style.height = "375px";
  backCard.style.width = "255px";
  backCard.style.height = "300px";

  frontCard.style.boxShadow = "0 18px 36px rgba(15, 23, 42, 0.12)";
  backCard.style.boxShadow = "0 18px 36px rgba(15, 23, 42, 0.12)";

  frontDecor.style.display = "block";
  backDecor.style.display = "block";

  frontDecor.style.position = "absolute";
  frontDecor.style.right = "-34px";
  frontDecor.style.bottom = "-18px";
  frontDecor.style.width = "160px";
  frontDecor.style.height = "120px";
  frontDecor.style.background = `linear-gradient(135deg, rgba(31,143,74,0.10), rgba(11,61,36,0.24))`;
  frontDecor.style.transform = "rotate(-36deg)";
  frontDecor.style.borderRadius = "18px";

  backDecor.style.position = "absolute";
  backDecor.style.right = "-30px";
  backDecor.style.bottom = "-10px";
  backDecor.style.width = "150px";
  backDecor.style.height = "110px";
  backDecor.style.background = `linear-gradient(135deg, rgba(31,143,74,0.10), rgba(11,61,36,0.24))`;
  backDecor.style.transform = "rotate(-36deg)";
  backDecor.style.borderRadius = "18px";

  frontHeader.style.position = "relative";
  frontHeader.style.zIndex = "2";
  frontHeader.style.padding = "18px 14px 8px";
  frontHeader.style.display = "flex";
  frontHeader.style.alignItems = "center";
  frontHeader.style.gap = "10px";

  backHeader.style.position = "relative";
  backHeader.style.zIndex = "2";
  backHeader.style.padding = "18px 14px 8px";
  backHeader.style.textAlign = "center";

  frontBody.style.position = "relative";
  frontBody.style.zIndex = "2";
  frontBody.style.padding = "10px 14px 12px";
  frontBody.style.display = "grid";
  frontBody.style.gridTemplateColumns = "88px 1fr";
  frontBody.style.gridTemplateRows = "auto auto auto";
  frontBody.style.columnGap = "10px";
  frontBody.style.rowGap = "8px";
  frontBody.style.alignItems = "center";

  photo.style.gridColumn = "1 / 2";
  photo.style.gridRow = "1 / 3";
  photo.style.width = "86px";
  photo.style.height = "86px";
  photo.style.borderRadius = "50%";
  photo.style.border = `4px solid ${theme.primaryColor}`;
  photo.style.background = "#dfe7f1";
  photo.style.display = "flex";
  photo.style.alignItems = "center";
  photo.style.justifyContent = "center";
  photo.style.color = "#64748b";
  photo.style.fontSize = "13px";
  photo.style.fontWeight = "700";

  studentName.style.gridColumn = "2 / 3";
  studentName.style.gridRow = "1 / 2";
  studentName.style.textAlign = "left";
  studentName.style.fontWeight = "800";
  studentName.style.fontSize = "15px";
  studentName.style.lineHeight = "1.05";
  studentName.style.color = "#0f172a";

  infoGrid.style.gridColumn = "2 / 3";
  infoGrid.style.gridRow = "2 / 4";
  infoGrid.style.width = "100%";
  infoGrid.style.background = "rgba(248,250,252,0.90)";
  infoGrid.style.border = "1px solid rgba(15,23,42,0.08)";
  infoGrid.style.borderRadius = "14px";
  infoGrid.style.padding = "10px 12px";
  infoGrid.style.fontSize = "10.5px";
  infoGrid.style.lineHeight = "1.5";
  infoGrid.style.color = "#334155";
  infoGrid.style.backdropFilter = "blur(4px)";

  qrWrap.style.gridColumn = "1 / 2";
  qrWrap.style.gridRow = "3 / 4";
  qrWrap.style.display = "flex";
  qrWrap.style.flexDirection = "column";
  qrWrap.style.alignItems = "center";
  qrWrap.style.justifyContent = "flex-end";
  qrWrap.style.gap = "4px";

  [missionSection, visionSection, valuesSection].forEach((section) => {
    section.style.background = "rgba(255,255,255,0.88)";
    section.style.border = "1px solid rgba(15,23,42,0.08)";
    section.style.borderRadius = "12px";
    section.style.padding = "9px 10px";
    section.style.marginBottom = "8px";
    section.style.backdropFilter = "blur(3px)";
  });
}

function styleSharedPreviewText() {
  const headerText = document.querySelectorAll(".mini-header-text h4");
  const headerMeta = document.querySelectorAll(".mini-header-text p");
  const headerLabel = document.getElementById("previewDesignName");
  const backTitle = document.querySelectorAll(".mini-back-section h5");
  const backText = document.querySelectorAll(".mini-back-section p");

  headerText.forEach((el) => {
    el.style.margin = "0";
    el.style.fontSize = "11px";
    el.style.fontWeight = "800";
    el.style.lineHeight = "1.05";
  });

  headerMeta.forEach((el) => {
    el.style.margin = "2px 0 0";
    el.style.fontSize = "8px";
    el.style.lineHeight = "1.2";
  });

  if (headerLabel) {
    headerLabel.style.display = "block";
    headerLabel.style.marginTop = "3px";
    headerLabel.style.fontSize = "10px";
    headerLabel.style.fontWeight = "700";
  }

  backTitle.forEach((el) => {
    el.style.margin = "0 0 4px";
    el.style.fontSize = "10px";
    el.style.fontWeight = "800";
  });

  backText.forEach((el) => {
    el.style.margin = "0";
    el.style.fontSize = "8px";
    el.style.lineHeight = "1.35";
  });
}

function renderPreview() {
  const data = getFormData();

  const theme = {
    primaryColor: data.primary_color || defaultTheme.primary_color,
    secondaryColor: data.secondary_color || defaultTheme.secondary_color,
    accentColor: data.accent_color || defaultTheme.accent_color,
    textColor: data.text_color || defaultTheme.text_color,
    backgroundColor: data.background_color || defaultTheme.background_color,
    footerText: data.card_footer_text || defaultTheme.card_footer_text,
    designKey: data.card_design_key || defaultTheme.card_design_key,
    useFullIdentity: data.show_full_card_identity === true,
  };

  const elements = {
    frontCard: document.getElementById("previewFrontCard"),
    backCard: document.getElementById("previewBackCard"),
    frontHeader: document.getElementById("previewFrontHeader"),
    backHeader: document.getElementById("previewBackHeader"),
    frontFooter: document.getElementById("previewFrontFooter"),
    backFooter: document.getElementById("previewBackFooter"),
    topBand: document.getElementById("previewTopBand"),
    backTopBand: document.getElementById("previewBackTopBand"),
    frontDecor: document.getElementById("previewFrontDecor"),
    backDecor: document.getElementById("previewBackDecor"),
    frontBody: document.getElementById("previewFrontBody"),
    photo: document.getElementById("previewPhoto"),
    studentName: document.getElementById("previewStudentName"),
    infoGrid: document.getElementById("previewFrontInfoGrid"),
    qrWrap: document.getElementById("previewQrWrap"),
    backBody: document.getElementById("previewBackBody"),
    missionSection: document.getElementById("previewMissionSection"),
    visionSection: document.getElementById("previewVisionSection"),
    valuesSection: document.getElementById("previewValuesSection"),
  };

  setBaseCardTheme(elements.frontCard, theme);
  setBaseCardTheme(elements.backCard, theme);
  setTopBand(elements.topBand, theme.secondaryColor, theme.primaryColor, theme.accentColor);
  setTopBand(elements.backTopBand, theme.secondaryColor, theme.primaryColor, theme.accentColor);
  styleSharedPreviewText();

  if (theme.designKey === "prestige_clean_v1") {
    stylePrestigePreview(elements, theme);
  } else if (theme.designKey === "nova_modern_v1") {
    styleModernPreview(elements, theme);
  } else {
    styleClassicPreview(elements, theme);
  }

  document.getElementById("previewCenterNameFront").textContent =
    data.name || "Centro educativo";
  document.getElementById("previewCenterNameBack").textContent =
    data.name || "Centro educativo";
  currentCenterName.textContent = data.name || "Centro educativo";

  const contactParts = [data.phone, data.email].filter(Boolean);
  document.getElementById("previewContactLine").textContent =
    contactParts.length > 0 ? contactParts.join(" · ") : "Teléfono · correo";

  const designName = document.getElementById("previewDesignName");
  designName.textContent = designLabels[theme.designKey] || "Classic Green v1";
  designName.style.color = theme.designKey === "prestige_clean_v1" ? "#334155" : theme.primaryColor;

  document.getElementById("previewMission").textContent =
    theme.useFullIdentity
      ? (data.mission || "Texto institucional completo.")
      : (data.card_mission || data.mission || "Texto corto de misión.");

  document.getElementById("previewVision").textContent =
    theme.useFullIdentity
      ? (data.vision || "Texto institucional completo.")
      : (data.card_vision || data.vision || "Texto corto de visión.");

  document.getElementById("previewValues").textContent =
    theme.useFullIdentity
      ? (data.values || "Texto institucional completo.")
      : (data.card_values || data.values || "Texto corto de valores.");

  [elements.frontFooter, elements.backFooter].forEach((footer) => {
    footer.textContent = theme.footerText;
    footer.style.textAlign = "center";
    footer.style.fontSize = "9px";
    footer.style.color = "#5b6777";
    footer.style.padding = "6px 8px 8px";
    footer.style.position = "relative";
    footer.style.zIndex = "2";
  });

  elements.backBody.classList.toggle("preview-long", theme.useFullIdentity);
  elements.backBody.classList.toggle("preview-short", !theme.useFullIdentity);

  document.querySelectorAll(".mini-back-section h5").forEach((title) => {
    title.style.textAlign = "center";
  });

  document.querySelectorAll(".mini-back-section p").forEach((paragraph) => {
    paragraph.style.textAlign = theme.useFullIdentity ? "left" : "center";
  });

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

  const logoWraps = document.querySelectorAll(".mini-logo-wrap");
  logoWraps.forEach((wrap) => {
    wrap.style.width = "38px";
    wrap.style.height = "38px";
    wrap.style.borderRadius = theme.designKey === "prestige_clean_v1" ? "12px" : "10px";
    wrap.style.background = "#ffffff";
    wrap.style.border = "1px solid rgba(0,0,0,0.08)";
    wrap.style.display = "flex";
    wrap.style.alignItems = "center";
    wrap.style.justifyContent = "center";
    wrap.style.overflow = "hidden";
    wrap.style.flexShrink = "0";
  });

  if (logo) {
    logo.style.width = "100%";
    logo.style.height = "100%";
    logo.style.objectFit = "contain";
  }

  if (logoPlaceholder) {
    logoPlaceholder.style.width = "100%";
    logoPlaceholder.style.height = "100%";
    logoPlaceholder.style.background = "#e8eef7";
  }

  elements.backHeader.style.textAlign = "center";
  elements.backHeader.style.padding = "18px 14px 8px";
  elements.backHeader.style.position = "relative";
  elements.backHeader.style.zIndex = "2";

  document.getElementById("previewCenterNameBack").style.margin = "0";
  document.getElementById("previewCenterNameBack").style.fontSize = "12px";
  document.getElementById("previewCenterNameBack").style.fontWeight = "800";
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