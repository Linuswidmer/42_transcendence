var pongModule = (function() {
//////////////////////////////
// Establish ws connection manually for now
// remove later again

// const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';

// console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
// window.ws = new WebSocket(
// 	protocol + '://' + window.location.host + '/ws/pong_online/game/'
// );

// console.log("username", username);


// window.ws.onopen = function(e) {
// 	// telling the server that the client is ready
// 	console.log('WebSocket connection established');
// 	// let data = {'playerId': 'SESSION ID HERE?????'};
// 	// ws.send(JSON.stringify(data));
// 	ws.username = username
// 	ws.send(JSON.stringify({type: 'username', 'username': username}));
// 	// ws.send(JSON.stringify({type: 'lobby_update', 'action': 'display'}));
// };

////////////////////////////////


	///////////////////////////////
	// General Setup
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

const ws = window.ws;

let loggedInMsg = document.getElementById('loggedInMessage');
loggedInMsg.textContent += ws.username;


//////////////////////////////
// Helper functions
function norm2height(relativeY) {
	return (relativeY * canvas.height)
}

	function norm2width(relativeX) {
		return (relativeX * canvas.width)
	}

class Entity {
	constructor(x, y, type) {
		this.type = type
		this.x = x;
		this.y = y;
		this.position_buffer = [];
	}

	set_position(x, y) {
		this.x = x;
		this.y = y;
	}
}

class Ball extends Entity {
	constructor(x, y) {
		super(x, y, 'ball');
	}

	set_radius(radius) {
		this.radius = radius
	}

	draw(context) {
		// console.log("draw ball", this);
		context.beginPath();
		context.arc(this.x, this.y, this.radius, 0, Math.PI*2);
		context.fillStyle = "#000";
		context.fill();
		context.closePath();
	}
}

class Paddle extends Entity {
	constructor(username, x, y, screen_pos) {
		super(x, y, 'paddle');
		this.username = username;
		// console.log("paddle username:", this.username);
		this.screen_pos = screen_pos;
		this.score_display = document.getElementById(this.screen_pos === 'left' ? 'leftScore' : 'rightScore');
        this.name_display = document.getElementById(this.screen_pos === 'left' ? 'leftPlayerName' : 'rightPlayerName');
        this.name_display.textContent += this.username;
	}

	set_score(score) {
		this.score_display.textContent = score;
	}

	set_dimensions(width, height) {
		this.width = width;
		this.height = height;
	}

	draw(context) {
		// console.log("draw paddle", this);
		context.fillStyle = '#000';
    	context.fillRect(this.x, this.y, this.width, this.height);
	}
}

// In the Game class
class Game {
	constructor(ws, canvas, ctx) {
        this.ws = ws;
		this.canvas = canvas;
		this.ctx = ctx;

        this.entities = [];
        this.iterationTime = null;
		this.modus = null;
        this.ws.onmessage = (e) => this.handle_message(e);
    }

    handle_message(e) {
        try {
            const data = JSON.parse(e.data);
			console.log("pong message: ", data)
			if (data.type === 'send_to_group') {
				switch (data.identifier) {
					case 'game_end':
						this.handle_game_over(data);
						break;
					case 'game_update':
						// console.log('received game update from server');
						this.handle_game_update(data);
						this.draw_entities();
						break;
					case 'start_game':
						console.log('received start game msg from server');
						break;
					case 'initial_game_data':
						console.log('received initial game data from server', data);
						this.handle_initial_game_data(data);
						console.log('entities after init:', this.entities);
						this.setup_keys();
						break;
					default:
						console.log('Unknown message', data);
				}
			} else if (data.type == 'redirect_to_tournament_stats') {
				console.log(window.location.origin + '/tournament_stats/' + data.tournament_id)
				window.location.href = window.location.origin + '/tournament_stats/' + data.tournament_id;
			} else if (data.type == 'redirect_to_tournament_lobby') {
				console.log('/tournament/' + data.tournament_id)
				fetch('/tournament/' + data.tournament_id + '/')
					.then(response => response.text())
					/* .then(data => {
						document.body.innerHTML = data
					}) */
					.then(inner_data => {
						// Create a temporary DOM div element
						var tempDiv = document.createElement('div');
	
						// Set its innerHTML to the fetched HTML data
						tempDiv.innerHTML = inner_data;
				
						// Extract the src attribute from the script tag
						var scriptSrc = tempDiv.querySelector('script').src;
				
						// Use the fetched HTML data
						document.body.innerHTML = inner_data;
				
						//console.log(data);
						// Create a new script element
						var script = document.createElement('script');
				
						// Set its src attribute to the extracted src
						script.src = scriptSrc;

						script.onload = function() {
							// This function will be called when the script is fully loaded and executed
							console.log('Script loaded');
							// Send WebSocket message here
							ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': data.tournament_id}));
						};
						
						// Append the script element to the body of the document
						document.body.appendChild(script);
	
					})
					.catch((error) => {
						console.error('Error:', error);
					});
			}
            
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    }

	draw_entities() {
		// Clear the canvas
		ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
		for (var id in this.entities) {
			var entity = this.entities[id];
			entity.draw(this.ctx);
		}
	}

	handle_initial_game_data(data) {
		for (var id in data.initial_entity_data.entities) {
			var entity = data.initial_entity_data.entities[id];
			
			if (entity.entity_type === 'ball') {
				this.entities[id] = new Ball(norm2width(entity.relX), norm2height(entity.relY));
				this.entities[id].set_radius(norm2height(entity.relBallRadius));
			} else if (entity.entity_type === 'paddle') {
				this.entities[id] = new Paddle(id, norm2width(entity.relX), norm2height(entity.relY), entity.screen_pos);
				this.entities[id].set_dimensions(norm2width(entity.relPaddleWidth),
					norm2height(entity.relPaddleHeight));
			} else {
				console.log("Warning: an unknown entity was send by the server");
			}
		}
		this.modus = data.modus;
		console.log("modus:", this.modus);
	}

    setup_keys() {
		let keys = {
			'KeyA': false,
			'KeyD': false,
			'KeyJ': false,
			'KeyL': false,
		};

		window.addEventListener('keydown', (event) => {
			let data = undefined;
			if (event.code === 'KeyA' && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveUp'};
			} else if (event.code === 'KeyD'  && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveDown'};
			} else if (this.modus === 'local' && event.code === 'KeyJ' && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveUp'};
			} else if (this.modus === 'local' && event.code === 'KeyL'  && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveDown'};
			}
		
			if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
				this.ws.send(JSON.stringify(data));
			}
		});
				
		window.addEventListener('keyup', (event) => {
			let data = undefined;
			if (event.code === 'KeyA') {
				keys[event.code] = false;
				data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveUp'};
			} else if (event.code === 'KeyD') {
				keys[event.code] = false;
				data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveDown'};
			} else if (this.modus === 'local' && event.code === 'KeyJ') {
				keys[event.code] = false;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveUp'};
			} else if (this.modus === 'local' && event.code === 'KeyL') {
				keys[event.code] = false;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveDown'};
			}
		
			if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
				this.ws.send(JSON.stringify(data));
			}
		});
    }

	handle_game_update(data) {
		let server_entities = data.entity_data.entities;

		for (var id in server_entities) {
			var entity = this.entities[id];
	
			// entity.position_buffer.push([server_entity_data.timestamp,
			// 	norm2width(server_entities[id].relX),
			// 	norm2height(server_entities[id].relY)]);
			entity.set_position(norm2width(server_entities[id].relX), norm2height(server_entities[id].relY));
			if (entity.type === "paddle") {
				entity.set_score(server_entities[id].score)
			}
		}
	}

	handle_game_over(data) {
		fetch('/singleGameStats/?matchName=' + data.matchName + '&username=' + data.user)
			.then(response => response.text())
			.then(data => {
				document.body.innerHTML = data;
			}).catch((error) => {
				console.error('Error:', error);
			});
	}

    // ...
}

// After establishing the WebSocket connection
const game = new Game(ws, canvas, ctx);


// function interpolateEntities(entities, iteration_time) {
// 	var now = +new Date();
//     var render_timestamp = now - (1000.0 * iteration_time);


// 	for (var id in entities) {
//         var entity = entities[id];

//         // Find the two authoritative positions surrounding the rendering timestamp.
//         var buffer = entity.position_buffer;

//         // Drop older positions.
//         while (buffer.length >= 2 && buffer[1][0] <= render_timestamp) {
//             buffer.shift();
//         }
//         // Interpolate between the two surrounding authoritative positions.
// 		// console.log("render_timestamp:", render_timestamp);
// 		// console.log("now:", now);
// 		// console.log("first buffer element time:", buffer[0][0]);
// 		// console.log("second buffer element time:", buffer[1][0]);
//         if (buffer.length >= 2 && buffer[0][0] <= render_timestamp && render_timestamp <= buffer[1][0]) {
// 			// console.log("interpol")
//             var x0 = buffer[0][1];
//             var x1 = buffer[1][1];
//             var y0 = buffer[0][2];
//             var y1 = buffer[1][2];
//             var t0 = buffer[0][0];
//             var t1 = buffer[1][0];

//             var new_x = x0 + (x1 - x0) * (render_timestamp - t0) / (t1 - t0);
//             var new_y = y0 + (y1 - y0) * (render_timestamp - t0) / (t1 - t0);
//             entity.set_position(new_x, new_y);
//         }
//     }
// }

// const INTERPOLATION_RATE = 60;


// 			//clear interval
// 			// clearInterval(update_interval);

// 			// // Set a new update interval
// 			// //this interval is interpolating between game updates and drawing the entities
// 			// update_interval = setInterval(function() {
// 			// 	interpolateEntities(entities, iteration_time);
// 			// 	draw_entities(entities, ctx);
// 			// }, 1000 / INTERPOLATION_RATE);

const startButtonRemote = document.getElementById('startButtonRemote');
if (startButtonRemote) {
	startButtonRemote.addEventListener('click', function() {
		ws.send(JSON.stringify({'type': 'start', 'modus': 'remote'}));
		console.log('Start button remote clicked');
	});
}

////// later only one button for starting the game

const startButtonLocal = document.getElementById('startButtonLocal');
if (startButtonLocal) {
	startButtonLocal.addEventListener('click', function() {
		ws.send(JSON.stringify({'type': 'start', 'modus': 'local'}));
		console.log('Start button local clicked');
	});
}

const startButtonAi = document.getElementById('startButtonAi');
if (startButtonAi) {
	startButtonAi.addEventListener('click', function() {
		ws.send(JSON.stringify({'type': 'start', 'modus': 'ai'}));
		console.log('Start button ai clicked');
	});
}

const leaveButton = document.getElementById('leaveGame');
if (leaveButton) {
	leaveButton.addEventListener('click', function() {
		console.log("modus", ws.modus);
		ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': username, 'modus': ws.modus}));
		console.log('leaveButtonclicked');
	});
}

window.addEventListener('beforeunload', function(event) {
	//only send when tehre is a game running
	ws.send(JSON.stringify({'type': 'player_left', 'player': ws.username}));
});
// 		fetch('/lobby')
// 				.then(response => response.text())
// 				.then(data => {
	// 					// Create a temporary DOM div element
// 					var tempDiv = document.createElement('div');

// 					// Set its innerHTML to the fetched HTML data
// 					tempDiv.innerHTML = data;
			
// 					// Extract the src attribute from the script tag
// 					var scriptSrc = tempDiv.querySelector('script').src;
			
// 					// Use the fetched HTML data
// 					document.body.innerHTML = data;
			
// 					// Create a new script element
// 					var script = document.createElement('script');
			
// 					// Set its src attribute to the extracted src
// 					script.src = scriptSrc;
					
// 					// Append the script element to the body of the document
// 					document.body.appendChild(script);
// 				})
// 				.catch((error) => {
// 					console.error('Error:', error);
// 				});

})();