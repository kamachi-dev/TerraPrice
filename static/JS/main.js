let predictMap, datasetMap
let predictMarker, datasetMarker

// Philippine bounds
const philippinesBounds = [
  [4.2158, 116.87],
  [21.321, 126.605],
]
const philippinesCenter = [12.8797, 121.774]

const L = window.L

document.addEventListener("DOMContentLoaded", () => {
  initializeMaps()
  setupEventListeners()
})

function initializeMaps() {
  predictMap = L.map("predict-map", {
    center: philippinesCenter,
    zoom: 6,
    maxBounds: philippinesBounds,
    maxBoundsViscosity: 1.0,
  })

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(predictMap)

  // Initialize dataset map
  datasetMap = L.map("dataset-map", {
    center: philippinesCenter,
    zoom: 6,
    maxBounds: philippinesBounds,
    maxBoundsViscosity: 1.0,
  })

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(datasetMap)

  // Add click handlers
  predictMap.on("click", (e) => {
    handleMapClick(e, "predict")
  })

  datasetMap.on("click", (e) => {
    handleMapClick(e, "dataset")
  })
}

function handleMapClick(e, type) {
  const lat = e.latlng.lat
  const lng = e.latlng.lng

  if (lat >= 4.2158 && lat <= 21.321 && lng >= 116.87 && lng <= 126.605) {
    const roundedLat = lat.toFixed(6)
    const roundedLng = lng.toFixed(6)

    if (type === "predict") {
      if (predictMarker) {
        predictMarker.setLatLng(e.latlng)
      } else {
        predictMarker = L.marker(e.latlng).addTo(predictMap)
      }
      document.getElementById("predict-lat").textContent = roundedLat
      document.getElementById("predict-lng").textContent = roundedLng
      document.getElementById("predict-latitude").value = roundedLat
      document.getElementById("predict-longitude").value = roundedLng
    } else {
      if (datasetMarker) {
        datasetMarker.setLatLng(e.latlng)
      } else {
        datasetMarker = L.marker(e.latlng).addTo(datasetMap)
      }
      document.getElementById("dataset-lat").textContent = roundedLat
      document.getElementById("dataset-lng").textContent = roundedLng
      document.getElementById("dataset-latitude").value = roundedLat
      document.getElementById("dataset-longitude").value = roundedLng
    }
  } else {
    alert("⚠️ Please click only within the Philippines.")
  }
}

function setupEventListeners() {
  // Tab switching
  window.openTab = (evt, tabName) => {
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

    // Resize maps when tab is switched
    setTimeout(() => {
      if (tabName === "predict-tab") {
        predictMap.invalidateSize()
      } else {
        datasetMap.invalidateSize()
      }
    }, 100)
  }

  // Category change handlers
  document.getElementById("predict-category").addEventListener("change", function () {
    loadCommodities(this.value, "predict-commodity")
  })

  document.getElementById("dataset-category").addEventListener("change", function () {
    loadCommodities(this.value, "dataset-commodity")
  })

  // Form submissions
  document.getElementById("predict-form").addEventListener("submit", handlePredictSubmit)
  document.getElementById("dataset-form").addEventListener("submit", handleDatasetSubmit)
}

function loadCommodities(category, selectId) {
  const select = document.getElementById(selectId)
  select.innerHTML = '<option value="">Loading...</option>'

  if (!category) {
    select.innerHTML = '<option value="">Select Category First</option>'
    return
  }

  fetch(`/get_commodities/${category}`)
    .then((response) => response.json())
    .then((commodities) => {
      select.innerHTML = '<option value="">Select Commodity</option>'
      commodities.forEach((commodity) => {
        const option = document.createElement("option")
        option.value = commodity
        option.textContent = commodity
        select.appendChild(option)
      })
    })
    .catch((error) => {
      console.error("Error loading commodities:", error)
      select.innerHTML = '<option value="">Error loading commodities</option>'
    })
}

function handlePredictSubmit(e) {
  e.preventDefault()

  const formData = new FormData(e.target)
  const submitButton = e.target.querySelector('button[type="submit"]')

  if (!formData.get("latitude") || !formData.get("longitude")) {
    alert("Please select a location on the map first.")
    return
  }

  submitButton.disabled = true
  submitButton.textContent = "Predicting..."

  fetch("/predict_price", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        document.getElementById("result-commodity").textContent = data.commodity
        document.getElementById("result-pricetype").textContent = data.pricetype
        document.getElementById("result-location").textContent = data.location
        document.getElementById("result-price").textContent = data.predicted_price.toFixed(2)
        document.getElementById("prediction-result").style.display = "block"
      } else {
        alert("Prediction failed. Please try again.")
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      alert("An error occurred. Please try again.")
    })
    .finally(() => {
      submitButton.disabled = false
      submitButton.textContent = "Predict Price"
    })
}

function handleDatasetSubmit(e) {
  e.preventDefault()

  const formData = new FormData(e.target)
  const submitButton = e.target.querySelector('button[type="submit"]')

  if (!formData.get("latitude") || !formData.get("longitude")) {
    alert("Please select a location on the map first.")
    return
  }

  submitButton.disabled = true
  submitButton.textContent = "Adding..."

  fetch("/add_dataset", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      const resultDiv = document.getElementById("dataset-result")
      const messageDiv = document.getElementById("dataset-message")

      messageDiv.textContent = data.message
      messageDiv.className = data.success ? "success" : "error"
      resultDiv.style.display = "block"

      if (data.success) {
        e.target.reset()
        document.getElementById("dataset-lat").textContent = "-"
        document.getElementById("dataset-lng").textContent = "-"
        if (datasetMarker) {
          datasetMap.removeLayer(datasetMarker)
          datasetMarker = null
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      alert("An error occurred. Please try again.")
    })
    .finally(() => {
      submitButton.disabled = false
      submitButton.textContent = "Add to Dataset"
    })
}
