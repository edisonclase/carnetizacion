# Nova ID - Sistema de Carnetización y Control de Asistencia  
**by Aula Nova**

## 📌 Descripción

Nova ID es un sistema integral de identificación, control de asistencia y análisis institucional para centros educativos.

Permite gestionar tanto estudiantes como personal docente, incorporando registro de entradas, salidas, permisos y análisis de comportamiento.

---

## 🎯 Objetivos

- Digitalizar la asistencia escolar
- Automatizar el control de entradas y salidas
- Generar reportes institucionales
- Proveer analítica educativa en tiempo real
- Integrarse conceptualmente con Aula Nova

---

## 🧱 Arquitectura

- **Backend:** FastAPI
- **Base de datos:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migraciones:** Alembic
- **Validación:** Pydantic

---

## 🗂️ Modelos implementados

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

### Configuración institucional
- CenterSchedule
- CenterAttendanceDay

### Eventos especiales
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

## 👨‍🏫 Módulo de personal (EN DESARROLLO)

El sistema incluirá soporte para docentes y personal administrativo:

- Carnetización del personal
- Registro de múltiples entradas y salidas por día
- Identificación de salida final del día
- Registro de salidas con permiso
- Análisis de permanencia laboral

---

## 📊 Funcionalidades

### Estudiantes
- Registro de asistencia
- Tardanzas
- Ausencias
- Excusas
- Salidas autorizadas

### Personal docente (futuro)
- Entradas múltiples
- Salidas intermedias
- Permisos
- Control de jornada

### Reportes
- Diario
- Mensual
- Por curso
- Por sexo
- Por estudiante

### Analítica
- Porcentaje de asistencia
- Tendencias
- Incidencias
- Comportamiento institucional

---

## 🚀 Estado del proyecto

Fase actual:
- Modelado de datos completo ✔
- CRUDs principales ✔
- Registro de eventos ✔

Próximos pasos:
- Lógica automática de asistencia
- Generación de resúmenes
- Reportes y estadísticas
- Dashboard
- Módulo de personal docente

---

## 🧠 Visión

Convertirse en una plataforma inteligente de gestión educativa que combine:

- Identidad digital
- Control institucional
- Analítica educativa
- Toma de decisiones basada en datos

---

## 👨‍💻 Autor

Edison Clase  
Proyecto Aula Nova