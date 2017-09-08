import socket
import sys
import RPi.GPIO as GPIO
import time
import threading
import pyqrcode
import urllib.request
import os



global engineState
global switchPin 
global buzzerPin
global motorPin
global childBucklePin
global ledPin
global msgServer
global sendMsg
global buckleup
global tempState
global motor1E
global motor1A
global motor1B


engineState= True
sendMsg = False
buckleup = False
msgServer=""
switchPin = 33
motorPin = 38
childBucklePin = 35
buzzerPin = 15
ledPin = 29
motor1E = 22
motor1A = 18
motor1B = 16

def createQRcode():
        

        external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
        print("Server external IP: "+external_ip)
        
        server_ip = pyqrcode.create(external_ip)
        server_ip.png('server_ip.png', scale=4, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
        server_ip.show()

def gpioInit():
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(switchPin,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(buzzerPin,GPIO.OUT)
        GPIO.setup(motorPin,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ledPin, GPIO.OUT)
        GPIO.setup(childBucklePin,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(motor1E,GPIO.OUT)
        GPIO.setup(motor1A,GPIO.OUT)
        GPIO.setup(motor1B,GPIO.OUT)
        
    


# Create socket (allows two computers to connect)
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Bind socket to port (the host and port the communication will take place) and wait for connection from client
def socket_bind():
    try:
        global host
        global port
        global s
        print("Binding socket to port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")
        socket_bind()


# Establish connection with client (socket must be listening for them)
def socket_accept():
    global conn
    global msgServer

    
    conn, address = s.accept()
    print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))
    #recv_commands(conn)
    
    
    t1 = threading.Thread(name='buzzer', target=checkEngine, daemon=True)
    t2 = threading.Thread(name='recv_commands', target=recv_commands, daemon=True)
    t3 = threading.Thread(name='send_commands', target=send_commands, daemon=True)
    t4 = threading.Thread(name='sendAlert', target=sendAlert, daemon=True)
    t5 = threading.Thread(name='childBuckle', target=childBuckle, daemon=True)
    t6 = threading.Thread(name='tempSensor', target=tempSensor, daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    
    
    conn.close()

def temp_raw():

            temp_sensor = "/sys/bus/w1/devices/28-000008a4a886/w1_slave"
            f = open(temp_sensor, 'r')
            lines = f.readlines()
            f.close()
            return lines

def read_temp():

       
        lines = temp_raw()
        while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = temp_raw()


        temp_output = lines[1].find('t=')

        if temp_output != -1:
                temp_string = lines[1].strip()[temp_output+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c  

def tempSensor():

        global tempState
        global msgServer
        global sendMsg
        
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')


        MAX_TEMP = 24  # MAX_TEMP value for testing.
        
        
        while True:
                #check if engine off and child in the car
                #check temp from the sensor and save it to a local var
                #compare the current temp to the MAX_TEMP value

                tempState = read_temp()
                time.sleep(1)
                #print(tempState)

                if( (not engineState) and buckleup and (tempState > MAX_TEMP)):
                        motorActive()
                        msgServer = "windowOpened"
                        sendMsg = True
                        time.sleep(.5)
                        

    

def childBuckle():
        global buckleup

        while True:
                if(GPIO.input(childBucklePin) == 1):
                        buckleup = buckleup^1
                        if buckleup:
                                print("child buckled")
                        else:
                                print("child unbuckled")
                        time.sleep(.5)
                        
                
def motorActive():

        #open window
        global motor1E
        global motor1A
        global motor1B
        GPIO.output(motor1A,GPIO.HIGH)
        GPIO.output(motor1B,GPIO.LOW)
        GPIO.output(motor1E,GPIO.HIGH)
        time.sleep(2)

        GPIO.output(motor1A,GPIO.LOW)
        
        

        
                       
def windowUp():
        #close window
        global motor1E
        global motor1A
        global motor1B 
        
        GPIO.output(motor1A,GPIO.LOW)
        GPIO.output(motor1B,GPIO.HIGH)
        GPIO.output(motor1E,GPIO.HIGH)
        time.sleep(2)

        GPIO.output(motor1B,GPIO.LOW)
        
        
                

def checkEngine():
    global engineState
    
    while True:
            
        if(GPIO.input(switchPin) == 1):
                engineState = engineState^1
                if engineState:
                        print("engine on")
                else:
                        print("engine off")
                
        time.sleep(.5)

        while(not engineState and buckleup):
                kidRemainderBuzzer()
                GPIO.output(ledPin, True)
                time.sleep(.5)
                GPIO.output(ledPin, False)
                time.sleep(.5)
                GPIO.output(ledPin, False)
                time.sleep(.5)
                
                if(GPIO.input(switchPin) == 1):
                        engineState = engineState^1
                        print("engine on")
                        time.sleep(.5)
                        
                
def sendAlert():

         global engineState
         global msgServer
         global sendMsg
         
         time.sleep(2)
         while True:
                 
                 while (not engineState and buckleup):
                      msgServer = "alert"
                      sendMsg = True
                      time.sleep(20)
              
         


def kidRemainderBuzzer():

    global tempState
    
    GPIO.output(buzzerPin, True)
    time.sleep(.1)
    GPIO.output(buzzerPin, False)
    time.sleep(.1)
    GPIO.output(buzzerPin, True)
    time.sleep(.1)
    GPIO.output(buzzerPin, False)

    print(tempState)
    time.sleep(2)
    
    
    
#send command
def send_commands():
        global conn
        global s
        global msgServer
        global sendMsg

        while True:
                if(sendMsg):
                        print(msgServer)
                        conn.send(bytes(msgServer+"\r\n",'UTF-8'))
                        sendMsg = False
                        time.sleep(1)
                

# Recv commands
def recv_commands():

        while True:
        
                global engineState
                global sendMsg
                global msgServer
                global tempState
                

                cmd = str(conn.recv(1024), "utf-8").strip()

                if cmd == "led":
                    print("leds")
                    GPIO.output(ledPin, True)
                    time.sleep(1)
                    GPIO.output(ledPin, False)
                    
                elif (cmd == "Motor"):
                    #open window
                     motorActive()
                     msgServer = "windowOpened"
                     sendMsg = True 
                     print("Turn window down")
                    
                elif (cmd == "closeWindow"): 
                        windowUp()
                        msgServer = "windowUp"
                        sendMsg = True        
                        print("Turn window up")
                        
                elif (cmd == "Temperature"): 
                        print(tempState)
            
                else:
                    print(cmd)
            
	   

def main():
    
    try:
        createQRcode();
        gpioInit()
        socket_create()
        socket_bind()
        socket_accept()
        
    except KeyboardInterrupt:
        global s
        s.close()
        GPIO.cleanup()


main()
