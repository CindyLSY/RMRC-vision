from flask import Flask,render_template,request,Response,jsonify,send_file
import json

#import smbus
import time
import math

import subprocess
import os

#angles of the servo
alpha = 0
beta = 0

#lengths of the arm.
L1=12.5;
L2=12;

#global popen process object for audio recording
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

@app.route("/audiorecording",methods=["POST"])
def process_audiorecordingrequest():
    val = request.values.get("recording_on_off")

    global audio_process

    current_directory_path = os.path.dirname(os.path.realpath(__file__))
    file_path = current_directory_path+"/static/audio_recording.wav"

    #If val = 1 => i.e. start recording
    if (int(val) != 0):

        #if audio_process object exists, check if the process is still running. If it is, don't do anything
        if audio_process is not None:

            if audio_process.poll() > 0:
                response_content = 'Audio is still recording!'
                resp = Response(response_content)    
                resp.headers['Content-type'] = 'text/plain'
                resp.headers['Content-Length'] = len(response_content)
                return resp
        
        #audio process object either does not exist  or is not running
        #Start audio recording process

        #if the file exists delete it first and overwrite it.
        if os.path.exists(file_path):
            os.remove(file_path)

        #to find the device number, run sudo arecord -l

        args = ['arecord',"--device=hw:1,0","--format","S16_LE","--rate","48000",file_path]
        audio_process = subprocess.Popen(args)
        
        response_content = 'Started Recording Audio to ' + file_path
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
            audio_process.kill()
            
            response_content = 'Stopped Recording Audio to ' + file_path
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
    
    else:
        response_content = 'Request value not recognized'
        resp = Response(response_content)    
        resp.headers['Content-type'] = 'text/plain'
        resp.headers['Content-Length'] = len(response_content)
        return resp

#serve the current audio recording
@app.route("/audiorecordingfile")
def return_audio_recording_file():
    current_directory_path = os.path.dirname(os.path.realpath(__file__))
    file_path = current_directory_path+"/static/audio_recording.wav"
    return send_file(file_path)


@app.route("/send",methods=["POST"])
def send_request():
    instruction = request.values.get("instruction")
    command = request.values.get("command")

    if (len(instruction) > 0):
        instruction = instruction[0]

    print(instruction,command)

    if instruction != 'k':
        bus.write_byte(address,ord(instruction))
        time.sleep(0.01)
        bus.write_byte(address,int(command))
        time.sleep(0.01)
    else:
        time.sleep(0.1)
        bus.write_byte(address,ord(instruction))
        time.sleep(0.1)
        bus.write_byte(address,int(command))
        time.sleep(0.1)


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
    #app.run(host='0.0.0.0')
    app.run(host="192.168.0.104")
