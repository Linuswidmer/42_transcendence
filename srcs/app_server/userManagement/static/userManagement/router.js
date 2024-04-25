import {fetch_html_replace_dynamicDIV_activate_js, fetch_with_internal_js, getCookie, executeJavaScriptInContent} from "./land.js"


function router() {
    let view = location.pathname;
	let content = document.getElementById('content');

    if (view) {
		if (view === '/') {
			view = 'home';
		}
		console.log("router view:", view);
		fetch(view)
		.then(response => response.text())
		.then(html => {
			// Replace the content of the main container with the logged-in content
			content.innerHTML = html;
		})
		.catch(error => console.error('Error loading logged-in content:', error));
		// document.title = view.title;
    } else {
		console.log("else");
        history.replaceState("", "", "/");
        router();
    }
};

// Handle navigation
window.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
        e.preventDefault();
        history.pushState("", "", e.target.href);
        router();
    } else if (e.target.matches("[data-logout]")) {
		e.preventDefault();
		history.pushState("", "", e.target.href);
		console.log("logout pressed");
		let logoutUrl = "/accounts/logout/"; //maybe dynamic url later from django template
		fetch(logoutUrl, {
			method: "POST",
			headers: {
				"X-CSRFToken": getCookie("csrftoken")
			}
		})
		.then(response => {
			if (response.ok) {
				// document.getElementById("navbar").innerHTML = '';
				// document.getElementById("content").innerHTML = '';
				// fetch("/stranger")
				// 	.then(response => response.text())
				// 	.then(html => {
				// 		document.getElementById("content").innerHTML = html;
				// 	})
				// 	.catch(error => console.error('Error loading content:', error));
				console.log("logout successful");
        		router();
			} else {
				console.error("Logout failed");
			}
		})
		.catch(error => console.error('Error:', error));
	}
});

// Update router
window.addEventListener("popstate", router);

// load page the first time here
window.addEventListener("DOMContentLoaded", router);
