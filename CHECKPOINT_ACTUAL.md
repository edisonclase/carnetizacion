# CHECKPOINT ACTUAL — NOVA ID

## 📌 Estado del Proyecto

Nova ID es un sistema de carnetización y control de asistencia institucional, diseñado como un producto independiente, con branding propio y respaldo de Aula Nova.

---

## 🎯 Objetivo General

Desarrollar una solución que permita:

- Identificación de estudiantes y personal mediante carnet
- Registro de entradas y salidas
- Control de asistencia diario, mensual y anual
- Gestión de excusas
- Registro de salidas autorizadas
- Generación de reportes institucionales
- Visualización de datos mediante dashboard

---

## 🧱 Módulos Implementados

### 1. Estructura base
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### 2. Modelos principales
- Center
- SchoolYear
- Student (incluye MINERD ID)
- Guardian
- Card
- CenterSchedule (configurable)
- AttendanceEvent
- AttendanceDailySummary
- CenterAttendanceDay
- AuthorizedExit

---

### 3. Lógica de asistencia
- Registro de entrada
- Clasificación automática (on_time / late)
- Registro de salida
- Validación de días laborables
- Detección de tardanza

---

### 4. Validaciones avanzadas
- Salida autorizada validada contra AuthorizedExit
- Tolerancia configurable por centro
- Validación de carnet contra estudiante

---

### 5. Excusas
- Aplicación de excusas por día
- Registro de motivo

---

### 6. Reportes
- Reporte diario institucional
- Reporte agrupado por:
  - curso
  - sexo
- Reporte mensual

---

### 7. Dashboard (UI)
- Filtros por:
  - centro
  - año escolar
  - fecha
- Métricas:
  - presentes
  - tardanzas
  - ausentes
  - excusas
- Tablas:
  - por curso
  - por sexo
  - detalle individual
- Gráficos:
  - asistencia por curso
  - distribución por sexo

---

## 🧠 Decisiones Arquitectónicas Clave

### 🔹 Sistema independiente
Nova ID es un producto separado de Aula Nova  
(con branding: “by Aula Nova”)

---

### 🔹 Configuración por centro
Cada centro tiene:
- horarios
- tolerancias
- reglas propias

---

### 🔹 Uso de eventos
La asistencia se basa en eventos reales:
- entry
- exit

---

### 🔹 Validaciones reales institucionales
- salida autorizada obligatoria
- detección de no docencia
- detección de despacho temprano

---

## 🧑‍🏫 Módulo de Personal (Pendiente - DEFINIDO)

Se implementará un modelo:

### Staff / Personnel

Roles:
- docente
- secretaria
- digitador
- orientador
- administrativo

Permitirá:
- carnetización
- registro de asistencia
- control de entradas/salidas

---

## 🪪 Carnetización (Pendiente - DEFINIDO)

### Carnet Estudiantil

**Frontal:**
- nombre del centro
- nombre del estudiante
- foto
- código
- ID MINERD
- curso y sección
- año escolar
- QR
- branding Nova ID

**Reverso:**
- misión
- visión
- valores
- filosofía del centro

---

### Carnet de Personal
- nombre
- rol
- foto
- código
- QR

---

## 🚧 Próximas Fases

### Fase inmediata
- Selectores reales (centro y año escolar)
- Mejora UX dashboard

### Fase siguiente
- Diseño de carnets
- Generación de QR
- Plantilla imprimible
- Exportación a PDF

### Fase avanzada
- Módulo de personal
- Reportes exportables
- Alertas inteligentes

---

## 📊 Estado General

Proyecto en fase:
👉 MVP funcional avanzado

Listo para:
- pruebas reales en centro educativo
- validación operativa
- demostraciones

---

## ⚠️ Regla clave del proyecto

NO modificar lo que ya funciona correctamente.

Toda mejora debe:
- ser modular
- no romper lógica existente
- mantener consistencia de datos