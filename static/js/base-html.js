document.addEventListener("DOMContentLoaded", function () {
    // --- Настройки: открытие/закрытие ---
    const settingsToggle = document.getElementById("settingsToggle");
    const settingsDropdown = document.getElementById("settingsDropdown");
    settingsToggle.addEventListener("click", e => {
        e.preventDefault();
        settingsDropdown.style.display = settingsDropdown.style.display === "block" ? "none" : "block";
    });
    document.addEventListener("click", e => {
        if (!settingsToggle.contains(e.target) && !settingsDropdown.contains(e.target)) {
            settingsDropdown.style.display = "none";
        }
    });

    // --- Сайдбар мобильный ---
    const toggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    toggle.addEventListener("click", () => sidebar.classList.toggle("active"));

    // --- Подсветка активной ссылки ---
    const currentUrl = window.location.pathname;
    document.querySelectorAll('.sidebar a').forEach(link => {
        if (link.getAttribute('href') === currentUrl) link.parentElement.classList.add('active');
    });

});
