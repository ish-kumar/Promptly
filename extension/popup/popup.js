function stripSurroundingQuotes(str) {
  return str.trim().replace(/^["']|["']$/g, "");
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
});
