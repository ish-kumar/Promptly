function stripSurroundingQuotes(str) {
  return str.trim().replace(/^["']|["']$/g, "");
}

// Save a new prompt to history
function savePromptToHistory(entry) {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const history = data.promptHistory;
    history.unshift(entry); // Add to the top
    if (history.length > 20) history.pop();
    chrome.storage.local.set({promptHistory: history});
  });
}

// Render history in the popup
function renderHistory(filter = "") {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;
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
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div class="timestamp">
            <span>${new Date(entry.timestamp).toLocaleString()}</span>
            <span class="goal-badge">${entry.goal}</span>
          </div>
          <span class="star" data-idx="${idx}" style="cursor:pointer; font-size:1.2em; color:${entry.starred ? '#f59e42' : '#d1d5db'};">
            ${entry.starred ? "★" : "☆"}
          </span>
        </div>
        <div style="margin-bottom: 0.75rem;">
          <div style="margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;"><b>Original:</b></div>
          <div class="prompt-text">${entry.original}</div>
        </div>
        <div style="margin-bottom: 1rem;">
          <div style="margin-bottom: 0.5rem; color: var(--primary); font-size: 0.9rem;"><b>Optimized:</b></div>
          <div class="prompt-text">${entry.optimized}</div>
        </div>
        <button class="copy-btn" data-copy="${entry.optimized}">Copy Optimized Prompt</button>
      `;
      historyList.appendChild(div);
    });

    // Add event listeners for stars and copy buttons
    document.querySelectorAll(".star").forEach(star => {
      star.onclick = () => toggleStar(Number(star.dataset.idx));
    });
    document.querySelectorAll(".copy-btn").forEach(btn => {
      btn.onclick = async () => {
        try {
          await navigator.clipboard.writeText(btn.dataset.copy);
          btn.innerText = "Copied!";
          setTimeout(() => { btn.innerText = "Copy"; }, 1200);
        } catch (err) {
          console.error("Failed to copy text:", err);
          alert("Failed to copy text to clipboard. Please try again.");
        }
      };
    });
  });
}

function toggleStar(index) {
  chrome.storage.local.get({promptHistory: []}, (data) => {
    const history = data.promptHistory;
    if (history[index]) {
      history[index].starred = !history[index].starred;
      const searchInput = document.getElementById("search");
      const currentFilter = searchInput ? searchInput.value.toLowerCase() : "";
      chrome.storage.local.set({promptHistory: history}, () => renderHistory(currentFilter));
    }
  });
}

// Quality Checker Functionality
document.addEventListener("DOMContentLoaded", () => {
  // Debug helper
  const debug = (msg, ...args) => {
    console.log(`[Promptly Debug] ${msg}`, ...args);
  };

  // Tab switching logic
  const switchTab = (tabId) => {
    debug('Switching to tab:', tabId);
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    
    const button = document.querySelector(`[data-tab="${tabId}"]`);
    const tab = document.getElementById(`${tabId}-tab`);
    
    if (button && tab) {
      button.classList.add('active');
      tab.classList.add('active');
      debug('Tab switched successfully');
    } else {
      debug('Failed to find tab elements:', { button, tab });
    }
  };

  // Add tab button click handlers
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      switchTab(tabId);
      
      // Render history when switching to history tab
      if (tabId === 'history') {
        const searchInput = document.getElementById('search');
        if (searchInput) {
          renderHistory(searchInput.value.toLowerCase());
        }
      }
    });
  });

  // Initialize the default tab
  const defaultTab = 'optimize';
  switchTab(defaultTab);

  // Optimize logic
  document.getElementById("optimize").addEventListener("click", async () => {
    const goal = document.getElementById("goal").value;
    const loading = document.getElementById("loading");
    const output = document.getElementById("optimized");

    loading.style.display = "block";
    output.value = "";

    try {
      // Get the current active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        throw new Error("No active tab found");
      }

      // Check if content script is loaded
      try {
        const response = await chrome.tabs.sendMessage(tab.id, { type: "GET_PROMPT" });
        
        if (!response?.prompt) {
          throw new Error("No prompt detected");
        }

        const prompt = response.prompt;

        // Make the API request
        const res = await fetch("http://localhost:8000/optimize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, goal })
        });

        if (!res.ok) {
          throw new Error(`Server returned ${res.status}: ${res.statusText}`);
        }

        const data = await res.json();
        output.value = data.optimized_prompt || "No response received.";

        // Only save to history if the optimized prompt is valid
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
        }
      } catch (err) {
        if (err.message.includes("Receiving end does not exist")) {
          output.value = "Error: Please refresh the page and try again.";
        } else {
          output.value = "Error: " + err.message;
        }
      }
    } catch (err) {
      output.value = "Error: " + err.message;
    } finally {
      loading.style.display = "none";
    }
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
      chrome.tabs.sendMessage(
        tabs[0].id,
        { type: "REPLACE_PROMPT", optimized },
        (response) => {
          if (chrome.runtime.lastError) {
            alert("Could not replace the prompt. Make sure you're on a supported page.");
          }
        }
      );
    });
  });

  // History search
  const searchInput = document.getElementById("search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      renderHistory(e.target.value.toLowerCase());
    });
  }

  // Render history on load (for the history tab)
  renderHistory();
});
