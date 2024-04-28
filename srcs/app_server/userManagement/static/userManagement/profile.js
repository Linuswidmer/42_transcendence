import { getCookie, router } from "./main.js";

class Profile extends HTMLElement {
    constructor() {
        super();
		console.log("constructor profile custom element");

		let allProfilesUrl = this.getAttribute('data-allProfilesUrl');


		document.getElementById("allProfilesBtn").addEventListener("click", function() {
			console.log("allProfilesBtn");
			console.log("all profiles Url:", allProfilesUrl);
			history.pushState("", "", allProfilesUrl);
			router();
		});
		document.getElementById("profilePictureBtn").addEventListener("click", function() {
			console.log("profilePictureBtn");
			renderForm("{% url 'userManagement:update_profile' %}", "profilePicture", "Change Profile Picture");
		});
		document.getElementById("updateProfileBtn").addEventListener("click", function() {
			console.log("updateProfileBtn");
			renderForm("{% url 'userManagement:update_user' %}", "updateProfile", "Update Profile Info");
		});
		document.getElementById("passwordBtn").addEventListener("click", function() {
			console.log("passwordBtn");
			renderForm("{% url 'userManagement:change_password' %}", "password", "Change Password");
		});
		function renderForm(url, containerId, title) {
		console.log("triggered")
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
							enctype: "multipart/form-data",
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
								if (containerId == 'profilePicture' || containerId == 'updateProfile'){
									reloadProfilePage();
								}
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
	
	
	
	function reloadProfilePage() {
	  		console.log("reloading profile page")
			history.pushState("", "", "/profile/");
			router();
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
	const csrftoken = getCookie('csrftoken');
		// this will only work while the js is not a separate file
		var chartElement = document.getElementById('winLossChart');
		if (chartElement !== null)
		{
			var ctx = chartElement  .getContext('2d');
			var chart = new Chart(ctx, {
				type: 'pie',
				data: {
					labels: ['Wins', 'Losses'],
					datasets: [{
						data: [this.getAttribute('data-totalWins'), this.getAttribute('data-totalDefeats')],
						backgroundColor: ['green', 'red'],
					}] // workaround would be reading the data from the html element
				},
				options: {
					responsive: true,
					plugins: {
						title: {
							display: true,
							text: 'Games Win/Loss Ratio'
						}
					}
				}
			});
		}
	
		var chartElement2 = document.getElementById('winLossChartTournament');
		if (chartElement2 !== null)
		{
			var ctx2 = chartElement2.getContext('2d');
			var chart2 = new Chart(ctx2, {
				type: 'pie',
				data: {
					labels: ['Wins', 'Losses'],
					datasets: [{
						data: [this.getAttribute('data-wonTournaments'), this.getAttribute('data-totalTournaments')],
						backgroundColor: ['green', 'red'],
					}]
				},
				options: {
					responsive: true,
					plugins: {
						title: {
							display: true,
							text: 'Tournaments Win/Loss Ratio'
						}
					}
				}
			});
		}
	
		var localAveragePointsPerGame = this.getAttribute('data-localAveragePointsPerGame');
		var localBestGameScore = this.getAttribute('data-localBestGameScore');
		var localHighestWinningStreak = this.getAttribute('data-localHighestWinningStreak');
		var localLongestBallRally = this.getAttribute('data-localLongestBallRally');

		var remoteAveragePointsPerGame = this.getAttribute('data-remoteAveragePointsPerGame');
		var remoteBestGameScore = this.getAttribute('data-remoteBestGameScore');
		var remoteHighestWinningStreak = this.getAttribute('data-remoteHighestWinningStreak');
		var remoteLongestBallRally = this.getAttribute('data-remoteLongestBallRally');

		var aiAveragePointsPerGame = this.getAttribute('data-aiAveragePointsPerGame');
		var aiBestGameScore = this.getAttribute('data-aiBestGameScore');
		var aiHighestWinningStreak = this.getAttribute('data-aiHighestWinningStreak');
		var aiLongestBallRally = this.getAttribute('data-aiLongestBallRally');

		function setTableData(averagePointsPerGame, bestGameScore, highestWinningStreak, longestBallRally) {
			// Get the table body
			var tbody = document.getElementById('gameStats');
	
			// Get all the td elements in the tbody
			var tds = tbody.getElementsByTagName('td');
	
			// Set the content of the td elements
			tds[0].textContent = averagePointsPerGame;
			tds[1].textContent = bestGameScore;
			tds[2].textContent = highestWinningStreak;
			tds[3].textContent = longestBallRally;
		}
	
		setTableData(localAveragePointsPerGame, localBestGameScore, localHighestWinningStreak, localLongestBallRally);
	
		document.getElementById('localGamesButton').addEventListener('click', function() {
			console.log("localGames");
			setTableData(localAveragePointsPerGame, localBestGameScore, localHighestWinningStreak, localLongestBallRally);
		});
	
		document.getElementById('remoteGamesButton').addEventListener('click', function() {
			console.log("remoteGames");
			setTableData(remoteAveragePointsPerGame, remoteBestGameScore, remoteHighestWinningStreak, remoteLongestBallRally);
		});
	
		document.getElementById('aiGamesButton').addEventListener('click', function() {
			console.log("aiGames");
			setTableData(aiAveragePointsPerGame, aiBestGameScore, aiHighestWinningStreak, aiLongestBallRally);
		});
    }
}



customElements.define("pong-profile", Profile);
