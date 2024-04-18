if (typeof ws1 === 'undefined') {
    ws1 = window.ws; // Declare ws1 only if it's not already declared
}

ws1.onmessage = function(e) {
	try{
		const data = JSON.parse(e.data);
		console.log("ws1.onmessage:", data);
		
		if (data.action === "start_tournament_round"){
			console.log("starting round", data.match_id)
			//window.location.href = window.location.origin + '/lobby/';
			ws1.send(JSON.stringify({type: 'lobby_update', 'action': 'join', 'match_id': data.match_id, 'tournament_id': data.tournament_id, 'username': username, 'modus': 'remote'}));
		}
		if (data.type === "tournament_lobby_update") {
			console.log('Update tm lobby');
			updateTournamentLobby(data);
		}
		if (data.type === "redirect_to_tournament_stats") {
			console.log(window.location.origin + '/tournament_stats/' + data.tournament_id)
			window.location.href = window.location.origin + '/tournament_stats/' + data.tournament_id;
		}
		if (data.type === "leave_tournament"){
			console.log(window.location.origin + '/lobby/');
			window.location.href = window.location.origin + '/lobby/';
		}
		if (data.type === "join") {
			ws1.modus =  data.modus
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
					console.log(document.body)
				})
				.catch((error) => {
					console.error('Error:', error);
				});
		}

    } catch (error) {
		console.log('Error parsing JSON:', error);
	}
};

function updateTournamentLobby(data) {
	//tournaments_info = data.tournaments_info
	tournament_name = data.tournament_id;
	tournament_data = data.tournament_data
	if ('error' in data) {
		alert(data.error);
	}
    const tournamentNameElement = document.getElementById('tournamentName');
	tournamentNameElement.textContent = '';
    tournamentNameElement.textContent = tournament_name;

    // Get players container
    const playersContainer = document.getElementById('tournamentPlayers');
	playersContainer.textContent = '';
	playersContainer.textContent = `Players in tournament: ${data.players.join(', ')}`;

	// Create and add the leave tournament button
    var leaveTournamentButton = document.createElement('button');
    leaveTournamentButton.textContent = 'Leave Tournament';
    leaveTournamentButton.addEventListener('click', function() {
        console.log("Leave Tournament button clicked");
        ws1.send(JSON.stringify({type: 'lobby_update', 'action': 'leave_tournament', 'tournament_id': tournament_name}));
    });
    playersContainer.appendChild(leaveTournamentButton)

    // Get rounds container
    const roundsContainer = document.getElementById('rounds');
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
            const matchLink = document.createElement('a');
            matchLink.classList.add('match-info');
            if (match.winner != "None"){
                matchLink.href = 'http://localhost:8443/singleGameStats/?matchName=' + matchKey + '&username=' + match.winner; // Set the href to google.com
                matchLink.innerHTML = `<strong>${matchKey}</strong>: <br>Winner: ${match.winner} <br>Loser: ${match.loser}`;
            }else{
                matchLink.innerHTML = `<strong>${matchKey}</strong>: <br>Not played yet!`;
            }
            matchElement.appendChild(matchLink);

            // Append match to matches container
            matchesContainer.appendChild(matchElement);
        }

        // Append matches container to round
        roundElement.appendChild(matchesContainer);

        // Append round to rounds container
        roundsContainer.appendChild(roundElement);
    }
}
