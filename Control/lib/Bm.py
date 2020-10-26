#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  ---   nomenclatura dei componenti ----------------
#
#	
#	pin :		pin arduino a cui e' collegato il componente
# ------------------------------------------------------------------------

import paho.mqtt.client as mqtt #import the client

from threading import Thread


import logging
logger = logging.getLogger(__name__)
LOG_FILENAME = 'BM.log'

#logging.basicConfig(filename='BM.log',  format='%(name)s - %(levelname)s - %(message)s')%(filename)s:%(lineno)s 
logging.basicConfig(filename=LOG_FILENAME,
                    format=' %(levelname)s - %(threadname)s - %(asctime)s - %(message)s  ',
                    level=logging.DEBUG,
                    )


from lib import utils
import time

buffer = {}
valori = {}
pompe = []
first_time = {}


#-------------------------------------------------------------------------
class BM():

    def __init__(self, board,gruppo,consegna,consegna_grp=True):
        self.board = board
        self.gruppo = gruppo
        self.consegna=consegna
        self.consegna_grp=consegna_grp


        print("------------  istanzio pompa-----")

    #def run(self):      

        client = mqtt.Client(transport="websockets") #create new instance
        client.on_message=self.on_message #attach function to callback
        client.on_connect=self.on_connect #attach function to callback

        print("connecting to broker")
        logging.info("connecting to broker ........ ")
        client.connect("localhost",8080) 

        
        client.subscribe("BM/#")
        client.subscribe("TIMESTAMP")


        while True :
            print("---  messaggi  -----")

            client.loop_start()
	
            time.sleep(1) 
            client.loop_stop()

            return
        
   

    #--------------------------------------------------------
    def on_message(self,client, userdata, message):
        #print("message received " ,message.topic,"  ",str(message.payload.decode("utf-8")))
        #logging.debug("message received " +message.topic+"  "+str(message.payload.decode("utf-8")))
        
        # filtro solo le pompe del gruppo
        if (message.topic[-4:-2] ==  self.gruppo[-2:] )  :

            logging.debug("message received " +message.topic+"  "+str(message.payload.decode("utf-8")))
            stringa = str(message.payload.decode("utf-8"))
            valori[message.topic] = stringa
            
            compo = message.topic[message.topic.rfind("/")+1:]

            try:
                first_time[compo]
            except :
                first_time[compo] = True

            try:
                pompe.index(compo)
            except:
                pompe.append(compo)

        
        #-# eseguo i controlli di congruenza sui dati

        general_error = True

        for compo in pompe:
            
            error = read_settings(compo)
      
            if not error :
                if first_time[compo] :
                    set_pin(self.board)
                    first_time[compo] = False
                general_error = False
            else :
                general_error = True

        if not general_error :
            chk_consegna(self.board,self.gruppo,self.consegna, self.consegna_grp,client)

        # se un aggiornamento di clock aggiorno i tempi di lavoro delle pompe
        if (message.topic ==  "TIMESTAMP" ) :
            logging.debug("message received " +message.topic+"  "+str(message.payload.decode("utf-8")))
            upd_timestamp(str(message.payload.decode("utf-8"))  ,client )



        
    #------------------------------
    def on_connect(self):
        print("connected.........")
        logging.debug("connected.........")


#----------------------------------------------------------------------
def read_settings(compo):
    #print("--------- sono in read settings BM --------------- ",compo)

    errore = False
   


    # leggo il pin ----------------------------
    pin = valori.get(f"BM/PIN/{compo}",None)
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
    status = valori.get(f"BM/STATUS/{compo}",None)
    if status :
        status = status.strip()
    else :
        #print("status non inserito")
        logging.error("status non inserito : ")
        errore = True
    buffer['status']= status

    
    
    # leggo il tempo di alternanza ----------------------------
    try:
        job_alt_set = valori[f"BM/JOB/ALT/SET/{compo}"]
        job_alt_set = int(job_alt_set.strip())
    except :
        job_alt_set = None
        print("job_alt_set non inserito")
        
    buffer['job_alt_set']= job_alt_set

    # leggo il timestamp di start assoluto  ----------------------------
    try:
        job_start = valori[f"BM/JOB/START/{compo}"]
        job_start = int(job_start.strip())
    except:
        job_start = None
        print("job_start non inserito")

    buffer['job_start']= job_start

    # leggo il tempo  assoluto  di lavoro ----------------------------
    try:
        job_time = valori[f"BM/JOB/TIME/{compo}"]
        job_time = int(job_time.strip())
    except:
        job_time = None
        print("job_time non inserito")
        
    buffer['job_time']= job_time

    # leggo il timestamp di start alternanza ----------------------------
    try:
        job_alt_start = valori[f"BM/JOB/ALT/START/{compo}"]
        job_alt_start = int(job_alt_start.strip())
    except:
        job_alt_start = None
        print("job_alt_start non inserito ",compo)
        
    buffer['job_alt_start']= job_alt_start

    # leggo il tempo  di lavoro alternanza ----------------------------
    try:
        job_alt_time = valori[f"BM/JOB/ALT/TIME/{compo}"] 
        job_alt_time = int(job_alt_time.strip())
    except:
        job_alt_time = None
        print("job_alt_time non inserito ",compo)
        
    buffer['job_alt_time']= job_alt_time
    
    
    
    return errore

