# DOCUMENTO TÉCNICO - NOVA ID

## 1. OBJETIVO

Desarrollar un sistema de carnetización, control de asistencia y análisis institucional para centros educativos.

---

## 2. ALCANCE

El sistema incluye:

### Estudiantes
- Identificación mediante carnet
- Registro de asistencia
- Excusas
- Salidas autorizadas

### Personal docente (expansión)
- Carnetización
- Entradas y salidas múltiples
- Control de jornada
- Registro de permisos

---

## 3. ARQUITECTURA

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic

Arquitectura modular orientada a servicios.

---

## 4. MODELO DE DATOS

### Núcleo
- Center
- SchoolYear
- Student
- Guardian

### Identificación
- Card

### Asistencia
- AttendanceEvent
- AttendanceDailySummary

### Institucional
- CenterSchedule
- CenterAttendanceDay

### Eventos especiales
- AuthorizedExit

---

## 5. FILOSOFÍA DE DISEÑO

Separación clara de responsabilidades:

- Event → evento crudo
- Summary → resultado diario
- Institutional → comportamiento global

---

## 6. REGLAS DE NEGOCIO

### Estudiantes

- Entrada: 7:30 AM
- Salida: 3:30 PM

#### Clasificación:
- Presente
- Tarde
- Ausente
- Ausente con excusa

#### Reglas:
- Sin registros → posible no docencia
- Muchas salidas antes de 3:00 → posible despacho temprano

---

## 7. SALIDAS AUTORIZADAS

Entidad independiente:

- Motivo
- Responsable
- Persona que retira
- Registro institucional

---

## 8. MÓDULO DE PERSONAL DOCENTE (DISEÑO FUTURO)

### Requisitos

- Múltiples entradas y salidas por día
- Identificación de salida final
- Registro de permisos
- Análisis de permanencia

### Reglas

- La última salida sin reentrada es la salida final
- Puede haber salidas intermedias
- Puede haber permisos registrados

---

## 9. REPORTES

### Operativos
- Asistencia diaria

### Administrativos
- Resumen mensual

### Analíticos
- Tendencias
- Comportamiento
- Incidencias

---

## 10. ESCALABILIDAD

- Multi-centro
- Multi-año escolar
- Integración con Aula Nova

---

## 11. SIGUIENTE FASE

- Generación automática de AttendanceDailySummary
- Generación de CenterAttendanceDay
- Endpoints de reportes
- Dashboard interactivo
- Módulo de personal docente