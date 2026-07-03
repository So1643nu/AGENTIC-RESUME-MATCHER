"""
app.py

Flask backend entry point for the Agentic Resume/Job Matcher project.

Routes:
  GET  /                 -> serves the frontend (index.html)
  GET  /api/sample-jobs  -> returns sample job descriptions (for the dropdown)
  POST /api/analyze      -> runs the full agent pipeline and returns results
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory

from orchestrator import Orchestrator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
orchestrator = Orchestrator()


@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/api/sample-jobs", methods=["GET"])
def sample_jobs():
    path = os.path.join(DATA_DIR, "sample_job_descriptions.json")
    with open(path, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    return jsonify(jobs)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    job_description = request.form.get("job_description", "").strip()
    resume_text = request.form.get("resume_text", "").strip()

    resume_file_bytes = None
    resume_filename = None

    if "resume_file" in request.files:
        file = request.files["resume_file"]
        if file and file.filename:
            resume_filename = file.filename
            resume_file_bytes = file.read()

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    if not resume_file_bytes and not resume_text:
        return jsonify({"error": "Please upload a resume file or paste resume text."}), 400

    result = orchestrator.run_pipeline(
        resume_file_bytes=resume_file_bytes,
        resume_filename=resume_filename,
        resume_text=resume_text,
        job_description=job_description
    )

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
