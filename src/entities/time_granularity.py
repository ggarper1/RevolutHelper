from enum import Enum


class Time_Granularity(str, Enum):
    DAY = "D"
    WEEK = "W"
    MONTH = "ME"
    YEAR = "YE"
