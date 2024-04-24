import {fetch_html_replace_dynamicDIV_activate_js, fetch_with_internal_js} from "./landing_test.js";

// const leaveButton = document.getElementById('leaveGame');
// if (leaveButton) {
// 	leaveButton.addEventListener('click', function() {
// 		console.log("modus", ws.modus);
// 		ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': username, 'modus': ws.modus}));
// 		console.log('leaveButtonclicked');
// 	});
// }
//////////////////////////////
// Helper functions


  class Entity {
    constructor(x, y, type) {
      this.type = type
      this.x = x;
      this.y = y;
      this.position_buffer = [];
    }

    set_position(x, y) {
      this.x = x;
      this.y = y;
    }
  }

  class Ball extends Entity {
    constructor(x, y) {
      super(x, y, 'ball');
    }

    set_radius(radius) {
      this.radius = radius
    }

    draw(context) {
      // console.log("draw ball", this);
      context.beginPath();
      context.arc(this.x, this.y, this.radius, 0, Math.PI*2);
      context.fillStyle = "#000";
      context.fill();
      context.closePath();
    }
  }

class Paddle extends Entity {
    constructor(username, x, y, screen_pos) {
      super(x, y, 'paddle');
      this.username = username;
      // console.log("paddle username:", this.username);
      this.screen_pos = screen_pos;
      this.score_display = document.getElementById(this.screen_pos === 'left' ? 'leftScore' : 'rightScore');
    }

    set_score(score) {
      this.score_display.textContent = score;
    }
    set_score(score) {
      this.score_display.textContent = score;
    }

    set_dimensions(width, height) {
      this.width = width;
      this.height = height;
    }
    set_dimensions(width, height) {
      this.width = width;
      this.height = height;
    }

    draw(context) {
      // console.log("draw paddle", this);
      context.fillStyle = '#000';
        context.fillRect(this.x, this.y, this.width, this.height);
    }
}

class js_wrapper {
	activate() {
		throw new Error("Subclasses must override this method.");
	}

	deactivate () {
		throw new Error("Subclasses must override this method.");
	}
}


// In the Game class
class Game extends js_wrapper {
	constructor(ws, username) {
		super();
        this.ws = ws;
		this.username = username;

        this.entities = [];
        this.iterationTime = null;
		this.modus = null;

    }

	norm2height(relativeY) {
		return (relativeY * this.canvas.height)
	}
	
	norm2width(relativeX) {
		return (relativeX * this.canvas.width)
	}

	activate() {
		this.ws.onmessage = (e) => this.handle_message(e);

		this.loggedInMsg = document.getElementById('loggedInMessage');
		this.loggedInMsg.textContent += this.username;

		this.canvas = document.getElementById('pongCanvas');
		this.ctx = this.canvas.getContext('2d');

		this.start_game_button = document.getElementById('startGameButton');
		this.start_game_button.addEventListener('click', 
			this.handle_start_game_button_click);
		
		this.leave_game_button = document.getElementById('leaveGame');
		this.leave_game_button.addEventListener('click',
		this.handle_leave_game_button_click);
	}

	deactivate() {
		this.ws.onmessage = null;
		this.start_game_button.removeEventListener('click', this.handle_start_game_button_click);
        this.leave_game_button.removeEventListener('click', this.handle_leave_game_button_click);
	}

	handle_start_game_button_click = () => {
		this.start_game_button.style.display = 'none';
		this.ws.send(JSON.stringify({'type': 'start', 'modus': 'remote'}));
		console.log('Start button remote clicked');
	}
	
	handle_leave_game_button_click = () => {
		this.ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': this.username, 'modus': this.modus}));
		fetch_html_replace_dynamicDIV_activate_js('/lobby', true);
		console.log('leaveButtonclicked');
	}

