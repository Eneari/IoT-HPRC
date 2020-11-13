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
    
    
    ritorno  = {}

    def __init__(self,gruppo):
        self.gruppo = gruppo
        
        
        LOG_FILENAME = './log/GR-'+self.gruppo+'.log'
        #logger = logging.getLogger(self.gruppo)
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
        
        #timestamp = int(time.time())  # Unix time in seconds
        
        pompe=[]
        
        for items in pumps:
            pompe.append(items[0])
               
        if consegna == '00' :       # tutte le pompe spente            
         
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

        #  solo la pompa indicata (forzata o automatico
        elif (consegna[1:2]  in ["1" ,"9"] ) and (consegna != "99"): 

            pompa_sel = None
            for compo in  pompe :
                if consegna[0:1] == compo[-1:] : # sono sulla pompa indicata in consegna
                    pompa_sel = compo
                    break
            
            if pompa_sel :
                self.set_pompa(pompe,pompa_sel,consegna_grp,valori)
            else:
                logging.error(" NON TROVATA LA POMPA DA ELABORARE")
                return

        elif consegna  == "99"  :   # automatico ( orario + temperatura ) da controllo gruppo + alternanza

            alt_pumps = {}
            
            for compo in  pompe :
                #alt_set = valori[f"BM/JOB/ALT/SET/{compo}"]
                alt_time = valori.get(f"BM/JOB/ALT/TIME/{compo}",0)
                status = valori.get(f"BM/STATUS/{compo}","")
                #alt_start = valori[f"BM/JOB/ALT/START/{compo}"]
                alt_pumps[compo] = status
                
            # Ordino la lista per avere prima lo stato a 1
            sorted_list=sorted(alt_pumps, key=alt_pumps.__getitem__,reverse=True)
            #print( sorted_list)
            
            #print(alt_pumps)
            
          
            pompa_sel = None
            for pompa in sorted_list :
                
                alt_set  = valori.get(f"BM/JOB/ALT/SET/{pompa}",0)
                alt_time = valori.get(f"BM/JOB/ALT/TIME/{pompa}",0)
                status   = valori.get(f"BM/STATUS/{pompa}","")
                
                if (status == "1" )  and (int(alt_time) > int(alt_set) ):
                    
                    continue
                else:
                    if status == "0" :
                        pompa_sel = pompa
                        # resetto il tempo di alternanza---
                        self.ritorno[f"BM/JOB/ALT/TIME/{pompa}"] = "0"
                        break
            
            if pompa_sel == None :
                pompa_sel = sorted_list[0]
                # resetto il tempo di alternanza---
                self.ritorno[f"BM/JOB/ALT/TIME/{pompa_sel}"] = "0"
                
            self.set_pompa(pompe,pompa_sel,consegna_grp,valori)
            

        #print("-----------   FINE  CHECK CONSEGNA BM -------")
        return 
        
####----------------------------------------------------------------------------------
    def set_pompa(self,pompe,pompa_sel,consegna_grp,valori) :
        
        #print("sono in set pompa---------------------------------")
        timestamp = int(time.time())  # Unix time in seconds


        for compo in  pompe :

            # leggo i dati della pompa
            #print("pompa in elab... 5",compo)
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
            #logging.debug(" Consegna              : "+consegna)

            if consegna_grp == True :  # check gruppo = acceso
                if pompa_sel == compo : # sono sulla pompa indicata 
                    if status == '0':
                        try:
                            #board.digital[int(pin)].write(1)
                            send_socket(f"DO;{str(pin)};1")
                            self.ritorno[f"BM/JOB/START/{compo}"] = str(timestamp)
                            logging.debug(" Aggiorno Arduino ------: PIN "+str(pin)+" - 1")

                        except:
                            logging.critical(" Errore comunicazione Arduino",exc_info=True)

                        #client.publish(f"BM/STATUS/{compo}", '1',retain=True)
                        logging.debug(f" aggiorno lo stato -  BM/STATUS/{compo}    = 1" )

                        self.ritorno[f"BM/STATUS/{compo}"] = '1'

                    
                else :  # se non e' la pompa indicata  ed e' accesa, la spengo
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


####----------------------------------------------------------------------------------
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
    def upd_timestamp(self,pumps,delta_time,valori,alternanza) :
        
        #print( valori)

        for compo in pumps  :
            # leggo i dati della pompa
            
            status = valori[f"BM/STATUS/{compo[0]}"]
            job_time     = valori.get(f"BM/JOB/TIME/{compo[0]}",0)
            job_alt_time = valori.get(f"BM/JOB/ALT/TIME/{compo[0]}",0)


            if status == "1" :
                self.ritorno[f"BM/JOB/TIME/{compo[0]}"] = str(int(job_time) + int(delta_time) )
                
                #if alternanza :
                    
                self.ritorno[f"BM/JOB/ALT/TIME/{compo[0]}"] = str(int(job_alt_time) + int(delta_time) )
                
            
# ----------------------------------------------------------------------------
def send_socket(stringa) :
    
    #print("----------  SEND SOCKET -------")
    #print(stringa)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(stringa.encode())
    
    return
#-------------------------------------------------------------------------

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
