#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

messaggi = []

def on_message(client, userdata, message):
    #print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
    
    global messaggi
    messaggi.append(message.topic +"|"+ str(message.payload.decode("utf-8"))  ) 

##------------------------------------------------------------
def get_message(topic="ST/VAL/ST02") :

    import time
    import paho.mqtt.client as mqtt #import the client
    from lib import utils
    #import utils
    global messaggi
    
# --- leggo l'indirizzo del broker MQTT ---
    broker_address = utils.getConfig('serverMQTT','host')
    port           = int(utils.getConfig('serverMQTT','port'))

    #print("creating new instance")
    client = mqtt.Client("prova") #create new instance
    #client.on_connect = on_connect
    client.on_message = on_message
    #print("connecting to broker")
    
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
            
            client.loop_stop()
            #client.disconnect()
            messaggi = []
            return valore

        client.loop_start()
       
	
        time.sleep(.1)
        


if __name__ == '__main__':
    get_message()

