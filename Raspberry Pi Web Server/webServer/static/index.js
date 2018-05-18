//idea: implement rotate base slider, and WASD for these 3 as redundancy, one for precise angle one for adjustments

//////////////////// HTTP requests to the Flask API /////////////////////////////


function sendrequest(instruction_val,command_val){
    $.post( "/send", { instruction: instruction_val, command: command_val } );
}

function sendarmrequest(){
    calculateXYtoAB(x_val,y_val);
    if (alpha==0) {
        myChart.data.datasets[2].data = [{x:0,y:0}, {x: 0, y: 0},{x: 0,y: 0}];
    }else{
    myChart.data.datasets[2].data = [{x:0,y:0},
        {x: L1 * Math.cos(alpha), y: L1 * Math.sin(alpha)},
        {x:x_val,y:y_val}];
    }
    myChart.update();
    //$.post("/sendarmval",{X: x_val, Y: y_val} );
} 

function collectSensorValues(){
    $.get("/collect", function(data){
        $("#accel-value").text(data);
    });
}

function sendaudiorequest(recording_on_off_selector){
    $.post("/audiorecording",{recording_on_off : recording_on_off_selector}, function(data){alert(data);});
}

function increaseX(){
    if(x_val<22){
        x_val = x_val+2;
        $('#x-coordinate-slider').attr("value", x_val.toString());
        $('#x-coordinate-value').text(x_val);
        sendarmrequest();
    }
}
function decreaseX(){
    if(x_val>1 && (y_val>=0 || x_val>11)){
        x_val = x_val-2;
        $('#x-coordinate-slider').attr("value", x_val.toString());
        $('#x-coordinate-value').text(x_val);
        sendarmrequest();
    }
}
function increaseY(){
    if(y_val<21){
        y_val = y_val+2;
        $('#y-coordinate-slider').attr("value", y_val.toString());
        $('#y-coordinate-value').text(y_val);
        sendarmrequest();
    }
}
function decreaseY(){
    if((x_val>=9 && y_val>-5) || (y_val>1)){
        y_val = y_val-2;
        $('#y-coordinate-slider').attr("value", y_val.toString());
        $('#y-coordinate-value').text(y_val);
        sendarmrequest();
    }
}
////////////////// Handle the arror keystrokes to drive the robot /////////////////////

var button_pressed = 0;
var speed = 127;

