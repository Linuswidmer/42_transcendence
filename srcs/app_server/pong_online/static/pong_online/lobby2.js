import {router, ws} from "../userManagement/land.js"

class Lobby extends HTMLElement {
    constructor() {
        super();

		this.username = this.getAttribute('data-username');
		console.log("username lobby:", this.username);

		ws.send(JSON.stringify({type: 'username', 'username': this.username}));


        this.innerHTML = /*html*/`
			<div>
				<button class="btn buttonblue" id="create_game">Create remote game</button>
				<button class="btn buttonblue" id="create_tournament">Create tournament</button>
				<button class="btn buttonblue" id="play_ai">Play against Ai</button>
				<button class="btn buttonblue" id="play_local">Play local</button>
			</div>
			
			<div id="remote_game_list"></div>
			<div id="tournament_list"></div>
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

		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
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
	
	handle_create_tournament_button_click = () => {
		console.log("Create tournament button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'create_tournament',
		'username': this.username}));
	}
	
	handle_play_local_button_click = () => {
		console.log("Local game button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 
		'username': this.username, 'modus': 'local'}))
	}
	
	handle_play_ai_button_click = () => {
		console.log("AI Opponent button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
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
					ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join',
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
		// this.ws.modus = modus;
		// fetch_html_replace_dynamicDIV_activate_js('/pong_online', true, () => {
		history.pushState("", "", "/pong_online");
		router();
		ws.send(JSON.stringify({type: 'get_game_data'}));
		// });
		console.log("join game");
	}

	join_tournament(server_data) {
		let tournamentGameUrl = '/tournament/' + server_data.tournament_id + '/';
		history.pushState("", "", tournamentGameUrl);
		router();
		ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': server_data.tournament_id}));
		// fetch_html_replace_dynamicDIV_activate_js('/tournament/' + server_data.tournament_id + '/', true, () => {
		// 	this.ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': server_data.tournament_id}));
		// });
		console.log("join tournament");
	}

	
}



customElements.define("pong-lobby", Lobby);
