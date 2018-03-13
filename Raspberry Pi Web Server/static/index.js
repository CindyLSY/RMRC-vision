
function sendrequest(instruction_val,command_val){
    $.post( "/send", { instruction: instruction_val, command: command_val } );
}  

var button_pressed = 0;

document.onkeydown = function(e) {

    if (button_pressed === 0){
        switch (e.keyCode) {
            case 37:                    // left key
                e.preventDefault();
                sendrequest("b",127);
                button_pressed = 1;
                $('#left-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 38:
                e.preventDefault();     // up key
                sendrequest("c",127);
                button_pressed = 1;
                $('#up-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 39:
                e.preventDefault();    // right key
                sendrequest("a",127);
                button_pressed = 1;
                $('#right-btn').css({"background-color":"#007bff","color":"white"});
                break;
            case 40:
                e.preventDefault();    // down key
                sendrequest("d",127);
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
            sendrequest("e",127);               //Stop the robot from moving
            button_pressed = 0;
            break;
    }
};