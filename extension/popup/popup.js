function stripSurroundingQuotes(str) {
  return str.trim().replace(/^["']|["']$/g, "");
}

// Save a new prompt to history
function savePromptToHistory(entry) {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const history = data.promptHistory;
    history.unshift(entry); // Add to the top
    // Limit history to last 20 entries
    if (history.length > 20) history.pop();
    chrome.storage.local.set({promptHistory: history});
  });
}

// Toggle star status
function toggleStar(index) {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const history = data.promptHistory;
    if (history[index]) {
      history[index].starred = !history[index].starred;
      chrome.storage.local.set({promptHistory: history}, renderHistory);
    }
  });
}

// Robust copy-to-clipboard with feedback and fallback
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text)
    .then(() => showCopyFeedback(btn, true))
    .catch(() => showCopyFeedback(btn, false));
}
function showCopyFeedback(btn, success) {
  const original = btn.innerText;
  btn.innerText = success ? "Copied!" : "Failed";
  btn.style.color = success ? "#059669" : "#dc2626";
  setTimeout(() => {
    btn.innerText = "Copy";
    btn.style.color = "";
  }, 1200);
}

// Render history in the popup
function renderHistory() {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;
    historyList.innerHTML = "";
    if (data.promptHistory.length === 0) {
      historyList.innerHTML = `<div class="text-xs text-gray-400 text-center py-2">No history yet.</div>`;
      return;
    }
    data.promptHistory.forEach((entry, idx) => {
      const div = document.createElement("div");
      div.className = "rounded-lg border border-gray-200 bg-white shadow-sm p-3 hover:shadow-md transition";
      div.innerHTML = `
        <div class="flex items-center justify-between mb-1">
          <span class="text-[11px] text-gray-500">${new Date(entry.timestamp).toLocaleString()} • <span class="uppercase">${entry.goal}</span></span>
          <span class="star" data-idx="${idx}" style="cursor:pointer; font-size:1.2em; color:${entry.starred ? '#f59e42' : '#d1d5db'};">
            ${entry.starred ? "★" : "☆"}
          </span>
        </div>
        <div class="text-xs text-gray-700 mb-1"><b>Original:</b> <span class="font-mono">${entry.original}</span></div>
        <div class="text-xs text-blue-700 mb-1"><b>Optimized:</b> <span class="font-mono">${entry.optimized}</span></div>
        <button class="copy-btn text-xs text-blue-600 underline" data-copy="${entry.optimized}">Copy</button>
      `;
      historyList.appendChild(div);
    });

    // Add event listeners for stars and copy buttons
    document.querySelectorAll(".star").forEach(star => {
      star.onclick = () => toggleStar(Number(star.dataset.idx));
    });
    document.querySelectorAll(".copy-btn").forEach(btn => {
      btn.onclick = () => {
        copyToClipboard(btn.dataset.copy, btn);
      };
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("optimize").addEventListener("click", () => {
    const goal = document.getElementById("goal").value;
    const loading = document.getElementById("loading");
    const output = document.getElementById("optimized");

    loading.style.display = "block";
    output.value = "";

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { type: "GET_PROMPT" }, async (response) => {
        if (chrome.runtime.lastError || !response?.prompt) {
          loading.style.display = "none";
          alert("Could not detect a prompt. Make sure you're focused on a prompt field.");
          return;
        }

        const prompt = response.prompt;

        try {
          const res = await fetch("http://localhost:8000/optimize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt, goal })
          });

          const data = await res.json();
          output.value = data.optimized_prompt || "No response received.";
          
          // Only save to history if the optimized prompt is valid (not an error)
          if (
            data.optimized_prompt &&
            !data.optimized_prompt.startsWith("Error") &&
            !data.optimized_prompt.startsWith("API Error")
          ) {
            savePromptToHistory({
              original: prompt,
              optimized: data.optimized_prompt,
              goal: goal,
              timestamp: Date.now(),
              starred: false
            });
            renderHistory();
          }
        } catch (err) {
          output.value = "Error: " + err.message;
        } finally {
          loading.style.display = "none";
        }
      });
    });
  });

  document.getElementById("replace").addEventListener("click", () => {
    let optimized = document.getElementById("optimized").value;
    if (!optimized) {
      alert("No optimized prompt to insert.");
      return;
    }

    // Strip leading/trailing quotes
    optimized = stripSurroundingQuotes(optimized);

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      console.log("Sending REPLACE_PROMPT message:", optimized);
      chrome.tabs.sendMessage(
        tabs[0].id,
        { type: "REPLACE_PROMPT", optimized },
        (response) => {
          if (chrome.runtime.lastError) {
            alert("Could not replace the prompt. Make sure you're on a supported page.");
          } else {
            console.log("Popup: REPLACE_PROMPT response:", response);
          }
        }
      );
    });
  });

  document.getElementById("toggle-history").addEventListener("click", () => {
    const section = document.getElementById("history-section");
    const btn = document.getElementById("toggle-history");
    if (section.style.display === "none") {
      section.style.display = "block";
      btn.innerText = "Hide History";
    } else {
      section.style.display = "none";
      btn.innerText = "Show History";
    }
  });

  // Render history on popup load
  renderHistory();
});
