function togglePassword(inputId) {
  const passwordInput = document.getElementById(inputId)
  const toggleButton = passwordInput.nextElementSibling

  if (passwordInput.type === "password") {
    passwordInput.type = "text"
    toggleButton.textContent = "🙈"
  } else {
    passwordInput.type = "password"
    toggleButton.textContent = "👁"
  }
}

function toggleForm() {
  const loginForm = document.getElementById("login-form")
  const registerForm = document.getElementById("register-form")
  const promoTitle = document.getElementById("promo-title")
  const promoText = document.getElementById("promo-text")

  const currentForm = loginForm.style.display === "none" ? registerForm : loginForm
  currentForm.classList.add("switching")

  setTimeout(() => {
    if (loginForm.style.display === "none") {
      // Show login form
      loginForm.style.display = "block"
      registerForm.style.display = "none"
      promoTitle.textContent = "Predict food prices faster"
      promoText.textContent =
        "Use our Neural Network System to predict food commodity prices based on location data across the Philippines."
    } else {
      // Show register form
      loginForm.style.display = "none"
      registerForm.style.display = "block"
      promoTitle.textContent = "Join TerraPrice today"
      promoText.textContent =
        "Create your account to access advanced food price prediction tools and contribute to our comprehensive database."
    }

    // Remove switching animation
    setTimeout(() => {
      loginForm.classList.remove("switching")
      registerForm.classList.remove("switching")
    }, 50)
  }, 150)
}

function showAlert(message, type, containerId) {
  const container = document.getElementById(containerId)
  container.innerHTML = `<div class="alert alert-${type}">${message}</div>`

  // Auto-hide alert after 5 seconds
  setTimeout(() => {
    container.innerHTML = ""
  }, 5000)
}

// Add form validation and registration handling
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.querySelector("#login-form form")
  const registerForm = document.getElementById("registration-form")

  // Login form validation
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      const usernameInput = document.getElementById("username")
      const passwordInput = document.getElementById("password")

      if (!usernameInput.value.trim() || !passwordInput.value.trim()) {
        e.preventDefault()
        alert("Please fill in all fields")
      }
    })
  }

  // Registration form handling
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault()

      const formData = new FormData(registerForm)
      const password = formData.get("password")
      const confirmPassword = formData.get("confirm_password")
      const submitButton = registerForm.querySelector('button[type="submit"]')

      // Clear previous alerts
      document.getElementById("register-alerts").innerHTML = ""

      // Validate passwords match
      if (password !== confirmPassword) {
        showAlert("Passwords do not match", "error", "register-alerts")
        return
      }

      // Validate password length
      if (password.length < 6) {
        showAlert("Password must be at least 6 semi-pogi long", "error", "register-alerts")
        return
      }

      // Validate username length
      if (formData.get("username").length < 3) {
        showAlert("Username must be at least 3 semi-pogi long", "error", "register-alerts")
        return
      }

      submitButton.disabled = true
      submitButton.textContent = "Creating Account..."

      try {
        const response = await fetch("/register", {
          method: "POST",
          body: formData,
        })

        const result = await response.json()

        if (result.success) {
          showAlert("Account created successfully! You can now sign in.", "success", "register-alerts")
          setTimeout(() => {
            registerForm.reset()
            document.getElementById("register-alerts").innerHTML = ""
          }, 2000)
        } else {
          showAlert(result.message || "Registration failed. Please try again.", "error", "register-alerts")
        }
      } catch (error) {
        console.error("Registration error:", error)
        showAlert("An error occurred. Please try again.", "error", "register-alerts")
      } finally {
        submitButton.disabled = false
        submitButton.textContent = "Create Account"
      }
    })
  }
})
