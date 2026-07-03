"""
suggestion_agent.py

Agent 4: SuggestionAgent  (the "G" in RAG - Generation)
Uses the retrieved job-description context + missing skills to generate
human-readable improvement suggestions.

Tries a local Ollama LLM first (no API key needed, fully offline/local).
If Ollama isn't installed or isn't running, it automatically falls back
to a rule-based suggestion generator so the app never crashes or blocks
submission because of a missing local model.
"""

from utils import llm_client


class SuggestionAgent:
    name = "SuggestionAgent"

    def run(self, missing_skills, matched_skills, retrieved_chunks, verdict):
        if llm_client.is_available():
            try:
                prompt = self._build_prompt(missing_skills, matched_skills, retrieved_chunks, verdict)
                response = llm_client.generate(prompt)
                if response:
                    return {"suggestions": response, "source": "local-llm (ollama)"}
            except Exception:
                # Fall through to rule-based generation below
                pass

        return {
            "suggestions": self._rule_based_suggestions(missing_skills, matched_skills, verdict),
            "source": "rule-based (fallback)"
        }

    def _build_prompt(self, missing_skills, matched_skills, retrieved_chunks, verdict):
        context = "\n".join(f"- {c['text']}" for c in retrieved_chunks)
        return f"""You are a career coach AI. A candidate's resume was compared against a job description.

Verdict: {verdict}
Skills already matched: {', '.join(matched_skills) if matched_skills else 'None'}
Skills missing: {', '.join(missing_skills) if missing_skills else 'None'}

Relevant job description context:
{context}

Write 3-4 short, specific, encouraging bullet-point suggestions to help the candidate
improve their resume or skillset to better match this job. Keep it concise."""

    def _rule_based_suggestions(self, missing_skills, matched_skills, verdict):
        lines = []
        if verdict == "Strong Match":
            lines.append("Your resume already aligns well with this role.")
        elif verdict == "Moderate Match":
            lines.append("Your resume partially matches this role; a few improvements could strengthen it.")
        else:
            lines.append("Your resume currently has a low overlap with this role's requirements.")

        if missing_skills:
            top_missing = ", ".join(missing_skills[:5])
            lines.append(f"Consider learning or highlighting these skills if you have them: {top_missing}.")
            lines.append("Add specific projects or coursework that demonstrate these skills with measurable outcomes.")
        else:
            lines.append("You already cover the key skills detected in this job description.")

        if matched_skills:
            lines.append(f"Make sure to quantify your experience with: {', '.join(matched_skills[:5])} using metrics (e.g., % improvement, time saved).")

        lines.append("Tailor your resume summary to mirror key phrases from the job description for better ATS matching.")

        return "\n".join(f"- {line}" for line in lines)
