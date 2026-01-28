async function crawlUrl() {
  const urlInput = document.getElementById("urlInput");
  const crawlBtn = document.getElementById("crawlBtn");
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const error = document.getElementById("error");

  const url = urlInput.value.trim();

  if (!url) {
    showError("Please enter a URL");
    return;
  }

  // Hide previous results
  result.style.display = "none";
  error.style.display = "none";
  loading.style.display = "block";
  crawlBtn.disabled = true;

  try {
    const response = await fetch("http://localhost:5000/crawl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to crawl URL");
    }

    // Display results
    displayResults(data);
  } catch (err) {
    showError(err.message || "Failed to connect to server");
  } finally {
    loading.style.display = "none";
    crawlBtn.disabled = false;
  }
}

function displayResults(data) {
  const result = document.getElementById("result");
  const content = document.getElementById("content");

  if (data.summary) {
    content.textContent = `Summary:\n\n${data.summary}\n\n(Original: ${data.length} characters)`;
  } else {
    content.textContent = data.text;
  }

  result.style.display = "block";
}

function showError(message) {
  const error = document.getElementById("error");
  error.textContent = `Error: ${message}`;
  error.style.display = "block";
}

// Allow Enter key to submit
document.getElementById("urlInput").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    crawlUrl();
  }
});
