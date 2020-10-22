#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt #import the client
import time
from lib import utils
import json
import sqlite3
from websocket import create_connection

conn = sqlite3.connect(utils.getConfig('Sqlitedb','dbfile'), timeout=30.0)


messaggi = []

def on_message(client, userdata, message):
    print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
    #ws = create_connection("ws://localhost:8000/ws/acs")
    #print("invio ws")
    #x = {"message": message.topic , "valore": str(message.payload.decode("utf-8"))}
    x = {"message": {"componente":message.topic , "valore": str(message.payload.decode("utf-8"))} }
    # convert into JSON:
    y = json.dumps(x)

    # the result is a JSON string:
    #print(y) 
    #stringa = f'{ "message":"{message.topic}"}'
    #print(stringa)
    #ws.send(y)
    global messaggi
    messaggi.append(message.topic +"|"+ str(message.payload.decode("utf-8"))  ) 
    #print("messaggi caricati  ")
    #print(messaggi)
    
    righe = c.execute(query)
    #print(righe)
    c.execute("commit")
    
def on_connect():
    print("connected.........")
    

    
broker_address = utils.getConfig('serverMQTT','host')
port           = int(utils.getConfig('serverMQTT','port'))
    
print("creating new instance")
client = mqtt.Client(transport="websockets") #create new instance
client.on_message=on_message #attach function to callback
client.on_connect=on_connect #attach function to callback

print("connecting to broker")
client.connect(broker_address,8080) #connect to broker
#client.loop_start() #start the loop

#client.loop_forever()



#print("Subscribing to topic","ST/VAL/ST10")
#client.subscribe("VT/#")
#client.subscribe("BM/#")
#client.subscribe("GR/#")
#client.subscribe("ST/#")
client.subscribe("#")

# all'avvio pubblico tutti i settings presenti sul db -------------------------
query = f"SELECT codice,valore,componente  FROM settings "
c = conn.cursor()
c.execute(query)
settings = c.fetchall()
c.close()

for setting in settings :
    client.publish(f"{setting[0]}/{setting[2]}", setting[1] ,retain=True)
    print("Pubblico -- ",f"{setting[0]}/{setting[2]}", setting[1])

while True :
    #print("---  messaggi  -----")
    
    for messaggio in messaggi :
        appo = messaggio.split("|")
        lista = appo[0].split("/")
        compo  = lista[len(lista)-1]
        codice = appo[0][: appo[0].index(compo)-1]
        valore = appo[1]
        #print(compo)
        #print(codice)
        #print(valore)
        query = f"REPLACE INTO settings (codice,valore,componente) VALUES('{codice}','{valore}' ,'{compo}' ) "
        c = conn.cursor()
        #print(query)
        c.execute(query)
        c.execute("commit")
        c.close()
        messaggi.remove(messaggio)
        break
	
    client.loop_start()
    
    if messaggi :
        continue
	
    time.sleep(1)
