btn = null;
lspan = null;
rspan = null;

function sendState(state) {
    const url = "/toggle";

    console.log("sendState ", url, state);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(state),
    }).then(response => {
        if (!response.ok) {
            console.error('Error sending state to server');
        }
    }).catch(error => {
        console.error('Error sending state to server:', error);
    });
}

function receiveState() {
    const url = "/update";

    function makeHttpRequest() {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();  // Change to response.json() if expecting JSON
            })
            .then(data => {
                console.log('data:', data);
                lspan.classList.toggle("toggle");
                rspan.classList.toggle("toggle");
                btn.textContent = data["relay"];
                if (btn.textContent == "On") {
                    btn.classList.add("on");
                    btn.classList.remove("off");
                } else {
                    btn.classList.remove("on");
                    btn.classList.add("off");
                }
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    // Call the function immediately
    makeHttpRequest();

    // Set the interval to call the function every 2 seconds (2000 milliseconds)
    setInterval(makeHttpRequest, 2000);
}

function controlShelly() {
    if (btn.textContent == "On") {
        btn.textContent = "Off";
        btn.classList.remove("on");
        btn.classList.add("off");
    } else {
        btn.textContent = "On";
        btn.classList.add("on");
        btn.classList.remove("off");
    }
    sendState({"relay": btn.textContent});
}


document.addEventListener("DOMContentLoaded", function() {
    btn = document.getElementById("button");
    lspan = document.getElementById("left");
    rspan = document.getElementById("right");
    receiveState();
});