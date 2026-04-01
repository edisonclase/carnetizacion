# DOCUMENTO TÉCNICO - NOVA ID

## 1. OBJETIVO

Desarrollar un sistema independiente de carnetización y control de asistencia escolar con capacidades analíticas, integrado conceptualmente a Aula Nova.

---

## 2. ENFOQUE

Sistema modular con:
- registro de identidad
- eventos de asistencia
- procesamiento de datos
- análisis institucional

---

## 3. MODELO DE DATOS

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

## 4. FILOSOFÍA DE DISEÑO

Separación de responsabilidades:

- Event → evento crudo
- Summary → resultado diario
- Institutional → análisis global

---

## 5. REGLAS DE NEGOCIO

### Entrada
- Hora oficial: 7:30 AM

### Salida
- Hora oficial: 3:30 PM

### Tardanza
- Entrada después de la hora definida

### Ausencia
- No registro dentro del rango esperado

### Excusa
- Ausencia justificada manualmente

### No docencia
- Día laborable sin registros

### Despacho temprano
- Alta cantidad de salidas antes de las 3:00 PM

---

## 6. SALIDAS AUTORIZADAS

Modelo independiente:
- motivo
- responsable
- persona que retira
- registro de autorización

---

## 7. REPORTES

### Operativos
- asistencia diaria

### Administrativos
- mensual por curso

### Analíticos
- tendencias
- patrones

---

## 8. ESCALABILIDAD

Preparado para:
- múltiples centros
- múltiples años escolares
- integración futura con Aula Nova

---

## 9. SIGUIENTE FASE

- CRUD
- lógica de asistencia
- generación de reportes
- dashboard interactivo