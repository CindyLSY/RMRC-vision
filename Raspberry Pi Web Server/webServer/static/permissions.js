
function sendrequest(){
    $.get("/graph");
}  

var button = document.getElementById("button");
button.onclick = sendrequest;
