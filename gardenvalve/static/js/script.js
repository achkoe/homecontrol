var eValveButton, eHistory;


function createElementWithAttributes(name, attributes=Object()) {
    let element = document.createElement(name);
    for (const key in attributes) {
        element.setAttribute(key, attributes[key]);
    }
    return element;
}

function populateHistory(data) {
    map = {"time": "Time", "close": "Closed", "rain_mm": "Rain/mm", "status": "Status"}
    eHistory.innerHTML = "";
    let tr = createElementWithAttributes("tr");
    for (const key in map) {
        let th = createElementWithAttributes("th");
        th.classList.add("center");
        th.innerText = map[key];
        if (key === "time") {
            th.classList.add("left");
        }
        tr.append(th);
    }
    eHistory.append(tr);
    for (const item of data) { 
        let tr = createElementWithAttributes("tr");
        eHistory.append(tr);
        for (const key in map) {
            let td = createElementWithAttributes("td");
            if (key === "close") {
                td.innerText = item[key] ? "yes" : "no";
                td.classList.add(item[key] ? "yes" : "no");
                td.classList.add("center");
            } else if (key === "rain_mm") {
                td.innerText = Number.parseFloat(item[key]).toFixed(2); 
                td.classList.add("center");
            } else if (key == "status") {
                td.innerText = item[key] == 200 ? "ok" : "error";
                td.classList.add("center");
                if (item[key] != 200) {
                    tr.classList.add("error");
                }
            } else if (key == "time") {
                td.classList.add("left");
                td.innerText = item[key];
            } else {
                td.innerText = item[key];
                td.classList.add("center");
            }
            tr.append(td);
        }
    }
    for (const item of data) { 
        eValveButton.innerText = item["close"] ? "Press to open" : "Press to close";
        eValveButton.value = item["close"];
        break;
    }
}

function press() {
    console.log("press");
    const url = "/set";
    const state = {"state": eValveButton.value};
    console.log("press ", url, state);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(state),
    }).then(response => {
        if (!response.ok) {
            console.error('Error sending state to server');
        } else {
            console.log("SUCCESS");
        }
    }).catch(error => {
        console.error('Error sending state to server:', error);
    });
}



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
            populateHistory(data);
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}
    
window.onload = (event) => {
    console.log("onload");
    eValveButton = document.getElementById("valve");
    eHistory = document.getElementById("history");
    // Set the interval to call the function every 2 seconds (2000 milliseconds)
    getStatus();
    setInterval(getStatus, 2000);
}