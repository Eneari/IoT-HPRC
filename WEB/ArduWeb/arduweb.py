from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flask_cors import CORS


import json

from ArduWeb.auth import login_required
from ArduWeb.db import get_db

bp = Blueprint('arduweb', __name__,static_folder='static')



# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]



@bp.route('/')
def index():
    
    return render_template('index.html')


@bp.route('/<string:sezione>/list'  )
@login_required
def list(sezione):
    
    
    db = get_db()
    
    stringa = f'''SELECT id, codice, descrizione ,topic ,modifica
                    FROM gruppi WHERE section = "{sezione}" order by ordinamento''' 
        
    gruppi = db.execute(stringa).fetchall()


    stringa = f'''SELECT id, codice, descrizione 
                    FROM sottogruppi WHERE section = "{sezione}" ''' 
        
    sottogruppi = db.execute(stringa).fetchall()
    
    
#     
#     stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id
#          FROM componenti c , gruppi g
#          WHERE g.section = "{sezione}"
#          AND  c.gruppo_id = g.id 
#          AND  c.livello = "0"
#          order by g.ordinamento, c.ordinamento'''
#     
    
    stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id, c.livello, c.sottogruppo_id
         FROM componenti c , gruppi g
         WHERE g.section = "{sezione}"
         AND  c.gruppo_id = g.id 
         order by g.ordinamento, c.ordinamento'''
         
    componenti = db.execute(stringa).fetchall()
    

    return render_template('list.html', gruppi=gruppi, componenti=componenti, sottogruppi = sottogruppi)

@bp.route('/get_decod' , methods=['GET']  )
def get_decod():
    
    
    db = get_db()
    
   
    stringa = " SELECT id,codice,valore,descrizione FROM decodifica "
         
    decodifica = db.execute(stringa).fetchall()
    
    
    # Enable Access-Control-Allow-Origin
    response = jsonify(decodifica)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, {'Content-Type': 'application/json; charset=utf-8'}
    
    
    #items = []
    #for riga in decodifica :
    #    items.append({'id':riga[0], 'codice':riga[1],'valore':riga[2],'descrizione':riga[3]})
    
    #print(items)
    #decodifica = json.dumps({'items':items})
    #decodifica = jsonify(items)
    
    #print(decodifica)
    #prova =  dict(zip(decodifica.keys(), decodifica)) 
    #decodifica = jsonify(decodifica)
    #print(stringa)
    #print(decodifica)
    #print(prova)

    #return decodifica   
##----------------------------------------------------------------------
@bp.route('/get_gruppi/' , methods=['GET'] )

def get_gruppi():
    
    sezione = "acs"
    
    db = get_db()
    
    stringa = f'''SELECT id, codice, descrizione ,topic ,modifica
                    FROM gruppi WHERE section = "{sezione}" order by ordinamento'''
         
    gruppi = db.execute(stringa).fetchall()
    
    return jsonify(gruppi)
    
##----------------------------------------------------------------------
@bp.route('/get_compo/' , methods=['GET'] )
@bp.route('/get_compo/<gruppo>/' , methods=['GET'] )

def get_compo(gruppo="*"):
    
    sezione = "acs"
    
    print("gruppo : ",gruppo)
    
    db = get_db()
    
    if gruppo == "*" :
    
      stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id, c.livello, c.sottogruppo_id
           FROM componenti c , gruppi g
           WHERE g.section = "{sezione}"
           AND  c.gruppo_id = g.id 
           order by g.ordinamento, c.ordinamento'''
    else:
      stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id, c.livello, c.sottogruppo_id
           FROM componenti c , gruppi g
           WHERE g.section = "{sezione}"
           AND  c.gruppo_id = g.id 
           AND  g.id = {gruppo}
           order by g.ordinamento, c.ordinamento'''
         
    componenti = db.execute(stringa).fetchall()
    return jsonify(componenti)
    
    
# A route to return all of the available entries in our catalog.
@bp.route('/get_prova/' , methods=['GET'] )
def get_prova():
    
    print("sono in get provaaaaaaaaaaaaaaa")
    pippo = jsonify(books)
    
    print(pippo)
    
    
    return pippo

    
    
@bp.route('/get_sonda'   )
def get_sonda():
    
    print("sono in get sonda")
    db = get_db()
    
   
    stringa = " SELECT id,codice,compo,descrizione FROM componenti WHERE tipo_compo = 'ST' ORDER BY id"
         
    decodifica = db.execute(stringa).fetchall()
    return jsonify(decodifica)
    items = []
    for riga in decodifica :
        items.append({'id':riga[0], 'codice':riga[1],'compo':riga[2],'descrizione':riga[3]})
    decodifica = json.dumps({'items':items})
    #decodifica = jsonify(items)
    
    #print(decodifica)
    #prova =  dict(zip(decodifica.keys(), decodifica)) 
    #decodifica = jsonify(decodifica)
    #print(stringa)
    #print(decodifica)
    #print(prova)

    return decodifica



@login_required
@bp.route('/<string:sezione>/schema'  )
def schema(sezione):
    
    db = get_db()
    
    stringa = f'''SELECT id, codice, descrizione ,topic ,modifica
                    FROM gruppi WHERE section = "{sezione}" order by ordinamento''' 
        
    gruppi = db.execute(stringa).fetchall()
    
#     
#     stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id
#          FROM componenti c , gruppi g
#          WHERE g.section = "{sezione}"
#          AND  c.gruppo_id = g.id 
#          AND  c.livello = "0"
#          order by g.ordinamento, c.ordinamento'''
#     
    
    stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id, c.livello
         FROM componenti c , gruppi g
         WHERE g.section = "{sezione}"
         AND  c.gruppo_id = g.id 
         order by g.ordinamento, c.ordinamento'''
         
    componenti = db.execute(stringa).fetchall()
    

    return render_template('schema.html', gruppi=gruppi, componenti=componenti)

