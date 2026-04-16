# DOCUMENTO TÉCNICO - NOVA ID

---

## 1. OBJETIVO

Desarrollar un sistema profesional de:

- Carnetización digital
- Control de acceso
- Gestión de asistencia
- Facturación institucional
- Analítica institucional

Diseñado como producto SaaS multi-centro.

---

## 2. ALCANCE

### Estudiantes
- Identificación mediante carnet QR
- Registro de asistencia
- Control de acceso

### Institucional
- Gestión por centros
- Control de usuarios
- Facturación de servicios

---

## 3. ARQUITECTURA

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication

Arquitectura modular orientada a servicios.

---

## 4. SEGURIDAD Y AUTENTICACIÓN

- JWT (python-jose)
- Hash bcrypt
- Roles:
  - super_admin
  - admin_centro
  - registro
  - consulta

- Protección por endpoint
- Resolución de centro

---

## 5. MODELO DE DATOS

### Núcleo
- Center
- SchoolYear
- Student
- Guardian

### Identificación
- Card

### Usuarios
- User

### Asistencia
- AttendanceEvent
- AttendanceDailySummary

### Facturación (nuevo)
- BillingInvoice
- BillingPayment

---

## 6. MULTI-CENTRO

- Separación por `center_id`
- Acceso restringido por usuario
- super_admin global
- Escalabilidad SaaS

---

## 7. FACTURACIÓN

Permite:

- Generar facturas por centro
- Registrar pagos
- Calcular balances
- Control financiero básico

Diseñado para monetización del sistema.

---

## 8. MIGRACIONES

- Alembic configurado
- Versionado activo
- Correcciones manuales realizadas

---

## 9. ESTADO ACTUAL

- Backend estable ✔
- Dashboard funcional ✔
- Facturación backend ✔
- UI en desarrollo ✔
- Seguridad en consolidación ✔

---

## 10. SIGUIENTE FASE

- UI de facturación
- Seguridad frontend total
- Reportes financieros
- Auditoría
- Integración con dispositivos físicos