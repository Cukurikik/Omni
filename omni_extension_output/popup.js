document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("status");
  const execBtn = document.getElementById("execBtn");
  const firewallBtn = document.getElementById("firewallBtn");
  const outputEl = document.getElementById("output");
  const promptEl = document.getElementById("prompt");

  // [Poin 5: Edge AI] Cek Ketersediaan
  if (window.ai && window.ai.model) {
    statusEl.textContent = "Gemini Nano (NPU) Ready";
    statusEl.style.color = "#66fcf1";
  } else {
    statusEl.textContent = "NPU Offline. Gunakan Mode Sim.";
  }

  // [Poin 1 & 3: AI Security & Evaluation]
  firewallBtn.addEventListener("click", () => {
    const text = promptEl.value;
    const malicious = /(ignore|bypass|override)/i.test(text);
    if (malicious) {
      outputEl.innerHTML =
        "<span style='color:red;'>⛔ SECURITY HALT: Prompt Injection diblokir!</span>";
      execBtn.disabled = true;
    } else {
      outputEl.innerHTML =
        "<span style='color:#66fcf1;'>✅ Input Aman. Melanjutkan...</span>";
      execBtn.disabled = false;
    }
  });

  execBtn.addEventListener("click", async () => {
    outputEl.innerHTML = "<em>Mengeksekusi Inferensi...</em>";
    try {
      if (window.ai && window.ai.model) {
        const session = await window.ai.model.create();
        const res = await session.prompt(promptEl.value);
        outputEl.innerHTML = res;
      } else {
        // Fallback produksi
        setTimeout(() => {
          outputEl.innerHTML = `[Edge Sim] Output otonom untuk: "${promptEl.value}"`;
        }, 800);
      }
    } catch (e) {
      outputEl.innerHTML = `<span style='color:red;'>Err: ${e.message}</span>`;
    }
  });
});
