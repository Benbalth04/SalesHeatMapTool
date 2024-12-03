document.addEventListener("DOMContentLoaded", function () {
    // Fetch and insert sidebar HTML
    fetch('/partial-views/settings-sidebar.html')
        .then((response) => response.text())
        .then((data) => {
            document.getElementById('sidebar-placeholder').innerHTML = data;

            // Sidebar toggle functionality
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            const settingsIcon = document.getElementById('settings-icon');

            settingsIcon.addEventListener('click', function () {
                sidebar.classList.add('active');
                overlay.style.display = 'block';
            });

            overlay.addEventListener('click', function () {
                sidebar.classList.remove('active');
                overlay.style.display = 'none';
            });
        })
        .catch((error) => console.error('Error loading sidebar:', error));
});
