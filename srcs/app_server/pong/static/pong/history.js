function loadContent(url) {
    fetch(url)
    .then(response => response.text())
    .then(html => {
        document.getElementById("content").innerHTML = html;
        executeJavaScriptInContent(html);
    })
    .catch(error => console.error('Error loading content:', error));
}
// Handle back/forward button clicks
window.onpopstate = function(event) {
    const url = location.pathname;
    loadContent(url);
};

function executeJavaScriptInContent(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const scriptElements = doc.querySelectorAll('script');
    scriptElements.forEach(script => {
    const scriptContent = script.textContent.trim();
        if (scriptContent) {
            // Create a new script element and set its content to execute
            const newScript = document.createElement('script');
            newScript.textContent = scriptContent;
            // Append the script to the document head to execute it
            document.head.appendChild(newScript);
        }
    });
}
if (typeof csrftoken === 'undefined' || csrftoken === null) {
    csrftoken = getCookie('csrftoken');
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

function extractErrorMessage(errorMessage) {
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = '';
    tempDiv.innerHTML = errorMessage;
    var errorList = tempDiv.querySelector('.errorlist');
    if (errorList) {
        var errorMessageText = errorList.querySelector('li').textContent;
        return errorMessageText;
    } else {
        return null;
    }
}

function renderForm(url, containerId, title) {
    fetch(url, {
    // Include CSRF token in the headers if includeCSRF is true
    headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
})
    .then(response => response.text())
    .then(html => {
    // Create a modal using the fetched HTML content
    const modalHtml = `
        <div class="modal fade" id="${containerId}Modal" tabindex="-1" role="dialog" aria-labelledby="${containerId}ModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-scrollable" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${containerId}ModalLabel">${title}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body text-center">
                        ${html} <!-- Render the fetched form here -->
                    </div>
                </div>
            </div>
        </div>
    `;
    // Add the modal HTML to the container
    document.getElementById("modalContainer").innerHTML = modalHtml;
    const modal = document.getElementById(`${containerId}Modal`);
    modal.classList.add('show');
    modal.style.display = 'block';

    // Add event listener to close modal when clicking on the cross (close button)
    const closeButton = modal.querySelector('.close');
    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    const form = modal.querySelector("form");
    if (form) {
        form.id = `${containerId}Form`;
        form.addEventListener("submit", function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            fetch(url, {
                method: "POST",
                body: formData,
                enctype: "multipart/form-data",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                }
            })
            .then(response => {
                if (!response.url.includes(url)) {
                    const modal = document.getElementById(`${containerId}Modal`);
                    modal.classList.remove('show');
                    modal.style.display = 'none';
                    if(containerId == 'loginModal' || containerId == 'registerModal' || containerId == 'guestModal')
                        loadLoggedInContent();
                    if (containerId == 'profilePicture' || containerId == 'updateProfile'){
                        fetch(response.url)
                        .then(response => response.text())
                        .then(html => {
                            document.getElementById("content").innerHTML = html;
                            executeJavaScriptInContent(html);
                        })
                        .catch(error => console.error('Error loading logged-in content:', error));
                    }
                } else {
                    response.text().then(errorMessage => {
                    var extractedMessage = extractErrorMessage(errorMessage);
                    const modal = document.getElementById(`${containerId}Modal`);
                    const errorContainerOld = document.querySelector(".alert-danger");
                    if (!errorContainerOld){
                        const errorContainer = document.createElement("div");
                        errorContainer.classList.add("alert", "alert-danger");
                        errorContainer.textContent = extractedMessage;
                        modal.querySelector(".modal-body").appendChild(errorContainer);
                    } else {
                        errorContainerOld.textContent = extractedMessage;
                    }
                });
            }})
            .catch(error => console.error('Error:', error));
        });
    }
    })
    .catch(error => console.error('Error fetching form:', error));
}
