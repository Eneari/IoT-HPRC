#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Arducontrol.py
#  
#  Copyright 2020 Enea Rinaldi <rinaldienea.rinaldi@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import logging
logger = logging.getLogger(__name__)

##logging.basicConfig(filename='Ardupython.log',  format='%(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='example.log',level=logging.DEBUG)

from lib import Vm
from lib import Gr
from lib import utils
import time

import paho.mqtt.client as mqtt #import the client

import sqlite3
conn = sqlite3.connect(utils.getConfig('Sqlitedb','dbfile'),timeout=30.0)


MAX_TIME = 60  # costante aggiornamento clock

# --- connetto arduino a firmata ---
board = utils.getArduino(utils.getConfig('Arduino','vid'),utils.getConfig('Arduino','pid'))
#board = ""


def main():
   
    # ---leggo tutte le valvole presenti
    query = "SELECT codice FROM apparati WHERE tipo = 'VT' "
    c = conn.cursor()
    c.execute(query)
    valvole = c.fetchall()
    c.close()

    logging.debug(" ELABORO LE VALVOLE-------")
        
    for row in  valvole :
        valvola = Vm.VM(board,f"{row[0]}")
        valvola.start()

    print("sono uscito da valvole  ...............")

    # ---leggo tutti i gruppi presenti
    query = "SELECT codice FROM groups "
    c = conn.cursor()
    c.execute(query)
    gruppi = c.fetchall()
    c.close()
    for row in  gruppi :
        gruppo = Gr.GR(board,f"{row[0]}")
        gruppo.start()#

        # time.sleep(.2)

    print("sono uscito da gruppi  ...............")

    
    # Loop infinito per inviare il clock a intervalli di tempo
    # serve per forzare i controlli da parte dei componenti
    # e gestire l'alternanza

    old_time = 0


    while True:

        timestamp = int(time.time())  # Unix time in seconds

        """ print("-----------------------------------")
        print("timestamp   ", str(timestamp))
        print("old_time    ", str(old_time))
        print("MAX_TIME    ", str(MAX_TIME))
        print("-----------------------------------") """


        if timestamp > ( MAX_TIME + old_time ) : 
            
            
            # attivo il client MQTT
            print("creating new instance")

            client = mqtt.Client(transport="websockets") #create new instance

            print("connecting to broker")
            #logging.info("connecting to broker ........ ")
            client.connect("localhost",8080) 

            old_time = timestamp
            print(" aggiorno timestamp......... ",str(timestamp))
            client.publish("TIMESTAMP", str(timestamp),retain=True)
            client.disconnect()


        time.sleep(10)
    
    
    
    

if __name__ == '__main__':
    main()
