

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

var sonda_codice = [];
var sonda_descrizione = [];



//window.console.log("INIZIALIZZOOOOO");

var origin   = window.location.origin;   // Returns base URL (https://example.com)

// carico la tabella di decodifica
//--------------------------------------------
$.get( origin+"/get_decod" , function( result ) {

    decod = JSON.parse(result);
    
     for (var y = 0; y < decod.items.length; y++) {
         
        dec_codice[y] = decod.items[y].codice;  
        dec_valore[y] = decod.items[y].valore;
        dec_descrizione[y] = decod.items[y].descrizione; 
    }             
    
});
// carico la lista delle sonde
//--------------------------------------------
$.get( origin+"/get_sonda" , function( result ) {

    decod = JSON.parse(result);
    
     for (var y = 0; y < decod.items.length; y++) {
         
        sonda_codice[y] = decod.items[y].codice;  
        sonda_descrizione[y] = decod.items[y].descrizione; 
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
    
    
    // aggiorno la lista dei valori
    setValore(componente,valore);
    
    //window.console.log(componente.replace(/\//g,"_"));
    //window.console.log(valore);
    var svgObject = document.getElementById('svgObject').contentDocument;
    //var svg = svgObject.getElementById('external-1');
   
    var normal = svgObject.getElementById(componente.replace(/\//g,"_"));
        
    
    
    //window.console.log("componente----"+componente)
    

     
    //var modal  = document.getElementById("modal-"+componente.replace(/\//g,"_"));
    
   
    if (normal !== null) {
       // window.console.log(normal)
        Fill(componente,valore,normal);    
    }
    
    /*
    if (modal !== null) {
        Fill(componente,valore,modal,"MODAL");   
    }
    */
    
}


// Publish a Message
/*---------------------------------------------------------*/

function MessageSend(codice,valore) {

    //window.console.log(" dati mqtt------- "+codice + "  "+valore)
    var message = new Paho.MQTT.Message(valore);
    message.destinationName = codice;
    message.qos = 0;
    message.retained = true;
    
    mqttClient.send(message);

}

/*---------------------------------------------------------*/

function Fill(componente,valore,target){
 
    var tipo_campo =componente.substring(0,2) ;

    //window.console.log(" FILL")
    //window.console.log(componente+valore+target+tipo_campo)

    var svgObject = document.getElementById('svgObject').contentDocument;
        
    switch(tipo_campo) {
        case "ST":  
            var val = Number(valore);
            target.innerHTML = val.toFixed(2) + "  C°";
    
            break;
        
        case "VT":  
            // valvola aperta ------
            if (valore == '1' ) {
                var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-open");
                if (prova !== null) {
                    prova.setAttribute('visibility', "visible");
                    prova.style.setProperty('visibility', 'visible');

                }
                var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-close");
                if (prova !== null) {
                    prova.setAttribute('visibility', "hidden");
                    prova.style.setProperty('visibility', 'hidden');

                }
            }
            else {

                //window.console.log("VALVOLA TRE VIE --------")

                var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-open");
                if (prova !== null) {
                    prova.setAttribute('visibility', "hidden");
                    prova.style.setProperty('visibility', 'hidden');
                    
                }
                var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-close");
                if (prova !== null) {

                    prova.setAttribute('visibility', "visible");
                    prova.style.setProperty('visibility', 'visible');
                }
            }
        
        
              break;
             
        case "BM":  
         
            // decodifico lo stato in forma testuale
            target.innerHTML = valore + " " +LookUpDescrizione(componente.substring(0,componente.lastIndexOf("/")),valore);
           
            //window.console.log(componente+"-color")
            // setto il colore di sfondo in base allo stato--------------
            var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-color");

            if (prova !== null) {
                //window.console.log(prova)
                
                if (valore == '1' ) {
                    prova.style.setProperty('fill', '#0CF612');
                    prova.style.setProperty('fill-opacity', '0.6');
                    prova.style.setProperty('stroke-width', '2');
                    prova.style.setProperty('stroke', '#000000');
                }
                else {
                    prova.style.setProperty('fill', '#F6150C');
                    prova.style.setProperty('fill-opacity', '0.6');
                    prova.style.setProperty('stroke-width', '2');
                    prova.style.setProperty('stroke', '#000000');

                }
            }    
            // setto l'animazione in base allo stato--------------
            var prova = svgObject.getElementById(componente.replace(/\//g,"_")+"-animate");

            if (prova !== null) {
                //window.console.log(prova)
                
                if (valore == '1' ) {
				    prova.setAttribute('attributeName', "transform");
                }
                else {
				    prova.setAttribute('attributeName', "");
                }
                
            }
            

            break;
               
        default:

            window.console.log("ESEGUO DEFAULT______")
            compo = componente.substring(0,componente.lastIndexOf("/"));
            target.innerHTML = valore + " " +LookUpDescrizione(compo,valore);
            
    }
}


/*******************************************************************/
function LookUpDescrizione(codice,valore) { 

    //window.console.log("-----------dentro loockup------------")
    //window.console.log(dec_codice);
    //window.console.log(codice);
    //window.console.log(valore);
    
for (var y = 0; y < dec_codice.length; y++) {
                   
    if (dec_codice[y] == codice  &  dec_valore[y] == valore  ){
        
        //window.console.log(decod.items[y].descrizione);
        //window.console.log(dec_descrizione[y]);
        return dec_descrizione[y];
        
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

/************************************************************/

function getSonda() {

    var ret_valori = [];
    var ret_descrizioni = [];

     for (var z = 0; z < sonda_codice.length; z++) {
    
        
            ret_valori.push(sonda_codice[z]);
            ret_descrizioni.push(sonda_descrizione[z]);
        
    }
    return [ret_descrizioni,ret_valori];
}

