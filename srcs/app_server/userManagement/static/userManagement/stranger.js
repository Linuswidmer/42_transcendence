var strangerWrapper = (function() {
	
	const data = document.currentScript.dataset;
	const loginURL = data.login;
	const registerURL = data.register;
	const registerGuestURL = data.registerguest;
	console.log("login URL: ", loginURL);
	console.log("register URL: ", registerURL);
	console.log("register guest URL: ", registerGuestURL);
	
	
	// Event listeners for each button
	document.getElementById("loginBtn").addEventListener("click", function() {
		console.log("loginbtn");
		renderForm(loginURL, "loginModal", "Login");
	});
	document.getElementById("registerBtn").addEventListener("click", function() {
		console.log("registerbtn");
		renderForm(registerURL, "registerModal", "Register");
	});
	document.getElementById("guestBtn").addEventListener("click", function() {
		console.log("guestbtn");
		renderForm(registerGuestURL, "guestModal", "Continue as guest");
	});
	document.getElementById("42Btn").addEventListener("click", function() {
		console.log("42btn");
	});
	
	// Function to fetch and render forms
	function renderForm(url, containerId, title) {
		console.log("triggered wirh url:", url);
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
				console.log(url)
				fetch(url, {
					method: "POST",
					body: formData,
					// Include CSRF token in the headers
					headers: {
						"X-CSRFToken": getCookie("csrftoken"),
					}
				})
				.then(response => {
					console.log(response);
					if (!response.url.includes(url)) {
						const modal = document.getElementById(`${containerId}Modal`);
						modal.classList.remove('show');
						modal.style.display = 'none';
						loadLoggedInContent();
					} else {
						// Login failed
						// Display error message
						response.text().then(errorMessage => {
							var extractedMessage = extractErrorMessage(errorMessage);
							const modal = document.getElementById(`${containerId}Modal`);
							const errorContainer = document.createElement("div");
							errorContainer.classList.add("alert", "alert-danger");
							errorContainer.textContent = extractedMessage;
							modal.querySelector(".modal-body").appendChild(errorContainer);
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
	console.log("loading")
	showSection('');
}

// Function to extract the error message from the provided HTML
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
})();