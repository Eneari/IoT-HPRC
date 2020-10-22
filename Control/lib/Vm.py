#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  ---   nomenclatura dei componenti ----------------
#
#	consegna :	consegna del componente
#	time_on :	orario di accensione del componente
#	time_off :	orario di spegnimento del componente
#	set_point :	set point temperatura del componente
#	sonda_t :	sonda temperatura per controllare il set point del componente
#	pin :		pin arduino a cui e' collegato il componente
# ------------------------------------------------------------------------
import paho.mqtt.client as mqtt #import the client

import logging
logger = logging.getLogger(__name__)
LOG_FILENAME = 'VM.log'

#logging.basicConfig(filename='VM.log',  format='%(name)s - %(levelname)s - %(message)s')%(filename)s:%(lineno)s 
logging.basicConfig(filename=LOG_FILENAME,
                    format=' %(levelname)s - %(filename)s - %(asctime)s - %(message)s  ',
                    level=logging.DEBUG,
                    )

from threading import Thread
from lib import utils
import time
import sys
buffer = {}
messaggi = {}
valori = {}


#-------------------------------------------------------------------------
class VM(Thread):

    def __init__(self,board,compo):
        Thread.__init__(self)
        self.board = board
        self.compo = compo
        self.first_time = True

       
    #----------------------------------
    def run(self):

        print("creating new instance")

        client = mqtt.Client(transport="websockets") #create new instance
        client.on_message=self.on_message #attach function to callback
        client.on_connect=self.on_connect #attach function to callback
        #client.on_subscribe=self.on_subscribe #attach function to callback


        #print("connecting to broker")
        logging.info("connecting to broker ........ ")
        client.connect("localhost",8080) 

        client.subscribe("VT/#")
        #client.subscribe("ST/#")
        client.subscribe("TIMESTAMP")


        while True :
            #print("---  messaggi  -----")

            client.loop_start()
	
            time.sleep(1)
    
             

    #------------------------------
    def on_message(self,client, userdata, message):
        #print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
        logging.debug("message received " +message.topic+"  "+str(message.payload.decode("utf-8")))

        valori[message.topic] = str(message.payload.decode("utf-8"))

        
        # todo bisogna filtrare la valvola !!!!!!!!!!!!!!
        if message.topic == f"VT/ST/{self.compo}"  :
            client.subscribe(str(message.payload.decode("utf-8")))
            
        
        # eseguo i controlli in base alla consegna
        error = read_settings(self.compo,client)
      
        if not error :
            if self.first_time :
                set_pin(self.board)
                self.first_time = False

            chk_consegna(self.compo,self.board,client)
        
    #------------------------------
    def on_connect(self):
        #print("connected.........")
        logging.debug("connected.........")


# leggo la consegna ----------------------------------------
def read_settings(compo,client):

    errore = False

    #print("SONO IN Read_settings-------------")
    #logging.debug("SONO IN Read_settings-------------")

    consegna=valori.get(f"VT/CONS/{compo}",  None)
    if consegna :
        consegna = consegna.strip()
        ammessi=['0','1','9']
        if consegna not in ammessi :
            #print("consegna non ammessa : ",consegna)
            logging.error("consegna non ammessa : "+consegna)
            consegna = None
            errore = True
    else:
        #print("consegna non inserita")
        logging.error("consegna non inserita ")
        errore = True
    buffer["consegna"]= consegna

    # leggo orario accensione ----------------------------------

    time_on = valori.get(f"VT/ALM/ON/{compo}",None)
    if time_on :
        time_on = time_on.strip()
        if not utils.isTimeFormat(time_on) :
            print("orario accensione non ammesso : ",time_on)
            time_on = None
    #else :
    #    print("orario accensione non inserito")
    buffer['time_on']= time_on

    # leggo orario spegnimento ----------------------------------

    time_off = valori.get(f"VT/ALM/OFF/{compo}",None)
    if time_off :
        time_off = time_off.strip()
        if not utils.isTimeFormat(time_off) :
            print("orario accensione non ammesso : ",time_off)
            time_off = None
    #else :
    #    print("orario spegnimento non inserito")
    buffer['time_off']= time_off

    # leggo il set point temperatura ----------------------------

    set_point = valori.get(f"VT/SP/{compo}",None)
    if set_point :
        set_point = set_point.strip()
        try:
            set_point = float(set_point)
        except ValueError:
            print("set_point non ammesso : ",set_point)
            set_point = None
    #else :
        #print("set point non inserito")
    buffer['set_point']= set_point

