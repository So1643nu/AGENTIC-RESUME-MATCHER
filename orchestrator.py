"""
orchestrator.py

The Orchestrator is the "agentic" brain of this project. It decides the
sequence in which agents run, passes outputs from one agent as inputs to
the next, and handles errors gracefully at each step so a failure in one
agent (e.g. LLM unavailable) never crashes the whole pipeline.

Pipeline:
  1. ParserAgent      -> clean resume text
  2. RetrieverAgent   -> RAG: retrieve relevant JD chunks + similarity score
  3. ScorerAgent      -> compute fit score, matched/missing skills
  4. SuggestionAgent  -> generate improvement suggestions (LLM or rule-based)
"""

from agents.parser_agent import ParserAgent
from agents.retriever_agent import RetrieverAgent
from agents.scorer_agent import ScorerAgent
from agents.suggestion_agent import SuggestionAgent


class Orchestrator:
    def __init__(self):
        self.parser = ParserAgent()
        self.retriever = RetrieverAgent()
        self.scorer = ScorerAgent()
        self.suggester = SuggestionAgent()
        self.trace = []  # keeps a log of each agent step for transparency in the UI

    def _log(self, step, status, detail=""):
        self.trace.append({"step": step, "status": status, "detail": detail})

    def run_pipeline(self, resume_file_bytes=None, resume_filename=None,
                      resume_text=None, job_description=""):
        self.trace = []

        # Step 1: Parse resume
        try:
            parsed = self.parser.run(
                resume_file_bytes=resume_file_bytes,
                resume_filename=resume_filename,
                resume_text=resume_text
            )
            self._log("ParserAgent", "success")
        except Exception as e:
            self._log("ParserAgent", "failed", str(e))
            return {"error": str(e), "trace": self.trace}

        # Step 2: Retrieve relevant JD context (RAG)
        try:
            retrieval = self.retriever.run(
                resume_clean_text=parsed["clean_text"],
                job_description=job_description
            )
            self._log("RetrieverAgent", "success")
        except Exception as e:
            self._log("RetrieverAgent", "failed", str(e))
            retrieval = {"retrieved_chunks": [], "similarity_score": 0.0}

        # Step 3: Score the resume against the job description
        try:
            scoring = self.scorer.run(
                resume_raw_text=parsed["raw_text"],
                job_description=job_description,
                similarity_score=retrieval["similarity_score"]
            )
            self._log("ScorerAgent", "success")
        except Exception as e:
            self._log("ScorerAgent", "failed", str(e))
            return {"error": str(e), "trace": self.trace}

        # Step 4: Generate suggestions (LLM if available, else rule-based)
        try:
            suggestion = self.suggester.run(
                missing_skills=scoring["missing_skills"],
                matched_skills=scoring["matched_skills"],
                retrieved_chunks=retrieval["retrieved_chunks"],
                verdict=scoring["verdict"]
            )
            self._log("SuggestionAgent", "success", suggestion["source"])
        except Exception as e:
            self._log("SuggestionAgent", "failed", str(e))
            suggestion = {"suggestions": "Could not generate suggestions.", "source": "error"}

        return {
            "fit_score": scoring["fit_score"],
            "verdict": scoring["verdict"],
            "matched_skills": scoring["matched_skills"],
            "missing_skills": scoring["missing_skills"],
            "retrieved_chunks": retrieval["retrieved_chunks"],
            "suggestions": suggestion["suggestions"],
            "suggestion_source": suggestion["source"],
            "agent_trace": self.trace
        }
