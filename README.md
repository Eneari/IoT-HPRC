# Open-HAS
Open Source Hotel Automation System over IoT

Sistema de Automation  Salas de maquinas para Hoteles en Internet de las Cosas

La evolución actual de los microcontroladores permite el uso de componentes de bajo costo con características muy similares a las computadoras  reales, donde se pueden usar método de desarrollo que están muy cerca del sector de TI en general.

Dicho esto, ya no tiene sentido utilizar métodos de programación simplificados (escaleras, etc.) basados en esquemas lógicos. En estos dispositivos, ahora es posible utilizar soluciones de software idénticas a las utilizadas en el campo de TI (Sistemas operativos, lenguages de alto nivel, bases de datos, servidores Web etc.).
Esto significa que la parte estrictamente electrónica del sistema de automatización pasa a un segundo plano, es un sistema de TI que simplemente administra periféricos.

Al adoptar la filosofía de IoT, un componente "estúpido" como una sonda de temperatura, equipada con un dispositivo de interfaz simple, puede transformarse en un periférico “inteligente” que puede intercambiar información con cualquier sistema de TI, con cualquier protocolo y en cualquier contexto .



Esquema General de los componentes :

![alt text](https://github.com/Eneari/IoT-HPRC/blob/main/Doc/Overview.svg?raw=True)


1 Broker MQTT
Es el corazon de todo el projecto : todas las comunicaciones entre componentes se realizan en MQTT. Mosquitto / Paho-Mqtt por el Client ( instalar a parte )

2 Remote Station
Todos los sensores requeridos por el sistema (temperatura, presion, etc.) se equipan con un microcontrolador ESP ( ESP8266 o ESP32) que se encarga de gestionar el sensor y transmitir las lecturas al Broker MQTT.

Lenguaje : Micropython / Arduino C C++


3 ModBus Gateway
La mayoria ( si no todas) de la maquinaria existente en una planta hotelera o industrial comunica en ModBus. Este Gateway , hecho por un microcontrolador ESP  se encarga de transformar la comunicacion Modbus en MQTT en ambas directione

NO IMPLEMENTADO AL MOMENTO

4  Logic Control

Es el componente que se encarga de controlar el funcionamiento de los actuadores. Cada cambiamento en los mensaje MQTT refleja las actiones de los componente fisicos del sistema ( Bombas, valvulas etc.) 
Hecho en Python3 , se compone de pequeños modulos dedicados por componente que trabajan como Trhead en Background.
Funciona en un normal ordenador o un Single Board Computer ( Raspberry, etc.)
Se connecta via puerto serial ad un dispositivo de I-O que se hace cargo de la parte electrica del sistema, donde se conectan los componente fisico 

Al momento un Arduino o Arduino PLC con protocol Firmata.
 

5 Web Application
La aplication web comunica de forma estricta con MQTT. De aqui el usuario puede leer y configurar todos los parametros del sistema
Hecha en Flask Bootstrap es automaticamente reactiva sin usar React o Vue.js, porque el client MQTT en Javascript (PAHO) funciona ad eventos y automaticamente actualiza los contenidos cada ves que hay un cambio en los topics MQTT subscrito.

La costrucion de las paginas es dinamica, es decir que configurando los parametro de una pequeña base de datos en SQLite , la paginas se generan sola.
