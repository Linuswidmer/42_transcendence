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
		}else {
			ws.onopen = function(event) {
				//console.log('WS open in navbar after waiting')
				ws.send(JSON.stringify({type: 'test'}));
			}
		}

        this.innerHTML = /*html*/`
			<div id="navbar">
			<div class="navbar navbar-light" style="background-color: #6a0dad;">
				<a href="/lobby/" class="navbar-button" id="lobbyBtn" data-link>Lobby</a>
				<a href="/profile/${this.username}" class="navbar-button" id="profileBtn" data-link>Profile</a>
				<a href="/" class="navbar-button" id="logoutBtn" data-logout>Logout</a>
			</div>
		</div>
        `;
        
		let logoBtn = document.querySelector("#logoBtn");
        let lobbyBtn = this.querySelector("#lobbyBtn");
		let profileBtn = this.querySelector("#profileBtn");
		let logoutBtn = this.querySelector("#logoutBtn");

        // State
		logoBtn.onclick = () => {
			//console.log("logo button on navbar tag clicked");
        };
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
