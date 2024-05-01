import "./navbar.js"
import "./stranger.js"
import "./profile.js"
import "./profile_list.js"
import "./singleGameStats.js"
import "./tournament_stats.js"
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
    "/": { fetch: "/home/" },
    "/lobby/": { fetch: "/fetch/lobby" },
	"/profile_list/": { fetch: "/fetch/profile_list"},
    "/pong_online/": { fetch: "/fetch/pong_online" },
	"/singleGameStats/": { fetch: () => { return "/fetch" + location.href.replace(location.origin, ''); } },
	"/tournament_stats/": { fetch: () => { return "/fetch" + location.href.replace(location.origin, ''); } },
	"/profile/": { fetch: () => { return "/fetch" + location.href.replace(location.origin, ''); } },
	"/tournament/":  { fetch: () => { return "/fetch" + location.href.replace(location.origin, ''); } },
};

function getFirstPath(urlPath) {
    let parts = urlPath.split('/');
    if (parts.length > 2) {
        return '/' + parts[1] + '/';
    } else {
        return urlPath;
    }
}

let lastRoute = null;

function router(url=null, callback=null) {
	if (typeof url !== 'string') {
		url = null;
	}

	let currentURLPath = lastRoute;
	console.log('Current urlPath: ', currentURLPath)
	console.log('Requested URL: ', url)
	console.log('last route', lastRoute)

	if (url === null) {
		url = location.pathname;
	}
	if (url) {
		let requestedURLPath = getFirstPath(url);
		console.log('Requested urlPath: ', requestedURLPath)
		if (lastRoute === null && requestedURLPath === '/pong_online/'){
			console.log('REFRESH TRIGGERED')
			ws.onopen = function(event) {
				ws.send(JSON.stringify({type: 'unusual_leave'}));
				console.log('UNUSUAL REFRESH SEND');
			}
		}else if (currentURLPath === '/pong_online/'){
			//The only way to leave a game legally is going to the game stats or to the tm lobby if it is a tm game
			if (requestedURLPath !== "/singleGameStats/" && requestedURLPath !== "/tournament/"){
				//I think this triggers yanns leave game logic, should also handle normal leave button presses, since I commented the ws.send out there
				ws.send(JSON.stringify({type: 'unusual_leave'}));
				console.log('UNUSUAL MEME LEAVE');
			}
			history.replaceState("", "", url)
		}else if (currentURLPath === '/tournament/'){
			if (requestedURLPath !== "/pong_online/" && requestedURLPath !== "/tournament_stats/"){
				//I think this triggers yanns working leave tournament logic
				//ws.send(JSON.stringify({'type': 'player_left', 'player': this.username}));
				ws.send(JSON.stringify({type: 'unusual_leave'}));
				console.log('UNUSUAL TM LEAVE');
			}
			history.replaceState("", "", url)
		}else {
			history.pushState("", "", url);
			console.log('USUAL PUSH');
		}
		currentURLPath = requestedURLPath//getFirstPath(location.pathname);
	}

	lastRoute = currentURLPath;
	let view = routes[currentURLPath];

	// console.log("entire url", location.href);
	console.log("router path:", currentURLPath);
	console.log("router view:", view);


	let content = document.getElementById('content');

    if (view) {
		let fetchUrl = typeof view.fetch === 'function' ? view.fetch() : view.fetch;
		fetch(fetchUrl)
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
	let currentURL = location.href.replace(location.origin, '');
    if (e.target.matches("[data-link]")) {
		/* if (currentURL == '/pong_online/' || currentURL.includes('/tournament/')){
			ws.send(JSON.stringify({type: 'reset_consumer_after_unusual_game_leave'}));
			history.replaceState(null, "", "/");
		} */
        e.preventDefault();
        //history.pushState("", "", e.target.href);
		
        router(e.target.href.replace(e.target.origin, '')); //@LEON: das brauchen wir ja dann nicht mehr 
    } else if (e.target.matches("[data-logout]")) {
		/* if (currentURL == '/pong_online/' || currentURL.includes('/tournament/')){
			ws.send(JSON.stringify({type: 'reset_consumer_after_unusual_game_leave'}));
			history.replaceState(null, "", "/");
		} */
		e.preventDefault();
		//history.pushState("", "", e.target.href);
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
				console.log("logout successful");
        		router(e.target.href.replace(e.target.origin, '')); //@LEON: das brauchen wir ja dann nicht mehr 
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
window.addEventListener("DOMContentLoaded", router('/', null));


export {getCookie, router, ws};