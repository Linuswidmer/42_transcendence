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

let     leftPaddleX = 0;
let     leftPaddleY = 0;
let     rightPaddleX = 0
let     rightPaddleY = 0

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

function join_game(name) {
	const protocol = window.location.protocol.match(/^https/) ? 'wss' : 'ws';
    // const wsUrl = protocol + `://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

    const ws = new WebSocket(
        protocol + '://' + window.location.host + '/ws/pong_online/game/'
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
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'moveUp'};
		} else if (event.code === 'KeyD'  && !keys[event.code]) {
			keys[event.code] = true;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'moveDown'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	});
	
	window.addEventListener('keyup', function(event) {
		let data = undefined;
		if (event.code === 'KeyA') {
			keys[event.code] = false;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'stopMoveUp'};
		} else if (event.code === 'KeyD') {
			keys[event.code] = false;
			data = {'playerId': ws.user_id, 'type': 'keypress', 'action': 'stopMoveDown'};
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