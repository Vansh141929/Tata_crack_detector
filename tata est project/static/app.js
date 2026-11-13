/* ══════════════════════════════════════════════════════════
   STEELGUARD AI · APP LOGIC
══════════════════════════════════════════════════════════ */

let currentPredictionData = null;
let rawHeatmapData = null;
let rawOriginalData = null;

document.addEventListener("DOMContentLoaded", () => {
  setupSpecimenChips();
  setupDropzone();
  setupSlider();
  setupReportDownload();

  // Load default initial specimen
  loadSpecimen("crazing");
});

function setupSpecimenChips() {
  const chips = document.querySelectorAll(".chip");
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const sampleId = chip.getAttribute("data-sample");
      loadSpecimen(sampleId);
    });
  });
}

function setupDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const browseBtn = document.getElementById("browseBtn");

  browseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropzone.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) {
      uploadFile(fileInput.files[0]);
    }
  });

  ["dragenter", "dragover"].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });
}

function setupSlider() {
  const slider = document.getElementById("gradcamSlider");
  slider.addEventListener("input", () => {
    if (!rawOriginalData || !rawHeatmapData) return;
    const alpha = slider.value / 100.0;
    blendGradCam(alpha);
  });
}

function blendGradCam(alpha) {
  const canvas = document.createElement("canvas");
  const imgOrig = new Image();
  const imgHeat = new Image();

  imgOrig.src = rawOriginalData;
  imgHeat.src = rawHeatmapData;

  imgOrig.onload = () => {
    canvas.width = imgOrig.naturalWidth;
    canvas.height = imgOrig.naturalHeight;
    const ctx = canvas.getContext("2d");

    // Draw original
    ctx.globalAlpha = 1.0;
    ctx.drawImage(imgOrig, 0, 0);

    // Draw heatmap with alpha
    ctx.globalAlpha = alpha;
    ctx.drawImage(imgHeat, 0, 0);

    document.getElementById("imgGradcam").src = canvas.toDataURL("image/jpeg", 0.92);
  };
}

async function loadSpecimen(sampleId) {
  showLoading(true);
  try {
    const formData = new FormData();
    formData.append("sample_id", sampleId);

    const res = await fetch("/api/predict", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Inference failed");
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    console.error("Error running prediction:", err);
  } finally {
    showLoading(false);
  }
}

async function uploadFile(file) {
  // Deselect chips
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  showLoading(true);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/predict", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Inference failed");
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    console.error("Error running prediction:", err);
  } finally {
    showLoading(false);
  }
}

function showLoading(isLoading) {
  document.getElementById("loadingState").style.display = isLoading ? "flex" : "none";
  document.getElementById("resultsDash").style.opacity = isLoading ? "0.4" : "1";
}

function renderResults(data) {
  currentPredictionData = data;
  const p = data.prediction;

  // Banner
  document.getElementById("resultDefectName").textContent = p.display;
  document.getElementById("resultDefectDesc").textContent = p.description;

  const riskBadge = document.getElementById("resultRiskBadge");
  riskBadge.textContent = `${p.risk_level} RISK`;
  if (p.risk_level === "HIGH") {
    riskBadge.style.background = "#fee2e2";
    riskBadge.style.color = "#b91c1c";
    riskBadge.style.borderColor = "#fca5a5";
  } else if (p.risk_level === "MEDIUM") {
    riskBadge.style.background = "#fef3c7";
    riskBadge.style.color = "#b45309";
    riskBadge.style.borderColor = "#fcd34d";
  } else {
    riskBadge.style.background = "#dcfce7";
    riskBadge.style.color = "#15803d";
    riskBadge.style.borderColor = "#86efac";
  }

  document.getElementById("resultRiskScore").textContent = p.risk_score;
  document.getElementById("resultConfidence").textContent = `${p.confidence}%`;

  // Images
  rawOriginalData = data.images.original;
  rawHeatmapData = data.images.heatmap_raw;

  document.getElementById("imgOriginal").src = data.images.original;
  document.getElementById("imgGradcam").src = data.images.gradcam;
  document.getElementById("imgEdge").src = data.images.edge_map;

  // Reset slider
  document.getElementById("gradcamSlider").value = 70;

  // Telemetry & Metallurgy
  document.getElementById("metaRootCause").textContent = p.root_cause;
  document.getElementById("metaAction").textContent = p.action;
  document.getElementById("telDefectArea").textContent = `${p.defect_area_pct}%`;
  document.getElementById("telLatency").textContent = `${data.latency_ms} ms`;

  // Probabilities
  const probContainer = document.getElementById("probBarsContainer");
  probContainer.innerHTML = "";

  data.probabilities.forEach(item => {
    const row = document.createElement("div");
    row.className = "prob-row";

    const isTop = item.class === p.class;
    row.innerHTML = `
      <div class="prob-name" style="${isTop ? 'font-weight: 700; color: #0c0d10;' : ''}">${item.display}</div>
      <div class="prob-track">
        <div class="prob-fill" style="width: ${item.prob}%; background: ${item.color};"></div>
      </div>
      <div class="prob-val">${item.prob.toFixed(1)}%</div>
    `;
    probContainer.appendChild(row);
  });
}

function setupReportDownload() {
  const btn = document.getElementById("downloadReportBtn");
  btn.addEventListener("click", () => {
    if (!currentPredictionData) return;

    const report = {
      title: "Tata Steel Surface Quality Inspection Certificate",
      standard: "ASTM E381 & ISO 9001:2015",
      timestamp: new Date().toISOString(),
      plant_unit: "Hot Strip Mill 4 / Finishing Stand 6",
      classification: currentPredictionData.prediction,
      probabilities: currentPredictionData.probabilities,
      inspection_latency_ms: currentPredictionData.latency_ms,
      operator_signoff: "Tata Steel Automated AI Vision Engine v2.4",
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tata_steel_inspection_${currentPredictionData.prediction.class}_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}
