import {fetch_html_replace_dynamicDIV_activate_js} from "./landing_test.js";

class js_wrapper {
	activate() {
		throw new Error("Subclasses must override this method.");
	}

	deactivate () {
		throw new Error("Subclasses must override this method.");
	}
}

	
class Lobby extends js_wrapper {
	static counter = 0;

	constructor(ws, username) {
		super();
		Lobby.counter++;
		console.log("lobby instances: ", Lobby.counter);
        this.ws = ws;
		this.username = username;
		console.log("username:", username);
		
		this.modus = null;
    }
	
	send_initial_data_to_server(e) {
		console.log('WebSocket connection established');
		this.ws.send(JSON.stringify({type: 'username', 'username': this.username}));
		this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
	}
	
	activate() {
		this.ws.onmessage = (e) => this.handle_message(e);
		this.create_game_button = document.getElementById('create_game');
		this.create_game_button.addEventListener('click', 
			this.handle_create_game_button_click);
		
		this.create_tournament_button = document.getElementById('create_tournament');
		this.create_tournament_button.addEventListener('click',
			this.handle_create_tournament_button_click);
		
		this.play_local_button = document.getElementById('play_local');
		this.play_local_button.addEventListener('click', 
			this.handle_play_local_button_click);
		
		this.play_ai_button = document.getElementById('play_ai');
		this.play_ai_button.addEventListener('click',
			this.handle_play_ai_button_click);
		
		this.remote_game_list_DIV = document.getElementById('remote_game_list');
		this.tournament_list_DIV = document.getElementById('tournament_list');

		// this.ws.onopen = (e) => this.send_initial_data_to_server(e);

		this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
	}

	deactivate() {
		this.create_game_button.removeEventListener('click', this.handle_create_game_button_click);
        this.create_tournament_button.removeEventListener('click', this.handle_create_tournament_button_click);
        this.play_local_button.removeEventListener('click', this.handle_play_local_button_click);
        this.play_ai_button.removeEventListener('click', this.handle_play_ai_button_click);

        this.ws.onmessage = null;
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
						default:
							console.log('Unknown message', data);
						}
					} catch (error) {
						console.log('Error parsing JSON:', error);
					}
		}
				
		handle_create_game_button_click = () => {
			console.log("Create game button clicked");
			this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create',
			'username': this.username, 'modus': 'remote'}));
		}
		
		handle_create_tournament_button_click = () => {
			console.log("Create tournament button clicked");
			this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create_tournament',
			'username': this.username}));
		}
		
		handle_play_local_button_click = () => {
			console.log("Local game button clicked");
			this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 
			'username': this.username, 'modus': 'local'}))
		}
		
		handle_play_ai_button_click = () => {
			console.log("AI Opponent button clicked");
			this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
			'username': this.username, 'modus': 'ai'}));
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
				matchElement.innerHTML = `
				<h2>Match ID: ${id}</h2>
				<p>Registered Users: ${registered_users.join(', ')}</p>
				<button class="join" data-match-id="${id}">Join Game</button>
				`;
				
				this.remote_game_list_DIV.appendChild(matchElement);
				
				let joinButton = matchElement.querySelector('.join');
				joinButton.addEventListener('click', () => {
					console.log("Join button clicked for match id: ", id);
					this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
					'match_id': id, 'username': this.username, 'modus': 'remote'}));
				});
			})(match_id);
		}
		
		for (var tournament_id in tournaments_info) {
			((id) => {
				var registered_users = tournaments_info[id];
				
				var tournamentElement = document.createElement('div');
				tournamentElement.innerHTML = `
				<h2>Tournament ID: ${id}</h2>
				<p>Registered Users: ${registered_users.join(', ')}</p>
				<button class="join" data-tournament-id="${id}">Join Tournament</button>
				`;
				
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
		this.ws.modus = modus;
		fetch_html_replace_dynamicDIV_activate_js('/pong_online', true, () => {
			this.ws.send(JSON.stringify({type: 'get_game_data'}));
		});
		
		// fetch('/pong_online')
		// 	.then(response => response.text())
		// 	.then(data => {
			// 		// Create a temporary DOM div element
			// 		var tempDiv = document.createElement('div');
			
			// 		// Set its innerHTML to the fetched HTML data
			// 		tempDiv.innerHTML = data;
			
			// 		// Extract the src attribute from the script tag
			// 		var scriptSrc = tempDiv.querySelector('script').src;
			
			// 		// Use the fetched HTML data
			// 		document.body.innerHTML = data;
			
			// 		// Create a new script element
			// 		var script = document.createElement('script');
			
					// Set its src attribute to the extracted src
				// 	script.src = scriptSrc;

				// 	script.onload = function() {
				// 		// This function will be called when the script is fully loaded and executed
				// 		console.log('loaded pong_online: ');
				// 		// Send WebSocket message here
				// 		ws.send(JSON.stringify({type: 'get_game_data'}));
				// 	};
					
				// 	// Append the script element to the body of the document
				// 	document.body.appendChild(script);
				// })
				// .catch((error) => {
				// 	console.error('Error:', error);
				// });
	}

	join_tournament(data1) {
		document.body.innerHTML = '';
		fetch('/tournament/' + data.tournament_id + '/')
			.then(response => response.text())
			/* .then(data => {
				document.body.innerHTML = data
			}) */
			.then(data => {
				console.log('/tournament/' + data1.tournament_id)
				// Create a temporary DOM div element
				var tempDiv = document.createElement('div');

				// Set its innerHTML to the fetched HTML data
				tempDiv.innerHTML = data;
		
				// Extract the src attribute from the script tag
				var scriptSrc = tempDiv.querySelector('script').src;
		
				// Use the fetched HTML data
				document.body.innerHTML = data;
		
				//console.log(data);
				// Create a new script element
				var script = document.createElement('script');
		
				// Set its src attribute to the extracted src
				script.src = scriptSrc;

				script.onload = function() {
					// This function will be called when the script is fully loaded and executed
					console.log('Script loaded');
					// Send WebSocket message here
					ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': data1.tournament_id}));
				};
				
				// Append the script element to the body of the document
				document.body.appendChild(script);
			})
			.catch((error) => {
				console.error('Error:', error);
			});
	}
}

export default Lobby;
