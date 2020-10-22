#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  ---   nomenclatura dei componenti ----------------
#
#	consegna :	consegna del componente
#	time_on :	orario di accensione del componente
#	time_off :	orario di spegnimento del componente
#	set_point :	set point temperatura del componente
#	sonda_t :	sonda temperatura per controllare il set point del componente

##
##    00 - Paro total
##    11 - forzato marcha solo bomba 1
##    19 - solo bomba 1 en automatico
##    21 - forzato marcha solo bomba 2
##    29 - Solo bomba 2 en automatico 
##    91 - Forzado todo en marcha     ------------- da implementare
##    92 - Todo en marcha automatico  ------------- da implementare
##    99 - todas las bombas en automatico y alternancia
##
##
import paho.mqtt.client as mqtt #import the client
import logging
logger = logging.getLogger(__name__)
LOG_FILENAME = 'GR.log'

#logging.basicConfig(filename='VM.log',  format='%(name)s - %(levelname)s - %(message)s')%(filename)s:%(lineno)s 
logging.basicConfig(filename=LOG_FILENAME,
                    format=' %(levelname)s - %(filename)s - %(asctime)s - %(message)s  ',
                    level=logging.DEBUG,
                    )




# ------------------------------------------------------------------------
from threading import Thread

from lib import Bm
from lib import utils
import time
import sys
buffer = {}
valori = {}
messaggi = {}
pompe = {}


#-------------------------------------------------------------------------
class GR(Thread):

    def __init__(self,board,gruppo):
        Thread.__init__(self)
        self.board = board
        self.gruppo = gruppo


    def run(self):


        client = mqtt.Client(transport="websockets") #create new instance
        client.on_message=self.on_message #attach function to callback
        client.on_connect=self.on_connect #attach function to callback

        #print("connecting to broker")
        logging.info("connecting to broker ........ ")
        client.connect("localhost",8080) 

        client.subscribe("GR/#")
        #client.subscribe("BM/#")
        client.subscribe("TIMESTAMP")

        

        while True :
            #print("---  messaggi  -----")

            client.loop_start()
	
            time.sleep(1)
    
 #------------------------------
    def on_message(self,client, userdata, message):
        #print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
        logging.debug("message received " +message.topic+"  "+str(message.payload.decode("utf-8")))



        # carico le pompe del gruppo a parte
        # print("PUMP DETECT-----------------------")
        # print(message.topic[-4:-2])
        # print(self.gruppo[-2:])
        # print(message.topic[-4:-2])

        # if (message.topic[-4:-2] ==  self.gruppo[-2:] ) and ( message.topic[0:2]) ==  "BM" :
        #     #print("POMPEEE")
        #     pompe[message.topic] = str(message.payload.decode("utf-8"))
        # else :
        
        
        valori[message.topic] = str(message.payload.decode("utf-8"))


        #     client.subscribe(str(message.payload.decode("utf-8")))
         # todo bisogna filtrare la valvola !!!!!!!!!!!!!!
        if message.topic == f"GR/ST/{self.gruppo}"  :
            client.subscribe(str(message.payload.decode("utf-8")))
            
        
        # eseguo i controlli in base alla consegna
        error = read_settings(self.gruppo,client)
      
        if not error :
            chk_consegna(self.gruppo,self.board,client)
        
    #------------------------------
    def on_connect(self):
        #print("connected.........")
        logging.debug("connected.........")


