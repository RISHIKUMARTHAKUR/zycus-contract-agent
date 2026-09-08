"""The blank NDA template, as a structured list of (heading, body) sections.
Kept as data (not a raw .docx) so the drafting agent can reason about /
transform individual sections before final document generation.
"""

NDA_TEMPLATE_SECTIONS = [
    {
        "id": "preamble",
        "heading": None,
        "body": (
            'This Mutual Non-Disclosure Agreement ("Agreement") is entered '
            "into as of {effective_date}, by and between {disclosing_party}, "
            'and {receiving_party} (each a "Party" and collectively the '
            '"Parties").'
        ),
    },
    {
        "id": "purpose",
        "heading": "1. Purpose.",
        "body": (
            "The Parties wish to explore {purpose_of_disclosure} (the "
            '"Purpose"), and in connection with the Purpose, each Party may '
            "disclose certain confidential information to the other."
        ),
    },
    {
        "id": "definition",
        "heading": "2. Confidential Information.",
        "body": (
            '"Confidential Information" means any non-public information '
            "disclosed by one Party to the other, whether orally or in "
            "writing, that is designated as confidential or that reasonably "
            "should be understood to be confidential given the nature of "
            "the information."
        ),
    },
    {
        "id": "term",
        "heading": "3. Term.",
        "body": (
            "This Agreement shall remain in effect for {term} from the "
            "Effective Date. The obligations of confidentiality shall "
            "survive termination for a period of {survival_period}."
        ),
    },
    {
        "id": "restrictions",
        "heading": "4. Restrictions on Use and Disclosure.",
        # {special_clause} is deliberately left as its own placeholder so the
        # validator/drafter can decide HOW (or whether) to insert it, rather
        # than the template silently granting whatever was requested.
        "body": (
            "The Receiving Party shall not disclose Confidential "
            "Information to any third party without the prior written "
            "consent of the Disclosing Party, except as expressly permitted "
            "under Section 5. {special_clause}"
        ),
    },
    {
        "id": "permitted_disclosures",
        "heading": "5. Permitted Disclosures.",
        "body": (
            "Confidential Information may be disclosed to the Receiving "
            "Party's employees, officers, and professional advisors who "
            "need to know such information for the Purpose, provided they "
            "are bound by confidentiality obligations no less protective "
            "than this Agreement."
        ),
    },
    {
        "id": "governing_law",
        "heading": "6. Governing Law.",
        "body": (
            "This Agreement shall be governed by the laws of "
            "{governing_law}, without regard to its conflict of law "
            "principles."
        ),
    },
    {
        "id": "signatures",
        "heading": "7. Signatures.",
        "body": (
            "IN WITNESS WHEREOF, the Parties have executed this Agreement "
            "as of the Effective Date."
        ),
    },
]
