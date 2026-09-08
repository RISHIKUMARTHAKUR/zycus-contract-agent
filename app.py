import os
import streamlit as st
from dotenv import load_dotenv

from pipeline import run_pipeline
from inputs import BUSINESS_INPUTS

load_dotenv()

st.set_page_config(page_title="Contract Authoring Agent", page_icon="📄", layout="centered")

# ---- minimal, clean styling ------------------------------------------------
st.markdown(
    """
    <style>
    .block-container { max-width: 780px; padding-top: 2.5rem; }
    .flag-card {
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    .flag-auto { background: #F0FAF3; border-color: #2E9E5B; }
    .flag-review { background: #FFF8E8; border-color: #C98A00; }
    .flag-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        opacity: 0.75;
    }
    .flag-title { font-weight: 600; margin-top: 2px; }
    .flag-detail { font-size: 0.9rem; opacity: 0.85; margin-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Contract Authoring Agent")
st.caption("Track A — fills a Mutual NDA from business inputs, flags anything "
           "missing, ambiguous, or non-standard before it reaches a human.")

with st.expander("Business inputs", expanded=True):
    inputs = dict(BUSINESS_INPUTS)
    c1, c2 = st.columns(2)
    with c1:
        inputs["disclosing_party"] = st.text_input("Disclosing party", inputs["disclosing_party"])
        inputs["term"] = st.text_input("Term", inputs["term"])
        inputs["governing_law"] = st.text_input("Governing law", inputs["governing_law"])
    with c2:
        inputs["receiving_party"] = st.text_input("Receiving party", inputs["receiving_party"])
        inputs["survival_period"] = st.text_input("Survival period", inputs["survival_period"])
    inputs["purpose_of_disclosure"] = st.text_area(
        "Purpose of disclosure", inputs["purpose_of_disclosure"], height=70
    )
    inputs["special_clause_requested"] = st.text_area(
        "Special clause requested", inputs["special_clause_requested"], height=70
    )
    st.caption("Effective date and payment terms are intentionally left as-is "
               "for this sample — the agent decides how to handle them.")

generate = st.button("Generate draft", type="primary", use_container_width=True)

if generate:
    with st.spinner("Validating inputs, drafting clauses, generating document..."):
        try:
            result = run_pipeline(inputs, output_path="output/nda_draft.docx")
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()

    if result.llm_degraded:
        st.warning(
            "⚠️ LLM drafting step unavailable (no API key configured). The "
            "flagged clause was left explicitly pending rather than guessed "
            "at — see 'Items Flagged for Human Review' in the document.",
            icon="⚠️",
        )

    st.subheader("Agent findings")
    for f in result.flags:
        css_class = "flag-auto" if f.resolution == "auto_resolve" else "flag-review"
        label = "✅ Auto-resolved" if f.resolution == "auto_resolve" else "🟡 Needs human review"
        st.markdown(
            f"""
            <div class="flag-card {css_class}">
                <div class="flag-label">{label} · confidence {f.confidence:.0%} · {f.category}</div>
                <div class="flag-title">{f.field}</div>
                <div class="flag-detail">{f.issue}</div>
                <div class="flag-detail">{f.detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result.special_clause_explanation:
        st.info(f"**Special clause drafting note:** {result.special_clause_explanation}")

    st.subheader("Draft preview")
    for section in result.sections:
        if section["heading"]:
            st.markdown(f"**{section['heading']}**")
        st.write(section["body"])

    st.subheader("Download")
    with open(result.output_path, "rb") as f:
        st.download_button(
            "⬇️ Download NDA draft (.docx)",
            data=f.read(),
            file_name="NDA_Draft_Northwind_Zycus.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
else:
    st.info("Click **Generate draft** to run the agent pipeline on the inputs above.")
