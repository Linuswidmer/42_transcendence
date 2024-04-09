///////////////////////////////
// Define Constants
const   BALL_RADIUS = 5;
const	PADDLE_WIDTH = 15;
const	PADDLE_HEIGHT = 70;
const	WINNING_SCORE = 3;

///////////////////////////////
// General Setup
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

///////////////////////////////
// Setup Scoreboard

let     leftScore = 0;
let     rightScore = 0;
const   leftScoreElement = document.getElementById('leftScore');
const   rightScoreElement = document.getElementById('rightScore');


class Entity {
	constructor(x, y, type) {
		this.type = type
		this.x = x;
		this.y = y;
		this.position_buffer = [];
	}
}

///////////////////////////////
// Setup Game Objects
let	entities = [];
let iteration_time;

let     ballX;
let     ballY;
let		ballRadius;

let		paddleWidth;
let		paddleHeight;

let     leftPaddleX = 0;
let     leftPaddleY = 0;
let     rightPaddleX = 0
let     rightPaddleY = 0

/*****************************************************************************/
/*                               Game functions                              */
/*****************************************************************************/
function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, ballRadius, 0, Math.PI*2);
	// ctx.ellipse(ballX, ballY, ballRadiusX, ballRadiusY, 0, 0, Math.PI*2);
    ctx.fillStyle = "#000";
    ctx.fill();
    ctx.closePath();

	// let ballImage = new Image();
	// ballImage.src = '../static/pong_online/dvd_screen_saver.png'; // Replace with the path to your image

	// ctx.beginPath();
	// // Draw the image at the ball's position, adjusting for the image's size
	// ctx.drawImage(ballImage, ballX - ballRadiusX, ballY - ballRadiusY, ballRadiusX * 2, ballRadiusY * 2);

	// ctx.closePath();
}

function drawPaddle(x, y) {
    ctx.fillStyle = '#000';
    ctx.fillRect(x, y, paddleWidth, paddleHeight);
}

function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall();
	drawPaddle(leftPaddleX, leftPaddleY);
    drawPaddle(rightPaddleX, rightPaddleY);
}

function gameOver() {
    console.log('Game Over');
    // document.getElementById('gameOverMessage').style.display = 'block';
    // document.getElementById('reloadLocalGame').style.display = 'block';
    // document.getElementById('reloadPlayOptions').style.display = 'block';
}

function norm2height(relativeY) {
	return (relativeY * canvas.height)
}

function norm2width(relativeX) {
	return (relativeX * canvas.width)
}

function interpolateEntities(server_entities) {
	console.log("it: ", iteration_time);
	var now = +new Date();
    var render_timestamp = now - (1000.0 / iteration_time);

	for (var id in server_entities) {
        var entity = entities[id];

        // Find the two authoritative positions surrounding the rendering timestamp.
        var buffer = entity.position_buffer;

        // Drop older positions.
        while (buffer.length >= 2 && buffer[1][0] <= render_timestamp) {
            buffer.shift();
        }

        // Interpolate between the two surrounding authoritative positions.
        if (buffer.length >= 2 && buffer[0][0] <= render_timestamp && render_timestamp <= buffer[1][0]) {
            var x0 = buffer[0][1];
            var x1 = buffer[1][1];
            var y0 = buffer[0][2];
            var y1 = buffer[1][2];
            var t0 = buffer[0][0];
            var t1 = buffer[1][0];

            var new_x = x0 + (x1 - x0) * (render_timestamp - t0) / (t1 - t0);
            var new_y = y0 + (y1 - y0) * (render_timestamp - t0) / (t1 - t0);
            entity.set_position(new_x, new_y);
        }
    }
}

function initialize_entities(data) {
	if (data.rel_entity_sizes.relBallRadius !== undefined) {
		ballRadius = norm2height(data.rel_entity_sizes.relBallRadius);
	}
	if (data.rel_entity_sizes.relPaddleHeight !== undefined) {
		paddleHeight = norm2height(data.rel_entity_sizes.relPaddleHeight);
	}
	if (data.rel_entity_sizes.relPaddleWidth !== undefined) {
		paddleWidth = norm2width(data.rel_entity_sizes.relPaddleWidth);
	}
	if (data.initial_entity_data.entities !== undefined) {
		for (var id in data.initial_entity_data.entities) {
            var entity = data.initial_entity_data.entities[id];
            // Assuming `entities` is an object
            entities[id] = new Entity(entity.relX, entity.relY, id);
        }
		console.log("entities:", entities);
	}

	console.log("radius: ", ballRadius, " paddleHeight: ", paddleHeight, " paddleWidth: ", paddleWidth);
}

//update entities in game with informaation sent by server tick
function update(user_id, data) {
	try{
		iteration_time = data.iteration_time
		if (data.entity_data.entities !== undefined) {
			interpolateEntities(data.entity_data.entities);
		}
		if (leftScore == WINNING_SCORE || rightScore == WINNING_SCORE)
			gameOver()
	} catch (error) {
		console.log('Error parsing JSON:', error);
	}
}

