import {router, ws} from "../userManagement/main.js"

class tournamentStats extends HTMLElement{
	constructor(){
		super();
		var tournament_data = JSON.parse(this.getAttribute('tournamentData'));
		console.log('Constructor tournament stats custom called: ', tournament_data)

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

				if (match.winner !== "None") {
					matchLink.innerHTML = `<strong>${matchKey}</strong>: <br>Winner: ${match.winner} <br>Loser: ${match.loser}`;
				} else {
					matchLink.innerHTML = `<strong>${matchKey}</strong>: <br>Not played yet!`;
				}

				// Add a click event listener
				matchLink.addEventListener('click', function(event) {
					const statsURL = '/singleGameStats/' + matchKey + '/';
					console.log('Game link clicked: ', statsURL);
					//history.pushState("", "", statsURL);
					router(statsURL);
				});

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
}

customElements.define("pong-tournament-stats", tournamentStats);