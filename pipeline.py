"""
Orchestrator: Validator -> Drafter (LLM) -> Docgen.

This is the "multi-step / multi-tool" backbone. Each stage is independently
testable and has a single responsibility:
    1. validate_inputs      (deterministic rules)      -> list[Flag]
    2. draft_special_clause (LLM, only when needed)     -> clause text
    3. build_draft          (deterministic template-fill)-> sections
    4. generate_docx        (deterministic doc tool)    -> .docx file
"""

from dataclasses import dataclass

from agents.validator import validate_inputs, Flag
from agents.drafter import draft_special_clause, build_draft
from agents.docgen import generate_docx
from agents.llm_client import LLMUnavailable
from inputs import resolve_runtime_defaults


@dataclass
class PipelineResult:
    flags: list[Flag]
    sections: list[dict]
    output_path: str
    special_clause_explanation: str | None
    llm_degraded: bool  # True if we fell back because the LLM was unavailable


def run_pipeline(raw_inputs: dict, output_path: str = "output/nda_draft.docx") -> PipelineResult:
    # Stage 1: validate against the RAW inputs first, so an open field like
    # effective_date=None still produces a flag. Only resolve runtime
    # defaults afterward, for use in the template fill. (Resolving first
    # would silently erase the thing we need to flag.)
    flags = validate_inputs(raw_inputs)
    inputs = resolve_runtime_defaults(raw_inputs)

    # Stage 2: for the flag that needs judgment (special clause), attempt
    # an LLM draft. If the LLM is unavailable, degrade gracefully: leave the
    # clause explicitly marked as pending rather than guessing or crashing.
    special_clause_text = None
    special_clause_explanation = None
    llm_degraded = False

    needs_special_clause = any(
        f.field == "special_clause_requested" for f in flags
    )
    if needs_special_clause:
        try:
            special_clause_text, special_clause_explanation = draft_special_clause()
        except LLMUnavailable as e:
            llm_degraded = True
            special_clause_explanation = (
                f"LLM drafting unavailable ({e}). Clause left pending for "
                "manual drafting."
            )

    # Stage 3: deterministic template fill
    sections = build_draft(inputs, special_clause_text)

    # Stage 4: deterministic document generation
    generate_docx(sections, flags, output_path)

    return PipelineResult(
        flags=flags,
        sections=sections,
        output_path=output_path,
        special_clause_explanation=special_clause_explanation,
        llm_degraded=llm_degraded,
    )
