// history.js
function renderHistory(filter = "") {
    chrome.storage.local.get({promptHistory: []}, (data) => {
      const historyList = document.getElementById("history-list");
      historyList.innerHTML = "";
      let filtered = data.promptHistory;
      if (filter) {
        filtered = filtered.filter(entry =>
          entry.original.toLowerCase().includes(filter) ||
          entry.optimized.toLowerCase().includes(filter)
        );
      }
      if (filtered.length === 0) {
        historyList.innerHTML = `<div style="color: #9ca3af; text-align: center; padding: 2rem;">No history found.</div>`;
        return;
      }
      filtered.forEach((entry, idx) => {
        const div = document.createElement("div");
        div.className = "history-card";
        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; color: #6b7280;">${new Date(entry.timestamp).toLocaleString()} • <span style="text-transform: uppercase;">${entry.goal}</span></span>
            <span class="star" data-idx="${idx}" style="cursor:pointer; font-size:1.2em; color:${entry.starred ? '#f59e42' : '#d1d5db'};">
              ${entry.starred ? "★" : "☆"}
            </span>
          </div>
          <div style="margin-top: 0.5rem; font-size: 0.95rem;"><b>Original:</b> <span style="font-family: monospace;">${entry.original}</span></div>
          <div style="margin-top: 0.25rem; color: #2563eb; font-size: 0.95rem;"><b>Optimized:</b> <span style="font-family: monospace;">${entry.optimized}</span></div>
          <button class="copy-btn" data-copy="${entry.optimized}" style="margin-top: 0.5rem; color: #2563eb; background: none; border: none; cursor: pointer; font-size: 0.95rem;">Copy</button>
        `;
        historyList.appendChild(div);
      });
  
      // Add event listeners for stars and copy buttons
      document.querySelectorAll(".star").forEach(star => {
        star.onclick = () => toggleStar(Number(star.dataset.idx));
      });
      document.querySelectorAll(".copy-btn").forEach(btn => {
        btn.onclick = () => {
          navigator.clipboard.writeText(btn.dataset.copy);
          btn.innerText = "Copied!";
          setTimeout(() => { btn.innerText = "Copy"; }, 1200);
        };
      });
    });
  }
  
  function toggleStar(index) {
    chrome.storage.local.get({promptHistory: []}, (data) => {
      const history = data.promptHistory;
      if (history[index]) {
        history[index].starred = !history[index].starred;
        chrome.storage.local.set({promptHistory: history}, () => renderHistory(document.getElementById("search").value.toLowerCase()));
      }
    });
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    renderHistory();
    document.getElementById("search").addEventListener("input", (e) => {
      renderHistory(e.target.value.toLowerCase());
    });
  });
  