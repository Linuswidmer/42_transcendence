function setupButtons() {
	//////////////////////// REGISTER BUTTON ///////////////////////
    var registerButtons = document.querySelectorAll('.register');
    registerButtons.forEach(function(button) {
        // Remove any existing event listeners
        var newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        newButton.addEventListener('click', function() {
            var match_id = this.getAttribute('data-match-id');
            fetch('/register_player/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your CSRF token here
                },
                body: JSON.stringify({match_id: match_id})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    // Display error message
                    alert(data.error_message);
                } else {
                    // Handle success
                    alert("registered successfully");

					// Send a message to the server over the WebSocket connection
                    ws.send(JSON.stringify({type: 'lobby_update'}));
                }
            });
        });
    });

	//////////////////////// JOIN BUTTON /////////////////////////
	var joinButtons = document.querySelectorAll('.join');
    joinButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var match_id = this.getAttribute('data-match-id');
            fetch('/join/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Add your CSRF token here
                },
                body: JSON.stringify({match_id: match_id})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    // Display error message
                    alert(data.error_message);
                } else {
                    // Handle success
                    
                }
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', setupButtons);


const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
const ws = new WebSocket(
	protocol + '://' + window.location.host + '/ws/pong_online/game/'
);

ws.onopen = function(e) {
	// telling the server that the client is ready
	console.log('WebSocket connection established');
	let data = {'playerId': 'SESSION ID HERE?????'};
	ws.send(JSON.stringify(data));
};

ws.onmessage = function(e) {
	try{
		const data = JSON.parse(e.data);
	

		if (data.type === "lobby_update") {
			// Fetch the updated lobby HTML
            fetch('/lobby/')
            .then(response => response.text())
            .then(html => {
                // Replace the current lobby HTML with the updated one
                document.querySelector('#lobby').innerHTML = html;

                // Set up the register buttons again
                setupButtons();
            });
		}
		
	} catch (error) {
		console.log('Error parsing JSON:', error);
	}
};
