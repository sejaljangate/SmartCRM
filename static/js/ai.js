document.addEventListener("DOMContentLoaded", function () {
  const box = document.getElementById("aiAssistant");
  if (!box) return;

  const output = document.getElementById("aiOutput");
  const emailBtn = document.getElementById("aiEmailBtn");
  const summaryBtn = document.getElementById("aiSummaryBtn");
  const buttons = [emailBtn, summaryBtn];

  async function run(btn, url) {
    const original = btn.innerHTML;
    buttons.forEach(function (b) { b.disabled = true; });
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
    output.classList.remove("d-none", "ai-output-error");
    output.textContent = "";

    try {
      const response = await fetch(url, { method: "POST" });
      const data = await response.json();
      if (data.ok) {
        output.textContent = data.text;
      } else {
        output.textContent = data.error;
        output.classList.add("ai-output-error");
      }
    } catch (e) {
      output.textContent = "Couldn't reach the server. Please try again.";
      output.classList.add("ai-output-error");
    } finally {
      buttons.forEach(function (b) { b.disabled = false; });
      btn.innerHTML = original;
    }
  }

  emailBtn.addEventListener("click", function () { run(emailBtn, box.dataset.emailUrl); });
  summaryBtn.addEventListener("click", function () { run(summaryBtn, box.dataset.summaryUrl); });
});
