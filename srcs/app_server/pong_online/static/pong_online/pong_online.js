///////////////////////////////
// General Setup
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

const ws = window.ws;

///////////////////////////////
// Setup Scoreboard

let     leftScore = 0;
let     rightScore = 0;
const   leftScoreElement = document.getElementById('leftScore');
const   rightScoreElement = document.getElementById('rightScore');

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
	constructor(x, y) {
		super(x, y, 'paddle');
	}

	set_score(score) {
		this.score = score;
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
        this.ws.onmessage = (e) => this.handleMessage(e);
    }

    handleMessage(e) {
        try {
            const data = JSON.parse(e.data);
			if (data.type === 'send_to_group') {
				switch (data.identifier) {
					case 'redirect_to_game_page':
						// this.handleRedirect(data);
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
				this.entities[id] = new Paddle(norm2width(entity.relX), norm2height(entity.relY));
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
		}
	}

	handle_game_over() {

	}

    // ...
}

// After establishing the WebSocket connection
const game = new Game(ws, canvas, ctx);




///////////////////////////////
// Setup Game Objects
// let	entities = [];
// let iteration_time;

// let     ballX;
// let     ballY;
// let		ballRadius;

// let		paddleWidth;
// let		paddleHeight;

// let     leftPaddleX = 0;
// let     leftPaddleY = 0;
// let     rightPaddleX = 0
// let     rightPaddleY = 0

// /*****************************************************************************/
// /*                               Game functions                              */
// /*****************************************************************************/
// // function drawBall(x, y) {
// //     ctx.beginPath();
// //     ctx.arc(x, y, ballRadius, 0, Math.PI*2);
// // 	// ctx.ellipse(ballX, ballY, ballRadiusX, ballRadiusY, 0, 0, Math.PI*2);
// //     ctx.fillStyle = "#000";
// //     ctx.fill();
// //     ctx.closePath();

// 	// let ballImage = new Image();
// 	// ballImage.src = '../static/pong_online/dvd_screen_saver.png'; // Replace with the path to your image

// 	// ctx.beginPath();
// 	// // Draw the image at the ball's position, adjusting for the image's size
// 	// ctx.drawImage(ballImage, ballX - ballRadiusX, ballY - ballRadiusY, ballRadiusX * 2, ballRadiusY * 2);

// 	// ctx.closePath();
// // }

// // function drawPaddle(x, y) {
// //     ctx.fillStyle = '#000';
// //     ctx.fillRect(x, y, paddleWidth, paddleHeight);
// // }

// function draw_entities(entities, context) {
// 	// console.log("Draw");
//     // Clear the canvas
//     ctx.clearRect(0, 0, canvas.width, canvas.height);
// 	for (var id in entities) {
// 		var entity = entities[id];
// 		entity.draw(context);
// 	}
// }

// function gameOver() {
//     console.log('Game Over');
// 	clearInterval(update_interval);
//     // document.getElementById('gameOverMessage').style.display = 'block';
//     // document.getElementById('reloadLocalGame').style.display = 'block';
//     // document.getElementById('reloadPlayOptions').style.display = 'block';
// }

// function norm2height(relativeY) {
// 	return (relativeY * canvas.height)
// }

// function norm2width(relativeX) {
// 	return (relativeX * canvas.width)
// }

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

// function initialize_entities(data, entities) {
// 	if (data.initial_entity_data.entities !== undefined) {
// 		for (var id in data.initial_entity_data.entities) {
// 			var entity = data.initial_entity_data.entities[id];
			
// 			if (entity.entity_type === 'ball') {
// 				entities[id] = new Ball(norm2width(entity.relX), norm2height(entity.relY));
// 				entities[id].set_radius(norm2height(entity.relBallRadius));
// 			} else if (entity.entity_type === 'paddle') {
// 				entities[id] = new Paddle(norm2width(entity.relX), norm2height(entity.relY));
// 				entities[id].set_dimensions(norm2width(entity.relPaddleWidth),
// 					norm2height(entity.relPaddleHeight));
// 			} else {
// 				console.log("Warning: an unknown entity was send by the server");
// 			}
//         }
// 	}
// 	if (data.rel_entity_sizes.relBallRadius !== undefined) {
// 		ballRadius = norm2height(data.rel_entity_sizes.relBallRadius);
// 	}
// 	if (data.rel_entity_sizes.relPaddleHeight !== undefined) {
// 		paddleHeight = norm2height(data.rel_entity_sizes.relPaddleHeight);
// 	}
// 	if (data.rel_entity_sizes.relPaddleWidth !== undefined) {
// 		paddleWidth = norm2width(data.rel_entity_sizes.relPaddleWidth);
// 	}

// 	// console.log("radius: ", ballRadius, " paddleHeight: ", paddleHeight, " paddleWidth: ", paddleWidth);
// }

// //update local entities in game with information sent by server tick
// function process_server_update(server_entity_data, entities) {
// 	try{
// 		if (server_entity_data.entities) {
// 			server_entities = server_entity_data.entities;
// 		}

// 		for (var id in server_entities) {
// 			var entity = entities[id];
	
// 			// entity.position_buffer.push([server_entity_data.timestamp,
// 			// 	norm2width(server_entities[id].relX),
// 			// 	norm2height(server_entities[id].relY)]);
// 			entity.set_position(norm2width(server_entities[id].relX), norm2height(server_entities[id].relY));
// 		}
// 		if (leftScore == WINNING_SCORE || rightScore == WINNING_SCORE)
// 			gameOver();
// 	} catch (error) {
// 		console.log('Error parsing JSON:', error);
// 	}
// }

// // Define the local update rate in hertz (frames per second)
// const INTERPOLATION_RATE = 60;

// //TODO: find another way to access same websocket in multiple js files
// // let ws = window.ws
// function join_game(modus) {
// 	console.log("inside game join");
// 	let update_interval; //interval function
// 	let entities = [] //object (list) -> passed by ref
// 	let iteration_time;

// 	//prevents client from sending a lot of messages when holding a button pressed
// 	let keys = {
// 		'KeyA': false,
// 		'KeyD': false,
// 		'KeyJ': false,
// 		'KeyL': false,
// 	};

// 	window.addEventListener('keydown', function(event) {
// 		let data = undefined;
// 		if (event.code === 'KeyA' && !keys[event.code]) {
// 			keys[event.code] = true;
// 			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveUp'};
// 		} else if (event.code === 'KeyD'  && !keys[event.code]) {
// 			keys[event.code] = true;
// 			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveDown'};
// 		} else if (modus === 'local' && event.code === 'KeyJ' && !keys[event.code]) {
// 			keys[event.code] = true;
// 			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveUp'};
// 		} else if (modus === 'local' && event.code === 'KeyL'  && !keys[event.code]) {
// 			keys[event.code] = true;
// 			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveDown'};
// 		}
	
// 		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
// 			ws.send(JSON.stringify(data));
// 		}
// 	});
	
// 	window.addEventListener('keyup', function(event) {
// 		let data = undefined;
// 		if (event.code === 'KeyA') {
// 			keys[event.code] = false;
// 			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveUp'};
// 		} else if (event.code === 'KeyD') {
// 			keys[event.code] = false;
// 			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveDown'};
// 		} else if (modus === 'local' && event.code === 'KeyJ') {
// 			keys[event.code] = false;
// 			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveUp'};
// 		} else if (modus === 'local' && event.code === 'KeyL') {
// 			keys[event.code] = false;
// 			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveDown'};
// 		}
	
// 		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
// 			ws.send(JSON.stringify(data));
// 		}
// 	});
// };

// // Handle messages sent by the server
// ws.onmessage = function(e) {
// 	try{
// 		const data = JSON.parse(e.data);
// 		latest_data = data;
// 		if (data.type === "redirect_to_game_page") {
// 			console.log(e.data);
// 			fetch('/singleGameStats/?matchName=' + data.matchName + '&username=' + data.user)
// 			.then(response => response.text())
// 			.then(data => {
// 				document.body.innerHTML = data;
// 			}).catch((error) => {
// 				console.error('Error:', error);
// 			});
// 		}

// 		if (data.type === "playerId") {
// 			ws.user_id = data.playerId;
// 			console.log("user id from server", ws.user_id);
// 		}
// 		if (data.type === "group_game_state_update" && data.rel_entity_sizes !== undefined
// 			&& data.initial_entity_data !== undefined) {
// 			initialize_entities(data, entities);
// 			console.log("init data", entities);
// 			if (data.iteration_time) {
// 				iteration_time = data.iteration_time;
// 			}
// 			//clear interval
// 			// clearInterval(update_interval);

// 			// // Set a new update interval
// 			// //this interval is interpolating between game updates and drawing the entities
// 			// update_interval = setInterval(function() {
// 			// 	interpolateEntities(entities, iteration_time);
// 			// 	draw_entities(entities, ctx);
// 			// }, 1000 / INTERPOLATION_RATE);

// 		}
// 		if (data.type === "group_game_state_update" && data.entity_data !== undefined) {
// 			process_server_update(data.entity_data, entities);
// 			draw_entities(entities, ctx);
// 			// console.log("entities after server update:", entities);
// 		}
		
		
// 	} catch (error) {
// 		console.log('Error parsing JSON:', error);
// 	}
// };

// class 


const startButton = document.getElementById('startButtonRemote');
if (startButton) {
	startButton.addEventListener('click', function() {
		console.log("modus", ws.modus);
		ws.send(JSON.stringify({'type': 'start', 'modus': ws.modus}));
		// join_game(ws.modus);
		console.log('Start button clicked pong online');
	});
}

// const leaveButton = document.getElementById('leaveGame');
// if (leaveButton) {
// 	leaveButton.addEventListener('click', function() {
// 		console.log("modus", ws.modus);
// 		ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': username, 'modus': ws.modus}));
// 		console.log('leaveButtonclicked');

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
// 	});
// }

// window.addEventListener('beforeunload', function(event) {
// 	//only send when tehre is a game running
//     ws.send(JSON.stringify({'type': 'player_left', 'player': ws.username}));
// });
