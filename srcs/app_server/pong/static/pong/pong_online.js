///////////////////////////////
// Define Constants
const   BALL_RADIUS = 10;


///////////////////////////////
// General Setup
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

///////////////////////////////
// Setup Game Objects
let     ballX;
let     ballY;

/*****************************************************************************/
/*                               Game functions                              */
/*****************************************************************************/
function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, BALL_RADIUS, 0, Math.PI*2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();
}

function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawBall();
}

// function gameLoop() {
//     update();
//     draw();
//     requestAnimationFrame(gameLoop);
// }

//update entities in game with informaation sent by server tick
function update(data) {
	try{
		if (data.object_positions !== undefined) {
            if (data.object_positions.ballX !== undefined) {
                ballX = data.object_positions.ballX;
            }
            if (data.object_positions.ballY !== undefined) {
                ballY = data.object_positions.ballY;
            }
			console.log("ballX:", ballX, " ballY:", ballY);
        }
	} catch (error) {
		console.log('Error parsing JSON:', error);
	}
}

function join_game(name) {

    const roomName = "my_room";
    const wsUrl = `ws://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

    const ws = new WebSocket(wsUrl);

	window.addEventListener('keydown', function(event) {
		// Check if the space key was pressed
		if (event.code === 'Space') {
			// Create the message
			let data = {'playerId': ws.user_id, 'type': 'thrust'};

			// Send the message if the WebSocket connection is open
			if (ws.readyState === WebSocket.OPEN) {
				ws.send(JSON.stringify(data));
			}
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
				update(data)
			}
			draw()
			
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    };
};

document.getElementById('nameForm').addEventListener('submit', function(event) {
	event.preventDefault();

	var name = document.getElementById('nameInput').value;
    // Start the game
   join_game(name);
});