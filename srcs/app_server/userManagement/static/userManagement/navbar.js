import {fetch_html_replace_dynamicDIV_activate_js, fetch_with_internal_js, getCookie, executeJavaScriptInContent, ws} from "./land.js"



class Navbar extends HTMLElement {
    constructor() {
        super();

		ws.send(JSON.stringify({type: 'test'}));
        
		this.username = this.getAttribute('data-username');
		console.log("username please:", this.username);

        this.innerHTML = /*html*/`
			<div>
				<a href="/lobby" class="navbar-button" id="lobbyBtn" data-link>Lobby</a>
				<a href="/profile/${this.username}" class="navbar-button" id="profileBtn" data-link>Profile</a>
				<a href="/home" class="navbar-button" id="logoutBtn" data-logout>logout</a>
			</div>
        `;
        

        let lobbyBtn = this.querySelector("#lobbyBtn");
		let profileBtn = this.querySelector("#profileBtn");
		let logoutBtn = this.querySelector("#logoutBtn");

        // State
        lobbyBtn.onclick = () => {
			console.log("lobby button on navbar tag clicked");
			// fetch_html_replace_dynamicDIV_activate_js('/lobby', true);
        };

		profileBtn.onclick = () => {
			console.log("profile button on navbar tag clicked");
			// const url = `/profile/${this.username}`;
			// fetch_with_internal_js(url);
        };

		// logoutBtn.onclick = () => {
		// 	let logoutUrl = "/accounts/logout/"; //maybe dynamic url later from django template
		// 	fetch(logoutUrl, {
		// 		method: "POST",
		// 		headers: {
		// 			"X-CSRFToken": getCookie("csrftoken")
		// 		}
		// 	})
		// 	.then(response => {
		// 		if (response.ok) {
		// 			// document.getElementById("navbar").innerHTML = '';
		// 			// document.getElementById("content").innerHTML = '';
		// 			// fetch("/stranger")
		// 			// 	.then(response => response.text())
		// 			// 	.then(html => {
		// 			// 		document.getElementById("content").innerHTML = html;
		// 			// 	})
		// 			// 	.catch(error => console.error('Error loading content:', error));
		// 			console.log("logout successful");
		// 		} else {
		// 			console.error("Logout failed");
		// 		}
		// 	})
		// 	.catch(error => console.error('Error:', error));
        // };
    }

	logoutFunction = () => {
		// Log out the user
		console.log("Logging out...");
		// You can add more code here to log out the user
	}
}



customElements.define("pong-navbar", Navbar);
