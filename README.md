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
	        <li><a href="#containerization">Containerization</a></li>
	        <li><a href="#server-side-pong-and-API">Server-side Pong and API</a></li>
	        <li><a href="#user-management">User Management</a></li>
	        <li><a href="#OAuth">OAuth</a></li>
	        <li><a href="#AI-Opponent">AI Opponent</a></li>
	        <li><a href="#Statistics-and-dashboard">Statistics and Dashboard</a></li>
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

### 2.1 Server-side pong & API

### 2.1 User management

### 2.1 OAuth

### 2.1 AI-opponent
In order to develop a challenging computer opponent, two methods were considered: training a model or using geometry to predict the ball's position. Although the NEAT-trained model performed very well, the project's requirement that the AI opponent must only view the game once per second made a well-trained model almost useless. This is because the decisions made between each second are based on an outdated game state. In contrast, with geometry, you can accurately calculate where the ball will be in the next second. Therefore, you only need to know the current ball position, direction, and game dimensions. With this information, and some additional work to account for (multiple) bounces on the sidewalls, we created a challenging AI opponent. Here’s how:
![ai_geom_overview](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/ai_geometry_overview.png)

To predict the ball position at the AI oppenent's wall the following needs to be done. Let's have a closer look at the blue example:
![ai_geom_overview](https://raw.githubusercontent.com/Linuswidmer/42_transcendence/main/images/ai_prediction_example.png)
 - Construct a trinangle with the ball's direction β, the distance from the ball to the AI opponent's wall, to calculate the length of the oppsite site of the angle β.
 - Add the absolute value of the calculated side length to the ball's y position. This is like projecting the bounce to virtual added fields, because the result can be outside the field. If the result is not between 0 and HEIGHT, than there is at least one bounce.
 - Since at the sidewalls the angle of incidence equals the angle of the reflection we just need to 'eliminate' the added virtual canvases. Because every bounce creates on extra projection layer. The actual y_hit can therefore be extracted with the MODULO-operation.
 - The last thing to consider is the amount of bounces. For an even amout of bounces, the y_hit on the real canvas is just the result of the modulo operation. If not we need to subtract the result of the modulo operation from the HEIGHT. (The above red example might be irritating: If the y_virtual_hit is negative, than the absolute value is taken and in could it would be trated as the pink example)

### 2.1 Statistics and Dashboard


