from flask import render_template, Flask, session, url_for, request, redirect, jsonify, send_file, send_from_directory, flash, make_response, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import hashlib
import requests
import random
import numpy as np
import multiprocessing
import pandas as pd
import os 
import pyqrcode
import png
import tempfile
from PIL import Image , ImageDraw, ImageFont
from zipfile37 import ZipFile

dir_path = os.path.dirname(os.path.realpath(__file__))
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', "csv"}
app = Flask(__name__)
app.secret_key = b'52d8851b5d6cbe74f7c8bb01974008140b0ae997e5b2efd987ed5b90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_design.db'
app.config.supress_callback_exceptions = True
app.config.update({
    # as the proxy server will remove the prefix
    'routes_pathname_prefix': ''

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
    , 'requests_pathname_prefix': ''
})
db = SQLAlchemy(app)


### Models
class user_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(200), nullable = False)
    type = db.Column(db.String(200), nullable = False)
    lastvalue = db.Column(db.String(200), nullable = False, default=1)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    #to avoid storage of clear text password
    password_hash =db.Column(db.String)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

### Menu
@app.route('/home')
@app.route('/')
def home():
    if 'logged_in' not in session:
        session['logged_in']=False
    if 'username' in session:
        return render_template('home.html', username = session['username'], statut = session['logged_in'])
    else:
        session['username']=""
        return render_template('home.html', username = "", statut = session['logged_in'])

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return render_template("login.html", statut = session['logged_in'])
        session['username'] = request.form['username']
        session['logged_in'] = True
        return render_template('home.html', username = session['username'], statut = session['logged_in'])
    return render_template("login.html", statut = session['logged_in'])

@app.route("/new_user", methods = ['GET', 'POST'])
def create_user():
    if request.method=='POST':
        new_user = User(username = request.form['user'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        # init dbs
        init0=user_collected_URI(user = request.form['user'], type="actuator")
        init1=user_collected_URI(user = request.form['user'], type="plant")
        init2=user_collected_URI(user = request.form['user'], type="plot")
        init3=user_collected_URI(user = request.form['user'], type="pot")
        init4=user_collected_URI(user = request.form['user'], type="ear")
        init5=user_collected_URI(user = request.form['user'], type="leaf")
        init6=user_collected_URI(user = request.form['user'], type="sensor")
        init7=user_collected_URI(user = request.form['user'], type="vector")
        db.session.add(init0)
        db.session.add(init1)
        db.session.add(init2)
        db.session.add(init3)
        db.session.add(init4)
        db.session.add(init5)
        db.session.add(init6)
        db.session.add(init7)
        db.session.commit()
        session['username'] = request.form['user']
        session['logged_in'] = True
        return redirect(url_for('home', username = session['username'], statut = session['logged_in']))
    else:
        return render_template('new_user.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('home.html', username = session['username'], statut = session['logged_in'])

@app.route("/get_started")
def get_started():
    return render_template("get_started.html", username = session['username'],  statut = session['logged_in'])

### Fonctions
@app.route("/import_dataset", methods=['POST', 'GET'])
def import_dataset():
    if request.method == 'POST': 
        if not (session['logged_in']):
            flash('You need to be connected to use this functionnality')
            return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  

        session['hostname'] = request.form['hostname']
        session['installation'] = request.form['installation']  
        if 'sep' in request.form:
            SepSetting=request.form.get('sep')
        else:
            SepSetting=","
        if 'skiprow' in request.form:
            skipSetting=int(request.form['skiprow'])
        else: 
            skipSetting=0
        f = request.files.get('file')
        f.save(os.path.join(dir_path ,'uploads','uploaded_file.csv'))

        try:
          dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
        except pd.errors.EmptyDataError:
          flash("Invalid file, did you submit a csv file ?")
          return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  

        dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)

        if request.form.get('resource_type') in ['leaf', 'ear']:
            try:
                dataset.eval(request.form['relplant'])
            except pd.core.computation.ops.UndefinedVariableError:
                flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
                return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'], datasup = request.form['relplant'])
        
        if request.form.get('resource_type') == "species":
            try:
                dataset.eval(request.form['species'])
            except pd.core.computation.ops.UndefinedVariableError:
                flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
                return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , datasup = request.form['species'])  
        
        if request.form.get('resource_type') in ['plant', 'pot', 'plot']:
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'])
        
        if request.form.get('resource_type') in ['sensor', 'vector', 'data', 'image', 'event', 'annotation','actuator']:
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , year = request.form['year'])
        
        dataset_URI.to_csv(os.path.join(dir_path,'uploads','export_URI' + request.form.get('resource_type') + '.csv'))
        response = send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI'+request.form['resource_type']  +'.csv'), mimetype="text/csv", as_attachment=True)
        # resp = Response(response=response,
        #             status=200,
        #             mimetype="text/csv")
        # resp.headers['Content-Type'] = 'text/csv'
        # # response.headers['X-Content-Type-Options'] = 'nosniff'
        # resp.headers['X-Content-Type-Options'] = 'text/csv'
        return response
    else:
        if 'installation' in session:
            return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])    
        else:
            return render_template("import.html", username = session['username'], installation = 'your installation', statut = session['logged_in'])    

