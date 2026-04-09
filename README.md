# Nova ID - Sistema de Carnetización, Control de Acceso y Asistencia  
**by Aula Nova**

---

## 📌 Descripción

Nova ID es un sistema profesional de identificación digital, carnetización, control de acceso y análisis institucional para centros educativos.

Permite gestionar estudiantes, personal, accesos y asistencia mediante carnets con QR únicos, integrando seguridad, trazabilidad y analítica en tiempo real.

---

## 🎯 Objetivos

- Digitalizar la identificación institucional
- Automatizar el control de acceso
- Gestionar asistencia en tiempo real
- Proveer analítica educativa e institucional
- Implementar un modelo SaaS multi-centro escalable
- Integrarse con la plataforma Aula Nova

---

## 🧱 Arquitectura

- **Backend:** FastAPI
- **Base de datos:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migraciones:** Alembic
- **Validación:** Pydantic
- **Autenticación:** JWT (python-jose)
- **Seguridad:** Passlib + bcrypt

---

## 🔐 Sistema de autenticación

El sistema cuenta con autenticación completa basada en JWT.

### Roles implementados

- **super_admin**
  - Control total del sistema
  - Gestión global multi-centro

- **admin_centro**
  - Acceso a dashboard institucional
  - Visualización de estadísticas

- **registro**
  - Operación completa de estudiantes
  - Emisión de carnets

- **consulta**
  - Acceso de solo lectura

---

## 🏫 Multi-centro (SaaS Ready)

El sistema está diseñado para operar múltiples centros educativos:

- Separación de datos por `center_id`
- Control de acceso por usuario
- Restricción automática de datos por centro
- Escalable para comercialización

---

## 🗂️ Modelos implementados

### Núcleo
- Center
- SchoolYear
- Student
- Guardian

### Identificación
- Card (QR único por estudiante)

### Usuarios y seguridad
- User
- Roles

### Asistencia
- AttendanceEvent
- AttendanceDailySummary

### Configuración institucional
- CenterSchedule
- CenterAttendanceDay

### Eventos especiales
- AuthorizedExit

---

## 🪪 Carnetización

### Funcionalidades

- Generación automática de carnets
- Código único por estudiante
- Token QR único
- Impresión individual y masiva
- Preparado para PDF profesional

---

## 📊 Funcionalidades principales

### Estudiantes
- Registro completo
- Edición
- Validación de duplicados
- Asociación con tutor

### Carnets
- Generación automática
- QR único
- Impresión múltiple

### Asistencia
- Registro de entradas y salidas
- Clasificación automática
- Control institucional

### Usuarios
- Autenticación JWT
- Roles y permisos
- Multi-centro seguro

---

## 🚀 Estado del proyecto

Fase actual:

- Autenticación completa ✔
- Sistema de roles ✔
- Multi-centro ✔
- CRUD de estudiantes ✔
- Generación de carnets ✔
- Alembic configurado ✔
- UI operativa ✔

---

## 🧠 Visión

Convertirse en una plataforma educativa inteligente que combine:

- Identidad digital
- Control institucional
- Seguridad de acceso
- Analítica en tiempo real
- Modelo SaaS comercializable

---

## 👨‍💻 Autor

Edison Clase  
Proyecto Aula Nova