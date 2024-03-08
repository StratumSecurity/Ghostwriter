from enums import Grade


def _get_grade(score):
    if score >= Grade.A.value:
        grade = "A"
    elif score < Grade.A.value and score >= Grade.B.value:
        grade = "B"
    elif score < Grade.B.value and score >= Grade.C.value:
        grade = "C"
    elif score < Grade.C.value and score >= Grade.D.value:
        grade = "D"
    else:
        grade = "F"
    return grade


def calculate_grade(critical, high, medium, low):
    # This one is more accurate than the Defect Dojo because 1 critical and 1 high is being deducted
    # whereas DefectDojo, the high is excluded for some reason. Bug in their algorithm?
    # https://defectdojo.github.io/django-DefectDojo/usage/productgrading/
    health = 100

    # Adjust initial health score based on severity of findings
    health -= critical * 15
    health -= high * 5
    health -= medium * 3
    health -= low

    # Set minimum health score
    # Returns the grade letter to put in the report
    # template will color code the background based on the value
    return _get_grade(max(health, 5))
