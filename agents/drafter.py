"""
Drafting Agent.

Deliberate design split:
    - Filling known, unambiguous fields into the template is DETERMINISTIC
      (plain string formatting). There's no reason to spend an LLM call on
      substituting a party name into a sentence, and doing it deterministically
      means that part of the pipeline can never hallucinate.
    - Only the ONE piece that requires actual judgment -- drafting bounded
      replacement language for the non-standard affiliate carve-out -- goes
      through the LLM. That's the multi-tool boundary: template-fill tool
      (deterministic) + LLM drafting step (judgment), not one giant prompt
      doing both.
"""

from templates.nda_template import NDA_TEMPLATE_SECTIONS
from agents.llm_client import call_llm, LLMUnavailable

SPECIAL_CLAUSE_SYSTEM_PROMPT = """You are a contract drafting assistant helping \
draft NDA clause language. You are careful and conservative: you never grant \
broader rights than what is standard market practice, even if asked to, and \
you always explain the trade-off in plain English.

Task: The Receiving Party has requested a carve-out allowing disclosure of \
confidential information to their affiliates WITHOUT prior written consent \
from the Disclosing Party. This is broader than standard NDA practice.

Draft a BOUNDED alternative: allow disclosure to affiliates without requiring \
prior written consent each time, but only if those affiliates are contractually \
bound by confidentiality obligations at least as protective as this Agreement, \
and the Receiving Party remains liable for any breach by an affiliate.

Output EXACTLY two parts, separated by a line containing only "---":
1. The clause language itself (one or two sentences, ready to insert into the \
contract, written in formal contract style, starting with "provided that" or \
similar so it reads naturally as a continuation of Section 4).
2. A one-sentence plain-English explanation of the trade-off for a \
non-lawyer reviewer, aimed at someone who needs to approve this quickly.

Do not include any other commentary, headers, or markdown formatting."""


def draft_special_clause() -> tuple[str, str]:
    """Returns (clause_text, plain_english_explanation). Raises LLMUnavailable
    if the API can't be reached -- caller decides how to degrade."""
    raw = call_llm(
        system=SPECIAL_CLAUSE_SYSTEM_PROMPT,
        user="Draft the bounded affiliate carve-out clause now.",
        max_tokens=300,
    )
    if "---" in raw:
        clause, explanation = raw.split("---", 1)
    else:
        clause, explanation = raw, ""
    return clause.strip(), explanation.strip()


def build_draft(inputs: dict, special_clause_text: str | None) -> list[dict]:
    """Deterministically fills the template. `special_clause_text` is either
    the LLM-drafted bounded clause, or None if it should be omitted pending
    human review."""
    filled = []
    fmt_inputs = dict(inputs)
    fmt_inputs["special_clause"] = special_clause_text or (
        "[AFFILIATE CARVE-OUT PENDING REVIEW -- see flag below; not inserted "
        "automatically.]"
    )

    for section in NDA_TEMPLATE_SECTIONS:
        body = section["body"].format(**fmt_inputs)
        filled.append({
            "id": section["id"],
            "heading": section["heading"],
            "body": body,
        })
    return filled