    handle_message(e) {
        try {
            const data = JSON.parse(e.data);
			//console.log("pong message: ", data)
			if (data.type === 'send_to_group') {
				switch (data.identifier) {
					case 'deliver_init_game_data':
						console.log("received, deliver_init:", data);
						this.handle_game_view_population(data);
						break;
					case 'game_end':
						this.handle_game_over(data);
						break;
					case 'game_update':
						this.handle_game_update(data);
						this.draw_entities();
						break;
					case 'start_game':
						console.log('received start game msg from server');
						break;
					case 'initial_game_data':
						this.handle_initial_game_data(data);
						this.setup_keys();
						window.addEventListener('beforeunload', () => {
							//only send when tehre is a game running
							this.ws.send(JSON.stringify({'type': 'player_left', 'player': ws.username}));
						});
						break;
					default:
						console.log('Unknown message', data);
				}
			} else if (data.type == 'redirect_to_tournament_stats') {
				console.log(window.location.origin + '/tournament_stats/' + data.tournament_id)
				fetch_with_internal_js('/tournament_stats/' + data.tournament_id);
				//window.location.href = window.location.origin + '/tournament_stats/' + data.tournament_id;
			} else if (data.type == 'redirect_to_tournament_lobby') {
				console.log('/tournament/' + data.tournament_id)
				fetch_html_replace_dynamicDIV_activate_js('/tournament/' + data.tournament_id, true, () => {
					this.ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': data.tournament_id}));
				});
			}
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    }

	draw_entities() {
		// Clear the canvas
		this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
		for (var id in this.entities) {
			var entity = this.entities[id];
			entity.draw(this.ctx);
		}
	}

	handle_initial_game_data(data) {
		this.entities = [];
		var prompt = document.getElementById('userPrompt');
		prompt.textContent = "Good Luck - Play SAUBER!"

		this.leave_game_button.style.display = 'none';

		for (var id in data.initial_entity_data.entities) {
			var entity = data.initial_entity_data.entities[id];
			console.log("handle_entity:", entity);
			if (entity.entity_type === 'ball') {
				this.entities[id] = new Ball(this.norm2width(entity.relX), this.norm2height(entity.relY));
				this.entities[id].set_radius(this.norm2height(entity.relBallRadius));
			} else if (entity.entity_type === 'paddle') {
				this.entities[id] = new Paddle(id, this.norm2width(entity.relX), this.norm2height(entity.relY), entity.screen_pos);
				this.entities[id].set_dimensions(this.norm2width(entity.relPaddleWidth),
					this.norm2height(entity.relPaddleHeight));
			} else {
				console.log("Warning: an unknown entity was send by the server");
			}
		}
		this.modus = data.modus;
		console.log("modus:", this.modus);
	}

      setup_keys() {
      let keys = {
        'KeyA': false,
        'KeyD': false,
        'KeyJ': false,
        'KeyL': false,
      };

		window.addEventListener('keydown', (event) => {
			let data = undefined;
			if (event.code === 'KeyA' && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': this.username, 'type': 'keypress', 'action': 'moveUp'};
			} else if (event.code === 'KeyD'  && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': this.username, 'type': 'keypress', 'action': 'moveDown'};
			} else if (this.modus === 'local' && event.code === 'KeyJ' && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveUp'};
			} else if (this.modus === 'local' && event.code === 'KeyL'  && !keys[event.code]) {
				keys[event.code] = true;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveDown'};
			}
		
			if (typeof data !== 'undefined' && this.ws.readyState === WebSocket.OPEN) {
				this.ws.send(JSON.stringify(data));
			}
		});
				
		window.addEventListener('keyup', (event) => {
			let data = undefined;
			if (event.code === 'KeyA') {
				keys[event.code] = false;
				data = {'playerId': this.username, 'type': 'keypress', 'action': 'stopMoveUp'};
			} else if (event.code === 'KeyD') {
				keys[event.code] = false;
				data = {'playerId': this.username, 'type': 'keypress', 'action': 'stopMoveDown'};
			} else if (this.modus === 'local' && event.code === 'KeyJ') {
				keys[event.code] = false;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveUp'};
			} else if (this.modus === 'local' && event.code === 'KeyL') {
				keys[event.code] = false;
				data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveDown'};
			}
		
			if (typeof data !== 'undefined' && this.ws.readyState === WebSocket.OPEN) {
				this.ws.send(JSON.stringify(data));
			}
		});
    }

	handle_game_update(data) {
		let server_entities = data.entity_data.entities;
		console.log("server entities", server_entities);
		console.log("local entities:", this.entities);
		for (var id in server_entities) {
			var entity = this.entities[id];
	
			// entity.position_buffer.push([server_entity_data.timestamp,
			// 	norm2width(server_entities[id].relX),
			// 	norm2height(server_entities[id].relY)]);
			entity.set_position(this.norm2width(server_entities[id].relX), this.norm2height(server_entities[id].relY));
			if (entity.type === "paddle") {
				entity.set_score(server_entities[id].score)
			}
		}
	}

	handle_game_over(data) {
		//clear the local entities, they get loaded again for a new game
		const statsURL = '/singleGameStats/?matchName=' + data.matchName + '&username=' + data.user;
		fetch_with_internal_js(statsURL);
	}

	handle_game_view_population(data)
	{
		var left_name_display = document.getElementById('leftPlayerName');
		var right_name_display = document.getElementById('rightPlayerName');
		var prompt = document.getElementById('userPrompt');

		this.modus = data['modus'];

		if (data.hasOwnProperty("player1")){
			if (data["player1"] == this.username) {
				right_name_display.textContent = "Right Player: You";
				this.start_game_button.style.display = 'none';
			}else{
				right_name_display.textContent = "Right Player: " + data["player1"];
			}
		}
		if (!data.hasOwnProperty("player2")){
			left_name_display.textContent = "Left Player: ?";
			prompt.textContent = "Waiting for another Player . . .";
		}
		if (data.hasOwnProperty("player2")){
			if (this.username == data["player2"]) {
				left_name_display.textContent = "Left Player: You";
				prompt.textContent = data["player1"] + " is waiting. Press start to play " + data.match_name + " !";
			}
			else {
				left_name_display.textContent = "Left Player: " + data["player2"];
				prompt.textContent = "Wait for " + data["player2"] + " to start the match " + data.match_name + " !";
			}
		}
	} 
}

// After establishing the WebSocket connection
// const game = new Game(ws, canvas, ctx);

export default Game;
// function interpolateEntities(entities, iteration_time) {
// 	var now = +new Date();
//     var render_timestamp = now - (1000.0 * iteration_time);