@app.route('/existing_ID', methods = ['GET', 'POST'])
def existing_id():
    if request.method == 'POST':
        if not (session['logged_in']):
            flash('You need to be connected to use this functionnality')
            return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 

        session['hostname'] = request.form['hostname']
        session['installation'] = request.form['installation']  
        if 'sep' in request.form:
            SepSetting=request.form.get('sep')
        else:
            SepSetting=","
        if 'skiprow' in request.form:
            skipSetting=int(request.form['skiprow'])
        else: 
            skipSetting=0
        f = request.files['file']
        f.save(os.path.join(dir_path,'uploads','uploaded_file.csv'))
        try:
          dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
        except pd.errors.EmptyDataError:
          flash("Invalid file, did you submit a csv file ?")
          return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 
        dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
        try:
            dataset.eval(request.form['identifier'])
        except pd.core.computation.ops.UndefinedVariableError:
          flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
          return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 
        dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = "existing" , datasup = request.form['identifier'])
        dataset_URI.to_csv(os.path.join(dir_path,'uploads','export_URI_existing_ID.csv'))
        return send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI_existing_ID.csv'), mimetype="text/csv", as_attachment=True)
    else:
        if 'installation' in session:
            return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])    
        else:
            return render_template("existing.html", username = session['username'], installation = 'your installation', statut = session['logged_in'])    

@app.route("/qrcodes", methods = ['GET', 'POST'])
def etiquette():
    if (request.method == 'POST'):
        tempfile.mkdtemp()
        data=pd.read_csv(os.path.join(dir_path,'uploads','export_URI' + request.form.get('resource_type') + '.csv'))
        URI = data.URI
        variety = data.Variety
        zipObj = ZipFile(os.path.join(tempfile.gettempdir(),"qrcodes.zip"), 'w')
        for uri in data.index :
            etiquette = generate_qr_code(URI = data.URI[uri], variety = data.Variety[uri])
            zipObj.write(os.path.join(tempfile.gettempdir(), data.URI[uri][-10:] + '.png'))
        zipObj.close()
        # repertoire = os.path.join(tempfile.gettempdir(), "qrcodes", "png/*")
        # os.system('rm -r ' + repertoire)

        ## TODO Parallelisation
        return send_from_directory(directory = tempfile.gettempdir(), filename =  "qrcodes.zip")
    else:
        return render_template("qrcodes.html", username = session['username'],  statut = session['logged_in'])

def Premier_essai_parallele(data):
    CPU_count = multiprocessing.cpu_count()
    data=pd.read_csv("/home/jeaneudes/Documents/URI/generator/app/uploads/export_URIplant.csv")
    df_split = np.array_split(data, CPU_count)
    try:
        with multiprocessing.Pool() as pool:
            pool.map(etiquette, df_split)
        
    return "une fonction qui fait de la parallelisation..."


