from datetime import date, datetime

from pydantic import BaseModel


class DailyInstitutionalReportQuery(BaseModel):
    center_id: int
    school_year_id: int
    date: date


class StudentDailyStatusItem(BaseModel):
    student_id: int
    student_code: str
    minerd_id: str | None = None
    full_name: str
    gender: str | None = None
    grade: str
    section: str
    status: str
    has_excuse: bool
    excuse_note: str | None = None
    first_entry_time: datetime | None = None
    minutes_late: int | None = None


class DailyInstitutionalReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    is_workday: bool
    had_attendance_activity: bool
    possible_no_school_day: bool
    possible_early_dismissal: bool
    total_entries: int
    total_exits: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int
    present_students: list[StudentDailyStatusItem]
    late_students: list[StudentDailyStatusItem]
    absent_students: list[StudentDailyStatusItem]
    students_with_excuse: list[StudentDailyStatusItem]


class DailyCourseGroupItem(BaseModel):
    grade: str
    section: str
    total_students: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int


class DailyGenderGroupItem(BaseModel):
    gender: str
    total_students: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int


class DailyGroupedReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    total_entries: int
    total_exits: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int
    by_course: list[DailyCourseGroupItem]
    by_gender: list[DailyGenderGroupItem]


class MonthlyDayItem(BaseModel):
    date: date
    is_workday: bool
    had_attendance_activity: bool
    possible_no_school_day: bool
    possible_early_dismissal: bool
    total_entries: int
    total_exits: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int


class MonthlyInstitutionalReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    year: int
    month: int
    total_days: int
    total_workdays: int
    total_days_with_activity: int
    total_possible_no_school_days: int
    total_possible_early_dismissals: int
    total_entries: int
    total_exits: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int
    by_day: list[MonthlyDayItem]


class StudentsSummaryResponse(BaseModel):
    total_students: int
    by_gender: dict[str, int]
    by_grade: dict[str, int]


class PrintableTotalsByGender(BaseModel):
    male: int
    female: int
    total: int


class PrintableStatusBreakdown(BaseModel):
    present: PrintableTotalsByGender
    late: PrintableTotalsByGender
    absent: PrintableTotalsByGender
    excuse: PrintableTotalsByGender
    general: PrintableTotalsByGender
    enrollment: PrintableTotalsByGender


class PrintableCourseRow(BaseModel):
    grade: str
    section: str
    enrollment_male: int
    enrollment_female: int
    enrollment_total: int
    present_male: int
    present_female: int
    present_total: int
    late_male: int
    late_female: int
    late_total: int
    absent_male: int
    absent_female: int
    absent_total: int
    excuse_male: int
    excuse_female: int
    excuse_total: int


class PrintableGlobalReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    totals: PrintableStatusBreakdown
    by_course: list[PrintableCourseRow]


class PrintableCourseReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    grade: str
    section: str | None = None
    totals: PrintableStatusBreakdown
    students: list[StudentDailyStatusItem]


class PrintableMultiCourseReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    grades: list[str]
    totals: PrintableStatusBreakdown
    by_course: list[PrintableCourseRow]
    students: list[StudentDailyStatusItem]


class PrintableExcusesReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    grade: str | None = None
    section: str | None = None
    total_students_with_excuse: int
    students: list[StudentDailyStatusItem]