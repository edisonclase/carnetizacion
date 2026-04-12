from collections import defaultdict
from datetime import date

from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.models.attendance_daily_summary import AttendanceDailySummary
from app.models.center_attendance_day import CenterAttendanceDay
from app.models.student import Student


class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_center_day(self, center_id: int, school_year_id: int, target_date: date) -> CenterAttendanceDay:
        center_day = (
            self.db.query(CenterAttendanceDay)
            .filter(
                CenterAttendanceDay.center_id == center_id,
                CenterAttendanceDay.school_year_id == school_year_id,
                CenterAttendanceDay.date == target_date,
            )
            .first()
        )

        if not center_day:
            raise ValueError(
                "No existe consolidado institucional para la fecha indicada. "
                "Genera primero el CenterAttendanceDay."
            )

        return center_day

    def _get_summary_rows(self, center_id: int, school_year_id: int, target_date: date):
        return (
            self.db.query(AttendanceDailySummary, Student)
            .join(Student, Student.id == AttendanceDailySummary.student_id)
            .filter(
                Student.center_id == center_id,
                Student.school_year_id == school_year_id,
                AttendanceDailySummary.date == target_date,
            )
            .order_by(
                Student.grade.asc(),
                Student.section.asc(),
                Student.last_name.asc(),
                Student.first_name.asc(),
            )
            .all()
        )

    @staticmethod
    def _normalize_gender(value: str | None) -> str:
        raw = (value or "").strip().lower()
        if raw in {"m", "masculino", "male"}:
            return "male"
        if raw in {"f", "femenino", "female"}:
            return "female"
        return "other"

    def _build_student_item(self, summary: AttendanceDailySummary, student: Student) -> dict:
        return {
            "student_id": student.id,
            "student_code": student.student_code,
            "minerd_id": student.minerd_id,
            "full_name": f"{student.first_name} {student.last_name}",
            "gender": student.gender,
            "grade": student.grade,
            "section": student.section,
            "status": summary.status,
            "has_excuse": summary.has_excuse,
            "excuse_note": summary.excuse_note,
            "first_entry_time": summary.first_entry_time,
            "minutes_late": summary.minutes_late,
        }

    def _build_printable_totals(self, rows: list[tuple[AttendanceDailySummary, Student]]) -> dict:
        base = {
            "male": 0,
            "female": 0,
            "total": 0,
        }

        totals = {
            "present": base.copy(),
            "late": base.copy(),
            "absent": base.copy(),
            "excuse": base.copy(),
            "general": base.copy(),
            "enrollment": base.copy(),
        }

        for summary, student in rows:
            gender = self._normalize_gender(student.gender)

            if gender == "male":
                totals["general"]["male"] += 1
                totals["enrollment"]["male"] += 1
            elif gender == "female":
                totals["general"]["female"] += 1
                totals["enrollment"]["female"] += 1

            totals["general"]["total"] += 1
            totals["enrollment"]["total"] += 1

            if summary.status == "present":
                if gender == "male":
                    totals["present"]["male"] += 1
                elif gender == "female":
                    totals["present"]["female"] += 1
                totals["present"]["total"] += 1

            elif summary.status == "late":
                if gender == "male":
                    totals["late"]["male"] += 1
                elif gender == "female":
                    totals["late"]["female"] += 1
                totals["late"]["total"] += 1

            elif summary.status == "absent":
                if gender == "male":
                    totals["absent"]["male"] += 1
                elif gender == "female":
                    totals["absent"]["female"] += 1
                totals["absent"]["total"] += 1

            if summary.has_excuse:
                if gender == "male":
                    totals["excuse"]["male"] += 1
                elif gender == "female":
                    totals["excuse"]["female"] += 1
                totals["excuse"]["total"] += 1

        return totals

    def _build_printable_course_rows(self, rows: list[tuple[AttendanceDailySummary, Student]]) -> list[dict]:
        course_groups = defaultdict(
            lambda: {
                "grade": "",
                "section": "",
                "enrollment_male": 0,
                "enrollment_female": 0,
                "enrollment_total": 0,
                "present_male": 0,
                "present_female": 0,
                "present_total": 0,
                "late_male": 0,
                "late_female": 0,
                "late_total": 0,
                "absent_male": 0,
                "absent_female": 0,
                "absent_total": 0,
                "excuse_male": 0,
                "excuse_female": 0,
                "excuse_total": 0,
            }
        )

        for summary, student in rows:
            key = (student.grade, student.section)
            group = course_groups[key]
            group["grade"] = student.grade
            group["section"] = student.section

            gender = self._normalize_gender(student.gender)

            if gender == "male":
                group["enrollment_male"] += 1
            elif gender == "female":
                group["enrollment_female"] += 1
            group["enrollment_total"] += 1

            if summary.status == "present":
                if gender == "male":
                    group["present_male"] += 1
                elif gender == "female":
                    group["present_female"] += 1
                group["present_total"] += 1

            elif summary.status == "late":
                if gender == "male":
                    group["late_male"] += 1
                elif gender == "female":
                    group["late_female"] += 1
                group["late_total"] += 1

            elif summary.status == "absent":
                if gender == "male":
                    group["absent_male"] += 1
                elif gender == "female":
                    group["absent_female"] += 1
                group["absent_total"] += 1

            if summary.has_excuse:
                if gender == "male":
                    group["excuse_male"] += 1
                elif gender == "female":
                    group["excuse_female"] += 1
                group["excuse_total"] += 1

        return sorted(
            course_groups.values(),
            key=lambda item: (item["grade"], item["section"]),
        )

    def get_daily_institutional_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        present_students = []
        late_students = []
        absent_students = []
        students_with_excuse = []

        for summary, student in rows:
            item = self._build_student_item(summary, student)

            if summary.status == "present":
                present_students.append(item)
            elif summary.status == "late":
                late_students.append(item)
            elif summary.status == "absent":
                absent_students.append(item)

            if summary.has_excuse:
                students_with_excuse.append(item)

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "is_workday": center_day.is_workday,
            "had_attendance_activity": center_day.had_attendance_activity,
            "possible_no_school_day": center_day.possible_no_school_day,
            "possible_early_dismissal": center_day.possible_early_dismissal,
            "total_entries": center_day.total_entries,
            "total_exits": center_day.total_exits,
            "total_present": center_day.total_present,
            "total_late": center_day.total_late,
            "total_absent": center_day.total_absent,
            "total_with_excuse": center_day.total_with_excuse,
            "present_students": present_students,
            "late_students": late_students,
            "absent_students": absent_students,
            "students_with_excuse": students_with_excuse,
        }

    def get_daily_grouped_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        course_groups = defaultdict(
            lambda: {
                "grade": "",
                "section": "",
                "total_students": 0,
                "total_present": 0,
                "total_late": 0,
                "total_absent": 0,
                "total_with_excuse": 0,
            }
        )

        gender_groups = defaultdict(
            lambda: {
                "gender": "",
                "total_students": 0,
                "total_present": 0,
                "total_late": 0,
                "total_absent": 0,
                "total_with_excuse": 0,
            }
        )

        for summary, student in rows:
            course_key = (student.grade, student.section)
            course_groups[course_key]["grade"] = student.grade
            course_groups[course_key]["section"] = student.section
            course_groups[course_key]["total_students"] += 1

            if summary.status == "present":
                course_groups[course_key]["total_present"] += 1
            elif summary.status == "late":
                course_groups[course_key]["total_late"] += 1
            elif summary.status == "absent":
                course_groups[course_key]["total_absent"] += 1

            if summary.has_excuse:
                course_groups[course_key]["total_with_excuse"] += 1

            gender_value = (student.gender or "Sin especificar").strip() or "Sin especificar"
            gender_groups[gender_value]["gender"] = gender_value
            gender_groups[gender_value]["total_students"] += 1

            if summary.status == "present":
                gender_groups[gender_value]["total_present"] += 1
            elif summary.status == "late":
                gender_groups[gender_value]["total_late"] += 1
            elif summary.status == "absent":
                gender_groups[gender_value]["total_absent"] += 1

            if summary.has_excuse:
                gender_groups[gender_value]["total_with_excuse"] += 1

        by_course = sorted(
            course_groups.values(),
            key=lambda item: (item["grade"], item["section"]),
        )

        by_gender = sorted(
            gender_groups.values(),
            key=lambda item: item["gender"],
        )

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "total_entries": center_day.total_entries,
            "total_exits": center_day.total_exits,
            "total_present": center_day.total_present,
            "total_late": center_day.total_late,
            "total_absent": center_day.total_absent,
            "total_with_excuse": center_day.total_with_excuse,
            "by_course": by_course,
            "by_gender": by_gender,
        }

    def get_monthly_institutional_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        year: int,
        month: int,
    ) -> dict:
        rows = (
            self.db.query(CenterAttendanceDay)
            .filter(
                CenterAttendanceDay.center_id == center_id,
                CenterAttendanceDay.school_year_id == school_year_id,
                extract("year", CenterAttendanceDay.date) == year,
                extract("month", CenterAttendanceDay.date) == month,
            )
            .order_by(CenterAttendanceDay.date.asc())
            .all()
        )

        if not rows:
            raise ValueError(
                "No existen consolidados institucionales para el mes indicado."
            )

        by_day = [
            {
                "date": row.date,
                "is_workday": row.is_workday,
                "had_attendance_activity": row.had_attendance_activity,
                "possible_no_school_day": row.possible_no_school_day,
                "possible_early_dismissal": row.possible_early_dismissal,
                "total_entries": row.total_entries,
                "total_exits": row.total_exits,
                "total_present": row.total_present,
                "total_late": row.total_late,
                "total_absent": row.total_absent,
                "total_with_excuse": row.total_with_excuse,
            }
            for row in rows
        ]

        return {
            "center_id": center_id,
            "school_year_id": school_year_id,
            "year": year,
            "month": month,
            "total_days": len(rows),
            "total_workdays": sum(1 for row in rows if row.is_workday),
            "total_days_with_activity": sum(1 for row in rows if row.had_attendance_activity),
            "total_possible_no_school_days": sum(1 for row in rows if row.possible_no_school_day),
            "total_possible_early_dismissals": sum(1 for row in rows if row.possible_early_dismissal),
            "total_entries": sum(row.total_entries for row in rows),
            "total_exits": sum(row.total_exits for row in rows),
            "total_present": sum(row.total_present for row in rows),
            "total_late": sum(row.total_late for row in rows),
            "total_absent": sum(row.total_absent for row in rows),
            "total_with_excuse": sum(row.total_with_excuse for row in rows),
            "by_day": by_day,
        }

    def get_students_summary(
        self,
        *,
        center_id: int,
        school_year_id: int | None = None,
    ) -> dict:
        query = self.db.query(Student).filter(Student.center_id == center_id)

        if school_year_id is not None:
            query = query.filter(Student.school_year_id == school_year_id)

        students = query.all()

        by_gender: dict[str, int] = defaultdict(int)
        by_grade: dict[str, int] = defaultdict(int)

        for student in students:
            gender = (student.gender or "No especificado").strip() or "No especificado"
            grade = (student.grade or "No especificado").strip() or "No especificado"
            by_gender[gender] += 1
            by_grade[grade] += 1

        return {
            "total_students": len(students),
            "by_gender": dict(sorted(by_gender.items(), key=lambda item: item[0])),
            "by_grade": dict(sorted(by_grade.items(), key=lambda item: item[0])),
        }

    def get_printable_global_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "totals": self._build_printable_totals(rows),
            "by_course": self._build_printable_course_rows(rows),
        }

    def get_printable_course_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
        grade: str,
        section: str | None = None,
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        filtered_rows = [
            (summary, student)
            for summary, student in rows
            if student.grade == grade and (section is None or student.section == section)
        ]

        if not filtered_rows:
            raise ValueError("No hay datos para el curso seleccionado.")

        students = [self._build_student_item(summary, student) for summary, student in filtered_rows]

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "grade": grade,
            "section": section,
            "totals": self._build_printable_totals(filtered_rows),
            "students": students,
        }

    def get_printable_multi_course_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
        grades: list[str],
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        normalized_grades = [grade.strip() for grade in grades if grade and grade.strip()]
        if not normalized_grades:
            raise ValueError("Debes indicar al menos un curso.")

        filtered_rows = [
            (summary, student)
            for summary, student in rows
            if student.grade in normalized_grades
        ]

        if not filtered_rows:
            raise ValueError("No hay datos para los cursos seleccionados.")

        students = [self._build_student_item(summary, student) for summary, student in filtered_rows]

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "grades": normalized_grades,
            "totals": self._build_printable_totals(filtered_rows),
            "by_course": self._build_printable_course_rows(filtered_rows),
            "students": students,
        }

    def get_printable_excuses_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
        grade: str | None = None,
        section: str | None = None,
    ) -> dict:
        center_day = self._get_center_day(center_id, school_year_id, target_date)
        rows = self._get_summary_rows(center_id, school_year_id, target_date)

        filtered_rows = []
        for summary, student in rows:
            if not summary.has_excuse:
                continue
            if grade is not None and student.grade != grade:
                continue
            if section is not None and student.section != section:
                continue
            filtered_rows.append((summary, student))

        students = [self._build_student_item(summary, student) for summary, student in filtered_rows]

        return {
            "center_id": center_day.center_id,
            "school_year_id": center_day.school_year_id,
            "date": center_day.date,
            "grade": grade,
            "section": section,
            "total_students_with_excuse": len(students),
            "students": students,
        }