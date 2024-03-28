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


///////////////////////////////
// Setup Game Objects
let     ballX;
let     ballY;
let		ballRadiusX;
let		ballRadiusY;

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
    // // ctx.arc(ballX, ballY, ballRadius, 0, Math.PI*2);
	// ctx.ellipse(ballX, ballY, ballRadiusX, ballRadiusY, 0, 0, Math.PI*2);
    // ctx.fillStyle = "#000";
    // ctx.fill();
    // ctx.closePath();

	let ballImage = new Image();
	ballImage.src = '../static/pong_online/dvd_screen_saver.png'; // Replace with the path to your image

	ctx.beginPath();
	// Draw the image at the ball's position, adjusting for the image's size
	ctx.drawImage(ballImage, ballX - ballRadiusX, ballY - ballRadiusY, ballRadiusX * 2, ballRadiusY * 2);

	ctx.closePath();
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

//update entities in game with informaation sent by server tick
function update(user_id, data) {
	try{
		if (data.entity_data !== undefined) {
			if (data.entity_data.relBallRadiusY !== undefined) {
                ballRadiusY = norm2height(data.entity_data.relBallRadiusY);
            }
			if (data.entity_data.relBallRadiusX !== undefined) {
                ballRadiusX = norm2width(data.entity_data.relBallRadiusX);
            }
			if (data.entity_data.relPaddleHeight !== undefined) {
                paddleHeight = norm2height(data.entity_data.relPaddleHeight);
            }
			if (data.entity_data.relPaddleWidth !== undefined) {
                paddleWidth = norm2width(data.entity_data.relPaddleWidth);
            }


            if (data.entity_data.relativeBallX !== undefined) {
                ballX = norm2width(data.entity_data.relativeBallX);
            }
            if (data.entity_data.relativeBallY !== undefined) {
                ballY = norm2height(data.entity_data.relativeBallY);
            }
			if (data.entity_data[user_id] !== undefined) {
                leftPaddleX = norm2width(data.entity_data[user_id].relativeX);
                leftPaddleY = norm2height(data.entity_data[user_id].relativeY);
				leftScore = data.entity_data[user_id].score;
				leftScoreElement.textContent = leftScore;
            }
			for (let id in data.entity_data) {
                if (id !== "relativeBallX" && id !== "relativeBallY" && id != "score" && id !== user_id) {
                    rightPaddleX = norm2width(data.entity_data[id].relativeX);
                    rightPaddleY = norm2height(data.entity_data[id].relativeY);
					rightScore = data.entity_data[id].score;
					rightScoreElement.textContent = rightScore;
                }
            }
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
        
			// console.log(e.data);

			if (data.type === "playerId") {
				ws.user_id = data.playerId;
				console.log("user id from server", ws.user_id);
			}
			if (data.type === "group_game_state_update") {
				update(ws.username, data)
			}
			draw()
			
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

// document.getElementById('nameForm').addEventListener('submit', function(event) {
// 	event.preventDefault();
// 	console.log("test")
// 	var name = document.getElementById('nameInput').value;
//     // Start the game
//    join_game(name);
// });