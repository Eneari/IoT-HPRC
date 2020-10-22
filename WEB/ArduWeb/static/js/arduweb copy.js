

// ----   configurazione MQtt ---------- INIZIO ----------
var hostname = "localhost";
var port = 8080;
//var clientId = "ArduWeb";
var clientId = "clientID-" + parseInt(Math.random() * 100);
clientId += new Date().getUTCMilliseconds();
var username = "";
var password = "";
var decod=Object;


var codici = [];
var valori = [];
var dec_codice = [];
var dec_valore = [];
var dec_descrizione = [];

var origin   = window.location.origin;   // Returns base URL (https://example.com)

//--------------------------------------------
$.get( origin+"/get_decod" , function( result ) {

    decod = JSON.parse(result);
    
     for (var y = 0; y < decod.items.length; y++) {
         
        dec_codice[y] = decod.items[y].codice;  
        dec_valore[y] = decod.items[y].valore;
        dec_descrizione[y] = decod.items[y].descrizione; 
    }             
              
});

// ------------------------------------------------
mqttClient = new Paho.MQTT.Client(hostname, port, clientId);

mqttClient.onMessageArrived =  MessageArrived;
mqttClient.onConnectionLost = ConnectionLost;


Connect();


// ----   configurazione MQtt ---------- FINE ----------
/*Initiates a connection to the MQTT broker*/
function Connect(){
    window.console.log("----sono in connect -------");

    mqttClient.connect({
        onSuccess: Connected,
        onFailure: ConnectionFailed,
        keepAliveInterval: 60
        
    });
}

/*Callback for successful MQTT connection */
function Connected() {
  window.console.log("Connected");
  
    mqttClient.subscribe('#');
}

/*Callback for failed connection*/
function ConnectionFailed(res) {
    window.console.log("Connect failed:" + res.errorMessage);

}

/*Callback for lost connection*/
function ConnectionLost(res) {
  if (res.errorCode !== 0) {
    window.console.log("Connection lost:" + res.errorMessage);

    Connect();
  }
}

/*Callback for incoming message processing */
function MessageArrived(message) {
    //console.log(message.destinationName +" : " + message.payloadString);
    var componente = message.destinationName ;
    
     //var res = str.replace(/blue/g, "red"); 
    //componente = componente.replace(/\//g, "_")
    
    var valore     = message.payloadString ;
    
    // verifico se sono nel grafico
    var a = document.getElementById("svgObject");
    var grafo = false;
    
    if (a !== null){
        grafo = true;
    }
    
    // aggiorno la lista dei valori
    setValore(componente,valore);
    
   // window.console.log(componente);
    //window.console.log(valore);
    if ( grafo) {
        window.console.log(" sono in grafo---------------");
        //var normal = document.getElementById(componente);
        var svgDoc = a.contentDocument;
           // window.console.log(svgDoc);

        // Get one of the SVG items by ID;
        var normal = svgDoc.getElementById("ST_VAL_ST01");
        window.console.log(normal);
        //var normal = document.getElementById("ST02");pippo
    }
    else {
        var normal = document.getElementById(componente);
        
    }
    
    //window.console.log("componente")
    //window.console.log(normal)

     
    var modal  = document.getElementById("modal-"+componente);
    
   
    if (normal !== null) {
        Fill(componente,valore,normal,"NORMAL");    
    }
    
    if (modal !== null) {
        Fill(componente,valore,modal,"MODAL");   
    }
    
    
}


// Publish a Message
function MessageSend(codice,valore) {

    //window.console.log(" dati mqtt------- "+codice + "  "+valore)
    var message = new Paho.MQTT.Message(valore);
    message.destinationName = codice;
    message.qos = 0;
    message.retained = true;
    
    mqttClient.send(message);

}

/*---------------------------------------------------------*/

function Fill(componente,valore,target,tipo){
 
    var tipo_campo =target.dataset.tipo;
    
        
    switch(tipo_campo) {
        case "TEMP":  
            var val = Number(valore);
            target.innerHTML = val.toFixed(2) + "  C°";
    
            break;
            
        case "NUM":  
            var val = Number(valore);
             target.innerHTML = val ;
            
             break;
             
        case "RADIO":  
         
            // verifico se esiste il RADIO button nella form ----
            
            var label_off = 'label-0-'+componente;
            var label_on  = 'label-1-'+componente;
            var v_descr_off = "";
            var v_descr_on = "";
            
            var radio = document.getElementById(label_off);
            
            // -- definisco la decodifica dei valori-- 
            if (radio !== null & tipo == "NORMAL" ) {
                v_descr_off = LookUpDescrizione(componente.substring(0,componente.lastIndexOf("/")),"0");
                v_descr_on  = LookUpDescrizione(componente.substring(0,componente.lastIndexOf("/")),"1");
               
                document.getElementById(label_off).innerHTML = v_descr_off;  
                document.getElementById(label_on).innerHTML  = v_descr_on;
            
                var off = '0-'+componente;
                var on  = '1-'+componente;
                if (valore == '0') {
                    document.getElementById(off).checked  = true;
                    document.getElementById(off).disabled = false;
                    document.getElementById(on).disabled = true;
                    document.getElementById(on).checked  = false; 
                     
                }
                else {
                    document.getElementById(off).disabled = true;
                    document.getElementById(off).checked = false;
                    document.getElementById(on).disabled = false;
                    document.getElementById(on).checked = true;
                }
                 
                break;
            }
            else {
                target.innerHTML = valore + " " +LookUpDescrizione(componente.substring(0,componente.lastIndexOf("/")),valore);
            
            }  
            
            break;
               
        default:
        
            target.innerHTML = valore + " " +LookUpDescrizione(componente.substring(0,componente.lastIndexOf("/")),valore);
      
             
    }
}

/*******************************************************************/
function LookUpDescrizione(codice,valore) { 

        //window.console.log("-----------dentro loockup------------")
        
    for (var y = 0; y < decod.items.length; y++) {
                       
        if (decod.items[y].codice == codice  &  decod.items[y].valore == valore  ){
            
            //window.console.log(decod.items[y].descrizione);
            return decod.items[y].descrizione;
            
        }
    }
    
    return "" ;
}
/**************************************************************/
function setValore(codice,valore) { 

    var trovato = false;

    // verifico se il falore esiste gia', altrimenti lo aggiungo
     for (var y = 0; y < codici.length; y++) {
     
        if (codici[y] == codice)  {
            
            trovato = true;
            break;
        }
     }
     
     if(trovato){
         
         valori[y] = valore;
     }
     else {
         codici.push(codice);
         valori.push(valore);
         
     }

    return;

}
/**********************************************************/
function getValore(codice) { 

    for (var z = 0; z < codici.length; z++) {
    
        if (codici[z] == codice)  {
            return valori[z];
        }      
    }
    return null;
}

/************************************************************/
 
function getTxt(file){
  var result = false;
  $.ajax({
    url:file,
    async: false,
    dataType: "html",
    success: function (data){
    
     result = data;
    }
  });
  //line added to return ajax response
    return result;
}
    
/************************************************************/

function getDecod(codice) {

    var ret_valori = [];
    var ret_descrizioni = [];

     for (var z = 0; z < dec_codice.length; z++) {
    
        if (dec_codice[z] == codice)  {
            ret_valori.push(dec_valore[z]);
            ret_descrizioni.push(dec_descrizione[z]);
        }      
    }
    return [ret_descrizioni,ret_valori];
}



