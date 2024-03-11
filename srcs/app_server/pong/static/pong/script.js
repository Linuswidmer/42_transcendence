// Hide button(s) and show the canvas and other elements
document.getElementById("playLocalGame").addEventListener("click", function() {
    this.style.display = "none";
    document.getElementById("playLocalTournament").style.display = "none";

    document.getElementById("playerInputsLocalGame").style.display = "block";
    document.getElementById("submitLocalPlayerNames").style.display = "block";
});

document.getElementById("submitLocalPlayerNames").addEventListener("click", function() {
    var player1Name = document.getElementById("localGame1Name").value;
    var player2Name = document.getElementById("localGame2Name").value;

    document.getElementById("pongCanvas").style.display = "block";
    document.getElementById("leftScore").style.display = "block";
    document.getElementById("rightScore").style.display = "block";

    // Start the game
    startLocalGame();
});

function startLocalTournament() {
    var tournamentButton = document.getElementById("playLocalTournament");
    var playerInputsTournament = document.getElementById("playerInputsTournament");

    tournamentButton.style.display = "none";
    playerInputsTournament.style.display = "block";
}

// Attach the event listener to the "Start Local Tournament" button
document.getElementById("playLocalTournament").addEventListener("click", startLocalTournament);

document.getElementById("submitLocalTournamentPlayers").addEventListener("click", function() {
    var player1Name = document.getElementById("localTournament1Name").value;
    var player2Name = document.getElementById("localTournament2Name").value;
    var player3Name = document.getElementById("localTournament3Name").value;
    var player4Name = document.getElementById("localTournament4Name").value;


    playerInputsTournament.style.display = "none";
    submitLocalTournamentPlayers.style.display = "none";
    console.log('Data:', playersData);

    // Create an object with player information
    var playersData = {
        player1: player1Name,
        player2: player2Name,
        player3: player3Name,
        player4: player4Name
    };


    var csrftoken = getCookie('csrftoken');

    fetch('/create_local_tournament/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(playersData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
    
        // Get the tournament tree from the response data
        var tournamentTree = data;
    
        if (!tournamentTree) {
            console.error('No tournament tree in response data');
            return;
        }
    
        // Get the element where the tournament tree will be displayed
        var tournamentDiv = document.getElementById('tournamentTree');
    
        // Clear any existing content
        tournamentDiv.innerHTML = '';
    
        // Create a new div for each match
        tournamentTree.forEach((match, i) => {
            var matchDiv = document.createElement('div');
            matchDiv.textContent = 'Match ' + (i + 1) + ': ' + match[0] + ' vs ' + match[1];
            tournamentDiv.appendChild(matchDiv);
        });
    })
    .catch(error => {
        console.error('Error creating tournament:', error);
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}