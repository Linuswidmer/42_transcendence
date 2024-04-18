document.addEventListener("DOMContentLoaded", function() {
    if (isAuthenticated) {
        loadLoggedInContent();
    } else {
        loadNonAuthenticatedContent();
    }

    // Define functions to load content for logged-in and non-authenticated users
    function loadLoggedInContent() {
        // Fetch and render content for logged-in users
        // Example:
        fetch("/api/content/logged_in")
            .then(response => response.text())
            .then(html => {
                document.getElementById('content').innerHTML = html;
                // Add event listeners for logged-in user content
                // Example:
                document.getElementById("logoutBtn").addEventListener("click", function() {
                    logout();
                });
            })
            .catch(error => console.error('Error loading logged-in content:', error));
    }

    function loadNonAuthenticatedContent() {
        // Fetch and render content for non-authenticated users
        // Example:
        fetch("/api/content/stranger")
            .then(response => response.text())
            .then(html => {
                document.getElementById('content').innerHTML = html;
                // Add event listeners for non-authenticated user content
                // Example:
                document.getElementById("loginBtn").addEventListener("click", function() {
                    // Logic for showing login modal or form
                });
            })
            .catch(error => console.error('Error loading non-authenticated content:', error));
    }

    // Function to handle logout
    function logout() {
        // Logic for logout
    }
});
