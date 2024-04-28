import {ws} from "./main.js"

class Navbar extends HTMLElement {
    constructor() {
        super();

		ws.send(JSON.stringify({type: 'test'}));
        
		this.username = this.getAttribute('data-username');
		console.log("username please:", this.username);

        this.innerHTML = /*html*/`
			<div>
				<a href="/lobby/" class="navbar-button" id="lobbyBtn" data-link>Lobby</a>
				<a href="/profile/${this.username}" class="navbar-button" id="profileBtn" data-link>Profile</a>
				<a href="/" class="navbar-button" id="logoutBtn" data-logout>logout</a>
			</div>
        `;
        

        let lobbyBtn = this.querySelector("#lobbyBtn");
		let profileBtn = this.querySelector("#profileBtn");
		let logoutBtn = this.querySelector("#logoutBtn");

        // State
        lobbyBtn.onclick = () => {
			console.log("lobby button on navbar tag clicked");
        };

		profileBtn.onclick = () => {
			console.log("profile button on navbar tag clicked");
        };

		logoutBtn.onclick = () => {
			console.log("logout button on navbar tag clicked");
        };
    }
}



customElements.define("pong-navbar", Navbar);
