console.log("Promptly content script loaded.");

// Track the last focused input or editable element
let lastFocusedElement = null;

document.addEventListener("focusin", (e) => {
  if (
    e.target.tagName === "TEXTAREA" ||
    e.target.isContentEditable ||
    e.target.tagName === "INPUT"
  ) {
    lastFocusedElement = e.target;
    console.log("Promptly: Tracked new focused element:", lastFocusedElement);
  }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("📩 Message received in content script:", request);

  if (request.type === "GET_PROMPT") {
    // Use lastFocusedElement for reliability
    const prompt =
      lastFocusedElement?.value ||
      lastFocusedElement?.innerText ||
      "";
    console.log("📤 Sending prompt:", prompt);
    sendResponse({ prompt });
    return true;
  }

  if (request.type === "REPLACE_PROMPT") {
    let success = false;
    if (lastFocusedElement) {
      if (
        lastFocusedElement.tagName === "TEXTAREA" ||
        lastFocusedElement.tagName === "INPUT"
      ) {
        lastFocusedElement.value = request.optimized;
        lastFocusedElement.dispatchEvent(new Event("input", { bubbles: true }));
        success = true;
      } else if (lastFocusedElement.isContentEditable) {
        lastFocusedElement.innerText = request.optimized;
        lastFocusedElement.dispatchEvent(new Event("input", { bubbles: true }));
        success = true;
      }
      console.log("Promptly: Replaced prompt in last focused element.");
    } else {
      console.log("Promptly: No last focused element to replace.");
    }
    sendResponse({ success });
    return true;
  }
});
