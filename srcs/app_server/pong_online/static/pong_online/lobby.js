
const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
window.ws = new WebSocket(
	protocol + '://' + window.location.host + '/ws/pong_online/game/'
);

const data = document.currentScript.dataset;
const username = data.username;
console.log("username from request", username);


class Lobby {
	constructor(ws, username) {
        this.ws = ws;
		ws.username = username;  //maybe change later
		this.username = username;

		this.modus = null;

		this.play_local_button = document.getElementById('create_game');
		this.play_local_button.addEventListener('click', () => {
            this.handle_create_game_button_click();
        });

		this.play_local_button = document.getElementById('play_local');
		this.play_local_button.addEventListener('click', () => {
            this.handle_play_local_button_click();
        });

		this.play_local_button = document.getElementById('play_ai');
		this.play_local_button.addEventListener('click', () => {
            this.handle_play_ai_button_click();
        });

		this.remote_game_list_DIV = document.getElementById('remote_game_list');

		this.ws.onopen = (e) => this.send_initial_data_to_server(e);
        this.ws.onmessage = (e) => this.handle_message(e);
    }

	send_initial_data_to_server(e) {
		console.log('WebSocket connection established');
		ws.send(JSON.stringify({type: 'username', 'username': this.username}));
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
	}

    handle_message(e) {
        try {
            const data = JSON.parse(e.data);
			switch (data.type) {
				case 'lobby_update':
					this.update_lobby(data);
					break;
				case 'join':
					this.join_game(data.modus);
					break;
				default:
					console.log('Unknown message', data);
			}
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    }

	handle_create_game_button_click() {
		console.log("Create game button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create',
			'username': this.username}));
	}

	handle_play_local_button_click() {
		console.log("Local game button clicked");
		this.ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 
			'username': this.username, 'modus': 'local'}))
	}

	handle_play_ai_button_click () {
		console.log("AI Opponent button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
			'username': this.username, 'modus': 'ai'}));
	}

	update_lobby(data) {
		let matches_info = data.matches_info;

		//clear remote_game_list div
		this.remote_game_list_DIV.innerHTML = '';

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
	}

	join_game(modus) {
		ws.modus = modus;
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
}

const lobby = new Lobby(ws, username);
