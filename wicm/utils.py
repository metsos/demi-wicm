from wicm import get_info, get_vtn_name
import requests
import json
from flask_restful import Resource, abort
import logging 
from sqlalchemy import create_engine
import pytricia
import vnf


pyt = pytricia.PyTricia()
e = create_engine('sqlite:///database/wim_info.db')

def setRules(cond_name, in_seg,out_seg,ordered_pop):
		logging.info("Calling set_condition method")
		flag = set_condition(cond_name,in_seg, out_seg)
		logging.debug("Flag incoming:" +str(flag))
		if flag != 200:
			abort(500, message="Set condition uncompleted")
		logging.info("Condition set completed")
		flag = 200
		#TODO FIX incoming traffic 
		port_in, vbr1 = get_switch(in_seg) 
		port_out, vbr2 = get_switch(getPopIP(ordered_pop[0]))
		if vbr1 == 'notsure':
			port_in = get_exit(vbr2)
		bridge = vbr2 # Set final bridge
		port = port_out
		set_redirect(cond_name, vbr2, port_in, port_out)
		logging.info("Redirect from source to First PoP completed")
		# Redirecting through the PoPs now
		logging.debug("Redirect traffic through PoPs")
		for i in range(1,len(ordered_pop)):
			port_1, vbr1 = get_switch(getPopIP(ordered_pop[i-1]))
			logging.debug("port coming is: "+port_in+" with vbridge "+vbr1)
			port_2, vbr2 = get_switch(getPopIP(ordered_pop[i]))
			if vbr1 == vbr2:
				logging.debug("port to redirect is: "+port_out+" with vbridge "+vbr2)
				set_redirect(cond_name, vbr1, port_1, port_2)
			else:
				logging.debug("redirecting through different bridges")
				port_ex = get_exit(vbr1)
				set_redirect(cond_name, vbr1, port_1, port_ex)
				port_in = get_exit(vbr2)
				set_redirect(cond_name, vbr2, port_in, port_2)
			bridge = vbr2
			port = port_2
		logging.debug(" Inter PoP redirections completed ")
		port_out, exitbridge = get_switch(out_seg)
		if exitbridge == 'notsure':
			port_out = get_exit(bridge)
		elif exitbridge != bridge :
			logging.debug("redirecting through different bridges")
			port_ex = get_exit(bridge)
			set_redirect(cond_name, bridge, port, port_ex)
			port = get_exit(exitbridge)
			#set_redirect(cond_name, exitbridge, port_in, port_out)
			bridge = exitbridge
		else:
			bridge = exitbridge
		set_redirect(cond_name, bridge, port, port_out)
		# Need to implement (or not) going from last PoP to Outer Segment -- leaving Wan 
		#Just add to the flow array 
		logging.info("Posting new flow completed")
		return flag


def get_switch(seg):
	logging.debug("Incoming request for segment: "+seg)
	conn = e.connect()
	segment = pyt.get(seg)
	logging.debug("Segment to look in the database is: "+ str(segment))
	query = conn.execute('SELECT port_id, bridge_name FROM connectivity WHERE segment="%s";' %segment)
	dt = query.fetchone()
	logging.debug(str(dt))
	#TODO implement try 
	port, switch = dt[0],dt[1]
	logging.info("get_switch method completed. Returning: "+port+" "+switch+". If segment is 0.0.0.0/0, then it may not be correct")
	if segment == '0.0.0.0/0':
		switch = 'notsure'
	conn.close()
	return port, switch

def getPopIP(pop):
	logging.debug("Incoming request to find segment from VIM name: "+pop)
	conn = e.connect()
	query = conn.execute('SELECT segment FROM connectivity WHERE pop_name="%s";' %pop)
	logging.info(query)
	dt = query.fetchone()
	#TODO implement try 
	logging.info("getPopIP method completed. Returning: "+str(dt)+".")
	pop_ip = dt[0]
	logging.info("getPopIP method completed. Returning: "+pop_ip+".")
	conn.close()
	return pop_ip


