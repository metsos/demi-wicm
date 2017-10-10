from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

from sqlalchemy_declaritive import Base, Connectivity

engine = create_engine('sqlite:///wim_info.db')
# bind the engine to the metadata of the base 
Base.metadata.bind = engine 
DBSession = sessionmaker(bind=engine)
# dbsession establishes 'conversations' with the database 
session = DBSession()
#insert data on the table(s)
print ("Welcome to the WIM-info database helper")

while True:
	print ("Enter new database entry ")
	segment = input("Enter Segment: ")
	pop_name = input("If it is a VIM, please enter name as declared in OPB. Else you can leave it blank: ")
	bridge_name = input("Enter Vbridge name: ")
	port_id = input("Enter interface_id: ")
	print("You provided the following info: ")
	print("Segment: "+segment)
	print("VIM name: "+pop_name)
	print ("Bridge name: " +bridge_name)
	print ("Interface ID: "+port_id)
	var = input("If dissagree type 'q' ")
	if var == 'q':
		break
	new_conn = Connectivity(segment=segment, bridge_name=bridge_name,port_id=port_id,pop_name=pop_name)
	session.add(new_conn)
	session.commit()
	var = input("You want to add more? (y/q)")
	if var == 'q':
		break



