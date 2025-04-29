chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "COPY_TO_CLIPBOARD") {
      // Create a temporary textarea in the background page
      const textarea = document.createElement("textarea");
      textarea.value = request.text;
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        sendResponse({ success: true });
      } catch (err) {
        sendResponse({ success: false });
      }
      document.body.removeChild(textarea);
      return true; // Indicates async response
    }
  });
  