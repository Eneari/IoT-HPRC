from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flask_cors import CORS

import json

from ArduWeb.auth import login_required
from ArduWeb.db import get_db

bp = Blueprint('arduweb', __name__,static_folder='static')



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
    
    
    
@bp.route('/get_sonda'   )
def get_sonda():
    
    db = get_db()
    
   
    stringa = " SELECT id,codice,compo,descrizione FROM componenti WHERE tipo_compo = 'ST' ORDER BY id"
         
    decodifica = db.execute(stringa).fetchall()
    return jsonify(decodifica)
    items = []
    for riga in decodifica :
        items.append({'id':riga[0], 'codice':riga[1],'compo':riga[2],'descrizione':riga[3]})
    decodifica = json.dumps({'items':items})

    return decodifica



@login_required
@bp.route('/<string:sezione>/schema'  )
def schema(sezione):
    
    db = get_db()
    
    stringa = f'''SELECT id, codice, descrizione ,topic ,modifica
                    FROM gruppi WHERE section = "{sezione}" order by ordinamento''' 
        
    gruppi = db.execute(stringa).fetchall()
        
    
    stringa = f''' SELECT c.id, c.codice, c.descrizione , c.tipo, c.modifica, c.gruppo_id, c.livello
         FROM componenti c , gruppi g
         WHERE g.section = "{sezione}"
         AND  c.gruppo_id = g.id 
         order by g.ordinamento, c.ordinamento'''
         
    componenti = db.execute(stringa).fetchall()
    

    return render_template('schema.html', gruppi=gruppi, componenti=componenti)

