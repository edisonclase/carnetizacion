# Nova ID - Sistema de Carnetización y Control de Asistencia  
**by Aula Nova**

## 📌 Descripción

Nova ID es un sistema de identificación escolar, control de asistencia y análisis institucional, diseñado para centros educativos del sistema dominicano.

El sistema permite:
- Registro de estudiantes
- Emisión de carnets con QR
- Control de entradas y salidas
- Registro de tardanzas y ausencias
- Gestión de salidas autorizadas
- Generación de reportes y estadísticas
- Dashboard institucional

---

## 🧱 Arquitectura

- **Backend:** FastAPI
- **Base de datos:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migraciones:** Alembic
- **Validación:** Pydantic

---

## 🗂️ Modelos principales

- Center
- CenterSchedule
- CenterAttendanceDay
- SchoolYear
- Student (incluye minerd_id)
- Guardian
- Card
- AttendanceEvent
- AttendanceDailySummary (usa "excusa")
- AuthorizedExit

---

## 🏫 Reglas institucionales (CEJOMA)

- Entrada: 7:30 AM  
- Salida: 3:30 PM  
- Días laborables: lunes a viernes  

Reglas inteligentes:
- Sin registros → posible no docencia
- Muchas salidas antes de las 3:00 PM → posible despacho temprano

---

## 📊 Funcionalidades clave

### Asistencia
- Registro de entradas y salidas
- Tardanzas automáticas
- Ausencias
- Excusas

### Carnetización
- Generación de QR
- Código único por carnet

### Salidas autorizadas
- Registro de autorización
- Responsable
- Motivo
- Persona que retira

### Reportes
- Diario
- Mensual
- Por curso
- Por sexo
- Por estudiante

### Analítica
- Porcentaje de asistencia
- Ranking de incidencias
- Tendencias institucionales

---

## 🚀 Estado del proyecto

En desarrollo activo.

Fase actual:
- Modelado de datos completo
- Migraciones configuradas
- Schemas creados
- Próximo paso: Endpoints CRUD y lógica de negocio

---

## 🧠 Visión

Convertirse en una plataforma de gestión escolar inteligente que combine:
- identificación
- asistencia
- análisis de datos
- comunicación institucional

---

## 👨‍💻 Autor

Edison Clase  
Sistema Aula Nova