  // 	for (var id in entities) {
  //         var entity = entities[id];

  //         // Find the two authoritative positions surrounding the rendering timestamp.
  //         var buffer = entity.position_buffer;

  //         // Drop older positions.
  //         while (buffer.length >= 2 && buffer[1][0] <= render_timestamp) {
  //             buffer.shift();
  //         }
  //         // Interpolate between the two surrounding authoritative positions.
  // 		// console.log("render_timestamp:", render_timestamp);
  // 		// console.log("now:", now);
  // 		// console.log("first buffer element time:", buffer[0][0]);
  // 		// console.log("second buffer element time:", buffer[1][0]);
  //         if (buffer.length >= 2 && buffer[0][0] <= render_timestamp && render_timestamp <= buffer[1][0]) {
  // 			// console.log("interpol")
  //             var x0 = buffer[0][1];
  //             var x1 = buffer[1][1];
  //             var y0 = buffer[0][2];
  //             var y1 = buffer[1][2];
  //             var t0 = buffer[0][0];
  //             var t1 = buffer[1][0];

  //             var new_x = x0 + (x1 - x0) * (render_timestamp - t0) / (t1 - t0);
  //             var new_y = y0 + (y1 - y0) * (render_timestamp - t0) / (t1 - t0);
  //             entity.set_position(new_x, new_y);
  //         }
  //     }
  // }

  // const INTERPOLATION_RATE = 60;


  // 			//clear interval
  // 			// clearInterval(update_interval);

  // 			// // Set a new update interval
  // 			// //this interval is interpolating between game updates and drawing the entities
  // 			// update_interval = setInterval(function() {
  // 			// 	interpolateEntities(entities, iteration_time);
  // 			// 	draw_entities(entities, ctx);
  // 			// }, 1000 / INTERPOLATION_RATE);

// const startGameButton = document.getElementById('startGameButton');
// if (startGameButton) {
// 	startGameButton.addEventListener('click', function() {
// 		ws.send(JSON.stringify({'type': 'start'}));
// 		console.log('Start button remote clicked');
// 		startGameButton.style.display = 'none';
// 	});
// }