### Actions
@app.route("/your_database")
def your_database():
    collections = user_collected_URI.query.filter_by(user = session['username'])
    return render_template("your_database.html", collections = collections, username = session['username'], statut = session['logged_in'])

@app.route('/data/<path:filename>')
def download(filename):
    if "example" in filename:
        return send_from_directory(directory = dir_path, filename = os.path.join('download',filename), mimetype = "text/csv", as_attachment = True)

@app.route('/export_all_db')
def export_all_db():
    return(send_from_directory(directory = "", filename = 'custom_design.db', mimetype = "application/octet-stream"))

### Functions
def URIgenerator_series(host, installation, resource_type, year = "", lastvalue = "001", project = "", datasup = {} ):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"

    if resource_type == "agent":
        finalURI = finalURI + "id/agent/" + datasup["agentName"]
    
    if resource_type == "annotation":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/annotation/"+ year + "/" + Hash

    if resource_type == "actuator":
        finalURI = finalURI + year + "/a" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "document":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "documents/document" + Hash

    if resource_type == "data":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/data/" + Hash
    
    if resource_type == "ear":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/ea" + year[2:]+ str(lastvalue).rjust(6, "0") 

    if resource_type == "event":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/event/" + year + "/" + Hash

    if resource_type == "image":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/image/" + Hash

    if resource_type == "plant":
        finalURI = finalURI + year + "/" + project + "/pl" + year[2:]+ str(lastvalue).rjust(6, "0")
     
    if resource_type == "plot":
        finalURI = finalURI + year + "/" + project + "/pt" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "pot":
        finalURI = finalURI + year + "/" + project + "/po" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "leaf":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/lf" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "species":
        finalURI = finalURI + datasup['species']

    if resource_type == "sensor":
        finalURI = finalURI + year + "/se" + year[2:] + str(lastvalue).rjust(6, "0")
    
    if resource_type == "vector":
        finalURI = finalURI + year + "/ve" + year[2:] + str(lastvalue).rjust(6, "0")

    if resource_type == "existing":
        relPlant = datasup['identifier']
        finalURI = finalURI + relPlant

    return finalURI

def add_URI_col(data, host = "", installation = "", resource_type = "", project = "", year = "2017", datasup = "" ):
    activeDB = user_collected_URI.query.filter_by(user = session['username'], type = resource_type).first()
    datURI = []
    if(resource_type in ['plant', 'plot', 'pot', 'sensor', 'vector', 'actuator']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant)))
            lastplant +=1
        activeDB.lastvalue = str(lastplant)
        db.session.commit()
    if(resource_type in ['leaf', 'ear']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant), datasup = {'relPlant':data.eval(datasup)[l]}))
            lastplant +=1
        activeDB.lastvalue = str(lastplant)
        db.session.commit()

    if(resource_type in ['data', 'image', 'event', 'annotation']): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type))

    if(resource_type =="species"): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, datasup = {'species':data.eval(datasup)[l]}))

    if(resource_type =="existing"): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, resource_type = resource_type, datasup = {'identifier':data.eval(datasup)[l]}))

    data = data.assign(URI = datURI)
    return data

def generate_qr_code(URI, variety):
    fontPath = "app/static/fonts/DejaVuSansMono-Bold.ttf"
    sans16 = ImageFont.truetype(fontPath, 20)
    cod = URI[-10:]
    url = pyqrcode.create(URI)
    chemin = os.path.join(tempfile.gettempdir(), cod +'.png')
    url.png(chemin, scale = 8,  module_color = '#000', background = '#fff', quiet_zone = 8)
    img = Image.open(chemin)
    draw = ImageDraw.Draw(img)
    draw.text((15, 20), cod, font = sans16)
    draw.text((150, 20), "Variety: " + variety, font = sans16)
    img.save(chemin)
    return(url)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug = True, threaded = True, port = 3838)