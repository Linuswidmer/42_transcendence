import "./navbar.js"
import "./stranger.js"
import "../pong_online/lobby.js"
import "../pong_online/pong_online.js"
import "../pong_online/tournament.js"

const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
	// const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
let ws = new WebSocket(
	protocol + '://' + window.location.host + '/ws/pong_online/game/'
);

ws.onopen = function(event) {
	console.log('WebSocket connection established');
	ws.send(JSON.stringify({type: 'firstContactfromClient'}));
}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

const routes = {
    "/": { fetch: "/home" },
    "/lobby/": { fetch: "/fetch_lobby" },
    "/pong_online/": { fetch: "fetch_pong_online" },
};

function router(callback=null) {
	let urlWithoutOrigin = location.href.replace(location.origin, '');
	let view = routes[urlWithoutOrigin];
	console.log("router view:", view);

	let content = document.getElementById('content');

    if (view) {
		fetch(view.fetch)
		.then(response => response.text())
		.then(html => {
			content.innerHTML = html;
			if (callback && typeof callback === 'function') {
				callback();
			}
		})
		.catch(error => console.error('Error loading logged-in content:', error));
    } else {
		console.log("router else");
        history.replaceState("", "", "/");
        router();
    }
};

// Handle navigation
window.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
        e.preventDefault();
        history.pushState("", "", e.target.href);
        router();
    } else if (e.target.matches("[data-logout]")) {
		e.preventDefault();
		history.pushState("", "", e.target.href);
		console.log("logout pressed");
		let logoutUrl = "/accounts/logout/"; //maybe dynamic url later from django template
		fetch(logoutUrl, {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			}
		})
		.then(response => {
			if (response.ok) {
				// document.getElementById("navbar").innerHTML = '';
				// document.getElementById("content").innerHTML = '';
				// fetch("/stranger")
				// 	.then(response => response.text())
				// 	.then(html => {
				// 		document.getElementById("content").innerHTML = html;
				// 	})
				// 	.catch(error => console.error('Error loading content:', error));
				console.log("logout successful");
        		router();
			} else {
				console.error("Logout failed");
			}
		})
		.catch(error => console.error('Error:', error));
	}
});

// Update router
window.addEventListener("popstate", router);

// load page the first time here
window.addEventListener("DOMContentLoaded", router);


export {getCookie, router, ws};