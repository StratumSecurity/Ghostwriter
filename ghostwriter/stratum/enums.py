# Standard Libraries
from enum import Enum

from bs4 import BeautifulSoup


class Severity(Enum):
    CRIT = "Critical"
    HIGH = "High"
    MED = "Medium"
    LOW = "Low"
    INFO = "Info"


class Service(Enum):
    EXTERNAL = "External"
    INTERNAL = "Internal"
    WEB = "Web"
    MOBILE = "Mobile"
    CODE_REVIEW = "Code Review"
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    M365 = "M365"


class FindingStatusColor(Enum):
    OPEN = ("OPEN", "F0582B")
    CLOSED = ("CLOSED", "8BC53F")
    ACCEPTED = ("ACCEPTED", "4E81BD")


class Grade(Enum):
    A = 90
    B = 80
    C = 70
    D = 60
    F = 0

    @classmethod
    def get_value(cls, grade_str):
        try:
            return cls[grade_str].value
        except KeyError:
            return None


class GradeColor(Enum):
    A = "00B050"
    B = "70AD47"
    C = "FFC000"
    D = "ED7D31"
    F = "C00000"


def strip_html(value):
    # This is needed for the finding status since it's a text field
    # Strip HTML tags from UI data that get added by TinyMCE
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text()


def get_value_from_key(e, key):
    # Strip HTML tags from UI data that get added by TinyMCE
    key = strip_html(key)
    for item in e:
        if item.value[0].lower() == key.lower():
            return item.value[1]
    raise ValueError(f"{key} is not a valid {e.__name__} key")
