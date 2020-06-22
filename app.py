from flask import render_template, Flask, session, url_for, request, redirect, jsonify, send_file, flash
from markupsafe import escape
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import requests
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = b'52d8851b5d6cbe74f7c8bb01974008140b0ae997e5b2efd987ed5b90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_design.db'
""" CORS(app, resources={r'/*': {'origins': '*'}}) """
db = SQLAlchemy(app)
if __name__ == "__main__":
    app.run(debug=True)

### Models
class custom_design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return "Design %r" %self.id

class collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "URI %r" %self.id
    
class user_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    lastvalue = db.Column(db.String(200), nullable=False, default=1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class collected_variables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    URI = db.Column(db.String(200), nullable=False)
    Entity = db.Column(db.String(50), nullable=False)
    Quality = db.Column(db.String(50), nullable=False)
    Method = db.Column(db.String(50), nullable=False)
    Unit = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "Variable %r" %self.id

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

### Menu
@app.route('/', methods=['GET', 'POST'])
def home():
    username = session['username']
    return render_template('home.html', username = username)

@app.route("/variable/")
def variable():
    return render_template("variable.html")
    
@app.route("/device")
def device():
    return render_template("device.html")

@app.route("/scientificObject/")
def scientificObject():
    return render_template("scientificObject.html")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        query = User.query.filter_by(username = request.form['username'], password = request.form['password'] ).first()
        
        if query:
            session['username'] = request.form['username']
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

### Generation
@app.route("/uri/experiment")
def experiment():
    return render_template("experiment.html")

@app.route("/uri/document/")
def document():
   return render_template("document.html")

@app.route("/uri/sensor/")
def sensor():
   return render_template("sensor.html")

@app.route("/uri/vector/")
def vector():
   return render_template("vector.html")

@app.route("/uri/plant/")
def plant():
   return render_template("plant.html")

@app.route("/uri/pot/")
def pot():
   return render_template("pot.html")

@app.route("/uri/ear/")
def ear():
   return render_template("ear.html")

@app.route("/uri/leaf/")
def leaf():
   return render_template("leaf.html")

@app.route("/uri/data/")
def data():
   return render_template("data.html")

@app.route("/uri/method/")
def method():
   return render_template("method.html")

@app.route("/import_dataset", methods = ['GET', 'POST'])
def import_dataset():
    if request.method == 'POST':
        session['hostname'] = request.form['hostname']
        session['installation'] = request.form['installation']   
        if 'file' not in request.files:
            flash('No file part')
            return redirect("import_dataset.html")
        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect("import_dataset.html")
        f.save('uploads/uploaded_file.csv')
        dataset = pd.read_csv('uploads/uploaded_file.csv')
        if request.form.get('resource_type') in ['leaf', 'ear']:
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'], datasup = request.form['relplant'])
        if request.form.get('resource_type') =="species":
            dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'], datasup = request.form['species'])  
        # else:
        #     dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'])
        dataset_URI.to_csv('uploads/export_URI'+request.form.get('resource_type')  +'.csv')
        return send_file('uploads/export_URI'+request.form['resource_type']  +'.csv')
    else:
        return render_template("import.html", username = session['username'])    

### Actions
@app.route("/create_variable/", methods=['GET', 'POST'])
def create_variable():
    if request.method == "POST":
        session['Entity'] = request.form['Entity']
        session['Quality'] = request.form['Quality']       
        session['Method'] = request.form['Method']  
        session['Unit'] = request.form['Unit']  
        session['subpath'] = "variable"
        URI = URIgenerator(host = session['hostname'], installation=session['installationName'] , resource_type="variable")
        session['URI'] = URI
        
        your_variables = collected_variables(URI = URI, Entity = session['Entity'], Quality=session['Quality'], Method = session['Method'], Unit = session['Unit'])
        try:
            db.session.add(your_variables)
            db.session.commit()
        except:
            return "There was an error, try again"
        return redirect(url_for('success'))
    else:
        return render_template("create_variable.html")

@app.route('/success')
def success():
    return render_template("success.html")
    #return   'Creating the following '+ session['subpath'] +' URI %s' % escape(session['URI'])

@app.route('/new_schema', methods=['GET', 'POST'])
def new_schema():
    key = key_generator()
    designs = custom_design.query.all()
    if request.method == "POST" and 'content-name' in request.form:
        content_name = request.form['content-name']
        content = request.form['content']
        new_design = custom_design(content = content, name = content_name)
        try:
            db.session.add(new_design)
            db.session.commit()
        except:
            return "There was an error, try again"
        return redirect("/new_schema")
    else:
        return render_template("new_schema.html", designs = designs, key = key)

@app.route('/delete/<path:subpath>/<int:id>')
def delete(id, subpath):
    if subpath == "URI":
        URI_to_delete = collected_URI.query.get_or_404(id)
        try:
            db.session.delete(URI_to_delete)
            db.session.commit()
            return redirect('/your_collection')
        except:
            return 'There was a problem deleting that row'

    if subpath =="variable":
        variable_to_delete = collected_variables.query.get_or_404(id)
        try:
            db.session.delete(variable_to_delete)
            db.session.commit()
            return redirect('/your_variables')
        except:
            return 'There was a problem deleting that variable'
            
    
    else:
        task_to_delete = custom_design.query.get_or_404(id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/new_schema')
        except:
            return 'There was a problem deleting that row'

@app.route('/uri/<path:subpath>', methods = ['GET', 'POST'])
def execute_request(subpath):
    # show the subpath after /path/
    session['subpath'] = subpath[0:-1]
    session['hostname'] = request.form['hostname']
    session['installationName'] = request.form['installationName']       
    URI = URIgenerator(host = session['hostname'], installation=session['installationName'] , resource_type=session['subpath'])
    session['URI'] = URI
    
    your_collection = collected_URI(value = URI, type = subpath[0:-1])
    try:
        db.session.add(your_collection)
        db.session.commit()

    except:
        return "There was an error, try again"
    return redirect(url_for('success'))
    #return 'Creating the folllowing URI %s' % escape(session['URI']) + "for host" + escape(session['hostname'])

@app.route("/your_collection")
def your_collection():
    collections = collected_URI.query.all()
    return render_template("your_collection.html", collections=collections)

@app.route("/your_database")
def your_database():
    collections = user_collected_URI.query.filter_by(user = session['username'])
    return render_template("your_database.html", collections=collections)

@app.route("/your_variables")
def your_variables():
    variables = collected_variables.query.all()
    return render_template("your_variables.html", variables=variables)

@app.route('/data/<path:filename>')
def download(filename):
    if filename == "export_URI":
        table = collected_URI.query.all()
        pd.DataFrame([(d.type, d.value, d.id) for d in table], columns=['type', 'value', 'id']).to_csv("download/export_URI.csv", index=False)
        return send_file("download/"+filename+".csv")
    if filename == "export_variable":
        table = collected_variables.query.all()
        pd.DataFrame([(d.URI, d.Entity, d.Quality, d.Method, d.Unit, d.id) for d in table], columns=['URI', 'Entity', "Quality", "Method", "Unit", 'id']).to_csv("download/export_variable.csv", index=False)
        return send_file("download/"+filename+".csv")

### Functions
def URIgenerator(host, installation, resource_type, year="", project="", data={}):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"
    
    if resource_type == "document":
        title = request.form['doctitle']
        finalURI = finalURI + "document/" + title

    if resource_type == "method":
        title = request.form['methname']
        finalURI = finalURI + "method/" + title

    if resource_type == "variable":
        Entity = session['Entity'] = request.form['Entity']
        Quality = session['Quality'] = request.form['Quality']       
        Method = session['Method'] = request.form['Method']  
        Unit = session['Unit'] = request.form['Unit'] 
        title_base = Entity+"_"+Quality
        if Method != "empty":
            title = title_base+"_"+Method+"_"+Unit
        else :
            title = title_base+"_"+Unit
        finalURI = finalURI + "variable/" + title

    if resource_type == "sensor":
        year = request.form['year'] 
        finalURI = finalURI + year + "/se" + year[2:] + str(random.randrange(0, 1001)).rjust(6, "0")
    
    if resource_type == "vector":
        year = request.form['year'] 
        finalURI = finalURI + year + "/ve" + year[2:] + str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type == "plant":
        year = request.form['year']  
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/pl" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")
    
    if resource_type == "pot":
        year = request.form['year']  
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/pt" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type == "leaf":
        year = request.form['year']  
        relPlant = request.form['relPlant']
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/lf" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type == "ear":
        year = request.form['year']  
        relPlant = request.form['relPlant']
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/ea" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0") 

    if resource_type == "data":
        year = request.form['year'] 
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/data/" + Hash

    return finalURI

