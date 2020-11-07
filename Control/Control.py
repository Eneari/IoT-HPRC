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

import traceback

logger = logging.getLogger("Main")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('./log/Main.log')
fh.setLevel(logging.DEBUG)

logger.addHandler(fh)


from lib import Vm
from lib import Gr
from lib import utils
import time

import paho.mqtt.client as mqtt #import the client

from multiprocessing import Process
#import multiprocessing as mp

import sqlite3
conn = sqlite3.connect(utils.getConfig('Sqlitedb','dbfile'),timeout=30.0)


MAX_TIME = 60  # costante aggiornamento clock


def main():
       
    # ---leggo tutte le valvole presenti
    query = "SELECT codice FROM apparati WHERE tipo = 'VT' and active = 1"
    c = conn.cursor()
    c.execute(query)
    valvole = c.fetchall()
    c.close()

    logger.debug(" ELABORO LE VALVOLE-------")
        
    valvola = {}
    for row in  valvole :
        #print(" ------------------------ elaboro Valvola : ",str(row[0]))

        valvola[row[0]] = Process(target=Vm.VM, args=(f"{row[0]}",))
        valvola[row[0]].start()
        

    #print("sono uscito da valvole  ...............")

    # ---leggo tutti i gruppi presenti
    query = "SELECT codice , id FROM groups WHERE active = 1 "
    c = conn.cursor()
    c.execute(query)
    gruppi = c.fetchall()
    c.close()
    gruppo = {}
    # mp.set_start_method('spawn')    # provare con fork
    for row in  gruppi :
        
        # ---leggo tutti i componenti del gruppo
        query = f"SELECT componente FROM groups_component WHERE group_id = {row[1]}"
        c = conn.cursor()
        c.execute(query)
        pumps = c.fetchall()
        c.close()
        
        #print(" ------------------------ elaboro Gruppo : ",str(row[0]))
        
        gruppo[row[0]] = Process(target=Gr.GR, args=(f"{row[0]}",pumps,))
                
        gruppo[row[0]].start()   #
        

        # time.sleep(.2)

    #print("sono uscito da gruppi  ...............")

    
    # Loop infinito per inviare il clock a intervalli di tempo
    # serve per forzare i controlli da parte dei componenti
    # e gestire l'alternanza

    old_time = 0


    while True:
               
        timestamp = int(time.time())  # Unix time in seconds

        if timestamp > ( MAX_TIME + old_time ) : 
            #print("-----------------------------------")
            #print("timestamp   ", str(timestamp))
            #print("old_time    ", str(old_time))
            #print("MAX_TIME    ", str(MAX_TIME))
            #print("-----------------------------------") 
                
                
            # attivo il client MQTT
            #print("creating new instance")

            client = mqtt.Client(transport="websockets") #create new instance

     #       print("connecting to broker")
            #logging.info("connecting to broker ........ ")
            client.connect("localhost",8080) 

            old_time = timestamp
            #rint(" aggiorno timestamp......... ",str(timestamp))
            client.publish("TIMESTAMP", str(timestamp),retain=True)
            client.disconnect()


        time.sleep(10)
    
     

if __name__ == '__main__':
    main()
