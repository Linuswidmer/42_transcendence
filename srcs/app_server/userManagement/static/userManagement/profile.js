import { getCookie, router } from "./main.js";

class Profile extends HTMLElement {
    constructor() {
        super();
		//console.log("constructor profile custom element");

		let username = this.getAttribute('data-username');
		let allProfilesUrl = this.getAttribute('data-allProfilesUrl');
		let updateProfileUrl = this.getAttribute('data-updateProfileUrl');
		let updateUserUrl = this.getAttribute('data-updateUserUrl');
		let changePasswordUrl = this.getAttribute('data-changePasswordUrl');
		let followUrl = this.getAttribute('data-followUrl');


		let allProfilesBtn = document.getElementById("allProfilesBtn");
		if (allProfilesBtn) {
			allProfilesBtn.addEventListener("click", function() {
				//console.log("allProfilesBtn");
				//console.log("all profiles Url:", allProfilesUrl);
				//history.pushState("", "", allProfilesUrl);
				router(allProfilesUrl);
			});
		}

		let profilePictureBtn = document.getElementById("profilePictureBtn");
		if (profilePictureBtn) {
			profilePictureBtn.addEventListener("click", function() {
				//console.log("profilePictureBtn");
				renderForm(updateProfileUrl, "profilePicture", "Change Profile Picture");
			});
		}

		let updateProfileBtn = document.getElementById("updateProfileBtn");
		if (updateProfileBtn) {
			updateProfileBtn.addEventListener("click", function() {
				//console.log("updateProfileBtn");
				renderForm(updateUserUrl, "updateProfile", "Update Profile Info");
			});
		}

		let passwordBtn = document.getElementById("passwordBtn");
		if (passwordBtn) {
			passwordBtn.addEventListener("click", function() {
				//console.log("passwordBtn");
				renderForm(changePasswordUrl, "password", "Change Password");
			});
		}

		let followBtn = document.getElementById("followBtn");
		if (followBtn) {
			followBtn.addEventListener("click", function() {
				fetch(followUrl, {
					method: "POST",
					headers: {
						'Content-Type': 'application/x-www-form-urlencoded',
						"X-CSRFToken": getCookie("csrftoken")
					},
					body: new URLSearchParams({
						'follow': followBtn.value
					})
				})
				.then(response => {
					if (response.ok) {
						router(location.pathname, null, null, null);
					} else {
						console.error("(un)follow failed");
					}
				})
				.catch(error => console.error('Error:', error));
			});
		}


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
							enctype: "multipart/form-data",
							// Include CSRF token in the headers
							headers: {
								"X-CSRFToken": getCookie("csrftoken"),
							}
						})
						.then(response => {
							//console.log(response);
							if (!response.url.includes(url)) {
								const modal = document.getElementById(`${containerId}Modal`);
								modal.classList.remove('show');
								modal.style.display = 'none';
								if (containerId == 'profilePicture' || containerId == 'updateProfile' || containerId == 'password'){
									if (containerId == 'updateProfile') {
										username = formData.get('username');
										//console.log("new username: ", username)
									}
									reloadProfilePage(username);
								}
							} else {
                                if (response.status == 413)
                                {
                                    var extractedMessage = "The file size is too large. Please upload a file that is less than 1MB.";
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

                                }
                                else {
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
                            }
                            }})
						.catch(error => console.error('Error:', error));
						});
								} else {
									console.error("Form element not found in fetched HTML content");
								}
							})
							.catch(error => console.error('Error fetching form:', error));
						}
	
	
	
	function reloadProfilePage(username) {
	  		//console.log("reloading profile page")
			//history.pushState("", "", "/profile/" + username);
			router("/profile/" + username);
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
        var totalWinsSingle = parseInt(this.getAttribute('data-totalWins'));
        var totalLossesSingle = parseInt(this.getAttribute('data-totalDefeats'));
        
        var totalGamesSingle = totalWinsSingle + totalLossesSingle;
        document.getElementById('winsSingleDesc').innerHTML = totalWinsSingle;
        document.getElementById('lossesSingleDesc').innerHTML = totalLossesSingle;

        document.getElementById('winsSingle').style.height = (totalWinsSingle / totalGamesSingle * 100) + '%';
        document.getElementById('lossesSingle').style.height = (totalLossesSingle / totalGamesSingle * 100) + '%';

        //console.log(this.getAttribute('data-totalTournaments'));

        var totalWinsTournament = parseInt(this.getAttribute('data-wonTournaments'));
        var totalLossesTournament = this.getAttribute('data-totalTournaments') - totalWinsTournament;
        
        //console.log("totalWinsTournament: ", totalWinsTournament);
        //console.log("totalLossesTournament: ", totalLossesTournament);

        var totalGamesTournament = totalWinsTournament + totalLossesTournament;
        document.getElementById('winsTournamentDesc').innerHTML = totalWinsTournament;
        document.getElementById('lossesTournamentDesc').innerHTML = totalLossesTournament;

        document.getElementById('winsTournament').style.height = (totalWinsTournament / totalGamesTournament * 100) + '%';
        document.getElementById('lossesTournament').style.height = (totalLossesTournament / totalGamesTournament * 100) + '%';

	
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
			//console.log("localGames");
			setTableData(localAveragePointsPerGame, localBestGameScore, localHighestWinningStreak, localLongestBallRally);
		});
	
		document.getElementById('remoteGamesButton').addEventListener('click', function() {
			//console.log("remoteGames");
			setTableData(remoteAveragePointsPerGame, remoteBestGameScore, remoteHighestWinningStreak, remoteLongestBallRally);
		});
	
		document.getElementById('aiGamesButton').addEventListener('click', function() {
			//console.log("aiGames");
			setTableData(aiAveragePointsPerGame, aiBestGameScore, aiHighestWinningStreak, aiLongestBallRally);
		});

        document.getElementById("expand-btn").addEventListener("click", function() {
            var hiddenRows = document.querySelectorAll(".hideSingleGame");
            //console.log("hiddenRows: ", hiddenRows);
            hiddenRows.forEach(function(row) {
                row.style.display = "table-row";
            });
            document.getElementById("expand-btn").style.display = "none";
        });
    }
}



customElements.define("pong-profile", Profile);
