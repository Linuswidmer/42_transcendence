function element(id) {
	return document.getElementById(id);
}
  
const CANVAS_HEIGHT = element("server_canvas").height
const CANVAS_WIDTH = element("server_canvas").width

// =============================================================================
//  An Entity in the world.
// =============================================================================

class Entity {
	constructor(x, y, speed) {
		this.x = x;
		this.y = y;
		this.speed = speed;
		this.position_buffer = [];
	}
}

const   PADDLE_WIDTH = 60;
const   PADDLE_HEIGHT = 10;

class Paddle extends Entity {
	constructor(x, y, speed) {
		super(x, y, speed);
	}

	applyInput(input) {
		this.x += input.press_time * this.speed;
	}

	draw(canvas, color) {
		//drawing on 2d canvas
		this.ctx = canvas.getContext("2d");

		this.ctx.beginPath();
		this.ctx.rect(this.x, this.y, PADDLE_WIDTH, PADDLE_HEIGHT);
		this.ctx.fillStyle = color;
		this.ctx.fill();
		this.ctx.lineWidth = 5;
		this.ctx.strokeStyle = "dark" + color;
		this.ctx.stroke();
	}
}

const	BALL_RADIUS = 5;
const	BALL_DX = 30;
const	BALL_DY = 30;
const	BALL_ACCELERATION = 0.1;


class Ball extends Entity {
	constructor(x, y, speed) {
		super(x, y, speed);
		this.radius = BALL_RADIUS;
		this.dx = BALL_DX;
		this.dy = BALL_DY;
		this.acceleration = BALL_ACCELERATION;
	}

	resetPosition() {
		this.x = CANVAS_WIDTH / 2;
		this.y = CANVAS_HEIGHT / 2;
		this.dx = BALL_DX;
		this.dy = BALL_DY;
		this.acceleration = BALL_ACCELERATION;
	}

	draw(canvas, color) {
		//drawing on 2d canvas
		this.ctx = canvas.getContext("2d");

		this.ctx.beginPath();
		this.ctx.arc(this.x, this.y, this.radius, 0, 2*Math.PI, false);
		this.ctx.fillStyle = color;
		this.ctx.fill();
		this.ctx.lineWidth = 5;
		this.ctx.strokeStyle = "dark" + color;
		this.ctx.stroke();
	}

	accelerate(x, y, dx, dy, accel, dt) {
		let x2  = x + (dt * dx) + (accel * dt * dt * 0.5);
		let y2  = y + (dt * dy) + (accel * dt * dt * 0.5);
		let dx2 = dx + (accel * dt) * (dx > 0 ? 1 : -1);
		let dy2 = dy + (accel * dt) * (dy > 0 ? 1 : -1);
		return { nx: (x2-x), ny: (y2-y), x: x2, y: y2, dx: dx2, dy: dy2 };
	}

	intercept (x1, y1, x2, y2, x3, y3, x4, y4, d) {
		var denom = ((y4-y3) * (x2-x1)) - ((x4-x3) * (y2-y1));
		if (denom != 0) {
		  var ua = (((x4-x3) * (y1-y3)) - ((y4-y3) * (x1-x3))) / denom;
		  if ((ua >= 0) && (ua <= 1)) {
			var ub = (((x2-x1) * (y1-y3)) - ((y2-y1) * (x1-x3))) / denom;
			if ((ub >= 0) && (ub <= 1)) {
			  var x = x1 + (ua * (x2-x1));
			  var y = y1 + (ua * (y2-y1));
			  return { x: x, y: y, d: d};
			}
		  }
		}
		return null;
	}

