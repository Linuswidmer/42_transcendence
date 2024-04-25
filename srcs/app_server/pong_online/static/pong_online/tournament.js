import {router, ws} from "../userManagement/land.js"

class Tournament extends HTMLElement {
    constructor() {
        super();

		this.username = this.getAttribute('data-username');
		this.tournament_name = this.getAttribute('data-tournament');
		console.log("username tournament:", this.username);
		console.log("tournament name:", this.tournament_name);

        this.innerHTML = /*html*/`
				<div class="tournament-container">
					<!-- Tournament name -->
					<div class="tournament-name" id="tournamentName">
						Tournament Name
					</div>
				
					<!-- Players in the tournament -->
					<div class="tournament-players" id="tournamentPlayers">
						<!-- Players will be dynamically added here -->
					</div>
				
					<!-- Tournament rounds -->
					<div class="rounds" id="rounds">
						<!-- Rounds will be dynamically added here -->
					</div>
				</div>
        `;

		ws.onmessage = (e) => this.handle_message(e);

		this.leaveTournamentButton = document.createElement('button');
		this.leaveTournamentButton.textContent = 'Leave Tournament';
		this.leaveTournamentButton.addEventListener('click', this.handle_leave_tournament_button_click);
    }

	updateTournamentLobby(data) {
		this.tournament_name = data.tournament_id;
		let tournament_data = data.tournament_data;
		if ('error' in data) {
			alert(data.error);
		}
		const tournamentNameElement = this.querySelector('#tournamentName');
		tournamentNameElement.textContent = '';
		tournamentNameElement.textContent = this.tournament_name;
	
		// Get players container
		const playersContainer = this.querySelector('#tournamentPlayers');
		playersContainer.textContent = '';
		playersContainer.textContent = `Players in tournament: ${data.players.join(', ')}`;
	
		// Create and add the leave tournament button
		
		playersContainer.appendChild(this.leaveTournamentButton)
	
		// Get rounds container
		const roundsContainer = this.querySelector('#rounds');
		roundsContainer.textContent = '';
	
		// Iterate through rounds
		for (const roundKey in tournament_data) {
			const round = tournament_data[roundKey];
	
			// Create round element
			const roundElement = document.createElement('div');
			roundElement.classList.add('round');
	
			// Add round title
			const roundTitle = document.createElement('h2');
			roundTitle.classList.add('round-title');
			roundTitle.textContent = `Round ${parseInt(roundKey) + 1}`;
			roundElement.appendChild(roundTitle);
	
			// Create container for matches
			const matchesContainer = document.createElement('div');
			matchesContainer.classList.add('matches-container');
	
			// Iterate through matches in the round
			for (const matchKey in round) {
				const match = round[matchKey];
				// Create match element
				const matchElement = document.createElement('div');
				matchElement.classList.add('match');
	
				// Add match info
				const matchInfo = document.createElement('div');
				matchInfo.classList.add('match-info');
				if (match.winner != "None"){
					matchInfo.innerHTML = `<strong>${matchKey}</strong>: <br>Winner: ${match.winner} <br>Loser: ${match.loser}`;
				}else{
					matchInfo.innerHTML = `<strong>${matchKey}</strong>: <br>Not played yet!`;
				}
				matchElement.appendChild(matchInfo);
	
				// Append match to matches container
				matchesContainer.appendChild(matchElement);
			}
	
			// Append matches container to round
			roundElement.appendChild(matchesContainer);
	
			// Append round to rounds container
			roundsContainer.appendChild(roundElement);
		}
	}

	handle_leave_tournament_button_click= () => {
		console.log("Leave Tournament button clicked");
		ws.send(JSON.stringify({type: 'lobby_update', 'action': 'leave_tournament', 'tournament_id': this.tournament_name}));
	}

	handle_message(e) {
		try{
			const data = JSON.parse(e.data);
			console.log("ws.onmessage:", data);
			if (data.action === "start_tournament_round"){
				console.log("starting round", data.match_id)
				//window.location.href = window.location.origin + '/lobby/';
				ws.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 'match_id': data.match_id, 'tournament_id': data.tournament_id, 'username': username, 'modus': 'remote'}));
			}
			if (data.type === "tournament_lobby_update") {
				console.log('Update tm lobby');
				this.updateTournamentLobby(data);
			}
			if (data.type === "redirect_to_tournament_stats") {
				console.log(window.location.origin + '/tournament_stats/' + data.tournament_id);
				let tournamentStatsUrl = '/tournament_stats/' + data.tournament_id;
				history.pushState("", "", tournamentStatsUrl);
				router();
				// fetch_with_internal_js('/tournament_stats/' + data.tournament_id);
				//window.location.href = window.location.origin + '/tournament_stats/' + data.tournament_id;
			}
			if (data.type === "leave_tournament"){
				console.log(window.location.origin + '/lobby/');
				history.pushState("", "", "/lobby");
				router();
			}
			if (data.type === "join") {
				history.pushState("", "", "/pong_online");
				router();
				ws.send(JSON.stringify({type: 'get_game_data'}));
			}
	
		} catch (error) {
			console.log('Error parsing JSON:', error);
		}
	}
}



customElements.define("pong-tournament", Tournament);
