from datetime import timedelta
from itertools import groupby

from ghostwriter.reporting.models import ReportFindingLink
from .enums import Grade, Severity


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


def _group_findings_by_severity(findings, field):
    findings.sort(key=lambda f: f[field])
    # Group the data based on the key
    return {
        key.lower(): len(list(group))
        for key, group in groupby(findings, key=lambda f: f[field])
    }


def _calculate_numeric_grade(critical, high, medium, low):
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
    return max(health, 5)


def _calculate_grade(findings, func, field="severity"):
    # Group the data based on the key
    grouped_data = _group_findings_by_severity(findings, field)
    return func(
        grouped_data.get(Severity.CRIT.value.lower(), 0),
        grouped_data.get(Severity.HIGH.value.lower(), 0),
        grouped_data.get(Severity.MED.value.lower(), 0),
        grouped_data.get(Severity.LOW.value.lower(), 0),
    )


def get_services(findings):
    # This is needed to loop through each finding type for the grade calculation
    # For appsec we group the finding types together
    # e.g. [{'appsec': ['Web', 'Mobile', 'Code Review']}, {'azure': ['Azure']}, ...]
    unique_types = set(finding["finding_type"].lower() for finding in findings)

    # Add appsec category with hardcoded values
    appsec_type = "appsec"
    appsec_categories = ["Web".lower(), "Mobile".lower(), "Code Review".lower()]
    appsec_categories_capitalized = [
        category.capitalize() for category in appsec_categories
    ]
    finding_types = []
    if any(type_key in appsec_categories for type_key in unique_types):
        finding_types.append({appsec_type: appsec_categories_capitalized})

    # Add other types with their own categories
    for type_key in unique_types:
        type_key_capitalized = type_key.capitalize()  # Preserve original casing
        if type_key not in appsec_categories:
            # Avoid duplicates
            if not any(d.get(type_key_capitalized) for d in finding_types):
                finding_types.append(
                    {type_key_capitalized.lower(): [type_key_capitalized]}
                )
    return finding_types


def calculate_grade_by_findings(findings):
    # Returns the grade letter
    return _calculate_grade(findings, calculate_grade)


def calculate_average_grade(finding_types, project_start_date):
    one_year_ago = project_start_date - timedelta(days=365)

    findings = (
        ReportFindingLink.objects.filter(report__delivered__exact=True)
        .filter(
            report__project__start_date__gte=one_year_ago.date(),
            report__project__start_date__lt=project_start_date.date(),
        )
        .filter(finding_type__finding_type__in=finding_types)
        .values("severity__severity", "report__id")
        .order_by("report__id", "severity__weight")
    )

    # If no reports, we have no data as it's new service then return "A"
    if not findings:
        return _get_grade(Grade.A.value)

    # Group the found findings by report and calculate the score for each report
    reports = {
        key: list(group)
        for key, group in groupby(findings, key=lambda f: f["report__id"])
    }

    # Calculate the numeric grades for each report to calculate the "Stratum Customer Average" grade
    grades = list(
        map(
            # Had to pass "severity__severity" as severity was used for foreign key field
            lambda r: _calculate_grade(
                r[1], _calculate_numeric_grade, "severity__severity"
            ),
            reports.items(),
        )
    )
    average = sum(grades) / len(grades)
    return _get_grade(average)


def calculate_grade(critical, high, medium, low):
    # Returns the grade letter after calculating the numeric grade
    return _get_grade(_calculate_numeric_grade(critical, high, medium, low))