var y_val = 0;
var x_val = 0;
var y_inc = 1;
var x_inc = 1;
var incX;
var decX;
var incY;
var decY;
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
	    case 76://l
        		button_pressed = 1;
        		e.preventDefault();
        		sendrequest("k",1);
		      break;
        case 81:// q
                button_pressed = 1;
                e.preventDefault();
                sendrequest("j",1);
                break;
        case 69: //e
                button_pressed = 1;
                e.preventDefault();
                sendrequest("j",2);
                break;
        case 68://a
                button_pressed = 1;
                e.preventDefault();
                incX = setInterval(increaseX, 200);
                break;
        case 65://d
                button_pressed = 1;
                e.preventDefault();
                decX = setInterval(decreaseX, 200);
                break;
        case 87://w
                button_pressed = 1;
                e.preventDefault();
                incY = setInterval(increaseY, 200);
                break;
        case 83://s
                button_pressed = 1;
                e.preventDefault();
                decY = setInterval(decreaseY, 200);
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
	   case 76:
    	    sendrequest("k",0);
            button_pressed = 0;
    	    break;
        case 81:
        case 69:
            sendrequest("j",0);
            button_pressed = 0;
            break;
        case 68:
            clearInterval(incX);
            button_pressed = 0;
            break;
        case 65:
            clearInterval(decX);
            button_pressed = 0;
            break;
        case 87:
            clearInterval(incY);
            button_pressed = 0;
        case 83:
            clearInterval(decY);
            button_pressed = 0;
            break;
        default:
            pass()
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

    $('#disable_tip').text("Disabled Tip Servo");
    $('#disable_tip').css({"background-color":"white","color":"#007bff"});

    $("#disable_tip").click(function(){
        claw_btn = $('#disable_tip');
        if (claw_btn.css("background-color") == "rgb(0, 123, 255)"){
            sendrequest("l",1);
            claw_btn.css({"background-color":"white","color":"#007bff"});
            claw_btn.text("Enabled Tip Servo")
        }
        else{
            sendrequest("l",0);
            claw_btn.css({"background-color":"#007bff","color":"white"});
            claw_btn.text("Disabled Tip Servo");
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

    
    $('#push_up').css({"background-color":"white","color":"#007bff"});
    $("#push_up").click(function(){
       btn = $('#push_up');
        if (btn.css("background-color") == "rgb(0, 123, 255)"){
            sendrequest("m",0);
            btn.css({"background-color":"white","color":"#007bff"});
        }
        else{
            sendrequest("m",1);
            btn.css({"background-color":"#007bff","color":"white"});
        }
    });


    $('#push_down').css({"background-color":"white","color":"#007bff"});
    $("#push_down").click(function(){
       btn = $('#push_down');
        if (btn.css("background-color") == "rgb(0, 123, 255)"){
            sendrequest("m",0);
            btn.css({"background-color":"white","color":"#007bff"});
        }
        else{
            sendrequest("m",2);
            btn.css({"background-color":"#007bff","color":"white"});
        }
    });


    
    
    $("#audio_recording_on_btn").click(function(){
        sendaudiorequest(1);
    });

    $("#audio_recording_off_btn").click(function(){
        sendaudiorequest(0);
    });


}


var ctx = $("#myChart");
//var ctx = document.getElementById("myChart");
var myChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Robot core',
            data: [{
                x: 0,
                y: 0
            }, {
                x: 10,
                y: 0
            }],
            type: 'line',
            fill: '+1',
            lineTension: 0,
            //borderWidth: 10,
            showLine: true,
            backgroundColor: [
                'rgba(255, 99, 132, 1)'
            ]
        },{
            label: 'Bottom line',
            data: [{
                x: 0,
                y: -6
            }, {
                x: 10,
                y: -6
            }],
            type: 'line',
            fill: false,
            lineTension: 0,
            //borderWidth: 10,
            showLine: true,
            backgroundColor: [
                'rgba(255, 99, 132, 1)'
            ]
        },
        {
            label: 'Arm',
            data: [{
                x: 0,
                y: 0
            },{
                x: 0,
                y: 0
            }, {
                x: 0,
                y: 0
            }],
            type: 'line',
            showLine: true,
            fill: false,
            lineTension: 0,
            pointRadius: 5,
            backgroundColor: [
                'rgba(54, 162, 235,1)'
            ]
        }]
    },
    options: {
        scales: {
            xAxes: [{
                type: 'linear',
                position: 'bottom',
                ticks:{
                    max: 25
                }
            }],
            yAxes: [{
                ticks:{
                    min: -6,
                    max: 25
                }
            }]
        }
    }

});

var alpha; 
var beta;
var gamma;
var delta;

var L1 =12.5;
var L2 = 12;


    
function calculateXYtoAB(x,y){
    var ok = 1;
    
    var L3= Math.sqrt(Math.pow(x,2) + Math.pow(y,2));
    
    var hyp=(Math.pow(L1,2) + Math.pow(L2,2) - Math.pow(L3,2))/(2*L1*L2);
    
    if(hyp <= 1 && hyp >= -1){
        //arm is within reach
        beta=Math.acos(hyp);
    
        // to avoid division by zero
        if(Math.abs(x) < 0.001){
            gamma = Math.PI/2;
        }
        else{
            gamma = Math.atan(y/x);
        }
        
        delta = Math.asin((L2/L3)*Math.sin(beta));
    
        alpha = Math.PI - gamma - delta;
    
        alpha = Math.PI - alpha;//(alpha/Math.PI)*180;
        //beta = (beta/Math.PI)*180
    }
    else{
        ok = 0;
        alpha = 0; 
        beta = 0;
    }

    /*
    // PRINTING RESULTS
    print("unrounded")
    print("alpha: ",alpha,"   beta:",beta)
    alpha = round(alpha);
    beta = round(beta);

    print("rounded")
    print("alpha: ",alpha,"   beta:",beta)
    */

    if(alpha < 0 || alpha > Math.PI|| beta < 0 || beta > Math.PI){
        // check if values are out of range
        ok = 0;
    }

    return (ok,alpha,beta);
    
}