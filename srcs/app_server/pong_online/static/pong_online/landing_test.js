import Lobby from "./lobby.js";
import Game from "./pong_online.js"
import TournamentLobby from "./tournament.js"

const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
	// const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
let ws = new WebSocket(
	protocol + '://' + window.location.host + '/ws/pong_online/game/'
);

console.log("username from request", username);

ws.onopen = function(event) {
	console.log('WebSocket connection established');
	ws.send(JSON.stringify({type: 'username', 'username': username}));
}

const lobby = new Lobby(ws, username);
const game = new Game(ws, username);
const tournament_lobby = new TournamentLobby(ws, username);

let active_script = null;

function extractUntilSecondSlash(inputString) {
	var firstSlashIndex = inputString.indexOf('/');
	if (firstSlashIndex !== -1) {
		var secondSlashIndex = inputString.indexOf('/', firstSlashIndex + 1);
		if (secondSlashIndex !== -1) {
			return inputString.substring(0, secondSlashIndex);
		}
	}
	return inputString;
}

function activate_js(component_name) {
	component_name = extractUntilSecondSlash(component_name);
	console.log('activate_js: component name: ', component_name);
	switch (component_name) {
		case '/lobby':
			active_script = lobby;
			break;
		case '/pong_online':
			active_script = game;
			break;
		case '/tournament':
			active_script = tournament_lobby;
			break;
		default:
			console.log('Unknown component name', component_name);
	}
	if (active_script) {
		console.log("activating script");
		active_script.activate();
	}
}

function fetch_html_replace_dynamicDIV_activate_js(url, fetchJS=false, callback=null) {
	console.log("url:", url);
	//get DIV element where we want to display the new HTML
	let dynamicDIV = document.getElementById('content');

	if (active_script) {
		console.log("there is a script to deactivate");
		active_script.deactivate();
		active_script = null;
	}

	//fetch HTML
	fetch(url)
	.then(response => response.text())
	.then(text => {
		dynamicDIV.innerHTML = text;
		console.log('text:', text);
		console.log('Section loaded');
	})
	.then(() => {
		if (fetchJS) {
			activate_js(url);
		}
	})
	.then(() => {
		if (callback) {
			callback();
		}
	});
}

function fetch_marie(url) {
	fetch(url)
		.then(response => response.text())
		.then(html => {
			document.getElementById("content").innerHTML = html;
			executeJavaScriptInContent(html);
		})
		.catch(error => console.error('Error loading page:', error));
}

function executeJavaScriptInContent(html) {
	const parser = new DOMParser();
	const doc = parser.parseFromString(html, 'text/html');
	const scriptElements = doc.querySelectorAll('script');
	//console.log(scriptElements[0].textContent);
	//console.log(scriptElements[1].textContent);
	//eval(scriptElements[1].textContent)
	scriptElements.forEach(script => {
		 eval(script.textContent);
	});
}

export {fetch_html_replace_dynamicDIV_activate_js, fetch_marie};