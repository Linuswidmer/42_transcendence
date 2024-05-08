import {ws} from "./main.js"

class Navbar extends HTMLElement {
    constructor() {
        super();
		this.username = this.getAttribute('data-username');
		//console.log("username please:", this.username);

		//console.log('WS STATE: ', ws.readyState);
		if (ws.readyState == WebSocket.OPEN){
			//console.log('WS was already open in navbar')
			ws.send(JSON.stringify({type: 'test'}));
			fetch('/get_username/')
			.then(response => {
				// Check if the response is OK
				if (!response.ok) {
					console.log("not authenticated");
				}
				// Parse the JSON response
				return response.json();
			})
			.then(data => {
				// Extract the username from the JSON response
				const username = data.username;
				ws.send(JSON.stringify({type: 'username', 'username': username}));
				// Now you can use the username variable as needed
			})
			.catch(error => {
				// Log any errors
				console.error('Fetch error:', error);
			});
	
		}else {
			ws.onopen = function(event) {
				//console.log('WS open in navbar after waiting')
				ws.send(JSON.stringify({type: 'test'}));
				fetch('/get_username/')
				.then(response => {
					// Check if the response is OK
					if (!response.ok) {
						console.log("not authenticated");
					}
					// Parse the JSON response
					return response.json();
				})
				.then(data => {
					// Extract the username from the JSON response
					const username = data.username;
					ws.send(JSON.stringify({type: 'username', 'username': username}));
					// Now you can use the username variable as needed
				})
				.catch(error => {
					// Log any errors
					console.error('Fetch error:', error);
				});
	
			}
		}

        this.innerHTML = /*html*/`

		<div id="navbar">
    	<div class="navbar-content">
        	<h1 id="ingrid">${this.username}</h1>
        	<div class="navbar-button"  style="background-color: #6a0dad;">
				<a href="/lobby/" class="navbar-button" id="lobbyBtn" data-link>Lobby</a>
				<a href="/profile/${this.username}" class="navbar-button" id="profileBtn" data-link>Profile</a>
				<a href="/" class="navbar-button" id="logoutBtn" data-logout>Logout</a>
			</div>
			</div>
		</div>
        `;
        
        let lobbyBtn = this.querySelector("#lobbyBtn");
		let profileBtn = this.querySelector("#profileBtn");
		let logoutBtn = this.querySelector("#logoutBtn");


        lobbyBtn.onclick = () => {
			//console.log("lobby button on navbar tag clicked");
        };

		profileBtn.onclick = () => {
			//console.log("profile button on navbar tag clicked");
        };

		logoutBtn.onclick = () => {
			//console.log("logout button on navbar tag clicked");
        };
    }
}



customElements.define("pong-navbar", Navbar);