def key_generator():
    key_class = request.form.get('key_class')
    if key_class=="incremental":
        return "001"
    if key_class=="random":
        return str(random.randrange(0, 1001)).rjust(6, "0")
    if key_class=="crypto":
        return hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()

def URIgenerator_series(host, installation, resource_type, year="", lastvalue = "001", project="", datasup = {} ):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"

    # cas où local infra existe ou pas
    # if resource_type == "installation":
    #     finalURI = finalURI  

    # if resource_type == "infra":
    #     finalURI = finalURI

    # if resource_type == "project":
    #     finalURI = finalURI + project

    # if resource_type == "experiment":
    #     finalURI = finalURI + experiment

    if resource_type == "species":
        finalURI = finalURI + datasup['species']

    if resource_type == "event":
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/event/" + Hash

    if resource_type == "agent":
        finalURI = finalURI + "id/agent/" + datasup["agentName"]
    
    if resource_type == "annotation":
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/annotation/" + Hash

    if resource_type == "actuator":
        finalURI = finalURI + year + "/a" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "document":
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + "documents/document" + Hash

    if resource_type == "sensor":
        finalURI = finalURI + year + "/se" + year[2:] + str(lastvalue).rjust(6, "0")
    
    if resource_type == "vector":
        finalURI = finalURI + year + "/ve" + year[2:] + str(lastvalue).rjust(6, "0")

    if resource_type == "plant":
        finalURI = finalURI + year + "/" + project + "/pl" + year[2:]+ str(lastvalue).rjust(6, "0")
     
    if resource_type == "plot":
        finalURI = finalURI + year + "/" + project + "/pt" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "pot":
        finalURI = finalURI + year + "/" + project + "/po" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "leaf":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/lf" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "ear":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/ea" + year[2:]+ str(lastvalue).rjust(6, "0") 

    if resource_type == "data":
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/data/" + Hash
    
    if resource_type == "image":
        Hash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/image/" + Hash
    return finalURI

