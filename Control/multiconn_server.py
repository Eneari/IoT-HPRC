#!/usr/bin/env python3.9

import sys
import socket
import selectors
import types
import time


from pymata4 import pymata4

board = pymata4.Pymata4()

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ           # | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
        
        if data.outb:
            send_message(data.outb)
           
    #if mask & selectors.EVENT_WRITE:
    #    if data.outb:
    #        print("echoing", repr(data.outb), "to", data.addr)
    #        sent = sock.send(data.outb)  # Should be ready to write
    #        data.outb = data.outb[sent:]
            
##------------------------------------------------------------------            
            
def send_message(stringa): 
    print("Dati ricevuti ----- ")
    dati = stringa.decode().split(";")
    pin_mode = dati[0]
    pin = dati[1]
    setting = dati[2]
    print(pin_mode)
    print(pin)
    print(setting)
    
    # giro il setting per la scheda rele
    if setting == '0'  :
        setting = '1'
    else:
        setting = '0'

    # set the pin mode
    board.set_pin_mode_digital_output(int(pin))
    
    #pin_state = board.get_pin_state(pin)
    #print('pin status: ', pin_state)
    #await asyncio.sleep(4)
    
    board.digital_write(int(pin), int(setting))



#if len(sys.argv) != 3:
#    print("usage:", sys.argv[0], "<host> <port>")
#    sys.exit(1)

host = '127.0.0.1'
port = 65432
#host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
                
        time.sleep(.2)
                
                
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