def get_exit(vbr):
	logging.debug("Incoming request to find exit port of vbridge: "+vbr)
	conn = e.connect()
	query = conn.execute('SELECT port_id FROM connectivity WHERE segment="0.0.0.0/0" AND bridge_name="%s";'%vbr)
	dt = query.fetchone()
	port = dt[0]
	logging.info("get_exit method completed. Returning: "+port )
	conn.close()
	return port 

def set_condition(cond_name, source, dest):
	logging.debug("Incoming set_condition call")
	s_url = 'operations/vtn-flow-condition:set-flow-condition'
	username, password, host, url, headers = get_info()
	data = {'input': {'name': cond_name, 'vtn-flow-match': [
	    {'index': '1', 'vtn-inet-match': {'source-network': source, 'destination-network': dest}}]}}
	logging.debug("Data to be sent for flow setting in VTN: "+str(data))
	'''
	 this curl --user "username":"pass" -H "Content-type: application/json" -X POST http://localhost:8181/restconf/operations/vtn-flow-condition:set-flow-condition
	# -d '{"input":{"name":"cond1", "vtn-flow-match":[{"index":"1",
	# "vtn-inet-match":{"source-network":"10.0.0.1/32",
	# "destination-network":"10.0.0.3/32"}}]}}'
	'''
	logging.debug("Sending request to VTN to implement condition "+cond_name)
	r = requests.post(url + s_url, headers=headers,
	                  auth=(username, password), json=data)
	logging.info("Got this as response: " +str(r) )
	if not r.status_code == 200:
	    logging.error('FLOW COND ERROR ' + str(r.status_code))
	return r.status_code

def delete_condition(cond_name):
    s_url = 'operations/vtn-flow-condition:remove-flow-condition'
    username, password, host, url, headers = get_info()
    data = {'input': {'name': cond_name}}
    logging.debug("Sending request to delete condition "+cond_name)
    r = requests.post(url+s_url, headers=headers, auth=(username, password), json=data)
    logging.info("Got response:" +str(r))
    if not r.status_code == 200:
    	logging.error("Condition removal ERROR " + str(r.status_code))
    return r.status_code

def set_redirect(cond_name, vbr, port_id_in, port_id_out):
	s_url = 'operations/vtn-flow-filter:set-flow-filter'
	logging.debug("Incoming set_redirect call")
	username, password, host, url, headers = get_info()
	vtn_name = get_vtn_name()
	data = {"input": {"output": "false", "tenant-name": vtn_name, "bridge-name": vbr, "interface-name": port_id_in, "vtn-flow-filter": [
	    {"index": "1", "condition": cond_name, "vtn-redirect-filter": {"redirect-destination": {"bridge-name": vbr, "interface-name": port_id_out}, "output": "true"}}]}}
	'''
	 this: curl --user "username":"pass" -H "Content-type: application/json" -X POST http://localhost:8181/restconf/operations/vtn-flow-filter:set-flow-filter
	  -d '{"input":{"output":"false","tenant-name":"vtn1", "bridge-name":"vbr", interface-name":"if5", "vtn-flow-filter":[{"condition":"cond_1","index":"1","vtn-redirect-filter":
	  {"redirect-destination":{"bridge-name":"vbr1","interface-name":"if3"},"output":"true"}}]}}'
	'''
	logging.debug("Sending request to set condition: "+str(data))
	r = requests.post(url + s_url, headers=headers,
	                  auth=(username, password), json=data)
	logging.info("Got response:" +str(r))
	if not r.status_code == 200:
	    logging.error('FLOW FILTER ERROR ' + str(r.status_code))

def order_pop(pops):
	ordered_pop = []
	pop_list = [] 
	for item in pops:
		ordered_pop.append((item["port"],item["order"]))
	ordered_pop.sort(key=lambda tup: tup[1])
	for item in ordered_pop:
		pop_list.append(item[0])
	return pop_list
	 
def pop_nets():
	logging.debug("Populating network segments table")
	conn = e.connect()
	query = conn.execute('SELECT segment FROM connectivity;')	
	dt = query.fetchall()
	logging.debug("Show segments: " + str(dt))
	for d in dt: 
		pyt[d[0]] = d[0]
	user, flag = getUser()
	client, flag = getClient()
	try:
		pyt[user] = user
		pyt [client] = client
	except Exception as er:
		logging.error("Error while getting user or client")

