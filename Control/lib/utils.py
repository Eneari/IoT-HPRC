#!/usr/bin/python
# -*- coding: utf-8 -*-
# funzione che verifica a quale porta USB e' collegato arduino
def find_usb(vid,pid):

    import subprocess
    try:
        stringa=subprocess.check_output("ls /dev/ttyUSB*", shell=True)
    except:
        return None
    
    lista = stringa.decode('UTF-8').split('\n')
    porta = None
    for row in lista :
        if row :
            comando = f"udevadm info -n {row} "
            stringa=subprocess.check_output(comando, shell=True)
            stringa = stringa.decode('UTF-8')
            if (vid in stringa)  and  (pid in stringa) :
                porta = row
                break
    return porta

#------------------------------------------------------------------
##  cerco la porta di arduino con VID e PID

def getArduino(vid,pid):

    import pyfirmata
    import sys
    ArduinoPort = find_usb(vid,pid)

    if not ArduinoPort :
            print("Arduino non collegato---------------  Exit")
            sys.exit()
    else :
            print("Arduino collegato a ..... : ",ArduinoPort)

    board = pyfirmata.ArduinoMega(ArduinoPort)

    return board

#------------------------------------------------------------------
##  leggo i parametri dal file di configurazione (config.ini)
def getConfig(arg,param):
    from configparser import ConfigParser

    parser = ConfigParser()
    parser.read('config.ini')

    return parser.get(arg, param)

# ----------------------------------------------
def isTimeFormat(input):
    import time
    try:
        time.strptime(input, '%H:%M:%S')
        return True
    except ValueError:
        try :
            time.strptime(input, '%H:%M')
            return True
        except ValueError:
            return False


#--------------------------------------------------------------
# -------------------------------------------------------------------------------
messaggi = []

def on_message(client, userdata, message):
    print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
    
    global messaggi
    messaggi.append(message.topic +"|"+ str(message.payload.decode("utf-8"))  ) 


def start_mqtt() :
    from lib import utils
    import paho.mqtt.client as mqtt #import the client

    
    # --- leggo l'indirizzo del broker MQTT ---
    broker_address = utils.getConfig('serverMQTT','host')
    port           = int(utils.getConfig('serverMQTT','port'))

    print("creating new instance")
    client = mqtt.Client() #create new instance
      
    client.connect(broker_address,port) #connect to broker
    return client
##------------------------------------------------------------
def get_message(topic) :

    import time
    import paho.mqtt.client as mqtt #import the client

    
# --- leggo l'indirizzo del broker MQTT ---
    broker_address = getConfig('serverMQTT','host')
    port           = int(getConfig('serverMQTT','port'))

    print("creating new instance")
    client = mqtt.Client() #create new instance
    #client.on_connect = on_connect
    client.on_message = on_message
    print("connecting to broker")
    client.connect(broker_address,port) #connect to broker

    client.subscribe(topic)
    

    while True :
        # scorro la lista a rovescio per leggere il valore piu' recente
        #print("messaggi -----------------------")
        #print (messaggi)
        for messaggio in reversed(messaggi) :
            appo = messaggio.split("|")
            lista = appo[0].split("/")
            compo  = lista[len(lista)-1]
            codice = appo[0][: appo[0].index(compo)-1]
            valore = appo[1]
        
        if messaggi :
            client.loop_stop()
            client.disconnect()
            return valore

        client.loop_start()
       
	
        time.sleep(.1)
#--------------------------------------------------------------------
def publish_message(topic,value) :

    import paho.mqtt.client as mqtt #import the client

    
# --- leggo l'indirizzo del broker MQTT ---
    broker_address = getConfig('serverMQTT','host')
    port           = int(getConfig('serverMQTT','port'))

    #print("creating new instance")
    client_pub = mqtt.Client() #create new instance
    #client.on_connect = on_connect
    #print("connecting to broker")
    client_pub.connect(broker_address,port) #connect to broker

    client_pub.publish(topic,value,retain=True)
    client_pub.disconnect()
