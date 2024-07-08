# Standard Libraries
from enum import Enum

from bs4 import BeautifulSoup


class Severity(Enum):
    CRIT = "Critical"
    HIGH = "High"
    MED = "Medium"
    LOW = "Low"
    INFO = "Info"


class FindingStatusColor(Enum):
    OPEN = ("OPEN", "#F0582B")
    CLOSED = ("CLOSED", "#8BC53F")
    ACCEPTED = ("ACCEPTED", "#4E81BD")


class Service(Enum):
    APPSEC = "appsec"
    CLOUD = "cloud"
    EXTERNAL = "external"
    INTERNAL = "internal"
    PHYSICAL = "physical"
    WIRELESS = "wireless"

    @classmethod
    def get_finding_type(cls, service):
        try:
            if cls.APPSEC.value == service:
                return ["Web", "Mobile", "Code Review"]
            else:
                # upper() is needed for the key to be found
                return [cls[service.upper()].value.title()]
        except KeyError:
            return None


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


def get_value_from_key(e, key):
    # Strip HTML tags from UI data that get added by TinyMCE
    soup = BeautifulSoup(key, "html.parser")
    key = soup.get_text()
    for item in e:
        if item.value[0].lower() == key.lower():
            return item.value[1]
    raise ValueError(f"{key} is not a valid {e.__name__} key")
