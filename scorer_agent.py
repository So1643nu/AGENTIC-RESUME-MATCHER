"""
scorer_agent.py

Agent 3: ScorerAgent
Combines the TF-IDF similarity score from the RetrieverAgent with a
keyword-overlap check to produce a final "fit score" (0-100), plus lists
of matched and missing skills.
"""

from utils.text_utils import find_matched_skills, clean_text


class ScorerAgent:
    name = "ScorerAgent"

    def run(self, resume_raw_text: str, job_description: str, similarity_score: float):
        resume_skills = set(find_matched_skills(resume_raw_text))
        jd_skills = set(find_matched_skills(job_description))

        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        keyword_overlap_ratio = (
            len(matched_skills) / len(jd_skills) if jd_skills else 0.0
        )

        # Weighted blend: 40% semantic similarity (TF-IDF), 60% keyword overlap.
        # Keyword overlap is weighted higher because TF-IDF similarity on a
        # single short job description chunk can be noisy, while direct
        # skill overlap is a more reliable signal for this scale of demo.
        final_score = (0.4 * similarity_score * 100) + (0.6 * keyword_overlap_ratio * 100)
        final_score = round(min(final_score, 100), 2)

        if final_score >= 75:
            verdict = "Strong Match"
        elif final_score >= 50:
            verdict = "Moderate Match"
        else:
            verdict = "Weak Match"

        return {
            "fit_score": final_score,
            "verdict": verdict,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
