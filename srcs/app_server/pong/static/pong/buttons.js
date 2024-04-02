
document.getElementById("logoutBtn").addEventListener("click", logout);
document.getElementById("gameBtn").addEventListener("click", loadGame);
document.getElementById("profileBtn").addEventListener("click", loadProfile);


function logout() {
    console.log("coucou");
    fetch("{% url 'userManagement:logout' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken") 
        }
    })
    .then(response => {
        if (response.ok) {
            // If logout is successful, redirect the user to the landing page
            loadNonAuthenticatedContent();
        } else {
            // Handle logout error
            console.error("Logout failed");
        }
    })
    .catch(error => console.error('Error:', error));
}

function loadGame() {
    fetch("/game")
    .then(response => response.text())
    .then(html => {
        // Insert the content of game.html into your app's container
        document.getElementById("content").innerHTML = html;
    })
    .catch(error => console.error('Error loading game page:', error));
    }

function loadProfile() {
    fetch("{% url 'userManagement:profile' user.username %}")
    .then(response => response.text())
    .then(html => {
        // Insert the content of game.html into your app's container
        document.getElementById("content").innerHTML = html;
    })
    .catch(error => console.error('Error loading profile page:', error));
    }


// Function to retrieve CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
    }
    return cookieValue;
}
