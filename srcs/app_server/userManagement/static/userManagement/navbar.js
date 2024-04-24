import {fetch_html_replace_dynamicDIV_activate_js, fetch_with_internal_js, getCookie, executeJavaScriptInContent} from "./land.js"

class Navbar extends HTMLElement {
    constructor() {
        super();
        
		this.username = this.getAttribute('data-username');
		console.log("username please:", this.username);

        this.innerHTML = /*html*/`
			<div>
				<button class="navbar-button" id="lobbyBtn">Lobby</button>
				<button class="navbar-button" id="profileBtn">Profile</button>
				<button class="navbar-button" id="logoutBtn">Logout</button>
			</div>
        `;

        let lobbyBtn = this.querySelector("#lobbyBtn");
		let profileBtn = this.querySelector("#profileBtn");
		let logoutBtn = this.querySelector("#logoutBtn");

        // State
        lobbyBtn.onclick = () => {
			console.log("lobby button on navbar tag clicked");
			fetch_html_replace_dynamicDIV_activate_js('/lobby', true);
        };

		profileBtn.onclick = () => {
			console.log("profile button on navbar tag clicked");
			const url = `/profile/${this.username}`;
			fetch_with_internal_js(url);
        };

		logoutBtn.onclick = () => {
			let logoutUrl = "/accounts/logout/"; //maybe dynamic url later from django template
			fetch(logoutUrl, {
				method: "POST",
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				}
			})
			.then(response => {
				if (response.ok) {
					document.getElementById("navbar").innerHTML = '';
					document.getElementById("content").innerHTML = '';
					fetch("/stranger")
						.then(response => response.text())
						.then(html => {
							document.getElementById("content").innerHTML = html;
						})
						.catch(error => console.error('Error loading content:', error));
				} else {
					console.error("Logout failed");
				}
			})
			.catch(error => console.error('Error:', error));
        };
    }
}

customElements.define("pong-navbar", Navbar);
