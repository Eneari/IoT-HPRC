from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort


import json

from ArduWeb.auth import login_required
from ArduWeb.db import get_db

bp = Blueprint('arduweb', __name__)


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

@bp.route('/get_decod'   )
def get_decod():
    
    
    db = get_db()
    
   
    stringa = " SELECT id,codice,valore,descrizione FROM decodifica "
         
    decodifica = db.execute(stringa).fetchall()
    items = []
    for riga in decodifica :
        items.append({'id':riga[0], 'codice':riga[1],'valore':riga[2],'descrizione':riga[3]})
    decodifica = json.dumps({'items':items})
    #decodifica = jsonify(items)
    
    #print(decodifica)
    #prova =  dict(zip(decodifica.keys(), decodifica)) 
    #decodifica = jsonify(decodifica)
    #print(stringa)
    #print(decodifica)
    #print(prova)

    return decodifica
@bp.route('/get_sonda'   )
def get_sonda():
    
    
    db = get_db()
    
   
    stringa = " SELECT id,codice,compo,descrizione FROM componenti WHERE tipo_compo = 'ST' ORDER BY id"
         
    decodifica = db.execute(stringa).fetchall()
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

@bp.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s' % page_name)


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
