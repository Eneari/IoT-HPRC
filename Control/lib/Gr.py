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

import traceback
# ------------------------------------------------------------------------

from lib import Bm
from lib import utils
import time
import sys
buffer = {}

valori_GR = {}
valori_BM = {}

chk_time = False


#-------------------------------------------------------------------------
class GR():
    
    first_time = True
    
   
    def __init__(self,gruppo,pumps):

        self.gruppo = gruppo
        self.pumps=pumps
                
        # creo l'oggetto pompe -------------------------------
        self.oggio = Bm.BM(gruppo)
        
        #def run(self):
        #LOG_FILENAME = './log/GR-'+self.gruppo+'.log'
        LOG_FILENAME = './log/GR.log'
        logger = logging.getLogger(self.gruppo)

        

        logging.basicConfig(filename=LOG_FILENAME,
                            format=' %(levelname)s - %(filename)s:%(lineno)s  - %(asctime)s - %(message)s  -%(processName)s',
                            level=logging.DEBUG,
                            )


        client = mqtt.Client(transport="websockets") #create new instance
        client.on_message=self.on_message #attach function to callback
        client.on_connect=self.on_connect #attach function to callback
        #client.on_subscribe=self.on_subscribe #attach function to callback


        #print("connecting to broker")
                
        logging.info("--------  ELABORO GRUPPO ........ "+self.gruppo)
        
        logging.info("connecting to broker ........ ")
        client.connect("localhost",8080) 

        result = client.subscribe([("GR/CONS/"+self.gruppo,0),
                            ("GR/ST/"+self.gruppo,0),
                            ("GR/SP/"+self.gruppo,0),
                            ("GR/CONS/SP/"+self.gruppo,0),
                            ("GR/ALM/ON/"+self.gruppo,0),
                            ("GR/ALM/OFF/"+self.gruppo,0),
                            ("TIMESTAMP",0)
                            ])
                            
        logging.info("subscribe result ...1..... ")
        logging.info(result)
        # Sottoscrivo i messaggi delle pompe del gruppo  ----
        for pump in self.pumps :
            
            client.subscribe([("BM/STATUS/"+pump[0],0),
                            ("BM/JOB/START/"+pump[0],0),
                            ("BM/JOB/TIME/"+pump[0],0),
                            ("BM/PIN/"+pump[0],0),
                            ])
                            
        logging.info("subscribe result ...2..... ")
        logging.info(result)

        while True :

            client.loop_start()
	
            time.sleep(2)
            #client.loop_stop()
            
            

    
 #------------------------------------------------------------
    def on_message(self,client, userdata, message):
        
        
        #print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
        
        stringa = str(message.payload.decode("utf-8"))
        
        logging.debug("message received " +message.topic+"  "+stringa )
        
        if (message.topic[:2] == "BM" )  :
            valori_BM[message.topic] = stringa
            GR_chk = False
        else:
            valori_GR[message.topic] = stringa
            GR_chk = True
            
            
        if (message.topic=="TIMESTAMP" ):
            #print("ho ricevuto un timestamp")
            global chk_time
            chk_time = True
            GR_chk = True
            

        # se specificata una sonda, sottoscrivo il valore
        if message.topic == f"GR/ST/{self.gruppo}"  :
            client.subscribe(stringa)
    
            
        # se sono arrivati tutti i dati sulla consegna delle pompe 
        # eseguo una tantum l'allineamento di arduino in fase di avvio
        if self.first_time :
            if not read_settings_BM(self.pumps) :
                try:
                    self.oggio.sincro(self.pumps,valori_BM)
                    self.first_time = False
                except:
                    logging.error(" Errore chiamata sincro ",exc_info=True)
                    traceback.print_exc()

                    raise
        
        #------------------------------------------------------------
        
        
        
        # eseguo i controlli 
        if GR_chk :
            try:
                # verifico coerenza dei dati ricevuti per il gruppo
                try:
                    error_GR = read_settings_GR(self.gruppo)
                except:
                    logging.error("errore in error GR",exc_info=True)
                    traceback.print_exc()
                    raise
                    
                if not error_GR :
                    try:
                        error_BM = read_settings_BM(self.pumps) 
                    except:
                        logging.error("errore in read_settings BM",exc_info=True)
                        traceback.print_exc()
                        raise
                        
            except:
                logging.error("errore in read_settings nel Gruppo :" + self.gruppo)
                traceback.print_exc()
                raise
          
            if not error_GR and not error_BM :                    
                try:
                    chk_consegna_GR(self.oggio,self.gruppo,self.pumps,client)
                except:
                    logging.error("errore in chk_consegna GR nel Gruppo :" +self.gruppo)
                    traceback.print_exc()
                    raise
        
    #------------------------------
    def on_connect(self,client, userdata, flags, rc):
        #print("connected.........")
        logging.debug("connected.........")

    
    
