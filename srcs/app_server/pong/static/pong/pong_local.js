
/*****************************************************************************/
/*                             Intitialization                               */
/*****************************************************************************/

///////////////////////////////
// Define Constants

const   GAME_REFRESH_RATE = 10;
const   PADDLE_WIDTH = 10;
const   PADDLE_HEIGHT = 60;
const   PADDLE_SPEED = 5;
const   BALL_RADIUS = 10;

///////////////////////////////
// General Setup
const   keys = {};

window.addEventListener('keydown', handleKeyDown);
window.addEventListener('keyup', handleKeyUp);

function handleKeyDown(e) {
    keys[e.key] = true;
}

function handleKeyUp(e) {
    keys[e.key] = false;
}

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

let     clientLeftPaddleY = 0;
let     clientRightPaddleY = 0;
let     serverLeftPaddleY = 0
let     serverRightPaddleY = 0

let     ballX;
let     ballY;

/*****************************************************************************/
/*                               Game functions                              */
/*****************************************************************************/

function drawPaddle(x, y) {
    ctx.fillStyle = '#000';
    ctx.fillRect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT);
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, BALL_RADIUS, 0, Math.PI*2);
    ctx.fillStyle = "#000";
    ctx.fill();
    ctx.closePath();
}

function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    drawPaddle(0, serverLeftPaddleY);
    drawPaddle(canvas.width - PADDLE_WIDTH, serverRightPaddleY);
    drawBall();
}

function update() {

    clientLeftPaddleY = serverLeftPaddleY;
    clientRightPaddleY = serverRightPaddleY;

    if (keys['w'] && clientLeftPaddleY > 0) {
        clientLeftPaddleY -= PADDLE_SPEED;
    }
    if (keys['s'] && clientLeftPaddleY < canvas.height - PADDLE_HEIGHT) {
        clientLeftPaddleY += PADDLE_SPEED;
    }
    if (keys['ArrowUp'] && clientRightPaddleY > 0) {
        clientRightPaddleY -= PADDLE_SPEED;
    }
    if (keys['ArrowDown'] && clientRightPaddleY < canvas.height - PADDLE_HEIGHT) {
        clientRightPaddleY += PADDLE_SPEED;
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function gameOver() {
    console.log('Game Over');
    document.getElementById('gameOverMessage').style.display = 'block';
    document.getElementById('reloadLocalGame').style.display = 'block';
    document.getElementById('reloadPlayOptions').style.display = 'block';
}

/*****************************************************************************/
/*                          Websocket Communication                          */
/*****************************************************************************/

function startLocalGame(localPlayer1Name, localPlayer2Name) {

    console.log('Starting local game');

    const roomName = "my_room";
    const wsUrl = `ws://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

    const ws = new WebSocket(wsUrl);

    ws.onopen = function(e) {
        // telling the server that the client is ready
        console.log('WebSocket connection established');
        let data = {'ready': true};
        ws.send(JSON.stringify(data));

        gameLoop();

        setInterval(function() {
            let data = {'leftPaddleY': clientLeftPaddleY,
                        'rightPaddleY': clientRightPaddleY};
            if (ws.readyState === WebSocket.OPEN)
                ws.send(JSON.stringify(data));
        }, GAME_REFRESH_RATE);
    }; 

    // Handle messages sent by the server
    ws.onmessage = function(e) {
        try{
            const data = JSON.parse(e.data);
        
            if (data.leftPaddleY !== undefined) {
                serverLeftPaddleY = data.leftPaddleY;
            }
            if (data.rightPaddleY !== undefined) {
                serverRightPaddleY = data.rightPaddleY;
            }
            if (data.ballX !== undefined) {
                ballX = data.ballX;
            }
            if (data.ballY !== undefined) {
                ballY = data.ballY;
            }
            if (data.scorePlayerLeft !== undefined) {
                leftScore = data.scorePlayerLeft;
                leftScoreElement.textContent = leftScore;
            }
            if (data.scorePlayerRight !== undefined) {
                rightScore = data.scorePlayerRight;
                rightScoreElement.textContent = rightScore;
            }
            if (data.gameOver !== undefined) {
                gameOver();
            }
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    };
};
