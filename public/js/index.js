document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Get the email and password input values
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            window.location.href = "../views/main.html"; // Redirect to main.html on success 
        });
    }
});

