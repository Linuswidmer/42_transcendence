/*****************************************************************************/
/*                             Intitialization                               */
/*****************************************************************************/

///////////////////////////////
// Define Constants

const   GAME_REFRESH_RATE = 20;
const   PADDLE_WIDTH = 60;
const   PADDLE_HEIGHT = 10;
const   PADDLE_SPEED = 50;
const   BALL_RADIUS = 10;
const	BALL_SPEED = 5;

class Entity {
	constructor(x, y, speed) {
		this.x = x;
		this.y = y;
		this.speed = speed;
		this.position_buffer = [];
		
		//drawing on 2d canvas
		this.ctx = canvas.getContext("2d");
	}
}

class Paddle extends Entity {
	constructor(x, y, speed) {
		super(x, y, speed);
	}

	applyInput(input) {
		this.x += input.press_time * this.speed;
	}

	draw(color) {
		this.ctx.beginPath();
		this.ctx.rect(this.x, this.y, PADDLE_WIDTH, PADDLE_HEIGHT);
		this.ctx.fillStyle = color;
		this.ctx.fill();
		this.ctx.lineWidth = 5;
		this.ctx.strokeStyle = "dark" + color;
		this.ctx.stroke();
	}
}

class Ball extends Entity {
	constructor(x, y, speed) {
		super(x, y, speed);
		this.radius = BALL_RADIUS;
	}

	draw(color) {
		this.ctx.beginPath();
		this.ctx.arc(this.x, this.y, radius, 0, 2*Math.PI, false);
		this.ctx.fillStyle = color;
		this.ctx.fill();
		this.ctx.lineWidth = 5;
		this.ctx.strokeStyle = "dark" + color;
		this.ctx.stroke();
	}
}

///////////////////////////////
// Client

class Client {
	constructor(canvas, paddle) {
		//local representation of entities
		this.entities = [];
		this.entities.push(paddle);

		this.paddle = paddle;

		//input state
		this.key_left = false;
		this.key_right = false;

		//game improvements
		this.client_side_prediction = true;

		//UI
		this.canvas = canvas;

		//set update rate for processing player input
		this.setUpdateRate(50);
	}

	processInputs() {
		var now_ts = +new Date();
		var last_ts = this.last_ts || now_ts;
		var dt_sec = (now_ts - last_ts) / 1000.0;
		this.last_ts = now_ts;
	  
		// Package player's input.
		var input;
		if (this.key_right) {
		  input = { press_time: dt_sec };
		} else if (this.key_left) {
		  input = { press_time: -dt_sec };
		} else {
		  // Nothing interesting happened.
		  return;
		}

		//client-side prediction
		if (this.client_side_prediction) {
			this.paddle.applyInput(input);
		}
	}

	setUpdateRate(hz) {
		this.update_rate = hz;

		clearInterval(this.update_interval);

		// passing this.update() with an arrow function preservers the Client object
		this.update_interval = setInterval(() => {
		  this.update();
		}, 1000 / this.update_rate);
	}

	update() {
		this.processInputs();
		renderWorld(this.canvas, this.entities);
	}
}

///////////////////////////////
// Helpers

function element(id) {
	return document.getElementById(id);
}

function keyHandler(e) {
	//reset key state
	player1.key_left = false;
	player1.key_right = false;
	if (e.key == 'd') {
	player1.key_right = (e.type == "keydown");
	} else if (e.key == 'a') {
	player1.key_left = (e.type == "keydown");
	} else {
	console.log(e)
	}
}

function renderWorld(canvas, entities) {
	// Clear the canvas.
	canvas.width = canvas.width;
	
	for (var i in entities) {
	var entity = entities[i];

	entity.draw("red");
	}
}

//canvas where the pong game is displayed
const canvas = element('pongCanvas');

//listen to keypresses inside the tab, no matter what html element is selected
window.addEventListener('keydown', keyHandler);
window.addEventListener('keyup', keyHandler);

var paddle1 = new Paddle(50, 50, PADDLE_SPEED);

//create a player
//variable and function declaration is hoisted in JS (automatically moved to the top)
var player1 = new Client(element("pongCanvas"), paddle1);


