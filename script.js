// ---- Tab switching (Upload vs Paste resume) ----
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab + "Tab").classList.add("active");
  });
});

// ---- Load sample job descriptions into dropdown ----
async function loadSampleJobs() {
  try {
    const res = await fetch("/api/sample-jobs");
    const jobs = await res.json();
    const select = document.getElementById("sampleJobs");
    jobs.forEach(job => {
      const opt = document.createElement("option");
      opt.value = job.description;
      opt.textContent = job.title;
      select.appendChild(opt);
    });
  } catch (e) {
    console.warn("Could not load sample jobs:", e);
  }
}
loadSampleJobs();

document.getElementById("sampleJobs").addEventListener("change", (e) => {
  if (e.target.value) {
    document.getElementById("jobDescription").value = e.target.value;
  }
});

// ---- Main analyze action ----
document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const jobDescription = document.getElementById("jobDescription").value.trim();
  const resumeFileInput = document.getElementById("resumeFile");
  const resumeText = document.getElementById("resumeText").value.trim();
  const errorMsg = document.getElementById("errorMsg");

  errorMsg.textContent = "";

  if (!jobDescription) {
    errorMsg.textContent = "Please enter or select a job description.";
    return;
  }
  const hasFile = resumeFileInput.files.length > 0;
  if (!hasFile && !resumeText) {
    errorMsg.textContent = "Please upload a resume file or paste resume text.";
    return;
  }

  const formData = new FormData();
  formData.append("job_description", jobDescription);
  if (hasFile) {
    formData.append("resume_file", resumeFileInput.files[0]);
  } else {
    formData.append("resume_text", resumeText);
  }

  setLoading(true);

  try {
    const res = await fetch("/api/analyze", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Something went wrong.");
    }
    renderResult(data);
  } catch (err) {
    errorMsg.textContent = err.message;
    document.getElementById("emptyState").classList.remove("hidden");
    document.getElementById("resultState").classList.add("hidden");
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  document.getElementById("loadingState").classList.toggle("hidden", !isLoading);
  if (isLoading) {
    document.getElementById("emptyState").classList.add("hidden");
    document.getElementById("resultState").classList.add("hidden");
  }
}

function renderResult(data) {
  document.getElementById("emptyState").classList.add("hidden");
  document.getElementById("resultState").classList.remove("hidden");

  document.getElementById("scoreNumber").textContent = Math.round(data.fit_score);
  document.getElementById("verdictText").textContent = data.verdict;
  document.getElementById("sourceText").textContent = "Suggestions via: " + data.suggestion_source;

  const scoreCircle = document.getElementById("scoreCircle");
  if (data.fit_score >= 75) {
    scoreCircle.style.borderColor = "#2dd4bf";
  } else if (data.fit_score >= 50) {
    scoreCircle.style.borderColor = "#f5a623";
  } else {
    scoreCircle.style.borderColor = "#ef4444";
  }

  const matchedList = document.getElementById("matchedSkills");
  matchedList.innerHTML = "";
  if (data.matched_skills.length === 0) {
    matchedList.innerHTML = "<li>None detected</li>";
  } else {
    data.matched_skills.forEach(skill => {
      const li = document.createElement("li");
      li.textContent = skill;
      matchedList.appendChild(li);
    });
  }

  const missingList = document.getElementById("missingSkills");
  missingList.innerHTML = "";
  if (data.missing_skills.length === 0) {
    missingList.innerHTML = "<li>None — great coverage!</li>";
  } else {
    data.missing_skills.forEach(skill => {
      const li = document.createElement("li");
      li.textContent = skill;
      missingList.appendChild(li);
    });
  }

  document.getElementById("suggestionsText").textContent = data.suggestions;

  const traceList = document.getElementById("agentTrace");
  traceList.innerHTML = "";
  data.agent_trace.forEach(step => {
    const li = document.createElement("li");
    li.textContent = `${step.step}: ${step.status}${step.detail ? " (" + step.detail + ")" : ""}`;
    traceList.appendChild(li);
  });
}
