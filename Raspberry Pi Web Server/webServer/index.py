from flask import Flask,render_template,request,Response,jsonify
import json

import smbus
import time
import math

#angles of the servo
alpha = 0
beta = 0

#lengths of the arm.
L1=12.5;
L2=12;

#popen process object for audio recording
audio_process = None


app = Flask(__name__)

@app.route("/sendarmval",methods=["POST"])
def send_amrrequest():
    print("arm_request")
    X = request.values.get("X")
    Y = request.values.get("Y")

    #calculate the value of alpha and beta
    result = calculate(float(X),float(Y));

    bus.write_byte(address,105) #105 is ascii code for "i"
    time.sleep(0.01)

    bus.write_byte(address,result[1])
    time.sleep(0.01)

    bus.write_byte(address,result[2])
    time.sleep(0.01)

    response_content = 'sent instruction ' + X + Y
    resp = Response(response_content)    
    resp.headers['Content-type'] = 'text/plain'
    resp.headers['Content-Length'] = len(response_content)

    return resp

@app.route("/audiorecording",methods=["GET"])
def process_audiorecordingrequest():
    val = request.values.get("recording_on_off")


    #If val = 1 => i.e. start recording
    if (int(val) != 0):

        #if audio_process object exists, check if the process is still running. If it is, don't do anything
        if audio_process is not None:

            if audio_process.poll() != 0:
                response_content = 'Audio is still recording!'
                resp = Response(response_content)    
                resp.headers['Content-type'] = 'text/plain'
                resp.headers['Content-Length'] = len(response_content)
                return resp
        
        #audio process object either does not exist  or is not running
        else:

            #Start audio recording process
            args = ['arecord',"--device=hw:1,0","--format","S16_LE","--rate","44100","-c1","/home/pi/audio_recordings/test.wav"]
            audio_process = subprocess.Popen(args)
            
            response_content = 'Started Recording Audio'
            resp = Response(response_content)    
            resp.headers['Content-type'] = 'text/plain'
            resp.headers['Content-Length'] = len(response_content)
            return resp

    #Turn off audio recording
    elif (int(val) == 0):
        
        #check that the audio process exists
        if audio_process is not None:
            
            #kill the process
            audio_process.terminate()

            response_content = 'Stopped Recording Audio'
            resp = Response(response_content)    
            resp.headers['Content-type'] = 'text/plain'
            resp.headers['Content-Length'] = len(response_content)
            return resp
        
        else:
            response_content = 'Audio was not started'
            resp = Response(response_content)    
            resp.headers['Content-type'] = 'text/plain'
            resp.headers['Content-Length'] = len(response_content)
            return resp




@app.route("/send",methods=["POST"])
def send_request():
    instruction = request.values.get("instruction")
    command = request.values.get("command")

    if (len(instruction) > 0):
        instruction = instruction[0]

    print(instruction,command)


    bus.write_byte(address,ord(instruction))
    time.sleep(0.01)


    bus.write_byte(address,int(command))
    time.sleep(0.01)

    response_content = 'sent instruction ' + instruction + command
    resp = Response(response_content)    
    resp.headers['Content-type'] = 'text/plain'
    resp.headers['Content-Length'] = len(response_content)

    return resp
    
@app.route("/collect",methods = ["GET"])
def collect_values():
    msg = chr(bus.read_byte(address))

    response_content = "Collected Value: " + msg
    resp = Response(response_content)    
    resp.headers['Content-type'] = 'text/plain'
    resp.headers['Content-Length'] = len(response_content)

    return resp

@app.route("/")
def index():
    return render_template("index2.html")
    


def calculate(x,y):
    print("x ",x,"  y ",y);  
    ok = True;
    
    L3= math.sqrt(x**2 + y**2);
    
    hyp=(L1**2 + L2**2 - L3**2)/(2*L1*L2)
    print("hyp = ",hyp)
    
    if hyp <= 1 and hyp >= -1:
        #arm is within reach
        
        beta=math.acos(hyp)
    
        # to avoid division by zero
        if abs(x) < 0.001:
            gamma = math.pi/2;
        else:
            gamma = math.atan(y/x)
    
        delta = math.asin((L2/L3)*math.sin(beta))
    
        alpha = math.pi - gamma - delta
    
        alpha = (alpha/math.pi)*180
        beta = (beta/math.pi)*180
        
    else:
        #arm is out of reach
        ok = False;
        alpha = 0; 
        beta = 0;
   

    print("unrounded")
    print("alpha: ",alpha,"   beta:",beta)
    alpha = round(alpha);
    beta = round(beta);

    print("rounded")
    print("alpha: ",alpha,"   beta:",beta)

    if alpha < 0 or alpha > 180 or beta < 0 or beta > 180:
        # check if values are out of range
        ok = False

    #return a tuple of results
    return (ok,alpha,beta);

if __name__ == '__main__':
    #app = create_app()
    bus = smbus.SMBus(1)    
    address = 0x04
    
    app.run(host="192.168.0.102")
