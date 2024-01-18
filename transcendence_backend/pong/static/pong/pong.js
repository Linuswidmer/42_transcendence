/*****************************************************************************/
/*                             Intitialization                               */
/*****************************************************************************/

///////////////////////////////
// Define Constants

const   GAME_REFRESH_RATE = 20;
const   PADDLE_WIDTH = 10;
const   PADDLE_HEIGHT = 60;
const   PADDLE_SPEED = 5;
const   BALL_RADIUS = 10;

///////////////////////////////
// General Setup
let     clientId;
const   keys = {};

console.log('clientID: ', clientId);

window.addEventListener('keydown', handleKeyDown);
window.addEventListener('keyup', handleKeyUp);

function handleKeyDown(e) {
    keys[e.key] = true;
}

function handleKeyUp(e) {
    keys[e.key] = false;
}

function startGame() {
    let data = {'ready': true};
    chatSocket.send(JSON.stringify(data));
}

const startButton = document.getElementById('startButton');
startButton.addEventListener('click', startGame); // crashes if the start game is pressed twice

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
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT);
}

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

    // Draw paddles
    drawPaddle(0, serverLeftPaddleY);
    drawPaddle(canvas.width - PADDLE_WIDTH, serverRightPaddleY);
    drawBall();
}

function update() {

    clientLeftPaddleY = serverLeftPaddleY;
    clientRightPaddleY = serverRightPaddleY;

    if (clientId === 1)
    {
        if (keys['w'] && clientLeftPaddleY > 0) {
            clientLeftPaddleY -= PADDLE_SPEED;
        }
        if (keys['s'] && clientLeftPaddleY < canvas.height - PADDLE_HEIGHT) {
            clientLeftPaddleY += PADDLE_SPEED;
        }
    } else if (clientId === 2)
    {
        if (keys['ArrowUp'] && clientRightPaddleY > 0) {
            clientRightPaddleY -= PADDLE_SPEED;
        }
        if (keys['ArrowDown'] && clientRightPaddleY < canvas.height - PADDLE_HEIGHT) {
            clientRightPaddleY += PADDLE_SPEED;
        }
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

/*****************************************************************************/
/*                          Websocket Communication                          */
/*****************************************************************************/

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/pong/'
);

chatSocket.onopen = function(e) {
    gameLoop();

    setInterval(function() {
    let data = {};
    if (clientId === 1) {
        data = {'leftPaddleY': clientLeftPaddleY};
    } else if (clientId === 2) {
        data = {'rightPaddleY': clientRightPaddleY};
    }
    chatSocket.send(JSON.stringify(data));
    }, GAME_REFRESH_RATE);
}; 

// Handle messages sent by the server
chatSocket.onmessage = function(e) {
    console.log('Message from server:');
    try{
        const data = JSON.parse(e.data);
    
        if (data.client_id !== undefined) {
            clientId = data.client_id;
        }
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
    } catch (error) {
        console.log('Error parsing JSON:', error);
    }
};