document.addEventListener('DOMContentLoaded', function() {
    var registerButtons = document.querySelectorAll('.register');
    registerButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            console.log("register clicked");
            var match_id = this.getAttribute('data-match-id');
            fetch('/register_player/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your CSRF token here
                },
                body: JSON.stringify({match_id: match_id})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    // Display error message
                    alert(data.error_message);
                } else {
                    // Handle success
                    alert("registered successfully");
                }
            });
        });
    });

    var joinButtons = document.querySelectorAll('.join');
    joinButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var match_id = this.getAttribute('data-match-id');
            fetch('/join/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your CSRF token here
                },
                body: JSON.stringify({match_id: match_id})
            })
            .then(response => response.json())
            .then(data => {
                // Handle response
            });
        });
    });
});
