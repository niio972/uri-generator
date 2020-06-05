from flask import render_template, Flask, session, url_for, request, redirect, jsonify, send_file
from markupsafe import escape
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import requests
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_design.db'
""" CORS(app, resources={r'/*': {'origins': '*'}}) """
db = SQLAlchemy(app)

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
    """ def __init__(self, candid=None, rank=None, user_id=None):
        self.data = (type, value, id) """
    
class m3p_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

### Menu
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/variable/")
def variable():
    return render_template("variable.html")
    
@app.route("/device")
def device():
    return render_template("device.html")

@app.route("/scientificObject/")
def scientificObject():
    return render_template("scientificObject.html")

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

@app.route("/import_dataset")
def import_dataset():
   return render_template("import.html")

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
    collections = m3p_collected_URI.query.all()
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

@app.route('/import',methods = ['POST'])
def upload_route_summary():
    if request.method == 'POST':

        # Create variable for uploaded file
        f = request.files['fileupload']  

        #store the file contents as a string
        fstring = f.read()
        
        #avec pandas
        dataset = pd.read_csv()

        #create list of dictionaries keyed by header row
        #csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]

        #do something list of dictionaries
    return "success"

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

def read_multiple_URI(file):
    #read the file
    URI_table = pd.read_csv (file)
    for line in URI_table:
        host = session['hostname']
        installation = session['installationName']
        line_type = session['subpath']
        line_year = line.year        
        
        URIgenerator(host = host, installation = installation, resource_type=line_type, )

def URIgenerator_series(host, installation, resource_type, year="", lastvalue = "001", project="", datasup = {} ):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"

    # cas où local infra existe ou pas
    if resource_type == "installation":
        finalURI = finalURI  

    if resource_type == "infra":
        finalURI = finalURI

    if resource_type == "projet":
        finalURI = finalURI + project

    if resource_type == "experiment":
        finalURI = finalURI + experiment

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
    activeDB = m3p_collected_URI.query.filter_by(type = resource_type).first()
    datURI = []
    if(resource_type not in ['data', 'image', 'event', 'annotation']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, datasup = datasup, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant)))
            lastplant +=1
        activeDB.lastvalue = str(lastplant)
        db.session.commit()
    else: 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type), supdata = supdata)

    data = data.assign(URI = datURI)
    return data


data = pd.read_csv('ao_mau17.csv', sep=";")
"kl" not in ["ki", "kl"]

lastv = '2'
supdata = {"relPlant": "PLO2"}
add_URI_col(data = data, host = 'opensilex.org', installation = 'M3P', year = '2017', resource_type = 'leaf', project = 'DIA2017', datasup = supdata)
# generate lots of URI
#init dbs
# initm3p1=m3p_collected_URI(type="plant")
# db.session.add(initm3p1)
# db.session.commit()

# initm3p2=m3p_collected_URI(type="plot")
# db.session.add(initm3p2)
# db.session.commit()
        
# initm3p3=m3p_collected_URI(type="pot")
# db.session.add(initm3p3)
# db.session.commit()

# initm3p4=m3p_collected_URI(type="ear")
# db.session.add(initm3p4)
# db.session.commit()

# initm3p5=m3p_collected_URI(type="leaf")
# db.session.add(initm3p5)
# db.session.commit()

# initm3p6=m3p_collected_URI(type="sensor")
# db.session.add(initm3p6)
# db.session.commit()

# initm3p7=m3p_collected_URI(type="vector")
# db.session.add(initm3p7)
# db.session.commit()

if __name__=="__main__":
    app.run(debug=True)