import Lobby from "./lobby.js";
import Game from "./pong_online.js"

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

let active_script = null;

function activate_js(component_name) {
	switch (component_name) {
		case '/lobby':
			active_script = lobby;
			break;
		case '/pong_online':
			active_script = game;
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
	let dynamicDIV = document.getElementById('dynamicDIV');

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

let lobby_button = document.getElementById('lobbyBtn');
lobby_button.addEventListener('click', () => {
	fetch_html_replace_dynamicDIV_activate_js('/lobby', true);
});

export default fetch_html_replace_dynamicDIV_activate_js;
// console.log("test");

// showSection('/dashboard');