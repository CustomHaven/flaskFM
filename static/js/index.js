let button = document.getElementById("handle_click");

button.addEventListener("click", function() {
  let toggle = button.textContent === "Show Top 3" ? false : true;
  button.textContent = toggle ? "Show Top 3" : "All";

  // formData

  const formData = new FormData();
  formData.append("button_clicked", toggle);



  fetch("/dashboard", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ "button_clicked": toggle })
    // body: formData
  })
  .then(response => {
    if (response.ok) {
      console.log("Button click successful");
      return response.json();
    } else {
      console.error("Button click failed");
      throw new Error("Button click failed");
    }
  })
  .then(data => {
    // Update UI with received data
    console.log("are we going to update the .popular_song?")
    document.querySelector(".popular_songs").innerHTML = data.unpopular_songs_html;
  })
  .catch(error => {
    console.error("Error:", error);
  });
});