function tick_test(name) {

    const roomName = "my_room";
    const wsUrl = `ws://${window.location.host}/ws/pong/${roomName}/`; // this has to be modified to be a unique identifier

    const ws = new WebSocket(wsUrl);

    ws.onopen = function(e) {
        // telling the server that the client is ready
        console.log('WebSocket connection established');
        let data = {'username': name};
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
        
			console.log(e.data);
            // if (data.leftPaddleY !== undefined) {
            //     serverLeftPaddleY = data.leftPaddleY;
            // }
            // if (data.rightPaddleY !== undefined) {
            //     serverRightPaddleY = data.rightPaddleY;
            // }
            // if (data.ballX !== undefined) {
            //     ballX = data.ballX;
            // }
            // if (data.ballY !== undefined) {
            //     ballY = data.ballY;
            // }
            // if (data.scorePlayerLeft !== undefined) {
            //     leftScore = data.scorePlayerLeft;
            //     leftScoreElement.textContent = leftScore;
            // }
            // if (data.scorePlayerRight !== undefined) {
            //     rightScore = data.scorePlayerRight;
            //     rightScoreElement.textContent = rightScore;
            // }
        } catch (error) {
            console.log('Error parsing JSON:', error);
        }
    };
};

document.getElementById('nameForm').addEventListener('submit', function(event) {
	event.preventDefault();

	var name = document.getElementById('nameInput').value;
    // Start the game
    tick_test(name);
});