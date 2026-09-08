"""
Business inputs for the NDA (from Zycus_TrackA_Sample_ContractAuthoring).
In the real product this would come from a form / API call; for the
assignment it's hardcoded to match the given sample pack.
"""

from datetime import date

BUSINESS_INPUTS = {
    "contract_type": "Mutual Non-Disclosure Agreement (NDA)",
    "disclosing_party": "Zycus Inc.",
    "receiving_party": "Northwind Vendor Solutions Pvt. Ltd.",
    "effective_date": None,  # "use today's date" -> None signals "resolve at runtime"
    "term": "2 years",  # template already appends "from the Effective Date"
    "governing_law": "State of Delaware, USA",
    "survival_period": "3 years",  # template already says "survive termination for a period of..."
    "purpose_of_disclosure": (
        "evaluating a potential vendor relationship for procurement "
        "software integration"
    ),
    "special_clause_requested": (
        "Receiving party wants a carve-out allowing disclosure to their "
        "affiliates without prior written consent"
    ),
    "payment_terms": None,  # explicitly "not applicable" for an NDA
}


def resolve_runtime_defaults(inputs: dict) -> dict:
    """Fill in values that are meant to be resolved 'as of now', e.g. effective_date."""
    resolved = dict(inputs)
    if resolved.get("effective_date") is None:
        resolved["effective_date"] = date.today().strftime("%B %d, %Y")
    return resolved
