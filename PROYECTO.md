# DOCUMENTO TÉCNICO - NOVA ID

---

## 1. OBJETIVO

Desarrollar un sistema profesional de:

- Carnetización digital
- Control de acceso
- Gestión de asistencia
- Analítica institucional

Diseñado como producto SaaS multi-centro.

---

## 2. ALCANCE

### Estudiantes
- Identificación mediante carnet QR
- Registro de asistencia
- Control de acceso
- Gestión académica básica

### Personal (futuro)
- Carnetización
- Control de jornada
- Registro de entradas/salidas

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

### Sistema JWT

- Login con token
- Endpoint `/auth/me`
- Protección de rutas

### Roles

- super_admin
- admin_centro
- registro
- consulta

### Control de acceso

- Restricción por centro
- Validación de permisos por endpoint
- Separación multi-tenant

---

## 5. MODELO DE DATOS

### Núcleo
- Center
- SchoolYear
- Student
- Guardian

### Identificación
- Card (QR + código único)

### Usuarios
- User
- Roles

### Asistencia
- AttendanceEvent
- AttendanceDailySummary

### Institucional
- CenterSchedule
- CenterAttendanceDay

### Eventos especiales
- AuthorizedExit

---

## 6. FILOSOFÍA DE DISEÑO

Separación clara:

- Evento → dato crudo
- Resumen → resultado procesado
- Usuario → control de acceso
- Centro → aislamiento de datos

---

## 7. MULTI-CENTRO

- Cada usuario pertenece a un centro
- super_admin sin restricción
- Usuarios operan solo su centro
- Escalabilidad SaaS

---

## 8. CARNETIZACIÓN

- Código único por estudiante
- QR único por carnet
- Generación automática
- Impresión individual y masiva

---

## 9. REGLAS DE NEGOCIO

### Estudiantes
- Sin duplicados por centro/año
- Tutor principal único
- Carnet generado automáticamente

### Seguridad
- Acceso restringido por rol
- Validación por centro

---

## 10. MIGRACIONES

- Alembic configurado
- Versionado de base de datos
- Control de cambios estructurales

---

## 11. ESTADO ACTUAL

- Backend estable
- Autenticación funcional
- Tabla users implementada
- Roles operativos
- Multi-centro activo

---

## 12. SIGUIENTE FASE

- Protección de UI por rol
- Dashboard por centro
- Facturación de carnets
- Control de acceso físico
- API para dispositivos de entrada