def processJson(d):
	vnfrs = d['payload']['vnfr']  # Get all the vnfrs
	instance_id = d['payload']['id']
	logging.info("Got incoming request, with id as "+instance_id)
	vnfs = []
	for vm in vnfrs:
		logging.debug("Start to find VNFs")
		vim = vm['vdu'][0]['vimInstanceName']
		name =vm['name']
		v = vnf.Vnf(name)
		v.vim = vim[0]
		v.hostname = vm['vdu'][0]['vnfc_instance'][0]['hostname']
		fl = vm['vdu'][0]['vnfc_instance'][0]['floatingIps'][0]['ip'] # get the floating IP of the
		v.floating = fl
		logging.info("Got VNF with name :"+v.name)
		vnfs.append(v)
	pop_list = [] # the list that will store the PoP graph 
	dependency = d['payload']['vnf_dependency']
	logging.info("Looking at dependencies")
	for de in dependency:
		helper = de['idType']
		for key in helper:
			source_name = key # it is the source
		target_name = de['target'] # and the target VNF name
		for vm in vnfs:  # get their PoPs name 
			if source_name == vm.name:
				vm.source = True
				vm.goes = target_name
			elif target_name == vm.name:
				vm.target = True
				vm.by = source_name
	trigger = True 
	second = None
	i = 0
	while trigger or not (i <100) : # i is used as a failsafe mechanism
		if len(vnfs) == 0: # If there are no more vnfs in the list, then end while
			trigger = False
		for vm in vnfs:
			if vm.target is None: #finding the first in graph
				pop_list.append(vm.vim)
				logging.info("Found one VIM: "+vm.vim)
				second = vm.goes
				vnfs.remove(vm)
			elif vm.name == second and vm.goes is not None:
				if pop_list[-1] != vm.vim :
					pop_list.append(vm.vim)
					logging.info("Found one VIM: "+vm.vim)
				second = vm.goes
				vnfs.remove(vm)
			elif vm.name == second and vm.goes is None:
				trigger = False
				if pop_list[-1] != vm.vim:
					pop_list.append(vm.vim)
					logging.info("Found one VIM: "+vm.vim)
				vnfs.remove(vm)
		i += 1 
	logging.info("Got the list : "+str(pop_list))
	return (instance_id,pop_list)
# got the PoP list 

def setUser(segment):
	#logging.debug("Incoming request to set user as: "+segment)
	conn = e.connect()
	try:
		query = conn.execute('UPDATE  userclient SET user ="%s" WHERE id = 1;'%segment)
		conn.close()
		flag = 200
		message = "success"
		return (message, flag)
	except Exception as er:
		message = ("Unknown error. See logs")
		flag = 500
		#logging.error("request to set client raised error: "+er)
		conn.close()
		return (message,flag)

def getUser():
	#logging.debug("Incoming request to get client ")
	conn = e.connect()
	try:
		query = conn.execute('SELECT  user FROM userclient WHERE id = 1;')
		dt = query.fetchone()
		user = dt[0]
		flag = 200
		conn.close()
		return (user, flag)
	except Exception as er:
		message = ("Unknown error. See logs")
		flag = 500
		#logging.error("request to set client raised error: "+er)
		conn.close()
		return (message,flag)

def getClient():
	#logging.debug("Incoming request to get client ")
	conn = e.connect()
	try:
		query = conn.execute('SELECT  client FROM userclient WHERE id = 1;')
		dt = query.fetchone()
		client = dt[0]
		flag = 200
		conn.close()
		return (client, flag)
	except Exception as er:
		message = ("Unknown error. See logs")
		flag = 500
		#logging.error("request to set client raised error: "+er)
		conn.close()
		return (message,flag)		


def setClient(segment):
	#logging.debug("Incoming request to set client as: "+segment)
	conn = e.connect()
	try:
		query = conn.execute('UPDATE  userclient SET client ="%s" WHERE id = 1;'%segment)
		conn.close()
		flag = 200
		message = "success"
		return (message, flag)
	except Exception as er:
		message = ("Unknown error. See logs")
		flag = 500
		#logging.error("request to set client raised error: "+er)
		conn.close()
		return (message,flag)
