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

class Paddle {
	constructor() {
		this.y = 0;
		this.speed = PADDLE_SPEED;
		this.position_buffer = [];
	}

	applyInput(input) {
		this.y += input.press_time * this.speed;
	}
}

///////////////////////////////
// Client

class Client {
	constructor(canvas) {
		//paddle or other game objects
		this.paddle = new Paddle();

		//input state
		this.key_up = false;
		this.key_down = false;

		//UI
		this.canvas = canvas;
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
		this.paddle.applyInput(input);
	}
}

var element = function(id) {
	return document.getElementById(id);
}

var keyHandler = function(e) {
	if (e.key == 'd') {
	  player2.key_right = (e.type == "keydown");
	} else if (e.key == 'a') {
	  player2.key_left = (e.type == "keydown");
	} else {
	  console.log(e)
	}
}

var renderWorld = function(canvas, entities) {
	// Clear the canvas.
	canvas.width = canvas.width;
  
	var colours = ["blue", "red"];
  
	for (var i in entities) {
	  var entity = entities[i];
  
	  // Compute size and position.
	  var radius = canvas.height*0.9/2;
	  var x = (entity.x / 10.0)*canvas.width;
  
	  // Draw the entity.
	  var ctx = canvas.getContext("2d");
	  ctx.beginPath();
	  ctx.arc(x, canvas.height / 2, radius, 0, 2*Math.PI, false);
	  ctx.fillStyle = colours[entity.entity_id];
	  ctx.fill();
	  ctx.lineWidth = 5;
	  ctx.strokeStyle = "dark" + colours[entity.entity_id];
	  ctx.stroke();
	}
}

window.addEventListener('keydown', keyHandler);

var player1 = new Client(element("player1_canvas"));