let ws = window.ws
function join_game(modus) {

	// const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

	// console.log(protocol + '://' + window.location.host + '/ws/pong_online/game/')
    // const ws = new WebSocket(
    //     protocol + '://' + window.location.host + '/ws/pong_online/game/'
    // );

	//prevents client from sending a lot of messages when holding a button pressed
	let keys = {
		'KeyA': false,
		'KeyD': false,
		'KeyJ': false,
		'KeyL': false,
	};

	window.addEventListener('keydown', function(event) {
		let data = undefined;
		if (event.code === 'KeyA' && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveUp'};
		} else if (event.code === 'KeyD'  && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'moveDown'};
		} else if (modus === 'local' && event.code === 'KeyJ' && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': 'local_opponent', 'type': 'keypress', 'action': 'moveUp'};
		} else if (modus === 'local' && event.code === 'KeyL'  && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': 'local_opponent', 'type': 'keypress', 'action': 'moveDown'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	});
	
	window.addEventListener('keyup', function(event) {
		let data = undefined;
		if (event.code === 'KeyA') {
			keys[event.code] = false;
			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveUp'};
		} else if (event.code === 'KeyD') {
			keys[event.code] = false;
			data = {'playerId': ws.username, 'type': 'keypress', 'action': 'stopMoveDown'};
		} else if (modus === 'local' && event.code === 'KeyJ') {
			keys[event.code] = false;
			data = {'playerId': 'local_opponent', 'type': 'keypress', 'action': 'stopMoveUp'};
		} else if (modus === 'local' && event.code === 'KeyL') {
			keys[event.code] = false;
			data = {'playerId': 'local_opponent', 'type': 'keypress', 'action': 'stopMoveDown'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	});

    // ws.onopen = function(e) {
    //     // telling the server that the client is ready
    //     console.log('WebSocket connection established');
    //     let data = {'playerId': name};
    //     ws.send(JSON.stringify(data));

    //     // gameLoop();
		
    //     // setInterval(function() {
    //     //     let data = {'leftPaddleY': clientLeftPaddleY,
    //     //                 'rightPaddleY': clientRightPaddleY};
    //     //     if (ws.readyState === WebSocket.OPEN)
    //     //         ws.send(JSON.stringify(data));
    //     // }, GAME_REFRESH_RATE);
    // }; 

    // Handle messages sent by the server
    ws.onmessage = function(e) {
        try{
            const data = JSON.parse(e.data);
			if (data.type === "redirect_to_game_page") {
				console.log(e.data);
				fetch('/singleGameStats/?matchName=' + data.matchName + '&username=' + data.user)
				.then(response => response.text())
				.then(data => {
					document.body.innerHTML = data;
				}).catch((error) => {
					console.error('Error:', error);
				});
			}

			if (data.type === "playerId") {
				ws.user_id = data.playerId;
				console.log("user id from server", ws.user_id);
			}
			if (data.type === "group_game_state_update" && data.rel_entity_sizes !== undefined
				&& data.initial_entity_data !== undefined) {
				initialize_entities(data)
			}
			if (data.type === "group_game_state_update" && data.entity_data !== undefined
				&& data.iteration_time !== undefined) {
				update(ws.username, data)
			}
			// draw()
			
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    };
};


const startButton = document.getElementById('startButtonRemote');
if (startButton) {
	startButton.addEventListener('click', function() {
		console.log("modus", ws.modus);
		ws.send(JSON.stringify({'type': 'start', 'modus': ws.modus}));
		join_game(ws.modus);
		console.log('Start button clicked pong online');
	});
}

const leaveButton = document.getElementById('leaveGame');
if (leaveButton) {
	leaveButton.addEventListener('click', function() {
		console.log("modus", ws.modus);
		ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': username, 'modus': ws.modus}));
		console.log('leaveButtonclicked');

		fetch('/lobby')
				.then(response => response.text())
				.then(data => {
					// Create a temporary DOM div element
					var tempDiv = document.createElement('div');

					// Set its innerHTML to the fetched HTML data
					tempDiv.innerHTML = data;
			
					// Extract the src attribute from the script tag
					var scriptSrc = tempDiv.querySelector('script').src;
			
					// Use the fetched HTML data
					document.body.innerHTML = data;
			
					// Create a new script element
					var script = document.createElement('script');
			
					// Set its src attribute to the extracted src
					script.src = scriptSrc;
					
					// Append the script element to the body of the document
					document.body.appendChild(script);
				})
				.catch((error) => {
					console.error('Error:', error);
				});
	});
}

window.addEventListener('beforeunload', function(event) {
	//only send when tehre is a game running
    ws.send(JSON.stringify({'type': 'player_left', 'player': ws.username}));
});

// document.getElementById('nameForm').addEventListener('submit', function(event) {
// 	event.preventDefault();
// 	console.log("test")
// 	var name = document.getElementById('nameInput').value;
//     // Start the game
//    join_game(name);
// });