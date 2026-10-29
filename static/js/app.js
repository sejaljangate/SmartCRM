document.addEventListener("DOMContentLoaded", function () {
  // Sidebar toggle (mobile)
  const toggleBtn = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  // Auto-show any server-rendered toasts (from flash messages)
  const toastElements = document.querySelectorAll("#toastContainer .toast");
  toastElements.forEach(function (el) {
    const toast = new bootstrap.Toast(el);
    toast.show();
  });
});