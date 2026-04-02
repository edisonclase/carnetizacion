from datetime import date

from sqlalchemy.orm import Session

from app.models.attendance_daily_summary import AttendanceDailySummary
from app.models.center_attendance_day import CenterAttendanceDay
from app.models.student import Student


class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_institutional_report(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
    ) -> dict:
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

        rows = (
            self.db.query(AttendanceDailySummary, Student)
            .join(Student, Student.id == AttendanceDailySummary.student_id)
            .filter(
                Student.center_id == center_id,
                Student.school_year_id == school_year_id,
                AttendanceDailySummary.date == target_date,
            )
            .order_by(Student.grade.asc(), Student.section.asc(), Student.last_name.asc(), Student.first_name.asc())
            .all()
        )

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