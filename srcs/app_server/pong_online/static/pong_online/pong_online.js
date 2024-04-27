import {router, ws} from "../userManagement/main.js"

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

class Game extends HTMLElement {
    constructor() {
        super();

		this.username = this.getAttribute('data-username');
		console.log("username pong_online:", this.username);
		
		this.entities = [];
		this.iterationTime = null;
		this.modus = null;

		this.keys = {
			'KeyA': false,
			'KeyD': false,
			'KeyJ': false,
			'KeyL': false,
		}


        this.innerHTML = /*html*/`
			<div id="loggedInMessage">Logged in as: </div>

			<div id="userPrompt">Waiting for BLAH to start the game: </div>
		
			<div id="centeredContent">
				<div class="container" id="pongGamePage">
					<div id="scoreBoard">
						<div id="leftScore"></div>
						<div id="leftPlayerName">Left player: </div>
						<div id="rightScore"></div>
						<div id="rightPlayerName">Right player: </div>
					</div>
					<canvas id="pongCanvas" width="600" height="400"></canvas>
				</div>
				<button id="startGameButton">Start</button>
				<button id="leaveGame">leaveGame_backToLobby</button>
			</div>
        `;

		ws.onmessage = (e) => this.handle_message(e);

		this.loggedInMsg = document.querySelector('#loggedInMessage');
		this.loggedInMsg.textContent += this.username;

		this.canvas = document.querySelector('#pongCanvas');
		this.ctx = this.canvas.getContext('2d');

		this.start_game_button = document.querySelector('#startGameButton');
		this.start_game_button.addEventListener('click', 
			this.handle_start_game_button_click);
		
		this.leave_game_button = document.querySelector('#leaveGame');
		this.leave_game_button.addEventListener('click',
		this.handle_leave_game_button_click);
    }

	norm2height(relativeY) {
		return (relativeY * this.canvas.height)
	}
	
	norm2width(relativeX) {
		return (relativeX * this.canvas.width)
	}

	handle_beforeunload = () => {
		ws.send(JSON.stringify({'type': 'player_left', 'player': this.username}));
	}

	handle_start_game_button_click = () => {
		this.start_game_button.style.display = 'none';
		ws.send(JSON.stringify({'type': 'start', 'modus': 'remote'}));
		console.log('Start button remote clicked');
	}
	
	handle_leave_game_button_click = () => {
		ws.send(JSON.stringify({type: 'leave', 'action': 'leave', 'username': this.username, 'modus': this.modus}));
		history.pushState("", "", "/lobby");
		router();
		console.log('leaveButtonclicked');
	}

	add_event_listener() {
		window.addEventListener('keydown', this.handle_keydown);
		window.addEventListener('keyup', this.handle_keyup);
		window.addEventListener('beforeunload', this.handle_beforeunload);	
	}

	remove_event_listener() {
		window.removeEventListener('keydown', this.handle_keydown);
		window.removeEventListener('keyup', this.handle_keyup);
		window.removeEventListener('beforeunload', this.handle_beforeunload);
	}

    handle_message(e) {
        try {
            const data = JSON.parse(e.data);
			//console.log("pong message: ", data)
			if (data.type === 'send_to_group') {
				switch (data.identifier) {
					case 'deliver_init_game_data':
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
						this.add_event_listener();
						break;
					default:
						console.log('Unknown message', data);
				}
			} else if (data.type == 'redirect_to_tournament_stats') {
				this.remove_event_listener();
				let tournamentStatsUrl = '/tournament_stats/' + data.tournament_id;
				history.pushState("", "", tournamentStatsUrl);
				router();
				// fetch_with_internal_js('/tournament_stats/' + data.tournament_id);
			} else if (data.type == 'redirect_to_tournament_lobby') {
				this.remove_event_listener();
				let tournamentLobbyUrl = '/tournament/' + data.tournament_id;
				history.pushState("", "", tournamentLobbyUrl);
				router()(() => {
					ws.send(JSON.stringify({type: 'tournament_lobby_update', 'tournament_id': data.tournament_id}));
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

	handle_keydown = (event) => {
		let data = undefined;
		if (event.code === 'KeyA' && !this.keys[event.code]) {
			this.keys[event.code] = true;
			data = {'playerId': this.username, 'type': 'keypress', 'action': 'moveUp'};
		} else if (event.code === 'KeyD'  && !this.keys[event.code]) {
			this.keys[event.code] = true;
			data = {'playerId': this.username, 'type': 'keypress', 'action': 'moveDown'};
		} else if (this.modus === 'local' && event.code === 'KeyJ' && !this.keys[event.code]) {
			this.keys[event.code] = true;
			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveUp'};
		} else if (this.modus === 'local' && event.code === 'KeyL'  && !this.keys[event.code]) {
			this.keys[event.code] = true;
			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'moveDown'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
	}
				
	handle_keyup= (event) => {
		let data = undefined;
		if (event.code === 'KeyA') {
			this.keys[event.code] = false;
			data = {'playerId': this.username, 'type': 'keypress', 'action': 'stopMoveUp'};
		} else if (event.code === 'KeyD') {
			this.keys[event.code] = false;
			data = {'playerId': this.username, 'type': 'keypress', 'action': 'stopMoveDown'};
		} else if (this.modus === 'local' && event.code === 'KeyJ') {
			this.keys[event.code] = false;
			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveUp'};
		} else if (this.modus === 'local' && event.code === 'KeyL') {
			this.keys[event.code] = false;
			data = {'playerId': 'DUMP_LOCAL', 'type': 'keypress', 'action': 'stopMoveDown'};
		}
	
		if (typeof data !== 'undefined' && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(data));
		}
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
		this.remove_event_listener();
		const statsURL = '/singleGameStats/?matchName=' + data.matchName + '&username=' + data.user;
		history.pushState("", "", statsURL);
		router();
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



customElements.define("pong-game", Game);
