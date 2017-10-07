import logging
from flask_restful import Resource, abort
from flask import jsonify, request
import utils

flows = []
events = []

class Insert(Resource):
	
	def get(self):
		logging.debug("call for the flow stored. Returning: " + str(flows))
		logging.info("Call for flow accepted")
		return jsonify(flows = flows)

	def post(self):
		logging.info("POST API call incoming")
		data = request.json
		logging.debug("Recieved the following: "+str(data))
		cond_name = data["instance_id"]
		in_seg = data["in_seg"]
		out_seg = data["out_seg"]
		pops = data["ports"]
		logging.debug("Starting ordering PoPs")
		ordered_pop = utils.order_pop(pops) 
		# Put the incoming PoPs in order 
		logging.info("Calling set-up-the-rules method")
		message = utils.setRules(cond_name, in_seg,out_seg,ordered_pop)
		if flag == 200:
			flows.append(flow)
			return jsonify({'flow': flow}, 200)
		else:
			abort(500, message = "Unknown Error")

class Flows(Resource):

	def get(self, res_name):
		logging.info("Requesting "+res_name+" flow")
		for flow in flows:
			if flow['data']['instance_id'] == res_name:
				return flow
		abort(404, message="Resource not found") 

	def delete(self, res_name):
		logging.debug("Call to delete condition: " +res_name)
		
		for flow in flows:
			if flow['data']['instance_id'] == res_name:
				flows.remove(flow)
				logging.info("Resource found. Proceed to removal")
				flag = utils.delete_condition(res_name)
				if flag == 200: 
					return ("Resource was deleted")
				else:
					abort(406, message="Resource was not found in VTN and not deleted")
		logging.info("Resource not found. No action taken")
		abort(404, message="Resource not found")

class Initialise(Resource):
	
	def post(self):
		logging.info("Incoming Initialise data")
		data = request.get_json(force=True)
		logging.debug("Recieved the following: "+str(data))
		vnfrs = data['payload']['vnfr']  # Get all the vnfrs
		for vt in vnfrs:
			print (vt['vdu'][0]['vimInstanceName'])
			g = vt['vdu'][0]['vimInstanceName']
			logging.debug("Got VIM: "+(g[0])) #we take the name of the PoP initiated
		events.append(data)
		utils.pop_nets()
		logging.info("sending incoming data to be processed")
		instance_id, pop_list = utils.processJson(data) # sending data to be processed 
		logging.debug("Got Information back from processing")
		logging.debug("Original instance_id is: "+instance_id)
		helpers = instance_id.split('-',1)
		inst_id = helpers[0]
		logging.debug("New instance_id is: "+inst_id)
		logging.info("Getting user(incoming seg) and client(outgoing segment) info")
		try:
			in_seg, flag = utils.getUser()
			out_seg, flag = utils.getClient()
		except Exception as e:
			abort(500,message = "Couldn't get User or Client") 
		flag = utils.setRules(inst_id, in_seg,out_seg,pop_list)
		daty = {"instance_id": inst_id , "in_seg": in_seg , "out_seg": out_seg , "VIM list": pop_list }
		flow = { "data" : daty }
		if flag == 200:
			flows.append(flow)
			return jsonify({'flow': flows }, 200)
		else:
			abort(500)

	def get(self):
		logging.debug("call for stored event. Returning: " + str(events))
		logging.info("Call for flow accepted")
		return jsonify(events = events)

class Deleted(Resource):

	def post(self):
		logging.info("Incoming Delete data")
		data = request.get_json(force=True)
		logging.debug("Recieved the following: "+str(data))
		events.append(data)
		instance_id = data['payload']['id']
		logging.debug("Original instance_id is: "+instance_id)
		helpers = instance_id.split('-',1)
		inst_id = helpers[0]
		logging.debug("New instance_id is: "+inst_id)
		flag = utils.delete_condition(inst_id)
		if flag == 200:
			logging.info("Resource was deleted") 
			return ("Resource was deleted")
		else:
			logging.info("Resource was not found and was not deleted")
			abort(406, message="Resource was not found in VTN and not deleted")

	def get(self):
		logging.debug("call for stored event. Returning: " + str(events))
		logging.info("Call for flow accepted")
		return jsonify(events = events)

class User(Resource):

	def get(self):
		logging.info("Requesting user info")
		user, flag = utils.getUser()
		if flag == 200:
			return jsonify(user = user)
		else: 
			abort(500)
	
	def put(self):
		logging.info("Incoming data")
		data = request.get_json(force=True) # So that it gets it not matter what content send
		logging.info(data)
		try:
			user = data['user']
			logging.info("Got request to put user: "+user)
			message,flag = utils.setUser(user)
			if flag == 200:
				return ("User posted")
			else:
				abort (flag, message = message)
		except Exception as e:
			logging.error(str(e))
			abort(500,message = "Did not complete. Some error with the data?")

class Client(Resource):

	def get(self):
		logging.info("Requesting client info")
		client, flag = utils.getClient()
		if flag == 200 :
			return jsonify(client = client)
		else: 
			abort(500)

	def put(self):
		logging.info("Incoming data")
		data = request.get_json(force=True)  # So that it gets it not matter what content send
		logging.info(data) 
		
		try:
			client = data['client']
			logging.info("Got request to put client: "+client)
			message,flag = utils.setClient(client)
			if flag == 200:
				return ("Client posted")
			else:
				logging.error(message)
				abort (flag)
		except Exception as e:
			logging.error(str(e))
			abort(500,message = "Did not complete. Some error with the data?")
