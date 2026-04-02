from collections import defaultdict
from datetime import date

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
            item = {
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