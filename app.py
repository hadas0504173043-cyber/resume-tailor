import streamlit as st
from workflow.runner import run_workflow

st.set_page_config(page_title="Resume Tailor", page_icon="📄", layout="wide")

st.title("Resume Tailor")
st.caption("AI-powered resume and cover letter tailoring with hallucination prevention")

col1, col2 = st.columns(2)

with col1:
    resume_text = st.text_area(
        "Your Resume",
        height=400,
        placeholder="Paste your resume here (plain text)...",
    )

with col2:
    jd_text = st.text_area(
        "Job Description",
        height=400,
        placeholder="Paste the job description here...",
    )

if st.button("Tailor My Resume", type="primary", disabled=not (resume_text and jd_text)):
    with st.spinner("Analyzing your resume and the job description..."):
        result = run_workflow(resume_text, jd_text)

    if result.get("error"):
        st.error(f"An error occurred: {result['error']}")
        st.stop()

    st.divider()

    # ── Gap Analysis ──────────────────────────────────────────────────────────
    st.subheader("Gap Analysis")

    gap = result.get("gap_analysis")
    if gap:
        fit_col, _ = st.columns([1, 3])
        with fit_col:
            score = gap.overall_fit_score
            color = "green" if score >= 7 else "orange" if score >= 4 else "red"
            st.metric("Fit Score", f"{score}/10")

        match_col, partial_col, gap_col = st.columns(3)

        with match_col:
            st.markdown("**Strong Matches**")
            for m in gap.strong_matches:
                st.markdown(f"- {m.skill}")

        with partial_col:
            st.markdown("**Partial Matches**")
            for m in gap.partial_matches:
                st.markdown(f"- {m.skill}")

        with gap_col:
            st.markdown("**Gaps**")
            for g in gap.gaps:
                st.markdown(f"- {g}")

        st.info(f"**Tailoring Strategy:** {gap.tailoring_strategy}")
    else:
        st.warning("Gap analysis not available.")

    st.divider()

    # ── Tailored Resume ───────────────────────────────────────────────────────
    st.subheader("Tailored Resume")

    tailored = result.get("tailored_resume")
    if tailored:
        st.text_area(
            "Copy your tailored resume",
            value=tailored.resume_text,
            height=500,
            label_visibility="collapsed",
        )
        with st.expander("What changed?"):
            for change in tailored.key_changes_made:
                st.markdown(f"- {change}")
            if tailored.skills_emphasized:
                st.markdown(f"**Skills emphasized:** {', '.join(tailored.skills_emphasized)}")
    else:
        st.warning("Tailored resume not available.")

    st.divider()

    # ── Cover Letter ──────────────────────────────────────────────────────────
    st.subheader("Cover Letter")

    letter = result.get("cover_letter")
    if letter:
        st.text_area(
            "Copy your cover letter",
            value=letter.cover_letter_text,
            height=400,
            label_visibility="collapsed",
        )
    else:
        st.warning("Cover letter not available.")

    st.divider()

    # ── Validation Status ─────────────────────────────────────────────────────
    st.subheader("Validation Status")

    validation = result.get("validation_result")
    retry_count = result.get("retry_count", 0)

    if validation:
        if validation.is_valid:
            if retry_count == 0:
                st.success("✓ Passed — no hallucinations detected")
            else:
                st.warning(f"⚠ Passed after {retry_count} {'retry' if retry_count == 1 else 'retries'}")
        else:
            st.error("✗ Validation issues detected (max retries reached)")
            if validation.issues:
                st.markdown("**Issues found:**")
                for issue in validation.issues:
                    st.markdown(f"- {issue}")
            if validation.hallucinated_skills:
                st.markdown(f"**Hallucinated skills:** {', '.join(validation.hallucinated_skills)}")
            if validation.hallucinated_metrics:
                st.markdown(f"**Changed metrics:** {', '.join(validation.hallucinated_metrics)}")
            if validation.hallucinated_companies:
                st.markdown(f"**Fabricated companies:** {', '.join(validation.hallucinated_companies)}")
    else:
        st.warning("Validation result not available.")
