/*****************************************************************************/
/*                             Intitialization                               */
/*****************************************************************************/

///////////////////////////////
// General Setup
let clientId;
const keys = {};
let intervalId;

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

let leftScore = 0;
let rightScore = 0;
const leftScoreElement = document.getElementById('leftScore');
const rightScoreElement = document.getElementById('rightScore');


///////////////////////////////
// Setup Game Objects

const paddleWidth = 10;
const paddleHeight = 60;
const paddleSpeed = 5;

let leftPaddleY = 0;
let rightPaddleY = 0;
let leftPaddleUpdatePos = 0;
let rightPaddleUpdatePos = 0;
let serverLeftPaddleY = 0
let serverRightPaddleY = 0

let ballX;
let ballY;
let ballRadius = 10;

/*****************************************************************************/
/*                               Game functions                              */
/*****************************************************************************/

function drawPaddle(x, y) {
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, paddleWidth, paddleHeight);
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, ballRadius, 0, Math.PI*2);
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.closePath();
}

function draw() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    drawPaddle(0, serverLeftPaddleY);
    drawPaddle(canvas.width - paddleWidth, serverRightPaddleY);
    drawBall();
}

function update() {

    leftPaddleY = serverLeftPaddleY;
    rightPaddleY = serverRightPaddleY;

    if (clientId === 1)
    {
        if (keys['w'] && leftPaddleY > 0) {
            leftPaddleY -= paddleSpeed;
        }
        if (keys['s'] && leftPaddleY < canvas.height - paddleHeight) {
            leftPaddleY += paddleSpeed;
        }
    } else if (clientId === 2)
    {
        if (keys['ArrowUp'] && rightPaddleY > 0) {
            rightPaddleY -= paddleSpeed;
        }
        if (keys['ArrowDown'] && rightPaddleY < canvas.height - paddleHeight) {
            rightPaddleY += paddleSpeed;
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

// Handle messages sent by the server
chatSocket.onmessage = function(e) {
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
};

chatSocket.onopen = function(e) {
    // Initialize paddle positions

    // Start the game loop
    gameLoop();

    intervalId = setInterval(function() {
    let data = {};
    if (clientId === 1) {
        data = {'leftPaddleY': leftPaddleY};
    } else if (clientId === 2) {
        data = {'rightPaddleY': rightPaddleY};
    }
    chatSocket.send(JSON.stringify(data));
}, 20);
};