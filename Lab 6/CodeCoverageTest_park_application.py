"""Line/code coverage tests for amusement_park_ride_access.py."""
import pytest

from amusement_park_ride_access import (
    inspect_safety_restraints,
    process_ride_admissions,
)


def test_open_family_ride_adult_and_child_revenue():
    groups = [{
        "is_open": True,
        "ride_type": "family",
        "patrons": [
            {"height_cm": 150},
            {"height_cm": 130, "is_child": True},
        ],
    }]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 16.0, "status": "COMPLETED"
    }


def test_roller_coaster_revenue():
    groups = [{"is_open": True, "ride_type": "roller_coaster",
               "patrons": [{"height_cm": 180}]}]
    assert process_ride_admissions(groups, 5)["total_revenue"] == 25.0


def test_water_ride_revenue_with_fast_lane():
    groups = [{"is_open": True, "ride_type": "water_ride",
               "has_fast_lane": True, "patrons": [{"height_cm": 160}]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 23.0, "status": "COMPLETED"
    }


def test_invalid_arguments_raise_value_error():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5)
    with pytest.raises(ValueError):
        process_ride_admissions([], -1)


def test_closed_group_and_unknown_ride_are_skipped_or_rejected():
    groups = [
        {"is_open": False, "ride_type": "family",
         "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "unknown",
         "patrons": [{"height_cm": 150}]},
    ]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"
    }


def test_invalid_height_and_short_height_are_rejected():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [
        {"height_cm": 0}, {"height_cm": 110},
    ]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"
    }


def test_health_warning_on_non_coaster_does_not_charge_patron():
    groups = [{"is_open": True, "ride_type": "water_ride", "patrons": [
        {"height_cm": 150, "health_warning": True},
        {"height_cm": 150},
    ]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 18.0, "status": "COMPLETED"
    }


def test_health_warning_on_coaster_cancels_group_revenue():
    groups = [{"is_open": True, "ride_type": "roller_coaster", "patrons": [
        {"height_cm": 160}, {"height_cm": 160, "health_warning": True},
    ]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"
    }


def test_more_than_four_rejections_triggers_safety_audit():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [
        {"height_cm": 0}, {"height_cm": 0}, {"height_cm": 0},
        {"height_cm": 0}, {"height_cm": 0},
    ]}]
    assert process_ride_admissions(groups, 5)["status"] == "SAFETY_AUDIT"


def test_restraint_stream_empty_returns_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"
    assert inspect_safety_restraints(None) == "NO_DATA"


def test_restraints_safe_when_latched_or_only_one_zero():
    assert inspect_safety_restraints([[1, 1, 0, 1], [0, 1]]) == "SAFE"


def test_two_consecutive_unlatched_readings_trigger_emergency():
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"