def add_URI_col(data, host = "", installation="", resource_type = "", project ="", year = "2017", datasup ="" ):
    activeDB = user_collected_URI.query.filter_by(user = session['username'], type = resource_type).first()
    datURI = []
    if(resource_type in ['plant', 'plot', 'pot', 'sensor', 'vector', 'actuator']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, datasup = datasup, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant)))
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

    data = data.assign(URI = datURI)
    return data


# data = pd.read_csv('ao_mau17.csv', sep=";")
# data2 = pd.read_csv('Example data/example_leaf.csv')
# lastv = '2'
# supdata = ["PLO2", "PLO2", "PLO3", "PLO3", "PLO4"]
# add_URI_col(data = data2, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'leaf', project = 'DIA2017', datasup = 'Related_plant')
# URIgenerator_series(host="opensilex", installation="montpel", resource_type="leaf", year = "2029", lastvalue=lastv, project="diaph", datasup={'relPlant':data2.eval(proxy)[0]})
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'image')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'data')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'ear', project = 'DIA2017', datasup = supdata)
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'pot', project = 'DIA2017', datasup = supdata)
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'plot', project = 'DIA2017')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'plant', project = 'SECPRO')
# add_URI_col(data = data, host = 'opensilex.org', resource_type = 'project', project = 'DIA2017')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', resource_type = 'infra')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'sensor')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'vector')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', resource_type = 'annotation')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', resource_type = 'event')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'actuator')
# add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'document', datasup = {'title': 'H2G2'})
# generate lots of URI

# usertest = User("test", "test")
# db.session.add(usertest)
# useradmin = User("admin", "admin")
# db.session.add(useradmin)
# user_je = User("jeaneudes", "pic3.14")
# db.session.add(user_je)
# db.session.commit()

# @app.route('/test_user')
# def test_user():
#     query = User.query.filter_by(username = "test", password = "test" ).first()
#     print(query.username)
#     print(query.password)
#     return "Object not found "
# init dbs
# inittest0=user_collected_URI(user = "admin", type="actuator")
# db.session.add(inittest0)
# db.session.commit()

# inittest1=user_collected_URI(user = "admin", type="plant")
# db.session.add(inittest1)
# db.session.commit()

# inittest2=user_collected_URI(user = "admin", type="plot")
# db.session.add(inittest2)
# db.session.commit()
        
# inittest3=user_collected_URI(user = "admin", type="pot")
# db.session.add(inittest3)
# db.session.commit()

# inittest4=user_collected_URI(user = "admin", type="ear")
# db.session.add(inittest4)
# db.session.commit()

# inittest5=user_collected_URI(user = "admin", type="leaf")
# db.session.add(inittest5)
# db.session.commit()

# inittest6=user_collected_URI(user = "admin", type="sensor")
# db.session.add(inittest6)
# db.session.commit()

# inittest7=user_collected_URI(user = "admin", type="vector")
# db.session.add(inittest7)
# db.session.commit()