	ballIntercept(ball, rect, nx, ny) {
		var pt;
		if (nx < 0) {
		  pt = this.intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
									 rect.right  + ball.radius, 
									 rect.top    - ball.radius, 
									 rect.right  + ball.radius, 
									 rect.bottom + ball.radius, 
									 "right");
		}
		else if (nx > 0) {
		  pt = this.intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
									 rect.left   - ball.radius, 
									 rect.top    - ball.radius, 
									 rect.left   - ball.radius, 
									 rect.bottom + ball.radius,
									 "left");
		}
		if (!pt) {
		  if (ny < 0) {
			pt = this.intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
									   rect.left   - ball.radius, 
									   rect.bottom + ball.radius, 
									   rect.right  + ball.radius, 
									   rect.bottom + ball.radius,
									   "bottom");
		  }
		  else if (ny > 0) {
			pt = this.intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
									   rect.left   - ball.radius, 
									   rect.top    - ball.radius, 
									   rect.right  + ball.radius, 
									   rect.top    - ball.radius,
									   "top");
		  }
		}
		return pt;
	}
	
	update(dt, leftPaddle, rightPaddle) {
		let pos = this.accelerate(this.x, this.y, this.dx, this.dy, this.acceleration, dt);
		let maxX = CANVAS_WIDTH;
		let maxY = CANVAS_HEIGHT;
		let minX = 0;
		let minY = 0;

		if ((pos.dy > 0) && (pos.y > maxY)) {
		//   pos.y = maxY;
		//   pos.dy = -pos.dy;
			this.resetPosition();
			return;
		}
		else if ((pos.dy < 0) && (pos.y < minY)) {
		//   pos.y = minY;
		//   pos.dy = -pos.dy;
			this.resetPosition();
			return;
		}
		else if ((pos.dx > 0) && (pos.x > maxX)) {
			pos.x = maxX;
			pos.dx = -pos.dx;
		}
		else if ((pos.dx < 0) && (pos.x < minX)) {
			pos.x = minX;
			pos.dx = -pos.dx;
		}

		var paddle = (pos.dx < 0) ? leftPaddle : rightPaddle;
		var pt     = this.ballIntercept(this, paddle, pos.nx, pos.ny);

		if (pt) {
			switch(pt.d) {
			case 'left':
			case 'right':
				pos.x = pt.x;
				pos.dx = -pos.dx;
				break;
			case 'top':
			case 'bottom':
				pos.y = pt.y;
				pos.dy = -pos.dy;
				break;
			}

			// add/remove spin based on paddle direction
			if (paddle.up)
			pos.dy = pos.dy * (pos.dy < 0 ? 0.5 : 1.5);
			else if (paddle.down)
			pos.dy = pos.dy * (pos.dy > 0 ? 0.5 : 1.5);
		}


		this.x = pos.x;
		this.y = pos.y;
		this.dx = pos.dx;
		this.dy = pos.dy;
	}
}


// =============================================================================
//  A message queue with simulated network lag.
// =============================================================================
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

  // =============================================================================
  //  The Client.
  // =============================================================================
  var Client = function(canvas, status) {
	// Local representation of the entities.
	this.entities = {};
  
	// Input state.
	this.key_left = false;
	this.key_right = false;
  
	// Simulated network connection.
	this.network = new LagNetwork();
	this.server = null;
	this.lag = 0;
  
	// Unique ID of our entity. Assigned by Server on connection.
	this.entity_id = null;
  
	// Data needed for reconciliation.
	this.client_side_prediction = false;
	this.server_reconciliation = false;
	this.input_sequence_number = 0;
	this.pending_inputs = [];
  
	// Entity interpolation toggle.
	this.entity_interpolation = true;
  
	// UI.
	this.canvas = canvas;
	this.status = status;
  
	// Update rate.
	this.setUpdateRate(50);
  }
  
  
  Client.prototype.setUpdateRate = function(hz) {
	this.update_rate = hz;
  
	clearInterval(this.update_interval);
	this.update_interval = setInterval(
	  (function(self) { return function() { self.update(); }; })(this),
	  1000 / this.update_rate);
  }
  
  
  // Update Client state.
  Client.prototype.update = function() {
	// Listen to the server.
	this.processServerMessages();
  
	if (this.entity_id == null) {
	  return;  // Not connected yet.
	}
  
	// Process inputs.
	this.processInputs();
  
	// Interpolate other entities.
	if (this.entity_interpolation) {
	  this.interpolateEntities();
	}
  
	// Render the World.
	renderWorld(this.canvas, this.entities);
  
	// Show some info.
	var info = "Non-acknowledged inputs: " + this.pending_inputs.length;
	this.status.textContent = info;
  }
  
  
  // Get inputs and send them to the server.
  // If enabled, do client-side prediction.
  Client.prototype.processInputs = function() {
	// Compute delta time since last update.
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
  
	// Send the input to the server.
	input.input_sequence_number = this.input_sequence_number++;
	input.entity_id = this.entity_id;
	this.server.network.send(this.lag, input);
  
	// Do client-side prediction.
	if (this.client_side_prediction) {
	  this.entities[this.entity_id].applyInput(input);
	}
  
	// Save this input for later reconciliation.
	this.pending_inputs.push(input);
  }
  
  
