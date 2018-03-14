

//////////////////// HTTP requests to the Flask API /////////////////////////////

function sendrequest(instruction_val,command_val){
    $.post( "/send", { instruction: instruction_val, command: command_val } );
}  

function collectSensorValues(){
    $.get("/collect", function(data){
        $("#accel-value").text(data);
    });
}

////////////////// Handle the arror keystrokes to drive the robot /////////////////////

var button_pressed = 0;
var speed = 127;

document.onkeydown = function(e) {

    if (button_pressed === 0){
        switch (e.keyCode) {
            case 37:                    // left key
                e.preventDefault();
                sendrequest("b", -speed);         //left motor speed = -127
                sendrequest("a", speed);          //right motor speed = 127
                button_pressed = 1;
                $('#left-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 38:
                e.preventDefault();     // up key
                sendrequest("a", speed);           //right motor speed = 127
                sendrequest("b", speed);           //left motor speed = 127
                button_pressed = 1;
                $('#up-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 39:
                e.preventDefault();    // right key
                sendrequest("a", -speed);           //right motor speed = -127
                sendrequest("b", speed);            //left motor speed = 127
                button_pressed = 1;
                $('#right-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 40:
                e.preventDefault();    // down key
                sendrequest("a",-speed);            //right motor speed = -127
                sendrequest("b",-speed);            //left motor speed = -127
                button_pressed = 1;
                $('#down-btn').css({"background-color":"#007bff","color":"white"});
                break;
        }
    }

    else {
        if ((e.keyCode <= 40) && (e.keyCode >= 37)){
            e.preventDefault();
        }
    }
};

document.onkeyup = function(e) {
    switch (e.keyCode) {
        case 37:
            $('#left-btn').css({"background-color":"white","color":"#007bff"});
        case 38:
            $('#up-btn').css({"background-color":"white","color":"#007bff"});
        case 39:
            $('#right-btn').css({"background-color":"white","color":"#007bff"});
        case 40:
            $('#down-btn').css({"background-color":"white","color":"#007bff"});
            sendrequest("a",0);               //Stop the robot from moving
            sendrequest("b",0);
            button_pressed = 0;
            break;
    }
};



///////////////////// Other UI elements (slider and graphs / sensor values) /////////////////////////

window.onload = function(e){
    
    $.each($('.slider'),function(n,slider){

        slider.oninput = function(){
            slider.nextElementSibling.innerText = this.value;

            switch (slider.id){
                case "bot-servo-slider":
                    sendrequest("d",this.value);
                    break;
                case "mid-servo-slider":
                    sendrequest("e",this.value);
                    break;
                case "swinger-servo-slider":
                    sendrequest("f",this.value);
                    break;
                case "rotor-servo-slider":
                    sendrequest("h",this.value);
                    break;
                case "speed-slider":
                    speed = this.value;
                    break;
            }
        }
    });

    //Claw button starts deactivated. 
    //Make sure to set its color appropriately
    $('#claw-btn').text("Claw Deactivated!");
    $('#claw-btn').css({"background-color":"white","color":"#007bff"});

    $("#claw-btn").click(function(){
        claw_btn = $('#claw-btn');
        if (claw_btn.css("background-color") == "rgb(0, 123, 255)"){
            sendrequest("g",1);
            claw_btn.css({"background-color":"white","color":"#007bff"});
            claw_btn.text("Claw Deactivated!")
        }
        else{
            sendrequest("g",0);
            claw_btn.css({"background-color":"#007bff","color":"white"});
            claw_btn.text("Claw Activated!");
        }
    });


    //setInterval(function(){collectSensorValues();},3000);

}

