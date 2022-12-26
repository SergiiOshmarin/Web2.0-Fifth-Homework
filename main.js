// Send the request to the server when the form is submitted
document.getElementById('formChat').addEventListener('submit', async (event) => {
  event.preventDefault();
  // Send the request to the server
  const response = await fetch(`http://localhost:8000`);
  // Get the response data
  const data = await response.text();
  // Display the response data in the page
  document.getElementById('subscribe').innerHTML = data;
});
