document.addEventListener("DOMContentLoaded", function () {
  // Password show/hide toggle
  document.querySelectorAll(".auth-password-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const input = document.getElementById(btn.dataset.target);
      const icon = btn.querySelector("i");
      if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
      } else {
        input.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
      }
    });
  });

  // Loading state on submit (prevents double-submit too)
  const authForm = document.getElementById("authForm");
  if (authForm) {
    authForm.addEventListener("submit", function () {
      const submitBtn = authForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + submitBtn.dataset.loadingText;
      }
    });
  }
});