# leggo la consegna per il set point temperatura ------------------

    consegna_set_point = valori.get(f"VT/CONS/SP/{compo}",None)
    if consegna_set_point :
        consegna_set_point = consegna_set_point.strip()
        ammessi=['0','1']
        if consegna_set_point not in ammessi :
            print("consegna set point non ammessa : ",consegna_set_point)
            consegna_set_point = None
    #else:
    #    print("consegna set point non inserita")
    buffer["consegna_set_point"]= consegna_set_point

    # leggo la sonda temperatura ----------------------------
    sonda_t = valori.get(f"VT/ST/{compo}",None)
    if sonda_t :
        sonda_t = sonda_t.strip()
    #else :
    #   print("sonda temp  non inserito")
    buffer['sonda_t']= sonda_t

     # leggo la  temperatura della sonda se esiste----------------------------
    temperatura = None
    sonda_t  = get_settings('sonda_t')
    if sonda_t :
        temperatura = valori.get(sonda_t,None)
        temperatura = temperatura.strip()
        if temperatura :

            try:
                temperatura = float(temperatura)
            except ValueError:
                #print("pin non ammesso : ",pin)
                logging.error("temperatura non ammessa : "+temperatura)
                temperatura = None
                errore = True
        #else :
        #   print("sonda temp  non inserito")
    buffer['temperatura']= temperatura

    # leggo il pin ----------------------------
    pin = valori.get(f"VT/PIN/{compo}",None)
    if pin :
        pin = pin.strip()
        try:
            pin = int(pin)
        except ValueError:
            #print("pin non ammesso : ",pin)
            logging.error("pin non ammesso : "+pin)
            pin = None
            errore = True
    else :
        #print("pin non inserito")
        logging.error("pin non inserito : ")
        errore = True
    buffer['pin']= pin

    # leggo lo stato  ----------------------------
    status = valori.get(f"VT/STATUS/{compo}",None)
    if status :
        status = status.strip()
    else :
        #print("status non inserito")
        logging.error("status non inserito : ")
        errore = True
    buffer['status']= status

    return errore

# -----------------------------------------
def get_settings(var):
	return buffer[var]


# -----------------------------------------
# alla prima chiamata resetto il pin arduino

def set_pin(board):
    pin  = get_settings('pin')
    status  = get_settings('status')

    board.digital[int(pin)].write(int(status))
    return
       
#-----------------------------------------
def chk_consegna(compo,board,client) :

    #print("SONO IN chk_consegna-------------")
    #logging.debug("SONO IN chk_consegna-------------")


    from lib import utils
   


#       consegna :	consegna del componente
#	time_on :	orario di accensione del componente
#	time_off :	orario di spegnimento del componente
#	set_point :	set point temperatura del componente
#	sonda_t :	sonda temperatura per controllare il set point del componente
#	pin :	        pin output di arduino
#       status :        status attuale del componente
#       consegna_set_point : consegna per il set point temperatura


    consegna  = get_settings('consegna')
    time_on  = get_settings('time_on')
    time_off  = get_settings('time_off')
    set_point  = get_settings('set_point')
    sonda_t  = get_settings('sonda_t')
    temperatura  = get_settings('temperatura')
    pin  = get_settings('pin')
    status  = get_settings('status')
    consegna_set_point  = get_settings('consegna_set_point')

    chk_consegna  = True
    chk_set_point = True
    chk_time_on   = True
    chk_time_off  = True


  
    
    # se settata una sonda di temperatura, leggo dal broker
    # l'ultimo valore inviato
    # if sonda_t :
        
    #     temperatura = messages.get_message(f"ST/VAL/{sonda_t}")
    #     print("temperatura -- ; ",sonda_t," ",str(temperatura))
    
    # print("consegna ---- ",consegna)
    # print("time on ---- ",time_on)
    # print("time off ---- ",time_off)
    # print("set_point ---- ",set_point)
    # print("sonda_t ---- ",sonda_t)
    # print("pin ---- ",pin)
    # print("status ---- ",status)
    # print("consegna_set_point ---- ",consegna_set_point)
   
    logging.info("status ------  : "+status)
    logging.info("consegna ----  : "+consegna)
    logging.info("time on  ----  : "+time_on)
    logging.info("time off ----  : "+time_off)
    logging.info("set point ---  : "+str(set_point))
    logging.info("consegna sp -  : "+consegna_set_point)
    logging.info("sonda t  ----  : "+sonda_t)
    logging.info("temperatura -  : "+str(temperatura))
    logging.info("pin  --------  : "+str(pin))


    # eseguo i controlli in base ala consegna ----------------------
		
    if consegna == '0' :       # cerrada
        chk_consegna = False
    elif consegna == '1' :     # abierta
        chk_consegna = True       
        
    elif consegna == '9' :     # automatico ( orario + temperatura )
        #verifico set point temperatura-----------------------------
        if sonda_t and set_point :
            if temperatura :
                if float(temperatura) > float(set_point) :
                    # verifico la consegna per il set point temperatura
                    if consegna_set_point and consegna_set_point == '0' :
                        chk_set_point = False
                    else:
                        chk_set_point = True
                else :
                    # verifico la consegna per il set point temperatura
                    if consegna_set_point and consegna_set_point == '0' :
                        chk_set_point = True
                    else:
                        chk_set_point = False


        #verifico orario start -------------------------------------
        if time_on :
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if  current_time > time_on:
                chk_time_on = True
            else:
                chk_time_on = False
        #verifico orario stop -------------------------------------
        if time_off :
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if  current_time > time_off:
                chk_time_off = False
            else:
                chk_time_off = True

    #  ----   arduino
    #arduino_status = str(board.digital[pin].read())

    #print("Arduino Status ------ ", arduino_status)
    #print(board.digital[6].read())

    if chk_consegna  and  chk_set_point and  chk_time_on and  chk_time_off  :
        #print(" check true ------ ")
        
        if status == "0"  :
            #print(" ------- setto a 1 ")
            board.digital[pin].write(1)
            client.publish(f"VT/STATUS/{compo}", '1',retain=True)
            #utils.publish_message(f"VT/STATUS/{compo}", '1')
           
    else :
        #print(" check false ------  ")
        if status == "1" :
            #print("  ------ setto a 0 ")
            board.digital[pin].write(0)
            client.publish(f"VT/STATUS/{compo}", '0',retain=True)
            #utils.publish_message(f"VT/STATUS/{compo}", '0')


                