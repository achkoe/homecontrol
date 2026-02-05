var eValve, eHistory;

function getStatus() {
    url = "/get"
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();  
        })
        .then(data => {
            console.log('data:', data);
            eValve.classList.remove("off");
            eValve.classList.remove("on");
            eValve.classList.remove("error");
            if (data.status == "ok") {
                eValve.innerText = data.history[0].switch ? "on" : "off";
                eValve.classList.add(data.history[0].switch ? "on" : "off");
            } else {                
                eValve.innerText = data.status
                eValve.classList.add("error");
            }
            let text = new Array();
            data.history.forEach((value) => {
                console.log(value);
                text.push(`${value.switch} | ${value.time}`);
            });
            eHistory.innerText = text.join("<br/>");
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}
    
window.onload = (event) => {
    console.log("onload");
    eValve = document.getElementById("valve");
    eHistory = document.getElementById("history");
    // Set the interval to call the function every 2 seconds (2000 milliseconds)
    setInterval(getStatus, 2000);
}