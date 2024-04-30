import {router} from "./main.js"

class ProfileList extends HTMLElement {
    constructor() {
        super();
		console.log("constructor profile list custom element");

		document.querySelectorAll(".profileBtn").forEach(button => {
			button.addEventListener("click", function() {
				console.log("profileOtherBtn clicked");
				// Fetch the profile page for the specific user associated with the clicked button
				const username = this.dataset.username; // Retrieve username from data attribute
				console.log(username);
				const url = `/profile/${username}/`; // Construct the URL with the username
				//history.pushState("", "", url);
				router(url);
		 	});
		});
    }
}

customElements.define("pong-list", ProfileList);
