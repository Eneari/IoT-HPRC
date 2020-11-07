#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  ---   nomenclatura dei componenti ----------------
#
#	
#	pin :		pin arduino a cui e' collegato il componente
# ------------------------------------------------------------------------

import logging
import traceback


#from lib import utils
import time


import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


first_time = {}




#-------------------------------------------------------------------------
class BM():
    
    
    ritorno = {}


    def __init__(self,gruppo):
        self.gruppo = gruppo
        
        
        LOG_FILENAME = './log/GR-'+self.gruppo+'.log'
        logger = logging.getLogger(self.gruppo)
        #logging.basicConfig(filename=LOG_FILENAME,  
         #                   format='%(name)s - %(levelname)s - %(message)s)%(filename)s:%(lineno)s ' )
        
        
        logging.basicConfig(filename=LOG_FILENAME,
                            format=' %(levelname)s - %(filename)s:%(lineno)s  - %(asctime)s - %(message)s  ',
                            level=logging.DEBUG,
                            )
    
    # ----------------------------------------------------------------------------
    def chk_consegna_BM(self,gruppo,consegna, consegna_grp,pumps,valori) :
        
        #print("SONO IN CHK CONSEGNA----BM---------------------")
        logging.info("--------  SONO IN CHK CONSEGNA----BM........ ")
        logging.info("--consegna      :  " + consegna)
        logging.info("--consegna_grp  :  " + str(consegna_grp))


        #print(valori)
        
        pompe=[]
        
        for items in pumps:
            pompe.append(items[0])

        #alternanza = False
               
        if consegna == '00' :       # tutte le pompe spente
            logging.debug(" Consegna 00 -")
            
         
            for compo in pompe  :
                # leggo i dati della pompa
                #print("pompa in elab... 1",compo)
                
                stringa = f"BM/PIN/{compo}"
                pin = valori[str(stringa)]
                #print("pin... ",pin)
                stringa = f"BM/STATUS/{compo}"
                status = valori[str(stringa)]
                #print("status... ",status)
                
                logging.debug(" Pompa in elaborazione : "+compo)
                logging.debug(" Pin                   : "+pin)
                logging.debug(" Status                : "+status)
                logging.debug(" Consegna              : "+consegna)


                if status == '1':
                    #print("spengo la pompa ... ",compo)
                    try :
                        #board.digital[int(pin)].write(0)
                        send_socket(f"DO;{str(pin)};0")
                        logging.debug(" Aggiorno Arduino ------: PIN "+str(pin)+" - 0")

                    except :
                        logging.critical(" Errore comunicazione Arduino",exc_info=True)
                        
                    #print("aggiorno lo stato ... ",compo)
                    #client.publish(f"BM/STATUS/{compo}", '0',retain=True)
                    self.ritorno[f"BM/STATUS/{compo}"] = '0'


        elif consegna[1:2]  == "1"  : # marcha solo la pompa indicata
            #logging.debug(" Consegna 11 o 21 -")

            
            for compo in  pompe :

                # leggo i dati della pompa
                #print("pompa in elab...2 ",compo)
                pin = valori[f"BM/PIN/{compo}"]
                #print("pin... ",pin)
                status = valori[f"BM/STATUS/{compo}"]
                #print("status... ",status)
                #print("consegna... ",consegna[0:1])
                #print("compo... ",compo[-1:])
                
                logging.debug(" Pompa in elaborazione : "+compo)
                logging.debug(" Pin                   : "+pin)
                logging.debug(" Status                : "+status)
                logging.debug(" Consegna              : "+consegna)



            
                if consegna[0:1] == compo[-1:] : # sono sulla pompa indicata in consegna
                    #upd_status(compo,"1")
                    if status == '0':
                        try:
                            #board.digital[int(pin)].write(1)
                            
                            send_socket(f"DO;{str(pin)};1")
                            logging.debug(f" Aggiorno Arduino - {compo} ---: PIN "+str(pin)+" - 1")

                        except:
                            logging.critical(" Errore comunicazione Arduino",exc_info=True)

                        #print("aggiorno lo stato ... ",compo)
                        #client.publish(f"BM/STATUS/{compo}", '1',retain=True)
                        self.ritorno[f"BM/STATUS/{compo}"] = '1'
                        logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 1" )


                        
                else :  # se non e' la pompa indicata in consegna ed e' accesa, la spengo
                    # - aggiorno lo stato e il tempo di lavoro
                    #upd_status(compo,"0")
                    if status == '1':
                        try:
                            send_socket(f"DO;{str(pin)};0")
                            #board.digital[int(pin)].write(0)
                            logging.debug(f" Aggiorno Arduino - {compo} ---: PIN "+str(pin)+" - 0")


                        except:
                            logging.critical(" Errore comunicazione Arduino",exc_info=True)

                        #print("aggiorno lo stato ... ",compo)
                        #client.publish(f"BM/STATUS/{compo}", '0',retain=True)
                        self.ritorno[f"BM/STATUS/{compo}"] = '0'
                        logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 0" )



        elif consegna[1:2]  == "9"  :   # automatico ( orario + temperatura ) da controllo gruppo

            # verifico se selezionata  alternanza
            if consegna == '99' : # automatico con alternanza
                pass
            else :    
                for compo in  pompe :

                    # leggo i dati della pompa
                    #print("pompa in elab... 3",compo)
                    pin = valori[f"BM/PIN/{compo}"]
                    #print("pin... ",pin)
                    status = valori[f"BM/STATUS/{compo}"]
                    #print("status... ",status)
                    #print("consegna... ",consegna)
                    #print("compo... ",compo)

                    #print("consegna_grp... ",str(consegna_grp))
                    
                    logging.debug(" Pompa in elaborazione : "+compo)
                    logging.debug(" Pin                   : "+pin)
                    logging.debug(" Status                : "+status)
                    logging.debug(" Consegna              : "+consegna)

                    if consegna_grp == True :  # check gruppo = acceso
                        if consegna[0:1] == compo[-1:] : # sono sulla pompa indicata in consegna
                            # - aggiorno lo stato e il tempo di lavoro
                            if status == '0':
                                try:
                                    #board.digital[int(pin)].write(1)
                                    send_socket(f"DO;{str(pin)};1")

                                    logging.debug(" Aggiorno Arduino ------: PIN "+str(pin)+" - 1")

                                except:
                                    logging.critical(" Errore comunicazione Arduino",exc_info=True)

                                #client.publish(f"BM/STATUS/{compo}", '1',retain=True)
                                logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 1" )

                                self.ritorno[f"BM/STATUS/{compo}"] = '1'

                            
                        else :  # se non e' la pompa indicata in consegna ed e' accesa, la spengo
                            # - aggiorno lo stato 
                            
                            if status == '1':
                                
                                try:
                                    #board.digital[int(pin)].write(0)
                                    send_socket(f"DO;{str(pin)};0")

                                    logging.debug(" Aggiorno Arduino ------: PIN "+str(pin)+" - 0")

                                except:
                                    logging.critical(" Errore comunicazione Arduino",exc_info=True)

                                #client.publish(f"BM/STATUS/{compo}", '0',retain=True)
                                logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 0" )

                                self.ritorno[f"BM/STATUS/{compo}"] = '0'


                    if consegna_grp == False :  # check gruppo = spento
                        
                        # - aggiorno lo stato 
                        if status == '1':
                            try:
                                #board.digital[int(pin)].write(0)
                                send_socket(f"DO;{str(pin)};0")

                                logging.debug(" Aggiorno Arduino ------: PIN "+str(pin)+" - 0")

                            except:
                                logging.critical(" Errore comunicazione Arduino",exc_info=True)

                            #print("aggiorno lo stato ... ",compo)
                            #client.publish(f"BM/STATUS/{compo}", '0',retain=True)
                            logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 0" )

                            self.ritorno[f"BM/STATUS/{compo}"] = '0'

        #print("-----------   FINE  CHECK CONSEGNA BM -------")
        return self.ritorno


    def clear_ritorno(self):
        #print("---------clear retorno --------")
        self.ritorno = {}
        #print(self.ritorno)
        #print("---------clear retorno ---fineeeeee-----")
        
    #####------------------------------------------------------------------
    def sincro(self,pumps,valori_BM) :
    
        for pump in pumps :
                       
            status = valori_BM[f"BM/STATUS/{pump[0]}"]
            pin    = valori_BM[f"BM/PIN/{pump[0]}"]
                        
            send_socket(f"DO;{pin};{status}")
            


# aggiorna il tempo di lavoro dei componenti attivi  -------------------------
def upd_timestamp(timestamp,client) :

    #print("------   Upd timestamp ------------------")

    pass

    """ for compo in pompe  :
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
         """
# ----------------------------------------------------------------------------
def send_socket(stringa) :
    
    #print("----------  SEND SOCKET -------")
    #print(stringa)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(stringa.encode())
    
    return
#-------------------------------------------------------------------------

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
