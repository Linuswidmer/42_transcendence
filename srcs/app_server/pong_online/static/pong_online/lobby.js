import {router, ws} from "../userManagement/main.js"

class Lobby extends HTMLElement {
    constructor() {
        super();

		this.username = this.getAttribute('data-username');
		console.log("username lobby:", this.username);

		console.log('WS STATE: ', ws.readyState);
		if (ws.readyState == WebSocket.OPEN){
			console.log('WS was already open: send username to consumer: ', this.username);
			ws.send(JSON.stringify({type: 'username', 'username': this.username}));
			ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
		}else {
			var username = this.username; //this is necessary because i cannot use this in the onopen callback
			ws.onopen = function(event) {
				console.log('Waited for ws to open: send username to consumer after waiting: ', username);
				ws.send(JSON.stringify({type: 'username', 'username': username}));
				ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
			}
		}

        this.innerHTML = /*html*/`
			<div>
				<button class="btn buttonblue" id="create_game">Create remote game</button>
				<button class="btn buttonblue" id="create_tournament">Create tournament</button>
				<button class="btn buttonblue" id="play_ai">Play against Ai</button>
				<button class="btn buttonblue" id="play_local">Play local</button>
			</div>
			
			<div id="remote_game_list"></div>
			<div id="tournament_list"></div>
			<div id="modalContainer"></div>
        `;

		ws.onmessage = (e) => this.handle_message(e);

		this.create_game_button = this.querySelector('#create_game');
		this.create_game_button.addEventListener('click', 
			this.handle_create_game_button_click);
		
		this.create_tournament_button = this.querySelector('#create_tournament');
		this.create_tournament_button.addEventListener('click',
			this.handle_create_tournament_button_click);
		
		this.play_local_button = this.querySelector('#play_local');
		this.play_local_button.addEventListener('click', 
			this.handle_play_local_button_click);
		
		this.play_ai_button = this.querySelector('#play_ai');
		this.play_ai_button.addEventListener('click',
			this.handle_play_ai_button_click);
		
		this.remote_game_list_DIV = document.querySelector('#remote_game_list');
		this.tournament_list_DIV = document.querySelector('#tournament_list');

		// this.ws.onopen = (e) => this.send_initial_data_to_server(e);

    }

	handle_message(e) {
		console.log('handle message');
		try {
			const data = JSON.parse(e.data);
			console.log("data from server: ", data);
			switch (data.type) {
				case 'lobby_update':
					this.update_lobby(data);
					break;
				case 'join':
					this.join_game(data.modus);
					break;
				case 'join_tournament':
					this.join_tournament(data);
					break;
				case 'error':
					alert(data.message);
					break;
				default:
					console.log('Unknown message', data);
			}
		} catch (error) {
				console.log('Error parsing JSON:', error);
		}
	}

