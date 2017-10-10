# demi-wicm
A WAN Infastructure Connectivity Manager (WICM) created for the DEMI Experiment in order to be integrated to the SOFTFIRE testbed. DEMI addresses the integration of WAN connectivity service models with Network Function Virtualization (NFV), particularly for the deployment of transit VNFs, which account for a large share of the VNFs that are candidate to be offered following the widespread “as-a-Service” model. WICM manages the WAN resources in a similar way that the Virtualized Infrastructure Manager (VIM) manages resources within a NFVI Point of Presence (PoP) network. 

In brief, the DEMI WICM application provides new mechanisms and tools in order to describe the WAN network in terms of a set of common network abstractions and for this purpose WICM provides an abstraction to the NFVO to hide the specific characteristics of the underlying infrastructure. WICM is able to process and extract the networking graph defined in the Network Service Record (NSR) send by the NFVO after the successful initialisation of a Network Service Descriptor (NSD). Next, WICM orchestrates the services and infrastructure to establish connectivity over the physical network, providing the appropriate redirections of the traffic data through the PoPs defined in the NSR. 

## Repository Structure
  
 * `WICM` contains WICM source files.
    * `database` contains the scripts in order to build and populate the WICM DB.
    
### Building

The WICM application is entirely written in Python and does not require a special build process. Run:
* `python3 setup.py -install` in order to install dependencies

### Dependencies
 
The WICM application has the following dependencies:

* [argparse](https://pypi.python.org/pypi/argparse) >= 1.4.0 
* [Flask](https://pypi.python.org/pypi/Flask) >= 0.12 
* [flask_restful](https://pypi.python.org/pypi/Flask-RESTful) >= 0.3 
* [requests](https://pypi.python.org/pypi/requests) >= 2.11.1 
* [pytricia](https://pypi.python.org/pypi/pytricia) >= 0.9.6 
* [SQLAlchemy](https://pypi.python.org/pypi/SQLAlchemy/1.1.14) ==1.1.14

#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

* Stavros Kolometsos (https://github.com/metsos)
 
