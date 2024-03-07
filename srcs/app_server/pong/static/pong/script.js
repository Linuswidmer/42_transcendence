// Hide button(s) and show the canvas and other elements
document.getElementById("startLocalGame").addEventListener("click", function() {
    this.style.display = "none";
    document.getElementById("pongCanvas").style.display = "block";
    document.getElementById("leftScore").style.display = "block";
    document.getElementById("rightScore").style.display = "block";

    // Start the game
    startLocalGame();
});