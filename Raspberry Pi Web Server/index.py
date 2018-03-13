from flask import Flask,render_template,request,Response,jsonify
import json

import smbus
import time

app = Flask(__name__)

@app.route("/graph",methods=["GET"])
def send_graph_values():

    bus.write_byte(address, ord('a'))
    time.sleep(0.01)
    
    bus.write_byte(address, 129)

    time.sleep(1)
    bus.write_byte(address, ord('c'))
    time.sleep(0.01)
    bus.write_byte(address, 3)
    
    time.sleep(1)
    msg = chr(bus.read_byte(address))
    print(msg)
    
    #stops program
    bus.write_byte(address, 255)

    response_content = b'data transfer successful!'
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

    msg = "test"

    response_content = "Collected Value: " + msg
    resp = Response(response_content)    
    resp.headers['Content-type'] = 'text/plain'
    resp.headers['Content-Length'] = len(response_content)

    return resp

@app.route("/")
def index():
    return render_template("index2.html")
    


if __name__ == '__main__':
    #app = create_app()
    bus = smbus.SMBus(1)    
    address = 0x04
    
    app.run(host="172.28.176.223")
