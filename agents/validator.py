"""
Input Validator Agent.

Design decision (this is the one to put on your slide):
    Confidence here is NOT a single blended number. Each flag gets:
      - a `resolution`: "auto_resolve" | "auto_flag_only" | "needs_human_review"
      - a `confidence`: 0-1, how sure the agent is about its OWN read of the situation
      - a `category`: "formatting" | "scope_of_rights" | "risk_clause"

    Rule: confidence alone never authorizes auto-inserting language that
    changes a party's *rights or exposure* (category == "scope_of_rights" or
    "risk_clause"). Those always route to needs_human_review, no matter how
    confident the model is that it understood the request correctly. High
    confidence about what was ASKED is not the same as high confidence that
    it's SAFE to grant automatically -- those are two different questions,
    and collapsing them is exactly the kind of silent-approval failure this
    assignment is testing for.

    Only pure data-completion issues (missing date, N/A field) are eligible
    for auto_resolve, because getting those wrong is cheap to notice and
    cheap to fix, and doesn't change what either party is agreeing to.
"""

from dataclasses import dataclass, field
from typing import Literal

Resolution = Literal["auto_resolve", "auto_flag_only", "needs_human_review"]
Category = Literal["formatting", "scope_of_rights", "risk_clause"]


@dataclass
class Flag:
    field: str
    issue: str
    resolution: Resolution
    confidence: float
    category: Category
    detail: str = ""


def validate_inputs(inputs: dict) -> list[Flag]:
    flags: list[Flag] = []

    # --- Check 1: payment_terms doesn't apply to an NDA ---------------
    if inputs.get("payment_terms") is None:
        flags.append(
            Flag(
                field="payment_terms",
                issue="Field not applicable to this contract type",
                resolution="auto_resolve",
                confidence=0.99,
                category="formatting",
                detail=(
                    "This is an NDA, not a commercial agreement -- payment "
                    "terms have no corresponding clause in the template. "
                    "Excluded from output rather than forced into a section."
                ),
            )
        )

    # --- Check 2: effective_date left open -----------------------------
    if inputs.get("effective_date") is None:
        flags.append(
            Flag(
                field="effective_date",
                issue="No explicit date provided ('use today's date')",
                resolution="auto_resolve",
                confidence=0.95,
                category="formatting",
                detail="Resolved to the current date at generation time.",
            )
        )

    # --- Check 3: requested affiliate carve-out is broader than standard
    special_clause = inputs.get("special_clause_requested", "")
    if special_clause and "affiliate" in special_clause.lower():
        flags.append(
            Flag(
                field="special_clause_requested",
                issue=(
                    "Requested carve-out allows disclosure to affiliates "
                    "WITHOUT prior written consent -- broader than the "
                    "standard mutual NDA clause, which requires consent for "
                    "any third-party disclosure."
                ),
                resolution="needs_human_review",
                confidence=0.85,  # confident about WHAT was asked
                category="scope_of_rights",  # but this changes disclosure
                # rights, so confidence does not authorize auto-insert
                detail=(
                    "Not inserted as unrestricted language. A bounded "
                    "alternative (affiliates bound by equivalent "
                    "confidentiality obligations, no prior consent required) "
                    "is drafted for human sign-off instead of silently "
                    "granting the broader ask or silently rejecting it."
                ),
            )
        )

    return flags


def summarize(flags: list[Flag]) -> str:
    lines = []
    for f in flags:
        lines.append(
            f"[{f.resolution.upper()}] ({f.category}, conf={f.confidence:.2f}) "
            f"{f.field}: {f.issue}"
        )
    return "\n".join(lines) if lines else "No flags raised."
