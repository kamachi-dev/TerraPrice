let allDatasets = []
let latestDatasets = []

// Initialize admin dashboard
document.addEventListener("DOMContentLoaded", () => {
  loadAllDatasets()
  loadLatestDatasets()
  updateStats()
})

// Tab switching functionality
function openTab(evt, tabName) {
  const tabContents = document.getElementsByClassName("tab-content")
  const tabButtons = document.getElementsByClassName("tab-button")

  for (let i = 0; i < tabContents.length; i++) {
    tabContents[i].classList.remove("active")
  }

  for (let i = 0; i < tabButtons.length; i++) {
    tabButtons[i].classList.remove("active")
  }

  document.getElementById(tabName).classList.add("active")
  evt.currentTarget.classList.add("active")
}

// Load all datasets
async function loadAllDatasets() {
  try {
    const response = await fetch("/admin/datasets")
    if (!response.ok) throw new Error("Failed to fetch datasets")

    allDatasets = await response.json()
    renderDatasetsTable("all-datasets-table", allDatasets)
    updateStats()
  } catch (error) {
    console.error("Error loading datasets:", error)
    showError("all-datasets-table", "Failed to load datasets")
  }
}

// Load latest datasets
async function loadLatestDatasets() {
  try {
    const response = await fetch("/admin/latest-datasets")
    if (!response.ok) throw new Error("Failed to fetch latest datasets")

    latestDatasets = await response.json()
    renderDatasetsTable("latest-datasets-table", latestDatasets)
  } catch (error) {
    console.error("Error loading latest datasets:", error)
    showError("latest-datasets-table", "Failed to load latest datasets")
  }
}

// Render datasets table
function renderDatasetsTable(tableId, datasets) {
  const tbody = document.querySelector(`#${tableId} tbody`)

  if (datasets.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="loading">No datasets found</td></tr>'
    return
  }

  tbody.innerHTML = datasets
    .map(
      (dataset) => `
        <tr>
            <td>${dataset.id}</td>
            <td>${Number.parseFloat(dataset.latitude).toFixed(6)}</td>
            <td>${Number.parseFloat(dataset.longitude).toFixed(6)}</td>
            <td>${dataset.category}</td>
            <td>${dataset.commodity}</td>
            <td>${dataset.pricetype}</td>
            <td>₱${Number.parseFloat(dataset.price).toFixed(2)}</td>
        </tr>
    `,
    )
    .join("")
}

// Show error in table
function showError(tableId, message) {
  const tbody = document.querySelector(`#${tableId} tbody`)
  tbody.innerHTML = `<tr><td colspan="7" class="loading" style="color: #dc3545;">${message}</td></tr>`
}

// Update statistics
function updateStats() {
  document.getElementById("total-datasets").textContent = allDatasets.length.toLocaleString()
  document.getElementById("latest-count").textContent = latestDatasets.length
}

// Train model
async function trainModel() {
  const trainBtn = document.getElementById("train-btn")
  const trainingStatus = document.getElementById("training-status")
  const trainingLog = document.getElementById("training-log")
  const logContent = document.getElementById("log-content")

  // Disable button and show loading state
  trainBtn.disabled = true
  trainBtn.textContent = "🔄 Training..."
  trainingStatus.textContent = "Training in progress..."

  // Show training log
  trainingLog.style.display = "block"
  logContent.innerHTML = ""

  // Add log entries
  addLogEntry("Starting model training...", "info")
  addLogEntry("Loading dataset...", "info")

  try {
    const response = await fetch("/admin/train", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })

    const result = await response.json()

    if (result.success) {
      addLogEntry("Dataset loaded successfully", "success")
      addLogEntry("Initializing neural network...", "info")
      addLogEntry("Training model with new data...", "info")
      addLogEntry("Model training completed successfully!", "success")
      addLogEntry(`Result: ${result.message}`, "success")

      trainingStatus.textContent = "Training completed"
      document.getElementById("last-trained").textContent = new Date().toLocaleString()
      document.getElementById("model-status").textContent = "Updated"

      // Show success message
      setTimeout(() => {
        alert("✅ Model retrained successfully!")
      }, 1000)
    } else {
      addLogEntry(`Training failed: ${result.message}`, "error")
      trainingStatus.textContent = "Training failed"
      alert("❌ Model training failed. Check the log for details.")
    }
  } catch (error) {
    console.error("Training error:", error)
    addLogEntry(`Error: ${error.message}`, "error")
    trainingStatus.textContent = "Training failed"
    alert("❌ An error occurred during training.")
  } finally {
    // Re-enable button
    trainBtn.disabled = false
    trainBtn.textContent = "Retrain Model"

    // Reset status after delay
    setTimeout(() => {
      trainingStatus.textContent = "Ready"
    }, 5000)
  }
}

// Add log entry
function addLogEntry(message, type = "info") {
  const logContent = document.getElementById("log-content")
  const timestamp = new Date().toLocaleTimeString()
  const logEntry = document.createElement("div")
  logEntry.className = `log-entry ${type}`
  logEntry.textContent = `[${timestamp}] ${message}`
  logContent.appendChild(logEntry)

  // Auto-scroll to bottom
  logContent.scrollTop = logContent.scrollHeight
}

// Auto-refresh data every 30 seconds
setInterval(() => {
  loadLatestDatasets()
}, 30000)
