"""Constants for the Islamic Prayer component."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "islamic_prayer_times"
NAME: Final = "Islamic Prayer Times"

CONF_HIJRI_DATE: Final = "hijri_date"
CONF_CALC_METHOD: Final = "calculation_method"

CALC_METHODS: Final = [
    "jafari",
    "karachi",
    "isna",
    "mwl",
    "makkah",
    "egypt",
    "tehran",
    "gulf",
    "kuwait",
    "qatar",
    "singapore",
    "france",
    "turkey",
    "russia",
    "moonsighting",
    "custom",
]
DEFAULT_CALC_METHOD: Final = "isna"

CONF_LAT_ADJ_METHOD: Final = "latitude_adjustment_method"
LAT_ADJ_METHODS: Final = ["middle_of_the_night", "one_seventh", "angle_based"]
DEFAULT_LAT_ADJ_METHOD: Final = "middle_of_the_night"

CONF_MIDNIGHT_MODE: Final = "midnight_mode"
MIDNIGHT_MODES: Final = ["standard", "jafari"]
DEFAULT_MIDNIGHT_MODE: Final = "standard"

CONF_SCHOOL: Final = "school"
SCHOOLS: Final = ["shafi", "hanafi"]
DEFAULT_SCHOOL: Final = "shafi"

CONF_TUNE: Final = "tune"
IMSAK_TUNE: Final = "imsak_tune"
FAJR_TUNE: Final = "fajr_tune"
SUNRISE_TUNE: Final = "sunrise_tune"
DHUHR_TUNE: Final = "dhuhr_tune"
ASR_TUNE: Final = "asr_tune"
MAGHRIB_TUNE: Final = "maghrib_tune"
SUNSET_TUNE: Final = "sunset_tune"
ISHA_TUNE: Final = "isha_tune"
MIDNIGHT_TUNE: Final = "midnight_tune"
TIMES_TUNE: Final = [
    IMSAK_TUNE,
    FAJR_TUNE,
    SUNRISE_TUNE,
    DHUHR_TUNE,
    ASR_TUNE,
    MAGHRIB_TUNE,
    SUNSET_TUNE,
    ISHA_TUNE,
    MIDNIGHT_TUNE,
]