// Process all messages from the server, i.e. world updates.
// If enabled, do server reconciliation.
Client.prototype.processServerMessages = function() {
	while (true) {
		var message = this.network.receive();
		if (!message) {
		break;
		}

		// World state is a list of entity states.
		for (var i = 0; i < message.length; i++) {
		var state = message[i];

		// If this is the first time we see this entity, create a local representation.
		if (!this.entities[state.entity_id]) {
			let entity;
			if (state.type == "paddle") {
				entity = new Paddle(this.canvas.width / 2, 0, 200);
			} else if (state.type == "ball") {
				entity = new Ball(this.canvas.width / 2, this.canvas.height / 2, 0);
			} else {
				console.log("client received entity that is neither ball nor paddle");
			}
			entity.entity_id = state.entity_id;
			this.entities[state.entity_id] = entity;
		}

		var entity = this.entities[state.entity_id];

		if (state.entity_id == this.entity_id) {
			// Received the authoritative position of this client's entity.
			entity.x = state.x;
			entity.y = state.y;

			if (this.server_reconciliation) {
			// Server Reconciliation. Re-apply all the inputs not yet processed by
			// the server.
			var j = 0;
			while (j < this.pending_inputs.length) {
				var input = this.pending_inputs[j];
				if (input.input_sequence_number <= state.last_processed_input) {
				// Already processed. Its effect is already taken into account into the world update
				// we just got, so we can drop it.
				this.pending_inputs.splice(j, 1);
				} else {
				// Not processed by the server yet. Re-apply it.
				entity.applyInput(input);
				j++;
				}
			}
			} else {
			// Reconciliation is disabled, so drop all the saved inputs.
			this.pending_inputs = [];
			}
		} else {
			// Received the position of an entity other than this client's.

			if (!this.entity_interpolation) {
			// Entity interpolation is disabled - just accept the server's position.
			entity.x = state.x;
			entity.y = state.y;
			} else {
			// Add it to the position buffer.
			var timestamp = +new Date();
			entity.position_buffer.push([timestamp, state.x]);
			}
		}
		}
	}
}
  
  
  Client.prototype.interpolateEntities = function() {
	// Compute render timestamp.
	var now = +new Date();
	var render_timestamp = now - (1000.0 / server.update_rate);
  
	for (var i in this.entities) {
	  var entity = this.entities[i];
  
	  // No point in interpolating this client's entity.
	  if (entity.entity_id == this.entity_id) {
		continue;
	  }
  
	  // Find the two authoritative positions surrounding the rendering timestamp.
	  var buffer = entity.position_buffer;
  
	  // Drop older positions.
	  while (buffer.length >= 2 && buffer[1][0] <= render_timestamp) {
		buffer.shift();
	  }
  
	  // Interpolate between the two surrounding authoritative positions.
	  if (buffer.length >= 2 && buffer[0][0] <= render_timestamp && render_timestamp <= buffer[1][0]) {
		var x0 = buffer[0][1];
		var x1 = buffer[1][1];
		var t0 = buffer[0][0];
		var t1 = buffer[1][0];
  
		entity.x = x0 + (x1 - x0) * (render_timestamp - t0) / (t1 - t0);
	  }
	}
  }
  
  
  // =============================================================================
  //  The Server.
  // =============================================================================
  var Server = function(canvas, status) {
	// Connected clients and their entities.
	this.clients = [];
	this.entities = [];
  
	// Last processed input for each client.
	this.last_processed_input = [];
  
	// Simulated network connection.
	this.network = new LagNetwork();
  
	// UI.
	this.canvas = canvas;
	this.status = status;
  
	// Default update rate.
	this.setUpdateRate(10);

  }
  
  Server.prototype.connect = function(client) {
	// Give the Client enough data to identify itself.
	client.server = this;
	client.entity_id = this.clients.length;
	this.clients.push(client);
  
	// Create a new Entity for this Client.
	var entity = new Paddle(client.canvas.width / 2, 0, 200);
	this.entities.push(entity);
	entity.entity_id = client.entity_id;
  
	// Set the initial state of the Entity (e.g. spawn point)
	var spawn_points = [0, client.canvas.height - PADDLE_HEIGHT];
	entity.y = spawn_points[client.entity_id];
  }
  
  Server.prototype.setUpdateRate = function(hz) {
	this.update_rate = hz;
  
	clearInterval(this.update_interval);
	this.update_interval = setInterval(
	  (function(self) { return function() { self.update(); }; })(this),
	  1000 / this.update_rate);
  }
  
  Server.prototype.update = function() {
	let leftPaddle = this.entities[0];
	let rightPaddle = this.entities[1];

	this.ball.update(1, leftPaddle, rightPaddle);
	this.processInputs();
	this.sendWorldState();
	renderWorld(this.canvas, this.entities);
  }
  
  
  // Check whether this input seems to be valid (e.g. "make sense" according
  // to the physical rules of the World)
  Server.prototype.validateInput = function(input) {
	if (Math.abs(input.press_time) > 1/40) {
	  return false;
	}
	return true;
  }
  
  
  Server.prototype.processInputs = function() {
	// Process all pending messages from clients.
	while (true) {
	  var message = this.network.receive();
	  if (!message) {
		break;
	  }
  
	  // Update the state of the entity, based on its input.
	  // We just ignore inputs that don't look valid; this is what prevents clients from cheating.
	  if (this.validateInput(message)) {
		var id = message.entity_id;
		this.entities[id].applyInput(message);
		this.last_processed_input[id] = message.input_sequence_number;
	  }
  
	}
  
	// Show some info.
	var info = "Last acknowledged input: ";
	for (var i = 0; i < this.clients.length; ++i) {
	  info += "Player " + i + ": #" + (this.last_processed_input[i] || 0) + "   ";
	}
	this.status.textContent = info;
  }
  
  
  // Send the world state to all the connected clients.
