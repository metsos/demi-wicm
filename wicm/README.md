# Demi-wicm
A WAN Infastructure Connectivity Manager (WICM) created for the DEMI Experiment in order to be integrated to the SOFTFIRE testbed. DEMI addresses the integration of WAN connectivity service models with Network Function Virtualization (NFV), particularly for the deployment of transit VNFs, which account for a large share of the VNFs that are candidate to be offered following the widespread “as-a-Service” model. WICM manages the WAN resources in a similar way that the Virtualized Infrastructure Manager (VIM) manages resources within a NFVI Point of Presence (PoP) network.

In brief, the DEMI WICM application provides new mechanisms and tools in order to describe the WAN network in terms of a set of common network abstractions and for this purpose WICM provides an abstraction to the NFVO to hide the specific characteristics of the underlying infrastructure. WICM is able to process and extract the networking graph defined in the Network Service Record (NSR) send by the NFVO after the successful initialisation of a Network Service Descriptor (NSD). Next, WICM orchestrates the services and infrastructure to establish connectivity over the physical network, providing the appropriate redirections of the traffic data through the PoPs defined in the NSR.

### Installation and Configuration 

In order for the WICM to function, you will have to install Opendaylight with VTN Manager as well as make configurations on the WICMs database providing all the underlying physical network info. 
More information and instructions on how to achieve it are on the wiki: https://github.com/metsos/demi-wicm/wiki/Configuration

Once the configuration is completed, you may run the following command to start WICM: 
`python3 wicm/wicm.py -v vtnHostIP -u username -p userpassword -n VTN_name` 
Replacing the variables with the appropiate data. 

Once started a log will be created in the folder with the name wicm.log 

The REST API documentation can also be found in the wiki: https://github.com/metsos/demi-wicm/wiki/REST-API-Documentation

### Usage 

The WICM can either start a new network service by recieving a JSON message directly from the NFVO Openbaton, or it can be done manually. 
In the first case, in the configuration section of the wiki, more information can be found and instructions on how to achieve it. 
In the latter case, a JSON message should be sent to the interface of WICM that has to have the following format: 

`{ "instance_id": String, "in_seg": “xxx.xxx.xxx.xxx./xx”, "out_seg": “xxx.xxx.xxx.xxx./xx”, "vims": [ { "port": VIM_Name, "order": Integer } ] }`

The request should be sent to: `http:/wicm_ip:5000//api/v1/flows`

An example request : `curl  -x POST http://192.168.1.199:5000/api/v1/flows -d ‘{ "instance_id": “596k92”, "in_seg": “192.168.10.10/32”, "out_seg": “192.168.20.10/32”, "vims": [ { "port": “vim_one”, "order": 0 },{ "port": “vim_two”, "order": 1 } ] }’`
