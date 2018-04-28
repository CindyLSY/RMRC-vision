//idea: implement rotate base slider, and WASD for these 3 as redundancy, one for precise angle one for adjustments

//////////////////// HTTP requests to the Flask API /////////////////////////////

function sendrequest(instruction_val,command_val){
    $.post( "/send", { instruction: instruction_val, command: command_val } );
}

function sendarmrequest(){
    $.post("/sendarmval",{X: x_val, Y: y_val} );
} 

function collectSensorValues(){
    $.get("/collect", function(data){
        $("#accel-value").text(data);
    });
}

////////////////// Handle the arror keystrokes to drive the robot /////////////////////

var button_pressed = 0;
var speed = 127;

var y_val = 0;
var x_val = 0;
var y_inc = 1;
var x_inc = 1;

document.onkeydown = function(e) {

    if (button_pressed === 0){
        switch (e.keyCode) {
            case 37:                    // left key
                e.preventDefault();
                sendrequest("b", speed);         //left motor speed = -127
                sendrequest("a", -speed);          //right motor speed = 127
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
                sendrequest("a", speed);           //right motor speed = -127
                sendrequest("b", -speed);            //left motor speed = 127
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
            case 65://a
                sendrequest("j",1);
                break;
            case 68://d
                sendrequest("j",2);
                break;
            case 87://w
            case 83://s
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
        default:
            sendrequest("j",0);
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
		        case "y-coordinate-slider":
		            y_val = this.value;
		            sendarmrequest();
    		        break;
                case "x-coordinate-slider":
                    x_val = this.value;
                    sendarmrequest();
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


    /*
    $('#left_rot').text("Turn Left");
    $('#left_rot').css({"background-color":"white","color":"#007bff"});

    $("#left_rot").click(function(){
       btn = $('#left_rot');
        if (btn.css("background-color") == "rgb(0, 123, 255)"){
            sendrequest("j",0);
            btn.css({"background-color":"white","color":"#007bff"});
            btn.text("Turn Left")
        }
        else{
            sendrequest("j",1);
            btn.css({"background-color":"#007bff","color":"white"});
            btn.text("Turning Left");
        }
    });

    $('#right_rot').text("Turn Right");
    	$('#right_rot').css({"background-color":"white","color":"#007bff"});

    	$("#right_rot").click(function(){
       		btn = $('#right_rot');
        	if (btn.css("background-color") == "rgb(0, 123, 255)"){
            		sendrequest("j",0);
            		btn.css({"background-color":"white","color":"#007bff"});
           		 btn.text("Turn Right")
        	}
        	else{
            		sendrequest("j",2);
            		btn.css({"background-color":"#007bff","color":"white"});
            		btn.text("Turning Right");
        	}
    	});*/


    $("#datum").click(function(){
      sendrequest("j",3);
     });

    $("#x_down").click(function(){
       x_val -= x_inc; 
      $("#x_value").text("X cooridnate is: " + x_val);
      //sendarmrequest();
    });

    //setInterval(function(){collectSensorValues();},3000);

}

