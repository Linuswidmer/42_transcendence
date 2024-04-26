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

console.log("username from request", username);

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

function router(callback=null) {
    let view = location.href.replace(location.origin, '');
	let content = document.getElementById('content');

    if (view) {
		if (view === '/') {
			view = '/home';
		}
		console.log("router view:", view);
		fetch(view)
		.then(response => response.text())
		.then(html => {
			// Replace the content of the main container with the logged-in content
			content.innerHTML = html;
			if (callback && typeof callback === 'function') {
				callback();
			}
		})
		.catch(error => console.error('Error loading logged-in content:', error));
		// document.title = view.title;
    } else {
		console.log("else");
        history.replaceState("", "", "/");
        router();
    }
};

// Handle navigation
window.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
		console.log(location.href.replace(location.origin, ''));
		if (location.href.replace(location.origin, '') == '/pong_online/');
			ws.send(JSON.stringify({type: 'reset_consumer_after_unusual_game_leave'}));
        e.preventDefault();
        history.pushState("", "", e.target.href);
        router();
    } else if (e.target.matches("[data-logout]")) {
		if (location.href.replace(location.origin, '') == '/pong_online/');
			ws.send(JSON.stringify({type: 'reset_consumer_after_unusual_game_leave'}));
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