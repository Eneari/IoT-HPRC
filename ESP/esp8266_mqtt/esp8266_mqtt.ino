/*

25/12/2019     ----   prove MQTT su ESP8266


*/
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#include <Wire.h>  // Only needed for Arduino 1.6.5 and earlier
#include "heltec.h" // alias for `#include "SSD1306Wire.h"`

#include <math.h>

#include <ESP8266HTTPClient.h>

#include <NTPClient.h>
#include <PubSubClient.h>


#ifndef STASSID
#define STASSID "Martin Router King"
#define STAPSK  "fe1de2ri3co4"
#endif

const char* ssid = STASSID;
const char* password = STAPSK;

float temp_old = 0 ;

const long utcOffsetInSeconds = 0;
//char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

const String host = "192.168.1.21";
const String port = "88";

IPAddress mqtt_server(192, 168, 1, 39);

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

//----------------------------------------------------------------------
void setup() {
	
	Serial.begin(115200);
	Serial.println("Booting");
	//
	//Heltec.display->clear();
	//Heltec.display->setFont(ArialMT_Plain_10);
	//Heltec.display->drawString(0,2,"Booting..........");
	//Heltec.display->display();
	//
	setup_wifi();
	client.setServer(mqtt_server, 1883);
	client.setCallback(callback);
	
	while (WiFi.waitForConnectResult() != WL_CONNECTED) {
		Serial.println("Connection Failed! Rebooting...");
		delay(5000);
		ESP.restart();

	}

  // Port defaults to 8266
   ArduinoOTA.setPort(8266);

  // Hostname defaults to esp8266-[ChipID]
   ArduinoOTA.setHostname("myesp8266");

  // No authentication by default
  //ArduinoOTA.setPassword("admin");
  //ArduinoOTA.setPassword((const char *)"123");

  // Password can be set with it's md5 value as well
  //MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  //ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_SPIFFS
      type = "filesystem";
    }

    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  ArduinoOTA.begin();
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  //  fine  OTA  ---------------------
  
	// avvio NTP
	timeClient.begin();

	// - Declaramos los pines de entrada
	pinMode(0, INPUT);



	Heltec.begin(true /*DisplayEnable Enable*/, true /*Serial Enable*/);
	Heltec.display->init();
	Heltec.display->flipScreenVertically();
  
	// invio l'aggiornamento di data e ora ad arduino  --------------------

	String send_string ="";
	send_string = "http://"+host+":"+port+"/ajax_settings/SYN["+get_DateTime() +"]";
	  
	send_HTTP(send_string);  
  
}

void loop() {
  ArduinoOTA.handle();
  
  float temperatura = get_NTC();
  //Serial.print("differenza : ");
  //Serial.println(fabs(temperatura - temp_old));
  temperatura = round(temperatura*10)/10;
  
  if (fabs(temperatura - temp_old) > 0.3) {
	    
	  Serial.println("Scrivo sul display");
	  Heltec.display->clear();
	  
	  //Heltec.display->setFont(ArialMT_Plain_24);
	  Heltec.display->setFont(DejaVu_Sans_Mono_Bold_32);
	  Heltec.display->drawString(0,2,String(temperatura)+"°c");
	  Heltec.display->display();
	  
	  //-----------------------------
	  
	  
	  //String send_string ="";
	  
	  //send_string = "http://"+host+":"+port+"/ajax_settings/PUT[ST/VAL/ST10="+String(temperatura)+"]" ;
	  
	  // invio l'aggiornamento della temperatura ad arduino
	  //send_HTTP(send_string);
	  
	  // invio al broker mqtt la temperatura aggiornata ----
		if (!client.connected()) {
			reconnect();
		}
		client.loop();
		char result[8]; // Buffer big enough for 7-character float
		dtostrf(temperatura, 6, 2, result); // Leave room for too large numbers!
		Serial.println(result);
		client.publish("ST/VAL/ST10", result,true);
	   
  };
  
  
  temp_old = temperatura;
  

  delay(5000);
  
  

}

/****************************************************************************
** funzione che restituisce la temperatura da una sonda NTC                **
*****************************************************************************/
float get_NTC() 
{
	//Datos para las ecuaciones

	float Vin = 3.3;     // [V]       Tensión alimentación del divisor
	float Rfija = 10000;  // [ohm]     Resistencia fija del divisor
	//float R25 = 2980;    // [ohm]     Valor de NTC a 25ºC
	float R25 = 12600;    // [ohm]     Valor de NTC a 25ºC

	//float Beta = 3900.0; // [K]      Parámetro Beta de NTC
	float Beta = 3900.0; // [K]      Parámetro Beta de NTC
	float T0 = 293.15;   // [K]       Temperatura de referencia en Kelvin

	float Vout = 0.0;    // [V]       Variable para almacenar Vout
	float Rntc = 0.0;    // [ohm]     Variable para NTC en ohmnios

	float TempK = 0.0;   // [K]       Temperatura salida en Kelvin
	float TempC = 0.0;   // [ºC]      Temperatura salida en Celsius

	//Primero la Vout del divisor
	Vout=(Vin/1024)*(analogRead(A0));

	//Ahora la resistencia de la NTC
	Rntc=(Vout*Rfija)/(Vin-Vout);

	//Y por último la temperatura en Kelvin
	TempK = Beta/(log(Rntc/R25)+(Beta/T0));

	//Y ahora la pasamos a celsius
	TempC = TempK-273.15 + 2.0;
	
	return TempC;
	
}

/****************************************************************************
** funzione che restituisce dateTime da server NTP                         **
*****************************************************************************/
String get_DateTime() 
{
	String formattedDate="";
	
	timeClient.update();
	formattedDate = timeClient.getFormattedDate();
	
	// ripulisco la stringa
	formattedDate.replace('T','-');
	formattedDate.replace('Z',' ');
	
	return formattedDate;

	
}

/****************************************************************************
** funzione che restituisce dateTime da server NTP                         **
*****************************************************************************/
void send_HTTP(String stringa) 
{
	HTTPClient http;  //Declare an object of class HTTPClient

	Serial.println(stringa);

	http.begin(stringa);  
	
	http.addHeader("Content-Type", "Content-Type: text/xml");
	
	int httpCode = http.GET();     //Send the request     
		                                      

	if (httpCode > 0) { //Check the returning code

	  String payload = http.getString();   //Get the request response payload
	  Serial.println(payload);                     //Print the response payload
	} 
	else {
		Serial.println("[HTTP] GET... failed, error: ");
		Serial.println(http.errorToString(httpCode).c_str());

	} ;

	http.end();   //Close connection
	 
	
}
void setup_wifi() {
  Serial.print("Connecting to ");
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // booh ????
  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
