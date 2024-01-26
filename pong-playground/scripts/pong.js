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

class LagNetwork {
	constructor() {
		this.messages = [];
	}

	send(lag_ms, message) {
		this.messages.push({recv_ts: +new Date() + lag_ms,
			payload: message});
	}

	receive() {
		var now = +new Date();
		for (var i = 0; i < this.messages.length; i++) {
			var message = this.messages[i];
			if (message.recv_ts <= now) {
				this.messages.splice(i, 1);
				return message.payload;
			}
		}
	}
}

class Client {
	constructor(canvas) {
		//local representation of entities
		this.entities = [];

		//input state
		this.key_left = false;
		this.key_right = false;

		// Simulated network connection.
		this.network = new LagNetwork();
		this.server = null;
		this.lag = 0;

		//identify client
		this.client_id = 0;

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

		// send the input to the server
		input.entity_id = this.client_id;
		this.server.network.send(this.lag. input);

		//client-side prediction
		if (this.client_side_prediction) {
			this.entities[this.client_id].applyInput(input);
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

class Server {
	constructor() {
		// Connected clients and their entities.
		this.clients = [];
		this.entities = [];

		// Simulated network connection.
		this.network = new LagNetwork();

		// Default update rate.
		this.setUpdateRate(10);
	}

	connect(client) {
		client.server = this;

		client.entity_id = this.clients.length;

		this.clients.push(client);
	}

	setUpdateRate(hz) {
		this.update_rate = hz;

		clearInterval(this.update_interval);
		this.update_interval = setInterval(() => { this.update(); },
												1000 / this.update_rate);
	}

	update() {
		this.processInputs();
 		this.sendWorldState();
	}

	processInputs() {
		while (true) {
			let message = this.network.receive();
			if (!message)
				break;

			let id = message.entity_id;
			this.entities[id].applyInput(message);
		}
	}

	sendWorldState() {
		let world_state = [];
		let num_clients = this.clients.length;

		for (var i = 0; i < num_clients; i++) {
			let entity = this.entities[i];
			world_state.push({entity_id: entity.entity_id,
							position: entity.x,
							last_processed_input: this.last_processed_input[i]});
		}
		
    	// Broadcast the state to all the clients.
		for (var i = 0; i < num_clients; i++) {
			var client = this.clients[i];
			client.network.send(client.lag, world_state);
		}
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
