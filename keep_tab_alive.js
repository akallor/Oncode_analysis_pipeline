function connectToColab() {
  const connectBtn = document.querySelector("colab-connect-button");
  const status = connectBtn?.shadowRoot?.querySelector('#connect');

  if (status) {
    const currentText = status.innerText.trim();
    
    if (currentText === "Reconnect" || currentText === "Connect") {
      console.log("🔌 Disconnected – attempting to reconnect...");
      status.click();
    } else {
      console.log("✅ Still connected – keeping session alive...");
      status.click(); // Simulate activity to prevent timeout
    }
  } else {
    console.warn("❗ Could not find connect button – maybe layout changed?");
  }
}

// Check every 60 seconds (60000 ms)
setInterval(connectToColab, 60000);
