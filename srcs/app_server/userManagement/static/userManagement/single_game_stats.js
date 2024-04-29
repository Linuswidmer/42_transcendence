class Single_Game_Stats extends HTMLElement {
    constructor() {
        super();
    
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

        // Get the h2 element
        var h2 = document.getElementById('vs');

        // Get the scores
        var userScore = parseInt(cells[0].innerText);
        var opponentScore = parseInt(cells[2].innerText);

        // Add the crown emoji to the player with the higher score
        if (userScore > opponentScore) {
            h2.innerHTML = '👑 ' + h2.innerHTML;
            console.log('User wins');
        } else if (opponentScore > userScore) {
            h2.innerHTML = h2.innerHTML + ' 👑';
        }
    };

}

customElements.define("pong-single-game-stats", Single_Game_Stats);