# Standard Libraries
from enum import Enum


class Severity(Enum):
    CRIT = 'Critical'
    HIGH = 'High'
    MED = 'Medium'
    LOW = 'Low'
    BP = 'Best Practice'


class DifficultyExploitColor(Enum):
    LOW = (Severity.LOW, '#16A43E')
    MED = (Severity.MED, '#ED9146')
    HIGH = (Severity.HIGH, '#FF0000')


class FindingStatusColor(Enum):
    OPEN = ('OPEN', '#FF0000')
    CLOSED = ('CLOSED', '#16A43E')
    ACCEPTED = ('ACCEPTED', '#0C5AB2')


def get_value_from_key(enum, key):
    for item in enum:
        if item.value[0] == key:
            return item
        raise ValueError(f"{key} is not a valid {enum.__name__} key")
