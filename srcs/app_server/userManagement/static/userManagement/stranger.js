import {router, getCookie} from "./main.js"

class Stranger extends HTMLElement {
    constructor() {
        super();

        this.innerHTML = /*html*/`
			<div class="button-container">
				<!-- Content for non-authenticated users -->
				<button type="button" class="button" id="loginBtn">Login</button>
				<button type="button" class="button" id="registerBtn">Register</button>
				<button type="button" class="button" id="guestBtn">Continue as Guest</button>

			</div>

			<div id="modalContainer"></div>
        `;

		let loginBtn = this.querySelector("#loginBtn");
		let registerBtn = this.querySelector("#registerBtn");
		let guestBtn = this.querySelector("#guestBtn");
		// let _42Btn = doc.querySelector("#fortyTwoBtn");

		this.loginUrl = this.getAttribute("data-loginUrl");
		this.registerUrl = this.getAttribute("data-registerUrl");
		this.guestUrl = this.getAttribute("data-guestUrl");
		this.remoteAuthUrl = this.getAttribute("data-remoteAuthUrl");

		// State
		loginBtn.onclick = () => {
			//console.log("loginbtn");
			renderForm(this.loginUrl, "loginModal", "Login");
		};

		registerBtn.onclick = () => {
			//console.log("registerbtn");
			renderForm(this.registerUrl, "registerModal", "Register");
		};

		guestBtn.onclick = () => {
			//console.log("guestbtn");
			renderForm(this.guestUrl, "guestModal", "Continue as guest");
		};

		// _42Btn.onclick = () => {
		// 	//console.log("42btn");
		// 	window.location.href=this.remoteAuthUrl;
		// };


    }
}

customElements.define("pong-stranger", Stranger);

function renderForm(url, containerId, title) {
    //console.log("triggered")
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
						<div class="modal-dialog" role="document">
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
			// Show the modal
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

			// Find the form element within the modal
			const form = modal.querySelector("form");
            // Check if the form element was found
            if (form) {
                // Add the desired ID to the form element
                form.id = `${containerId}Form`;
                // Add event listener for form submission
                form.addEventListener("submit", function(event) {
                    event.preventDefault(); // Prevent default form submission
                    // Create FormData object using the form element
                    const formData = new FormData(form);
                    // Send POST request to register user
                    //console.log(url)
                    fetch(url, {
                        method: "POST",
                        body: formData,
                        // Include CSRF token in the headers
                        headers: {
                            "X-CSRFToken": getCookie("csrftoken"),
                        }
                    })
                    .then(response => {
                       // console.log(response);
                        if (!response.url.includes(url)) {
                            const modal = document.getElementById(`${containerId}Modal`);
                            modal.classList.remove('show');
                            modal.style.display = 'none';
							if(containerId == 'loginModal' || containerId == 'registerModal' || containerId == 'guestModal')
							loadLoggedInContent();
						} else {
							// Login failed
							// Display error message
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
                            } else {
                                console.error("Form element not found in fetched HTML content");
                            }
                        })
                        .catch(error => console.error('Error fetching form:', error));
}

const csrftoken = getCookie('csrftoken');
 // Function to load logged-in content after successful login
function loadLoggedInContent() {
	//history.pushState("", "", "/");
	router("/");
}

function extractErrorMessage(errorMessage) {
    // Create a temporary div element to hold the HTML
    var tempDiv = document.createElement('div');
    // Set the inner HTML of the temporary div to the provided errorMessage
    tempDiv.innerHTML = errorMessage;
    // Find the error message element
    var errorList = tempDiv.querySelector('.errorlist');
    // Check if the error message element exists
    if (errorList) {
        // Find the error message within the error list
        var errorMessageText = errorList.querySelector('li').textContent;
        // Return the error message
        return errorMessageText;
    } else {
        // Return null if no error message is found
        return null;
    }
}
