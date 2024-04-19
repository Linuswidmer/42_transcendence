import Lobby from '../pong_online/lobby.js';

let lobby = new Lobby(ws, username);



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showSection(url) {  
	console.log("show section url:", url);
	//get DIV element where we want to display the new HTML
	let dynamicDIV = document.getElementById('dynamicDIV');
	dynamicDIV.innerHTML = '';

	//fetch HTML
	fetch(url)
	.then(response => response.text())
	.then(text => {
		//set fetched HTML in the DIV
		dynamicDIV.innerHTML = text;
		
		//try to get the script element
		let scriptElement = dynamicDIV.querySelector('script');

		//if there is a script element, attach it to the DIV
		if (scriptElement) {
			console.log("showSection: there is a script tag in the html")
			fetchJS(scriptElement.src);
		} else {
			console.log("showSection: there is no script tag in the html");
		}

		
		console.log('Section loaded');
	});
}

function fetchJS(url) {
	fetch(url)
    .then(response => response.text())
    .then(script => {
        let scriptElement = document.createElement('script');
        scriptElement.textContent = script;
		// console.log('js:', scriptElement.textContent);
        document.body.appendChild(scriptElement);
    })
    .catch(error => console.error('Error:', error));
}
