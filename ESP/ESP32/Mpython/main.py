# Complete project details at https://RandomNerdTutorials.com

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()


#roms = ds_sensor.scan()
#print('Found DS devices: ', roms)

# definisco gli indirizzi delle sonde
SondeTemp = {}
SondeVal  = {}
SondeVal["ST/VAL/ST01"] = 0
SondeVal["ST/VAL/ST02"] = 0
SondeVal["ST/VAL/ST03"] = 0
SondeVal["ST/VAL/ST04"] = 0
SondeVal["ST/VAL/ST05"] = 0
SondeVal["ST/VAL/ST06"] = 0

SondeTemp["ST/VAL/ST01"] = bytearray(b'(\xffu\\\xb4\x16\x05f')
SondeTemp["ST/VAL/ST02"] = bytearray(b'(\xff\xe5\xca\xb4\x16\x03\xe4')
SondeTemp["ST/VAL/ST03"] = bytearray(b'(\xff\xee^\xb4\x16\x05\xa6')
SondeTemp["ST/VAL/ST04"] = bytearray(b'(\xff\x8fn\xb4\x16\x052')
SondeTemp["ST/VAL/ST05"] = bytearray(b'(\xff$\xc6\xc0\x16\x04\xeb')
SondeTemp["ST/VAL/ST06"] = bytearray(b'(\xff$\xc6\xc0\x16\x04\xeb')


while True:
  try:
    client.check_msg()
  except OSError as e:
    restart_and_reconnect()
    
  ds_sensor.convert_temp()
  time.sleep_ms(750)
  for sonda in SondeTemp:
    val = ds_sensor.read_temp(SondeTemp[str(sonda)])
   
    if val != SondeVal[str(sonda)] :
      #print(str(sonda))
      #print(val)
      SondeVal[str(sonda)] = val
      try:
        client.publish(str(sonda), str(val),retain=True)
      except OSError as e:
        restart_and_reconnect()
    
  time.sleep(1)

