// OMNI KERNEL - UI Polling Logic
const API_URL = "http://localhost:8899/api/omni-status";

const masterStatusEl = document.getElementById("masterStatus");
const nodesContainer = document.getElementById("nodesContainer");

// Time Update Logic
setInterval(() => {
  const now = new Date();
  document.getElementById("timeDisplay").innerText =
    `LOCAL HIVE TIME: ${now.toISOString().split("T")[1].slice(0, 8)} | SOVEREIGN MODE`;
}, 1000);

async function fetchOmniData() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error("API Server Tidak Merespon");

    const data = await response.json();
    renderDashboard(data);
  } catch (error) {
    console.error("Fetch Error:", error);
    masterStatusEl.innerText = "KONEKSI KERNEL TERPUTUS (SERVER OFFLINE)";
    masterStatusEl.style.color = "#ff2a6d";

    // Render fallback UI
    if (nodesContainer.innerHTML.includes("Mengesktrak")) {
      nodesContainer.innerHTML = `<div class="loading-data" style="color:#ff2a6d;">Tunggu Eksekusi Backend Python... (Jalankan omni_ui_server.py)</div>`;
    }
  }
}

function renderDashboard(data) {
  masterStatusEl.innerText = data.master_status;
  masterStatusEl.style.color = "#05d5ff";

  const blocksHTML = data.nodes
    .map(
      (node) => `
        <div class="node-card status-${node.status}">
            <div class="node-header">
                <span class="node-id">PILLAR [${String(node.id).padStart(2, "0")}]</span>
                <span class="node-status ${node.status}">${node.status}</span>
            </div>
            <h3 class="node-name">${node.name}</h3>
            <div class="node-metric">${node.metric}</div>
        </div>
    `,
    )
    .join("");

  nodesContainer.innerHTML = blocksHTML;
}

// Initial Fetch and Polling every 2 seconds
fetchOmniData();
setInterval(fetchOmniData, 2000);