#----------------------------------------------------------------------
def read_settings_GR(gruppo):


    #print("------------------ sono in read settings---GR-")
    #print(valori_GR)

    errore = False

    # leggo la consegna ----------------------------------------
    consegna = valori_GR.get(f"GR/CONS/{gruppo}",  None)
        
    if consegna :
        ammessi=['00','11','21','99','19','29']
        if consegna not in ammessi :
            #print("consegna non ammessa : ",consegna)
            consegna = None
            errore = True
    else:
        #print("consegna non inserita")
        pass
    buffer["consegna"]= consegna

    # leggo orario accensione ----------------------------------
    time_on = valori_GR.get(f"GR/ALM/ON/{gruppo}",  None)
        
    if time_on :
        if not utils.isTimeFormat(time_on) :
            print("orario accensione non ammesso : ",time_on)
            time_on = None
            errore = True
    
        
    buffer['time_on']= time_on

    # leggo orario spegnimento ----------------------------------
    time_off = valori_GR.get(f"GR/ALM/OFF/{gruppo}",  None)

    if time_off :
        if not utils.isTimeFormat(time_off) :
            print("orario spegnimento non ammesso : ",time_off)
            time_off = None
            errore = True
   
    buffer['time_off']= time_off
    
    # verifico se orari di accensione e spegnimento sono congruenti
    if (time_on and time_off)  or (not time_on and not time_off) :
        pass
    else:
        print("orari accensione-spegnimento incongruenti : ",time_on, time_off)
        errore = True

    # leggo il set point temperatura ----------------------------
    set_point = valori_GR.get(f"GR/SP/{gruppo}",  None)

    if set_point :
        try:
            set_point = float(set_point)
        except ValueError:
            #print("set_point non ammesso : ",set_point)
            set_point = None
            errore = True
    #else :
        #print("set point non inserito")
    buffer['set_point']= set_point
    
    # leggo la consegna per il set point temperatura ------------------
    consegna_set_point = valori_GR.get(f"GR/CONS/SP/{gruppo}",  None)

    if consegna_set_point :
        ammessi=['0','1']
        if consegna_set_point not in ammessi :
            #print("consegna set point non ammessa : ",consegna_set_point)
            consegna_set_point = None
            errore = True
    #else:
    #    print("consegna set point non inserita")
    buffer["consegna_set_point"]= consegna_set_point

    # leggo la sonda temperatura ----------------------------
    sonda_t = valori_GR.get(f"GR/ST/{gruppo}",  None)
    if sonda_t :
        sonda_t = sonda_t.strip()
    #else :
    #   print("sonda temp  non inserito")
    buffer['sonda_t']= sonda_t

    # leggo la  temperatura della sonda se esiste----------------------------
    temperatura = None
    sonda_t  = get_settings('sonda_t')
    if sonda_t :
        temperatura = valori_GR.get(sonda_t,None)
        if temperatura :

            temperatura = temperatura.strip()

            try:
                temperatura = float(temperatura)
            except ValueError:
                logging.error("temperatura non ammessa : "+temperatura)
                temperatura = None
                errore = True
        else :
            print("temperatura  non pervenuta")
            errore = True
            
    buffer['temperatura']= temperatura
    
    # leggo il timestamp del clock----------------------------------
    timestamp = valori_GR.get("TIMESTAMP",None)
    buffer['timestamp']= timestamp
    
    

    return errore 
    
#----------------------------------------------------------------------
def read_settings_BM(pumps):
    
    #print("------------------ sono in read settings BM----")
    #print(valori_BM)

    
    errore = False


    for compo in pumps :
        
        #print("Pompa in elab....", str(compo[0]))

        
        # leggo il pin ---------------------------------------------
        pin = valori_BM.get(f"BM/PIN/{compo[0]}", None )
            
        if pin :
            if pin.isdigit() :
                pass
            else:
                print("PIN non valido ",str(pin))
                errore = True
        else:
            #print("PIN non inserito")
            errore = True
           
        # leggo lo stato ---------------------------------------------
        status = valori_BM.get(f"BM/STATUS/{compo[0]}", None )
            
        if status :
            if status not in ['0','1']:
                print("Stato non valido ",str(status))
                errore = True
        else:
            print("stato non inserito")
            errore = True
        
    
    return errore 
    
# -----------------------------------------
def get_settings(var):

    try :
        return str(buffer[var])
    except:
        return None

