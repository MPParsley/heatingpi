#!/usr/bin/env python

# V1 Python program to listen for recvieved 
# temperature data via the USB serial port
# and insert into the database
#
# runs as a daemon process in the background
# started automatically at bootup
# 
# G. Naylor November 8th 2014

# include libs as necessary
import sqlite3
import serial

DEBUG=1				# set to 1 for extra output to console

# setup variables
DB="/home/pi/heatpi/db/test.db"	# alter as necessary
BASE="/home/pi/heatpi"
SPORT="/dev/ttyUSB0"		# Serial port Moteino is attached to.

#  nodes holds the node id to zone location mapping
# this needs to reflect the zones table in the db

nodes = [ (0,'Gateway'),
          (1,'Hall'),
          (2,'Lounge'),
          (3,'Study'),
          (4,'Kitchen') ]

if DEBUG==2: print nodes ;


if DEBUG==2: 
	print DB
	print BASE
	print SPORT

# Function to update database with data
def add_temp_reading (zonestr, temp):
    # I used triple quotes so that I could break this string into
    # two lines for formatting purposes
    curs.execute("""INSERT INTO temps values(date('now'),
        time('now'), (?), (?))""", (zonestr,temp))

    # commit the changes
    conn.commit()

# open serial port to gateway moteino
# open the Serial port at 115200 baud, with a timeout of 0 seconds
# /dev/ttyUSB0 is normally the first (lower) USB connection on the Raspberry Pi
# Check ls -l /dev/ttyUS* after plugging in the USB cable and
# ammend accordingly
# ensure the sketch running on the moteino has the same BAUD rate!

try:
	ser = serial.Serial(port=SPORT,
	baudrate=115200,
	bytesize=serial.EIGHTBITS,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	timeout=3)
except:
	print "\nSerial Port cannot be opened.  Is Motenio connected to lower USB ?\n"
	exit()


# open database connection
try:
	conn=sqlite3.connect(DB)
	curs=conn.cursor()
except:
	print "\nDatabase cannot be opened. Exiting...\n"

# if we have reached here USB is OK and DB is OK, look for data"
if DEBUG: print "\nport and DB opened, listening for data ....\n";

while 1:
	try:
		line = ser.readline()
		if DEBUG==2: print(line);
		# data will be format nodeid:temp*100
		# need to split out and divide temp by 100
		data=str(line).split(':',2)
		try:
			node=data[0]
			temp=float(data[1])/100.00
			zone=str(nodes[int(node)][1])
			if DEBUG: print("Node is %s , Zone is %s, Temp is %s " % (str(node),zone,str(temp)));
			# now update database with readings
			add_temp_reading(zone, temp)
		except:
			continue # if we get a corrupted data ignore it
	except:
		# close database connection
		conn.close()
		exit()
