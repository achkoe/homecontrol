window.onload = function() {
    var td, tr;
    console.log("I am here");
    const table = document.getElementById("table");
    for (const item of data["data"]) {
        console.log(item);
        const datetime = new Date(item[0] * 1000);
        console.log(`time -> ${datetime.toISOString()}: ${item[1]}`);
        tr = document.createElement("tr");
        td = document.createElement("td");
        td.innerText = datetime.toISOString();
        tr.append(td);
        td = document.createElement("td");
        td.innerText = item[1];
        tr.append(td);
        table.append(tr);
    }
 }