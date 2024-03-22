///////////////////////////////
// Define Constants
const   BALL_RADIUS = 5;
const	PADDLE_WIDTH = 70;
const	PADDLE_HEIGHT = 15;

///////////////////////////////
// General Setup
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

///////////////////////////////
// Setup Game Objects
let     ballX;
let     ballY;

let     topPaddleX = 0;
let     topPaddleY = 0;
let     bottomPaddleX = 0
let     bottomPaddleY = 0

/*****************************************************************************/
/*                               Game functions                              */
/*****************************************************************************/
function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, BALL_RADIUS, 0, Math.PI*2);
    ctx.fillStyle = "#000";
    ctx.fill();
    ctx.closePath();
}

function drawPaddle(x, y) {
    ctx.fillStyle = '#000';
    ctx.fillRect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT);
}

function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall();
	drawPaddle(topPaddleX, topPaddleY);
    drawPaddle(bottomPaddleX, bottomPaddleY);
}

// function gameLoop() {
//     update();
//     draw();
//     requestAnimationFrame(gameLoop);
// }

//update entities in game with informaation sent by server tick
function update(user_id, data) {
	try{
		if (data.object_positions !== undefined) {
            if (data.object_positions.ballX !== undefined) {
                ballX = data.object_positions.ballX;
            }
            if (data.object_positions.ballY !== undefined) {
                ballY = data.object_positions.ballY;
            }
			if (data.object_positions[user_id] !== undefined) {
                topPaddleX = data.object_positions[user_id].x;
                topPaddleY = data.object_positions[user_id].y;
            }
			for (let id in data.object_positions) {
                if (id !== "ballX" && id !== "ballY" && id !== user_id) {
                    bottomPaddleX = data.object_positions[id].x;
                    bottomPaddleY = data.object_positions[id].y;
                }
            }
        }
	} catch (error) {
		console.log('Error parsing JSON:', error);
	}
}

function join_game(name) {
	const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

    const ws = new WebSocket(
        protocol + '://' + window.location.host + '/ws/pong/game/'
    );

	//prevents client from sending a lot of messages when holding a button pressed
	let keys = {
		'KeyA': false,
		'KeyD': false
	};

	window.addEventListener('keydown', function(event) {
		let data = undefined;
		if (event.code === 'KeyA' && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'moveLeft'};
		} else if (event.code === 'KeyD'  && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'moveRight'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	});
	
	window.addEventListener('keyup', function(event) {
		let data = undefined;
		if (event.code === 'KeyA') {
			keys[event.code] = false;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'stopMoveLeft'};
		} else if (event.code === 'KeyD') {
			keys[event.code] = false;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'stopMoveRight'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	});

    ws.onopen = function(e) {
        // telling the server that the client is ready
        console.log('WebSocket connection established');
        let data = {'playerId': name};
        ws.send(JSON.stringify(data));

        // gameLoop();
		
        // setInterval(function() {
        //     let data = {'leftPaddleY': clientLeftPaddleY,
        //                 'rightPaddleY': clientRightPaddleY};
        //     if (ws.readyState === WebSocket.OPEN)
        //         ws.send(JSON.stringify(data));
        // }, GAME_REFRESH_RATE);
    }; 

    // Handle messages sent by the server
    ws.onmessage = function(e) {
        try{
            const data = JSON.parse(e.data);
        
			// console.log(e.data);

			if (data.type === "playerId") {
				ws.user_id = data.playerId;
				console.log("user id from server", ws.user_id);
			}
			if (data.type === "state_update") {
				update(ws.user_id, data)
			}
			draw()
			
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    };
};


const startButton = document.getElementById('startButton');
if (startButton) {
	startButton.addEventListener('click', function() {
		join_game("");
		console.log('Start button clicked pong online');
	});
}

// document.getElementById('nameForm').addEventListener('submit', function(event) {
// 	event.preventDefault();
// 	console.log("test")
// 	var name = document.getElementById('nameInput').value;
//     // Start the game
//    join_game(name);
// });