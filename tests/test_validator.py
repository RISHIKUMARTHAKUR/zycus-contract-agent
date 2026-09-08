"""Run with: python3 -m pytest tests/ -v  (or plain: python3 tests/test_validator.py)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.validator import validate_inputs


def test_catches_all_three_planted_issues():
    inputs = {
        "payment_terms": None,
        "effective_date": None,
        "special_clause_requested": "allow disclosure to affiliates without prior consent",
    }
    flags = validate_inputs(inputs)
    fields_flagged = {f.field for f in flags}
    assert fields_flagged == {"payment_terms", "effective_date", "special_clause_requested"}


def test_scope_of_rights_always_routes_to_human_review():
    # payment_terms/effective_date explicitly set (not None) so only the
    # special clause flag fires -- .get() on a missing key would also
    # return None and trigger the other two rules, which isn't what this
    # test is isolating.
    inputs = {
        "payment_terms": "Net 30",
        "effective_date": "January 1, 2027",
        "special_clause_requested": "affiliate carve-out requested",
    }
    flags = validate_inputs(inputs)
    assert len(flags) == 1
    assert flags[0].category == "scope_of_rights"
    assert flags[0].resolution == "needs_human_review"


def test_formatting_issues_auto_resolve():
    inputs = {"payment_terms": None, "effective_date": None}
    flags = validate_inputs(inputs)
    assert all(f.resolution == "auto_resolve" for f in flags)
    assert all(f.category == "formatting" for f in flags)


def test_no_flags_when_inputs_are_clean():
    inputs = {
        "payment_terms": "Net 30",
        "effective_date": "January 1, 2027",
        "special_clause_requested": "",
    }
    flags = validate_inputs(inputs)
    assert flags == []


if __name__ == "__main__":
    test_catches_all_three_planted_issues()
    test_scope_of_rights_always_routes_to_human_review()
    test_formatting_issues_auto_resolve()
    test_no_flags_when_inputs_are_clean()
    print("All tests passed.")
