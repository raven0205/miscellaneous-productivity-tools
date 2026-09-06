document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-file-input]").forEach((input) => {
    input.addEventListener("change", () => {
      const target = document.querySelector(input.dataset.fileInput);
      if (target) target.textContent = `${input.files.length} file${input.files.length === 1 ? "" : "s"} selected`;
    });
  });

  document.querySelectorAll("[data-filter-projects]").forEach((input) => {
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      document.querySelectorAll("[data-project-card]").forEach((card) => {
        card.hidden = query && !card.dataset.projectCard.includes(query);
      });
    });
  });
});