# -----------------------------------------
def get_settings(var):

    try :
        return str(buffer[var])
    except :
        return None

# ----------------------------------------------------------------------------
def chk_consegna(board,gruppo,consegna, consegna_grp,client) :


    # from lib import utils
    # from lib import messages
    import time



    #alternanza = False
           
    if consegna == '00' :       # tutte le pompe spente
        
        
        for compo in pompe  :
            # leggo i dati della pompa
            print("pompa in elab... ",compo)
            pin = valori[f"BM/PIN/{compo}"]
            print("pin... ",pin)
            status = valori[f"BM/STATUS/{compo}"]
            print("status... ",status)

            if status == '1':
                print("spengo la pompa ... ",compo)
                board.digital[int(pin)].write(0)
                print("aggiorno lo stato ... ",compo)
                client.publish(f"BM/STATUS/{compo}", '0',retain=True)


    elif consegna[1:2]  == "1"  : # marcha solo la pompa indicata
        
        for compo in  pompe :
            # leggo i dati della pompa
            print("pompa in elab... ",compo)
            pin = valori[f"BM/PIN/{compo}"]
            print("pin... ",pin)
            status = valori[f"BM/STATUS/{compo}"]
            print("status... ",status)
        
            if consegna[0:1] == compo[-1:] : # sono sulla pompa indicata in consegna
                #upd_status(compo,"1")
                if status == '0':
                    board.digital[int(pin)].write(1)
                    print("aggiorno lo stato ... ",compo)
                    client.publish(f"BM/STATUS/{compo}", '1',retain=True)
                    
            else :  # se non e' la pompa indicata in consegna ed e' accesa, la spengo
                # - aggiorno lo stato e il tempo di lavoro
                #upd_status(compo,"0")
                if status == '1':
                    board.digital[int(pin)].write(0)
                    print("aggiorno lo stato ... ",compo)
                    client.publish(f"BM/STATUS/{compo}", '0',retain=True)

    elif consegna[1:2]  == "9"  :   # automatico ( orario + temperatura ) da controllo gruppo

        # verifico se selezionata  alternanza
        if consegna == '99' : # automatico con alternanza
            pass
        else :    
            for compo in  pompe :
                # leggo i dati della pompa
                print("pompa in elab... ",compo)
                pin = valori[f"BM/PIN/{compo}"]
                print("pin... ",pin)
                status = valori[f"BM/STATUS/{compo}"]
                print("status... ",status)

                if consegna_grp == True :  # check gruppo = acceso
                    if consegna[0:1] == compo[-1:] : # sono sulla pompa indicata in consegna
                        # - aggiorno lo stato e il tempo di lavoro
                        #upd_status(compo,"1")
                        if status == '0':
                            board.digital[int(pin)].write(1)
                            print("aggiorno lo stato ... ",compo)
                            client.publish(f"BM/STATUS/{compo}", '1',retain=True)
                        
                    else :  # se non e' la pompa indicata in consegna ed e' accesa, la spengo
                        # - aggiorno lo stato 
                        #upd_status(compo,"0")
                        if status == '1':
                            board.digital[int(pin)].write(0)
                            print("aggiorno lo stato ... ",compo)
                            client.publish(f"BM/STATUS/{compo}", '0',retain=True)

                if consegna_grp == False :  # check gruppo = spento
                    # - aggiorno lo stato 
                    #upd_status(compo,"0")
                    if status == '1':
                            board.digital[int(pin)].write(0)
                            print("aggiorno lo stato ... ",compo)
                            client.publish(f"BM/STATUS/{compo}", '0',retain=True)





# alla prima chiamata resetto il pin arduino -----------------------------------
def set_pin(board):
    pin  = get_settings('pin')
    status  = get_settings('status')
    print("--------- sono in set pin --------------- ", str(pin)," ",str(status))

    board.digital[int(pin)].write(int(status))

    print("esco da set pin")
    return


# aggiorna il tempo di lavoro dei componenti attivi  -------------------------
def upd_timestamp(timestamp,client) :

    print("------   Upd timestamp ------------------")

    for compo in pompe  :
        # leggo i dati della pompa
        print("pompa in elab... ",compo)
        status = valori[f"BM/STATUS/{compo}"]
        print("status... ",status)

        job_start = valori[f"BM/JOB/START/{compo}"]
        #print("job_start... ",job_start)
        job_time = valori[f"BM/JOB/TIME/{compo}"]
        #print("job_time... ",job_time)

        lavoro = float(job_time) + float(timestamp) - float(job_start)

        client.publish(f"BM/JOB/START/{compo}", str(timestamp),retain=True)

        if status == "1" :
            client.publish(f"BM/JOB/TIME/{compo}", str(lavoro),retain=True)
        
