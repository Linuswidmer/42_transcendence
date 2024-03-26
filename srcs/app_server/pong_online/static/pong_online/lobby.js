// function setupButtons() {
// 	//////////////////////// REGISTER BUTTON ///////////////////////
//     let registerButton = document.querySelector('.register');
//     registerButton.addEventListener('click', function() {
//         // Your code here
//         console.log("Register button clicked");
//     });

// 	//////////////////////// JOIN BUTTON /////////////////////////
// 	var joinButtons = document.querySelectorAll('.join');
//     joinButtons.forEach(function(button) {
//         button.addEventListener('click', function() {
//             var match_id = this.getAttribute('data-match-id');
//             fetch('/join/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     // Add your CSRF token here
//                 },
//                 body: JSON.stringify({match_id: match_id})
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'error') {
//                     // Display error message
//                     alert(data.error_message);
//                 } else {
//                     // Handle success
                    
//                 }
//             });
//         });
//     });
// }

// document.addEventListener('DOMContentLoaded', (event) => {
//     let registerButtons = document.querySelectorAll('.register');
//     registerButtons.forEach((button) => {
//         button.addEventListener('click', function() {
//             let match_id = this.getAttribute('data-match-id');
//             console.log("Register button clicked for match id: ", match_id);
//             // Your code here...
//         });
//     });

//     let joinButtons = document.querySelectorAll('.join');
//     joinButtons.forEach((button) => {
//         button.addEventListener('click', function() {
//             let match_id = this.getAttribute('data-match-id');
//             console.log("Join button clicked for match id: ", match_id);
//             // Your code here...
//         });
//     });
// });


const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
window.ws = new WebSocket(
	protocol + '://' + window.location.host + '/ws/pong_online/game/'
);



ws.onopen = function(e) {
	// telling the server that the client is ready
	console.log('WebSocket connection established');
	// let data = {'playerId': 'SESSION ID HERE?????'};
	// ws.send(JSON.stringify(data));
	ws.username = username
	ws.send(JSON.stringify({type: 'username', 'username': username}));
	ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
};

ws.onmessage = function(e) {
	try{
		const data = JSON.parse(e.data);
		console.log("ws.onmessage:", data);

		if (data.type === "lobby_update") {
			updateLobby(data);
		}
		if (data.type === "join") {
			fetch('/pong_online')
				.then(response => response.text())
				.then(data => {
					// Create a temporary DOM div element
					var tempDiv = document.createElement('div');

					// Set its innerHTML to the fetched HTML data
					tempDiv.innerHTML = data;
			
					// Extract the src attribute from the script tag
					var scriptSrc = tempDiv.querySelector('script').src;
			
					// Use the fetched HTML data
					document.body.innerHTML = data;
			
					// Create a new script element
					var script = document.createElement('script');
			
					// Set its src attribute to the extracted src
					script.src = scriptSrc;
			
					// Append the script element to the body of the document
					document.body.appendChild(script);
				})
				.catch((error) => {
					console.error('Error:', error);
				});
		}
		
	} catch (error) {
		console.log('Error parsing JSON:', error);
	}
};

function updateLobby(data) {
	matches_info = data.matches_info

	if ('error' in data) {
		alert(data.error);
	}
    // Clear the current lobby
	console.log("matches:", matches_info)
    var lobby = document.getElementById('lobby');
    lobby.innerHTML = '';

	// Add the "Create game" button to the lobby
	var createGameButton = document.createElement('button');
	createGameButton.innerText = 'Create Game';
	createGameButton.className = 'create';
	lobby.appendChild(createGameButton);

	createGameButton.addEventListener('click', function() {
		console.log("Create game button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create', 'username': username}));
	});
	


   // Add the new match data to the lobby
   for (var match_id in matches_info) {
	(function(id) {
		var registered_users = matches_info[id];

		var matchElement = document.createElement('div');
		matchElement.innerHTML = `
			<h2>Match ID: ${id}</h2>
			<p>Registered Users: ${registered_users.join(', ')}</p>
			<button class="register" data-match-id="${id}">Register</button>
			<button class="join" data-match-id="${id}">Join Game</button>
		`;

		lobby.appendChild(matchElement);

		// New code to add event listeners to the buttons
		let registerButton = matchElement.querySelector('.register');
		registerButton.addEventListener('click', function() {
			console.log("Register button clicked for match id: ", id);
			ws.send(JSON.stringify({type: 'lobby_update', 'action': 'register', 'match_id': id, 'username': username}));
		});

		let joinButton = matchElement.querySelector('.join');
		joinButton.addEventListener('click', function() {
			console.log("Join button clicked for match id: ", id);
			ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 'match_id': id, 'username': username}));
		});
	})(match_id);
	}
}
