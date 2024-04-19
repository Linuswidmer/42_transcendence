var navbarWrapper = (function() {
	// let navbarDIV = document.getElementById('navbarDIV');
	
	// navbarDIV.addEventListener('click', function(event) {
		
		// });
		let lobbyButton = document.getElementById('lobbyBtn');
		lobbyButton.addEventListener('click', () => {
			showSection('/lobby');
		});
		
		const data = document.currentScript.dataset;
		const profileURL = data.profile;
		console.log("profile URL: ", profileURL);
		
		
		let profileButton = document.getElementById('profileBtn');
		profileButton.addEventListener('click', () => {
			showSection(profileURL);
		});
		
		
		const logoutURL = data.logout;
		console.log("logout URL: ", logoutURL);
		let logoutButton = document.getElementById('logoutBtn');
		logoutButton.addEventListener('click', () => {
			fetch(logoutURL, {
				method: "POST",
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				}
			})
			.then(response => {
				if (response.ok) {
					window.location.href = window.location.origin;
				} else {
					console.error("Logout failed");
				}
			})
			.catch(error => console.error('Error:', error));
		});
		
})();
		
		// document.querySelector('.navbar').addEventListener('click', function(event) {
// 	const target = event.target;
// 	if (target.matches('.navbar-button')) {
	// 		event.preventDefault();
	// 		console.log(target.textContent + ' button clicked');
	// 		switch (target.id) {
		// 			case 'gameBtn':
		// 				// var lobby = document.querySelector(".lobby")
		// 				// if (lobby) {
			// 				//     lobby.style.display = (lobby.style.display === "none") ? "block" : "none";
			// 				// }
			// 				document.getElementById("content").innerHTML = '';
			// 				// fetch("/lobby")
			// 				//     .then(response => response.text())
			// 				//     .then(html => {
				// 				//         document.getElementById("content").innerHTML = html;
				// 				//         executeJavaScriptInContent(html);
				// 				//         })
				// 				//     .catch(error => console.error('Error loading game page:', error));
				// 				showSection('/lobby');
				// 				break;
				// 			case 'profileBtn':
				// 				fetch("{% url 'userManagement:profile' %}")
// 					.then(response => response.text())
// 					.then(html => {
// 						document.getElementById("content").innerHTML = html;
// 						executeJavaScriptInContent(html);
// 					  })
// 					.catch(error => console.error('Error loading profile page:', error));
// 				break;
// 			case 'logoutBtn':
// 				console.log('Logout button clicked');
// 				fetch("{% url 'userManagement:logout' %}", {
	// 						method: "POST",
	// 						headers: {
		// 							"X-CSRFToken": getCookie("csrftoken")
		// 						}
		// 					})
		// 					.then(response => {
			// 						if (response.ok) {
				// 							document.getElementById("content").innerHTML = '';
				// 							fetch("/stranger")
				// 								.then(response => response.text())
				// 								.then(html => {
					// 									document.getElementById("content").innerHTML = html;
					// 									executeJavaScriptInContent(html);
					// 								  })
					// 								.catch(error => console.error('Error loading content:', error));
					// 						} else {
						// 							console.error("Logout failed");
						// 						}
						// 					})
						// 					.catch(error => console.error('Error:', error));
						// 				break;
						// 		}
						// 	}
						// }); 