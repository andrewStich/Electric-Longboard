import bluetooth
import RPi.GPIO as GPIO        #calling for header file which helps in using GPIOs of PI
import time
from i2clibraries import i2c_hmc5883l
MOTOR=18
 
GPIO.setmode(GPIO.BCM)     #programming the GPIO by BCM pin numbers. (like PIN40 as GPIO21)
GPIO.setwarnings(False)
GPIO.setup(MOTOR,GPIO.OUT)  #initialize GPIO18 (MOTOR) as an output Pin
p = GPIO.PWM(MOTOR, 50)		#set up PWM on the MOTOR pin
hmctest = i2c_hmc5883l.i2c_hmc5883l(1)
hmctest.setContinuousMode()
hmctest.setDeclination(0,13)	#sets up pins for I2C module

while 1:	# runs forever
        server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM ) 
        port = 1
        server_socket.bind(("",port))
        client_socket = 0				#setting up the bluetooth module to get ready for a connection
        print ("Awaiting SPP bluetooth connection")
        server_socket.listen(1)			#waits for an incoming connection before moving on.
 
        client_socket,address = server_socket.accept()	#accepts incoming connection.
        print ("Accepted connection from ",address)
        p.start( 2.5 ) #start PWM on MOTOR pin
        while client_socket != 0 :	#runs only when there is a connected device.
                try:	#checks to see if there is still a connection.
                        data = client_socket.recv(1024)	#Stores input into "data". Data can have a value from 0-100.
                        print ("Received: %s" % data)

                        heading = hmctest.getHeading()	#Stores measured heading 
                        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                        i = (heading[0] + 22)//45
                        test = dirs[i%8]	#checks heading and assigns "test" to one of the 8 directions.
                        client_socket.send(test)	#sends the direction to the phone
                        print(test)
                        
                        if (data == "q"):	#checks to see of the user pressed disconnect.
                                print ("Quit")
                                p.ChangeDutyCycle( 2.5 )	#set PWM signal to the zero position.
                                time.sleep ( 1 )
                                client_socket = 0	#disconnect bluetooth
                        elif (data != "q" ):
                                drive = (float(data) / 12.0) + 2.3	#calculates the PWM signal based off of "data". converts 0-100 to 2.3-10.83
                        if (drive < 101): #checks to see if drive is within it's limit.
                                p.ChangeDutyCycle( drive ) #sets the duty cycle based on drive.
                except : #if there's not a client connected.
                        print("Client disconnected")
                        p.ChangeDutyCycle( 2.5 )	# sets the PWM signal to the zero position.
                        break

client_socket.close()
server_socket.close()


