import argparse,parser
import requests
import socket 
import json
import utils
from classes import Insert, Flows, Initialise, User, Client, Deleted
import logging
from flask import Flask, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_info():
    logging.debug("Request for info")
    return username, password, host, url, headers

def get_vtn_name():
    logging.debug("Got request for VTN name")
    try:
        vtn_name
        logging.debug("VTN name was defined already: "+vtn_name)
    except NameError:
        logging.debug("VTN name not defined")    
        s_url = 'operational/vtn:vtns/'
        username, password, host, url, headers = get_info()
        r = requests.get(url + s_url, headers=headers, auth=(username, password))
        json_data = json.loads(r.text)
        # at the moment there is only on vtn tenant, so one name. TODO --- think
        # about if more
        vtn_name = json_data['vtns']['vtn'][0]['name']
        logging.info("VTN name recieved. Sending back: "+vtn_name)
    finally:
        return vtn_name



parser = argparse.ArgumentParser()   #handler for arguments passed 
parser.add_argument("-v", "--host",help="Enter the address for the host containing VTN",type=str, required=True)  # option configurations, needs to be required
parser.add_argument("-u", "--user",help="Enter Username",type=str,required=True)
parser.add_argument("-p", "--password",help="Enter Password",type=str, required=True)
parser.add_argument("-n", "--name",help="Enter VTN user name",type=str)
args = parser.parse_args()


if args.host:
    host = args.host
if args.user:
    username = args.user
if args.password:
    password = args.password
if args.name:
    vtn_name = args.name

url = 'http://'+host+':8181/restconf/' #this is should be the same always
headers = {'Content type' : 'application/json'} #also this

api.add_resource(Initialise,'/api/v1/nfvo/init')
api.add_resource(Deleted, '/api/v1/nfvo/delete')
api.add_resource(Insert, '/api/v1/flows')
api.add_resource(Flows, '/api/v1/flows/<string:res_name>')
api.add_resource(User, '/api/v1/sitea')
api.add_resource(Client,'/api/v1/siteb')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='wicm.log', format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        vtn_name
    except NameError:
        vtn_name = get_vtn_name()
    logging.debug("VTN name recieved: " + vtn_name)
    local = get_ip()
    app.run(debug=True,host=local)