#----------------------------------------------------------------------
def read_settings(gruppo,client):

    errore = False
    

    # leggo la consegna ----------------------------------------
    consegna = valori.get(f"GR/CONS/{gruppo}",  None)
        
    if consegna :
        ammessi=['00','11','21','99','19','29']
        if consegna not in ammessi :
            print("consegna non ammessa : ",consegna)
            consegna = None
            errore = True
    else:
        print("consegna non inserita")
    buffer["consegna"]= consegna

    # leggo orario accensione ----------------------------------
    time_on = valori.get(f"GR/ALM/ON/{gruppo}",  None)
        
    if time_on :
        if not utils.isTimeFormat(time_on) :
            print("orario accensione non ammesso : ",time_on)
            time_on = None
            errore = True
    #else :
        #print("orario accensione non inserito")
    buffer['time_on']= time_on

    # leggo orario spegnimento ----------------------------------
    time_off = valori.get(f"GR/ALM/OFF/{gruppo}",  None)

    if time_off :
        if not utils.isTimeFormat(time_off) :
            print("orario accensione non ammesso : ",time_off)
            time_off = None
            errore = True
    #else :
        #print("orario spegnimento non inserito")
    buffer['time_off']= time_off

    # leggo il set point temperatura ----------------------------
    set_point = valori.get(f"GR/SP/{gruppo}",  None)

    if set_point :
        try:
            set_point = float(set_point)
        except ValueError:
            print("set_point non ammesso : ",set_point)
            set_point = None
            errore = True
    #else :
        #print("set point non inserito")
    buffer['set_point']= set_point
    
    # leggo la consegna per il set point temperatura ------------------
    consegna_set_point = valori.get(f"GR/CONS/SP/{gruppo}",  None)

    if consegna_set_point :
        ammessi=['0','1']
        if consegna_set_point not in ammessi :
            print("consegna set point non ammessa : ",consegna_set_point)
            consegna_set_point = None
            errore = True
    #else:
    #    print("consegna set point non inserita")
    buffer["consegna_set_point"]= consegna_set_point

    # leggo la sonda temperatura ----------------------------
    sonda_t = valori.get(f"GR/ST/{gruppo}",  None)
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
                logging.error("temperatura non ammessa : "+temperatura)
                temperatura = None
                errore = True
        #else :
        #   print("sonda temp  non inserito")
    buffer['temperatura']= temperatura

    print(buffer)
    #print(pompe)
    return errore 

# -----------------------------------------
def get_settings(var):

    try :
        return str(buffer[var])
    except:
        return None

# ----------------------------------------------------------------------------
def chk_consegna(gruppo,board,conn) :

    from lib import utils
    from lib import messages
    import time

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

    #pin  = get_settings('pin')
    #status  = get_settings('status')
    consegna_set_point  = get_settings('consegna_set_point')
    #job_time  = get_settings('job_time')



    chk_consegna  = True
    chk_set_point = True
    chk_time_on   = True
    chk_time_off  = True
    
    print("consegna ---- ",consegna)
    print("time on ---- ",time_on)
    print("time off ---- ",time_off)
    print("set_point ---- ",set_point)
    print("sonda_t ---- ",sonda_t)
    #print("pin ---- ",pin)
    #print("status ---- ",status)
    print("consegna_set_point ---- ",consegna_set_point)
    #print("job_time ---- ",job_time)

    #logging.info("status ------  : "+status)
    logging.info("consegna ----  : "+consegna)
    logging.info("time on  ----  : "+time_on)
    logging.info("time off ----  : "+time_off)
    logging.info("set point ---  : "+str(set_point))
    logging.info("consegna sp -  : "+consegna_set_point)
    logging.info("sonda t  ----  : "+sonda_t)
    logging.info("temperatura -  : "+str(temperatura))
    #logging.info("pin  --------  : "+str(pin))

    
    

    # eseguo i controlli in base alla consegna ----------------------
		
    if consegna == '00' :       # paro total
        chk_consegna = False
    elif consegna[1:2] == '1' :     # marcha forzada de 1 bomba
        chk_consegna = True  
		
    if consegna[1:2] == '9' :       # automatico
        # se settata una sonda di temperatura, leggo dal broker
        # l'ultimo valore inviato
        # if sonda_t :
        #     temperatura = messages.get_message(f"ST/VAL/{sonda_t}")
        #     #print("temperatura -- ; ",sonda_t," ",str(temperatura))
            
        #verifico set point  --------------------------------------
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

    #  ---- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if chk_consegna  and  chk_set_point and  chk_time_on and  chk_time_off  :
        print(" check true ------ ")
        Bm.BM(board,gruppo,consegna, True)
        #pompa.run()
       
    else :
        print(" check false ------  ")
        Bm.BM(board,gruppo,consegna, False)
        #pompa.run()
        




           
# -------------------------------------------------------------------------------
