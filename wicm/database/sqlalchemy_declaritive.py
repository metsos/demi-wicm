import os 
import sys 
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker 
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()

class Connectivity(Base):
	__tablename__ = 'connectivity'
	# define the columns for the table
	segment = Column(String(250),nullable=False)
	bridge_name = Column(String(250), nullable=False)
	port_id = Column(String(250))
	pop_name = Column(String(250))
	id = Column(Integer, primary_key=True)

class UserClient(Base):
	__tablename__ = 'userclient'
	id = Column(Integer, primary_key=True)
	user = Column(String(250))
	client = Column(String(250))

# Create engine that stores data in the local directory's 
engine = create_engine('sqlite:///wim_info.db')


# Create the Table 
Base.metadata.create_all(engine)
try:
	Session = sessionmaker(bind=engine)	
	Session.configure(bind=engine)
	session = Session()
	initial = UserClient(id='1', user = 'Not set', client = 'Not set')
	session.add(initial)
	session.commit()
except Exception as e:
 	print ("User & Client init, already done")