# ----------------------------------------------------------------------------
def chk_consegna_GR(oggio,gruppo,pumps,client) :

    #from lib import utils
    #from lib import messages
    import time
    
    global chk_time

#       consegna :	consegna del componente
#	time_on :	orario di accensione del componente
#	time_off :	orario di spegnimento del componente
#	set_point :	set point temperatura del componente
#	sonda_t :	sonda temperatura per controllare il set point del componente
#	pin :	        pin output di arduino
#       status :        status attuale del componente
#       consegna_set_point : consegna per il set point temperatura



    consegna  = get_settings('consegna')
    time_on   = get_settings('time_on')
    time_off  = get_settings('time_off')
    set_point = get_settings('set_point')
    sonda_t   = get_settings('sonda_t')
    temperatura  = get_settings('temperatura')
    consegna_set_point  = get_settings('consegna_set_point')
    timestamp  = get_settings('timestamp')



    chk_consegna  = True
    chk_set_point = True
    chk_time_on   = True
    chk_time_off  = True
    
    #print("--------  PARAMETRI GRUPPO ------------",gruppo)
    #print("consegna ---- ",consegna)
    #print("time on ---- ",time_on)
    #print("time off ---- ",time_off)
    #print("set_point ---- ",set_point)
    #print("sonda_t ---- ",sonda_t)
    #print("consegna_set_point ---- ",consegna_set_point)

    #logging.info("status ------  : "+status)
    logging.info("consegna ----  : "+consegna)
    logging.info("time on  ----  : "+time_on)
    logging.info("time off ----  : "+time_off)
    logging.info("set point ---  : "+str(set_point))
    logging.info("consegna sp -  : "+consegna_set_point)
    logging.info("sonda t  ----  : "+sonda_t)
    logging.info("temperatura -  : "+str(temperatura))

    
    

    # eseguo i controlli in base alla consegna ----------------------
		
    if consegna == '00' :       # paro total
        chk_consegna = False
    elif consegna[1:2] == '1' :     # marcha forzada de 1 bomba
        chk_consegna = True  
		
    if consegna[1:2] == '9' :       # automatico
            
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
        if time_on != "None" :
            
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if  current_time > time_on:
                chk_time_on = True
            else:
                chk_time_on = False
        #verifico orario stop -------------------------------------
        if time_off != "None" :
           
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if  current_time > time_off:
                chk_time_off = False
            else:
                chk_time_off = True

    #  ---- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #print("------------ PARAMETRI CHECK ---")
    #print("---chk_consegna   :",str(chk_consegna))
    #print("---chk_set_point  :",str(chk_set_point))
    #print("---chk_time_on    :",str(chk_time_on))
    #print("---chk_time_off   :",str(chk_time_off))
    #print("------FINE------ PARAMETRI CHECK ---")

    
    
    if chk_consegna  and  chk_set_point and  chk_time_on and  chk_time_off  :
        #print(" check true ------ ")
        consegna_grp = True
    else :
        #print(" check false ------  ")
        consegna_grp = False


    #print("------------ PARAMETRI CHIAMATA chk_consegna_BM ---")
    #print("---gruppo  :",gruppo)
    #print("---consegna  :",consegna)
    #print("---consegna_grp  :",consegna_grp)
    #print("---pumps  :")
    #print(pumps)

    #print("------------ PARAMETRI CHIAMATA chk_consegna_BM ---FINEEEEEEE")
  
    
   
    
    try:
        ritorno = oggio.chk_consegna_BM( gruppo,consegna,consegna_grp,pumps,valori_BM)
    except:
        logging.error("errore in chiamata chk_consegna_BM")
        traceback.print_exc()
        
        raise
        
    # se arrivato un clock, aggiorno i tempi di lavoro delle pompe
    if chk_time :
        try:
            ritorno1 = oggio.upd_timestamp( pumps,timestamp,valori_BM)
            chk_time = False
        except:
            logging.error("errore in chiamata upd_timestamp")
            traceback.print_exc()
            raise
            
        for message in ritorno1 :
            #print(message,ritorno1[message])        
            client.publish(message, ritorno1[message],retain=True)
        oggio.ritorno1 = {}


    #print("------------MESSAGGI DA PUBBLICARE -----------")

    for message in ritorno :
        #print(message,ritorno[message])
        
        # memorizzo il messaggio per non processarlo nuovamente
        #messages_sends[message] = ritorno[message]
        
        client.publish(message, ritorno[message],retain=True)
        
    # ripulisco
    oggio.clear_ritorno()
    
           
# -------------------------------------------------------------------------------

