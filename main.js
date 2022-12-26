document.getElementById("formChat").addEventListener("submit", function(event) {
    // Prevent the form from being submitted
    event.preventDefault();
  
    // Get the number of days
    const days = document.getElementById("textField").value;
  
    // Create a WebSocket connection to the server
    const ws = new WebSocket("ws://localhost:8000");
  
    ws.onopen = function() {
      // Send the request to the server
      ws.send(days);
    };
  
    // Display the response from the server
    ws.onmessage = function(event) {
        const currentContent = document.getElementById("subscribe").innerHTML;
        document.getElementById("subscribe").innerHTML = currentContent + "<br>"  + "Privat API Answer" + event.data;
      };
  });
  