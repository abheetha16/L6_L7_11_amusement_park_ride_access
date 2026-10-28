"""Branch coverage tests for amusement_park_ride_access.py."""
import pytest

from amusement_park_ride_access import (
    inspect_safety_restraints,
    process_ride_admissions,
)


def test_input_validation_both_sides():
    with pytest.raises(ValueError):
        process_ride_admissions({}, 1)  # groups is not a list
    with pytest.raises(ValueError):
        process_ride_admissions([], -0.01)  # fee is negative
    assert process_ride_admissions([], 0) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"
    }


def test_group_open_and_closed_and_default_open_false():
    groups = [
        {"is_open": False, "ride_type": "family", "patrons": [{"height_cm": 150}]},
        {"ride_type": "family", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]},
    ]
    assert process_ride_admissions(groups, 5)["total_revenue"] == 10.0


def test_all_ride_type_branches_and_unknown_type():
    groups = [
        {"is_open": True, "ride_type": "roller_coaster", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "water_ride", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "unknown", "patrons": []},
        {"is_open": True, "patrons": [{"height_cm": 150}]},  # default family
    ]
    result = process_ride_admissions(groups, 0)
    assert result == {"total_revenue": 63.0, "status": "COMPLETED"}


def test_patron_height_and_health_warning_branches():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [
        {"height_cm": -1},                     # <= 0 true
        {"height_cm": 119},                    # height < 120 true
        {"height_cm": 150, "health_warning": True},  # warning true, non-coaster
        {"height_cm": 120, "is_child": True}, # exactly 120, child true
        {"height_cm": 150, "is_child": False},# child false
    ]}]
    result = process_ride_admissions(groups, 0)
    assert result == {"total_revenue": 16.0, "status": "COMPLETED"}


def test_coaster_health_warning_breaks_and_fast_lane_true():
    groups = [{"is_open": True, "ride_type": "roller_coaster",
               "has_fast_lane": True, "patrons": [
                   {"height_cm": 170},
                   {"height_cm": 170, "health_warning": True},
                   {"height_cm": 170},
               ]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 5.0, "status": "COMPLETED"
    }


def test_fast_lane_false_and_missing_patron_fields():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [{}]},
              {"is_open": True, "ride_type": "family", "has_fast_lane": False,
               "patrons": [{"height_cm": 150}]}]
    assert process_ride_admissions(groups, 5) == {
        "total_revenue": 10.0, "status": "COMPLETED"
    }


def test_safety_audit_threshold_and_zero_admissions_and_completed():
    four_rejections = [{"is_open": True, "ride_type": "family",
                        "patrons": [{"height_cm": 0}] * 4}]
    assert process_ride_admissions(four_rejections, 0)["status"] == "ZERO_ADMISSIONS"
    five_rejections = [{"is_open": True, "ride_type": "family",
                        "patrons": [{"height_cm": 0}] * 5}]
    assert process_ride_admissions(five_rejections, 0)["status"] == "SAFETY_AUDIT"
    assert process_ride_admissions(
        [{"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]}], 0
    )["status"] == "COMPLETED"


def test_restraint_stream_branches():
    assert inspect_safety_restraints([]) == "NO_DATA"
    assert inspect_safety_restraints([[0]]) == "SAFE"
    assert inspect_safety_restraints([[0, 1, 0]]) == "SAFE"  # reset streak
    assert inspect_safety_restraints([[], [1, 1]]) == "SAFE"
    assert inspect_safety_restraints([[0, 0], [1]]) == "EMERGENCY_LOCK"
