class singleGameStats extends HTMLElement {
	constructor() {
		super();
		//console.log("constructor singleGameStats custom element");

		var statsTable = document.getElementById('stats-table');
		var rows = statsTable.getElementsByTagName('tr');

		for (var i = 1; i < rows.length; i++) {
			var cells = rows[i].getElementsByTagName('td');
			var player1Stat = parseInt(cells[0].innerText);
			var player2Stat = parseInt(cells[2].innerText);

			if (player1Stat > player2Stat) {
				cells[0].classList.add('winner-border');
			} else if (player2Stat > player1Stat) {
				cells[2].classList.add('winner-border'); 
			}
		}
	}
}

customElements.define("pong-single-game-stats", singleGameStats);