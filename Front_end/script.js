
const API_BASE_URL =
  "http://127.0.0.1:8000";

const API_ENDPOINT = "/job-fit";

const USE_MOCK_API = false;

// ================== HELPERS ==================

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

function mapFitLabelToUi(labelRaw) {
  if (!labelRaw) return { label: "Unknown", type: "fit" };

  const value = String(labelRaw).toLowerCase().trim();

  // Backend returns: "Good Fit", "Potential Fit", or "No Fit"
  if (value === "good fit") {
    return { label: "Good Fit", type: "good-fit" };
  }

  if (value === "potential fit") {
    return { label: "Potential Fit", type: "fit" };
  }

  if (value === "no fit") {
    return { label: "No Fit", type: "not-fit" };
  }

  return { label: labelRaw, type: "fit" };
}

function updateResultUi(mapped, extraMessage) {
  const resultSection = document.getElementById("resultSection");
  const badge = document.getElementById("resultBadge");
  const text = document.getElementById("resultText");

  if (!resultSection || !badge || !text) return;

  badge.classList.remove("result-fit", "result-not-fit", "result-good-fit");

  switch (mapped.type) {
    case "fit":
      badge.classList.add("result-fit");
      text.textContent = extraMessage || "Your CV matches this job well.";
      break;
    case "good-fit":
      badge.classList.add("result-good-fit");
      text.textContent =
        extraMessage || "Your CV is a great match for this job.";
      break;
    case "not-fit":
      badge.classList.add("result-not-fit");
      text.textContent =
        extraMessage || "Your CV does not match this job closely.";
      break;
    default:
      badge.classList.add("result-fit");
      text.textContent = extraMessage || "Result received.";
  }

  badge.textContent = mapped.label;
  resultSection.classList.remove("hidden");
}

// ================== API CALL ==================

async function callJobFitApi(file, jobDescription) {
  if (USE_MOCK_API) {
    await new Promise((res) => setTimeout(res, 700));
    const options = ["Good Fit", "No Fit", "Potential Fit"];
    const choice = options[Math.floor(Math.random() * options.length)];
    return { raw: { mock: true, label: choice }, label: choice };
  }

  const formData = new FormData();

  // Field names MUST match backend API exactly:
  formData.append("resume_text_pdf", file); // Backend expects: resume_text_pdf
  formData.append("job_description_text", jobDescription); // Backend expects: job_description_text

  const response = await fetch(API_BASE_URL + API_ENDPOINT, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const bodyText = await response.text().catch(() => "");
    throw new Error(
      `API error: ${response.status} ${response.statusText} - ${bodyText}`
    );
  }

  const data = await response.json().catch(() => ({}));

  const label = data.label || null;

  return { raw: data, label };
}

// ================== DOM EVENTS ==================

document.addEventListener("DOMContentLoaded", () => {
  const getStartedBtn = document.getElementById("getStartedBtn");
  if (getStartedBtn) {
    getStartedBtn.addEventListener("click", () => {
      window.location.href = "analyze.html";
    });
  }

  const analyzeForm = document.getElementById("analyzeForm");
  const analyzeBtn = document.getElementById("analyzeBtn");

  if (analyzeForm && analyzeBtn) {
    analyzeForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const fileInput = document.getElementById("cvInput");
      const jdTextarea = document.getElementById("jobDescription");

      const file = fileInput && fileInput.files ? fileInput.files[0] : null;
      const jobDescription = jdTextarea ? jdTextarea.value.trim() : "";

      if (!file) {
        showToast("Please upload your CV file.");
        return;
      }

      if (!jobDescription) {
        showToast("Please paste the job description.");
        return;
      }

      analyzeBtn.disabled = true;
      analyzeBtn.textContent = "Analyzing...";

      try {
        const result = await callJobFitApi(file, jobDescription);

        if (!result.label) {
          updateResultUi(
            { label: "Unknown", type: "fit" },
            "Result received but label field was not found. Check API mapping."
          );
        } else {
          const mapped = mapFitLabelToUi(result.label);
          updateResultUi(mapped);
        }
      } catch (error) {
        console.error(error);
        showToast("Something went wrong while calling the API.");
      } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Fit";
      }
    });
  }

  const tryAgainBtn = document.getElementById("tryAgainBtn");
  if (tryAgainBtn) {
    tryAgainBtn.addEventListener("click", () => {
      const form = document.getElementById("analyzeForm");
      const resultSection = document.getElementById("resultSection");
      if (form) form.reset();
      if (resultSection) resultSection.classList.add("hidden");
    });
  }

  const homeBtn = document.getElementById("homeBtn");
  if (homeBtn) {
    homeBtn.addEventListener("click", () => {
      window.location.href = "index.html";
    });
  }
});
