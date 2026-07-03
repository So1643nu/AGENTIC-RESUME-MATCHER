"""
parser_agent.py

Agent 1: ParserAgent
Responsible for turning raw input (uploaded PDF bytes or pasted text) into
clean plain text that the rest of the pipeline can work with.

This is the first step of the agent pipeline orchestrated by orchestrator.py.
"""

from utils.text_utils import extract_text_from_pdf, clean_text


class ParserAgent:
    name = "ParserAgent"

    def run(self, resume_file_bytes=None, resume_filename=None, resume_text=None):
        """
        Returns cleaned resume text.
        Accepts either an uploaded PDF (bytes) or raw pasted text.
        """
        raw_text = ""

        if resume_file_bytes and resume_filename and resume_filename.lower().endswith(".pdf"):
            try:
                raw_text = extract_text_from_pdf(resume_file_bytes)
            except Exception as e:
                raise RuntimeError(f"ParserAgent failed to read PDF: {e}")
        elif resume_file_bytes and resume_filename and resume_filename.lower().endswith(".txt"):
            raw_text = resume_file_bytes.decode("utf-8", errors="ignore")
        elif resume_text:
            raw_text = resume_text
        else:
            raise ValueError("ParserAgent received no usable resume input.")

        if not raw_text.strip():
            raise ValueError("ParserAgent could not extract any text from the resume.")

        return {
            "raw_text": raw_text,
            "clean_text": clean_text(raw_text)
        }