Server.prototype.sendWorldState = function() {
	// Gather the state of the world. In a real app, state could be filtered to avoid leaking data
	// (e.g. position of invisible enemies).
	var world_state = [];
	var num_clients = this.clients.length;
	let num_entities = this.entities.length;
	let entity_type;

	for (var i = 0; i < num_entities; i++) {
		var entity = this.entities[i];

		if (entity instanceof Ball) {
			entity_type = "ball";
		} else if (entity instanceof Paddle) {
			entity_type = "paddle";
		} else {
			entity_type = "undefined";
		}


		world_state.push({entity_id: entity.entity_id,
						x: entity.x,
						y: entity.y,
						type: entity_type,
						last_processed_input: this.last_processed_input[i]});
	}

	// Broadcast the state to all the clients.
	for (var i = 0; i < num_clients; i++) {
		var client = this.clients[i];
		client.network.send(client.lag, world_state);
	}
}

Server.prototype.addBall = function(canvas) {
	this.ball = new Ball(canvas.width / 2, canvas.height / 2, 0);
	this.ball.entity_id = 2;
	this.entities.push(this.ball);
}

  
  // =============================================================================
  //  Helpers.
  // =============================================================================
  
  // Render all the entities in the given canvas.
  var renderWorld = function(canvas, entities) {
	// Clear the canvas.
	canvas.width = canvas.width;
  
	var colours = ["blue", "red", "green"];
  
	for (var i in entities) {
	  var entity = entities[i];
  
	  // Draw the entity.
	  entity.draw(canvas, colours[entity.entity_id]);
	}
  }
  
  

  // =============================================================================
  //  Get everything up and running.
  // =============================================================================
  
  // World update rate of the Server.
  var server_fps = 4;
  
  
  // Update simulation parameters from UI.
  var updateParameters = function() {
	updatePlayerParameters(player1, "player1");
	updatePlayerParameters(player2, "player2");
	server.setUpdateRate(updateNumberFromUI(server.update_rate, "server_fps"));
	return true;
  }
  
  
  var updatePlayerParameters = function(client, prefix) {
	client.lag = updateNumberFromUI(player1.lag, prefix + "_lag");
  
	var cb_prediction = element(prefix + "_prediction");
	var cb_reconciliation = element(prefix + "_reconciliation");
  
	// Client Side Prediction disabled => disable Server Reconciliation.
	if (client.client_side_prediction && !cb_prediction.checked) {
	  cb_reconciliation.checked = false;
	}
  
	// Server Reconciliation enabled => enable Client Side Prediction.
	if (!client.server_reconciliation && cb_reconciliation.checked) {
	  cb_prediction.checked = true;
	}
  
	client.client_side_prediction = cb_prediction.checked;
	client.server_reconciliation = cb_reconciliation.checked;
  
	client.entity_interpolation = element(prefix + "_interpolation").checked;
  }
  
  
  var updateNumberFromUI = function(old_value, element_id) {
	var input = element(element_id);
	var new_value = parseInt(input.value);
	if (isNaN(new_value)) {
	  new_value = old_value;
	}
	input.value = new_value;
	return new_value;
  }
  
  
  // When the player presses the arrow keys, set the corresponding flag in the client.
  var keyHandler = function(e) {
	if (e.keyCode == 39) {
	  player1.key_right = (e.type == "keydown");
	} else if (e.keyCode == 37) {
	  player1.key_left = (e.type == "keydown");
	} else if (e.key == 'd') {
	  player2.key_right = (e.type == "keydown");
	} else if (e.key == 'a') {
	  player2.key_left = (e.type == "keydown");
	} else {
	  console.log(e)
	}
  }
  document.body.onkeydown = keyHandler;
  document.body.onkeyup = keyHandler;
  
  
  // Setup a server, the player's client, and another player.
  var server = new Server(element("server_canvas"), element("server_status"));
  var player1 = new Client(element("player1_canvas"), element("player1_status"));
  var player2 = new Client(element("player2_canvas"), element("player2_status"));
  
  //for now the order is kind of important
  //player connected first is on the left, second on the right
  //ball has to be added afterwards (i know, not really elegant)
  // Connect the clients to the server.
  server.connect(player1);
  server.connect(player2);
  server.addBall(element("server_canvas"));
  
  
  // Read initial parameters from the UI.
  updateParameters();