	handle_create_game_button_click = () => {
		console.log("Create game button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create',
		'username': this.username, 'modus': 'remote'}));
	}
	
	// handle_create_tournament_button_click = () => {
	// 	console.log("Create tournament button clicked");
	
	// 	// Create a modal container
	// 	var modal = document.createElement('div');
	// 	modal.className = 'modal';
	// 	modal.classList.add("modalContainer");
	
	// 	// Create a modal content container
	// 	var modalContent = document.createElement('div');
	// 	modalContent.className = 'modal-content';
	
	// 	// Create a heading for the modal
	// 	var heading = document.createElement('h5');
	// 	heading.innerText = 'How many players?';
	// 	heading.className = 'modal-header';
	// 	modalContent.appendChild(heading);
		
	// 	var buttonContainer = document.createElement('div');
	// 	buttonContainer.className = 'button-popup-container';
	// 	// Create buttons for different levels
	// 	for (let i = 4; i <= 16; i = i * 2) {
	// 		var levelButton = document.createElement('button');
	// 		levelButton.classList.add('levelButton');
	// 		levelButton.classList.add('buttonblue');
	// 		levelButton.classList.add('btn');
	// 		levelButton.innerText = 'Size: ' + i;
	// 		levelButton.value = i; // Set the value attribute to distinguish levels
	// 		levelButton.addEventListener('click', function() {
	// 			// Action to perform when a level button is clicked
	// 			var selectedSize = this.value;
	// 			console.log("TM Size: " + selectedSize + " selected");
	// 			// Here, you can send the selected level to the server or perform any other action
	// 			// For example, you can send it via websockets
	// 			ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create_tournament', 'username': this.username, 'tm_size': selectedSize}));
	// 			// Close the modal after selecting a level
	// 			modal.remove();
	// 		});
	// 		// Append the level button to the modal content
	// 		buttonContainer.appendChild(levelButton);
	// 	}
	// 	modalContent.appendChild(buttonContainer);
	// 	// Append the modal content to the modal container
	// 	modal.appendChild(modalContent);
	
	// 	// Append the modal to the document body
	// 	document.body.appendChild(modal);
	// }
	handle_create_tournament_button_click = () => {
		console.log("Create tournament button clicked");
	
		// Function to create modal HTML dynamically
		const createModal = (containerId, title, html) => {
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
			// Append the modal HTML to the container
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

		 // Add event listener to handle button clicks inside the modal
		 modal.querySelectorAll('.levelButton').forEach(button => {
            button.addEventListener('click', function() {
                const selectedSize = this.getAttribute('data-level');
                console.log("TM Size: " + selectedSize + " selected");
                // Send selected size to the server via WebSockets
                ws.send(JSON.stringify({
                    type: 'lobby_update',
                    action: 'create_tournament',
                    username: this.username,
                    tm_size: selectedSize
                }));
                // Close the modal after selecting a size
                modal.style.display = 'none';
            });
        });
    };
	
		// Call createModal function with desired parameters
		createModal(
			'createTournament', // Container ID
			'How many players?', // Modal title
			`<div class="button-popup-container">
				<!-- Create buttons for different levels -->
				${[4, 8, 12, 16].map(level => `
					<button class="levelButton buttonblue btn" data-level="${level}">Size: ${level}</button>
				`).join('')}
			</div>`
		);
	}
	
	
	handle_play_local_button_click = () => {
		console.log("Local game button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 
		'username': this.username, 'modus': 'local'}))
	}
	
	handle_play_ai_button_click = () => {
		console.log("Play AI button clicked");
	
		// Function to create modal HTML dynamically
		const createModal = (containerId, title, html) => {
			const modalHtml = `
				<div class="modal fade" id="${containerId}Modal" tabindex="-1" role="dialog" aria-labelledby="${containerId}ModalLabel" aria-hidden="true">
					<div class="modal-dialog" role="document" style="max-width: 80%;">
						<div class="modal-content">
							<div class="modal-header">
								<h5 class="modal-title" id="${containerId}ModalLabel">${title}</h5>
								<button type="button" class="close" data-dismiss="modal" aria-label="Close">
									<span aria-hidden="true">&times;</span>
								</button>
							</div>
							<div class="modal-body text-center" style="max-height: 400px; overflow-y: auto;">
								${html} <!-- Render the fetched form here -->
							</div>
						</div>
					</div>
				</div>
			`;
			// Append the modal HTML to the container
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
	
			// Add event listener to handle button clicks inside the modal
			modal.querySelectorAll('.levelButton').forEach(button => {
				button.addEventListener('click', function() {
					const selectedLevel = this.getAttribute('data-level');
					console.log("AI Difficulty Level " + selectedLevel + " selected");
					// Send selected AI difficulty level to the server via WebSockets
					ws.send(JSON.stringify({
						type: 'lobby_update',
						action: 'join',
						username: this.username,
						modus: 'ai',
						ai_level: selectedLevel
					}));
					// Close the modal after selecting a level
					modal.style.display = 'none';
				});
			});
		};
	
		// Call createModal function with desired parameters
		createModal(
			'playAi', // Container ID
			'Select AI Difficulty', // Modal title
			`<div class="button-popup-container">
				<!-- Create buttons for AI difficulty levels -->
				${Array.from({ length: 10 }, (_, i) => i + 1).map(level => `
					<button class="levelButton buttonblue btn" data-level="${level}">Level: ${level}</button>
				`).join('')}
			</div>`
		);
	}
	

	update_lobby(data) {
		let matches_info = data.matches_info;
		let tournaments_info = data.tournaments_info;
		console.log("lobby_update tm-info: ", tournaments_info);
		
		//clear remote_game_list div
		this.remote_game_list_DIV.innerHTML = '';
		this.tournament_list_DIV.innerHTML = '';
		
		for (var match_id in matches_info) {
			((id) => {
				var registered_users = matches_info[id];
				
				var matchElement = document.createElement('div');
				matchElement.innerHTML = `<div class="my-4 card">
				<div class="card-header text-center text-white bg-purple"><h2>Match ID: ${id}</h2></div>
				<div class="card-body">
				<p>Registered Users: ${registered_users.join(', ')}</p>
				<button class="join btn buttonblue" data-match-id="${id}">Join Game</button></div>
				</div>`;
				
				this.remote_game_list_DIV.appendChild(matchElement);
				
				let joinButton = matchElement.querySelector('.join');
				joinButton.addEventListener('click', () => {
					console.log("Join button clicked for match id: ", id);
					ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
					'match_id': id, 'username': this.username, 'modus': 'remote'}));
				});
			})(match_id);
		}
		
		for (var tournament_id in tournaments_info) {
			((id) => {
				var registered_users = tournaments_info[id];
				
				var tournamentElement = document.createElement('div');
				tournamentElement.innerHTML = `<div class="my-4 card">
				<div class="card-header text-center text-white bg-purple"><h2>Tournament ID: ${id}</h2></div>
				<div class="card-body">
				<p>Registered Users: ${registered_users.join(', ')}</p>
				<button class="join btn buttonblue" data-tournament-id="${id}">Join Tournament</button></div>
				</div>`;
				
				this.tournament_list_DIV.appendChild(tournamentElement);
				
				let joinButton = tournamentElement.querySelector('.join');
				joinButton.addEventListener('click', () => {
					console.log("Join button clicked for tournament id: ", id);
					ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join_tournament',
					'tournament_id': id, 'username': this.username}));
				});
			})(tournament_id);
		}
	}

	join_game(modus) {
		history.pushState("", "", "/pong_online/");
		router(() => {
			ws.send(JSON.stringify({type: 'get_game_data'}));
		});
		console.log("join game");
	}

	join_tournament(server_data) {
		let tournamentGameUrl = '/tournament/' + server_data.tournament_id + '/';
		history.pushState("", "", tournamentGameUrl);
		router(() => {
			ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': server_data.tournament_id}));
		});
		console.log("join tournament");
	}

	
}



customElements.define("pong-lobby", Lobby);
