# Transcendence ☀️

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#features">Features</a></li>
		<ul>
	        <li><a href="#2.1-containerization">Containerization</a></li>
	        <li><a href="#2.2-server-side-pong-and-API">Server-side Pong and API</a></li>
	        <li><a href="#2.3-user-management">User Management</a></li>
	        <li><a href="#2.4-OAuth">OAuth</a></li>
	        <li><a href="#2.5-AI-Opponent">AI Opponent</a></li>
	        <li><a href="#2.6-Statistics-and-dashboard">Statistics and Dashboard</a></li>
        </ul>
  </ol>
</details>

## About the project
![transcendence1](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/pong_game.png)


The final project of the 42 Curriculum really put all our programming skills to test!
We developed a containerized web application that let users play the classic PONG game. Locally (on the same machine) or remote (on the network). Our main technology choices were developing the backend with Django. Connecting it to a Postgres Database. Setting up and using websockets for the communication between client and server. Using bootstrap to leverage the style of our website. Due to the projects contraint we had to write all the client interaction on the website using pure vanilla JavaScript.
More thorough explanations can be found in the  section [Features](#Features)

### Built with

## Getting started

### Prerequisites
Warning: `Makefile` is configured for `Linux` use only.
Requires `docker` and `docker-compose`

### Installation
> - Copy the Github repository to  your local machine
> -  Compile with `make`
> - Access the website at https://127.0.0.1:8443
> - To shut the server down, use `Ctrl` + `C`

## Features

### 2.1 Containerization
Our application used Docker and Docker Compose to create a scalable and efficient web application architecture. Our setup includes four containers, each serving a specific role in the application:

-   **Nginx**: Handling HTTP/HTTPS requests, upgrading to websocket connections
-   **Redis**: Used as a message broker and results backend, required for working with websockets in Django's channels framework
-   **Django**: Core application logic, serving the backend. Specificallz using Gunicorn (HTTP requests) and Daphne (Websocket requests)
-   **PostgreSQL**: As a relational database system.

**Benefits of using Docker and (multiple) containers**

The main benefit of using Docker is to ensure *consistency* & *portability*. Consitency means that the application runs the same way regardless of where it is deployed. Portability on the other hand describes that containers can be deployed across different environments with minimal configuration changes.

We could have setup all services in one container, but using multiple containers  offers several advantages:

-   **Separation of Concerns**: Each container is responsible for a specific service, which simplifies maintenance and development. Changes or updates to one service do not affect the others.
-   **Resource Optimization**: Resources can be allocated and optimized for each service individually. For instance, the database container might need more memory, while the web server container might require more CPU.
-   **Improved Fault Isolation**: If one service fails, it does not bring down the entire application. For example, if the Redis container fails, the rest of the application can continue to operate with limited functionality.
-   **Enhanced Security**: Running services in separate containers enhances security by isolating them from each other. This limits the impact of potential vulnerabilities to a single service.

**Drawbacks of using Docker and containers**
While containerization offers many benefits, it had also it's drawbacks: In many parts of the development process, we had to restart an entire container when making minor changes, e.g. for working on the consumers in the Django container. As this became very tedious, we had to come up with a soltion. By running ``make dev`` the Django container launches the Django development server. This replaces the responsibility of nginx, but more importantly the built-in development server tracks changes made to files inside the Django application and restarts the application automatically.
A similar behaviour could have probably been achived using ``docker compose watch``. Something that would be very intersting to investigate in future projects. 

### 2.2 Server-side pong & API

### 2.3 User management

### 2.4 OAuth

### 2.5 AI-opponent
In order to develop a challenging computer opponent, two methods were considered: training a model or using geometry to predict the ball's position. Although the NEAT-trained model performed very well, the project's requirement that the AI opponent must only view the game once per second made a well-trained model almost useless. This is because the decisions made between each second are based on an outdated game state. In contrast, with geometry, you can accurately calculate where the ball will be in the next second. Therefore, you only need to know the current ball position, direction, and game dimensions. With this information, and some additional work to account for (multiple) bounces on the sidewalls, we created a challenging AI opponent. Here’s how:
![ScreenShot](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/ai_geometry_overview.png)

To predict the ball position at the AI oppenent's wall the following needs to be done. Let's have a closer look at the blue example:
![ScreenShot](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/ai_prediction_example.png)
 - Construct a trinangle with the ball's direction β, the distance from the ball to the AI opponent's wall, to calculate the length of the oppsite site of the angle β.
 - Add the absolute value of the calculated side length to the ball's y position. This is like projecting the bounce to virtual added fields, because the result can be outside the field. If the result is not between 0 and HEIGHT, than there is at least one bounce.
 - Since at the sidewalls the angle of incidence equals the angle of the reflection we just need to 'eliminate' the added virtual canvases. Because every bounce creates on extra projection layer. The actual y_hit can therefore be extracted with the MODULO-operation.
 - The last thing to consider is the amount of bounces. For an even amout of bounces, the y_hit on the real canvas is just the result of the modulo operation. If not we need to subtract the result of the modulo operation from the HEIGHT. (The above red example might be irritating: If the y_virtual_hit is negative, than the absolute value is used and it would be trated as the pink example, the y_virtual_hit would then be greater than HEIGHT)

Since the AI opponent knows the ball position at its side of the game it knows where to go. It updates its position internally and in every refresh loop it tells the game with the same mechanism for the user paddle input if it needs to be moved up, down or stay in place. Different levels are acheived by adding a random error to the predicted position. The smaller (easier) the level, the bigger the range to chose the random offset, which is added to the predicted y_hit.

### 2.6 Statistics and Dashboard
To collect game data and show them on the users profile later the following relational database scheme is used:
![ScreenShot](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/DB_schema.png)

- `UserGameStats`: Data set which holds specific game performance data of one user. Therefore it has a one-to-one relation to a user and a many-to-one relation to a game, because always two `UserGameStats` reference one `Games`
- `Games`: Data set which holds general game data. It is referenced by two `UserGameStats`. It can reference a `Tournaments`
- `Tournaments`: Data set which just holds an ID. A tournament is just a collection of games.

When a game is started a class called `GameDataCollector` creates two `UserDataStats` (one for each user), on `Games` and optionally a `Tournaments` instance using Djangos ORM. During the game the `GameDataCollector` modifies the data of these instances. When the game is over, the instances are saved to the Postgre database.

The dashboard on the users profile page gives an overview of the performance data for every



  
