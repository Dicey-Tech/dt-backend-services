""" Constants """

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%d%m%y"
COURSE_RUN_FORMAT = "%Y%m%d%H%M%S%f"

SCHOOL_TERM = {
    1: "SPRING",
    2: "SUMMER",
    3: "AUTUMN",
}

# Role-based access control
CLASSROOM_TEACHER_ROLE = "school_classroom_teacher"
CLASSROOM_LEARNER_ROLE = "school_classroom_learner"

SYSTEM_ENTERPRISE_ADMIN_ROLE = "enterprise_admin"
SYSTEM_ENTERPRISE_LEARNER_ROLE = "enterprise_learner"
SYSTEM_ENTERPRISE_OPERATOR_ROLE = "enterprise_openedx_operator"

CLASSROOM_TEACHER_ACCESS_PERMISSION = "classroom.has_teacher_acces"
