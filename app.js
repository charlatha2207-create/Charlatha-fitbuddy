document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form").forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector("button[type='submit']");
            if (!button || form.dataset.noLoading === "true") return;
            button.disabled = true;
            button.textContent = "Working…";
        });
    });
});
