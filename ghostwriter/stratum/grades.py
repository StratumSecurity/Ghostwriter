from datetime import timedelta
from itertools import groupby

from config.settings.base import CLOUD_GRADE_WEIGHT
from ghostwriter.reporting.models import FindingType, ReportFindingLink
from .enums import Grade, Service, Severity

_DEFAULT_WEIGHT = 1


def _get_grade(score):
    if score >= Grade.A.value:
        grade = Grade.A.name
    elif score < Grade.A.value and score >= Grade.B.value:
        grade = Grade.B.name
    elif score < Grade.B.value and score >= Grade.C.value:
        grade = Grade.C.name
    elif score < Grade.C.value and score >= Grade.D.value:
        grade = Grade.D.name
    else:
        grade = Grade.F.name
    return grade


def _group_findings_by_severity(findings, field):
    findings.sort(key=lambda f: f[field])
    # Group the data based on the key
    return {
        key.lower(): len(list(group))
        for key, group in groupby(findings, key=lambda f: f[field])
    }


def _calculate_numeric_grade(critical, high, medium, low, weight):
    # This one is more accurate than the Defect Dojo because 1 critical and 1 high is being deducted
    # whereas DefectDojo, the high is excluded for some reason. Bug in their algorithm?
    # https://defectdojo.github.io/django-DefectDojo/usage/productgrading/
    health = 100

    # Weight shouldn't be negative or 0, or exceed 1 as it will cause incorrect grades
    if weight <= 0 or weight > _DEFAULT_WEIGHT:
        weight = _DEFAULT_WEIGHT

    # Adjust initial health score based on severity of findings
    health -= critical * 15 * weight
    health -= high * 5 * weight
    health -= medium * 3 * weight
    health -= low * weight

    # Set minimum health score
    # Returns the grade letter to put in the report
    # template will color code the background based on the value
    return max(health, 5)


def _calculate_grade(findings, func, weight, field="severity"):
    # Group the data based on the key
    grouped_data = _group_findings_by_severity(findings, field)
    return func(
        grouped_data.get(Severity.CRIT.value.lower(), 0),
        grouped_data.get(Severity.HIGH.value.lower(), 0),
        grouped_data.get(Severity.MED.value.lower(), 0),
        grouped_data.get(Severity.LOW.value.lower(), 0),
        weight,
    )


def get_services(findings):
    # This is needed to loop through each finding type for the grade calculation
    # For appsec we group the finding types together
    # e.g. [{"service":"appsec","finding_types":["Web","Mobile","..."],"weight":1},
    # {"service":"azure","finding_types":["Azure"],"weight":0.25}]
    unique_types = set(finding["finding_type"].lower() for finding in findings)
    # Add appsec category with hardcoded values
    appsec_type = "appsec"
    appsec_categories = [
        Service.WEB.value.lower(),
        Service.MOBILE.value.lower(),
        Service.CODE_REVIEW.value.lower(),
    ]
    appsec_categories_capitalized = [
        category.capitalize() for category in appsec_categories
    ]
    services = []

    if len(unique_types) == 0:
        # Report with no findings
        # In this case we get all the finding types to calculate the grades for each service
        # More expensive since we calculate average grades for each service but doesn't require
        # any user interaction to define the assessment being done
        types = FindingType.objects.all().values_list("finding_type", flat=True)
        unique_types = set(finding_type.lower() for finding_type in types)

    if any(type_key in appsec_categories for type_key in unique_types):
        services.append(
            {
                "name": appsec_type,
                "finding_types": appsec_categories_capitalized,
                "weight": _DEFAULT_WEIGHT,
            }
        )

    # Cloud finding types to set the weight based on the env variables
    # The rest of the services default to weight of 1
    # Cloud had many findings where the grade was always an F,
    # setting a different weight adjusts the grade score
    cloud_categories = [
        Service.AWS.value.lower(),
        Service.AZURE.value.lower(),
        Service.GCP.value.lower(),
        Service.M365.value.lower(),
    ]

    # Add other types with their own categories
    for type_key in unique_types:
        type_key_capitalized = type_key.capitalize()  # Preserve original casing
        if type_key not in appsec_categories:
            service = {
                "name": type_key_capitalized.lower(),
                "finding_types": [type_key_capitalized],
            }

            if type_key in cloud_categories:
                service["weight"] = CLOUD_GRADE_WEIGHT
            else:
                service["weight"] = _DEFAULT_WEIGHT
            services.append(service)
    return services


def calculate_grade_by_findings(findings, weight):
    # Returns the grade letter
    return _calculate_grade(findings, calculate_grade, weight)


def calculate_average_grade(finding_types, project_start_date, weight):
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
                r[1], _calculate_numeric_grade, weight, "severity__severity"
            ),
            reports.items(),
        )
    )
    average = sum(grades) / len(grades)
    return _get_grade(average)


def calculate_grade(critical, high, medium, low, weight):
    # Returns the grade letter after calculating the numeric grade
    return _get_grade(_calculate_numeric_grade(critical, high, medium, low, weight))
