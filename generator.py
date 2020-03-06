from flask import render_template, Flask, session, url_for, request, redirect, jsonify
from markupsafe import escape
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import requests
import random
import pandas as pd
#import csv


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///custom_design.db'
CORS(app, resources={r'/*': {'origins': '*'}})
db = SQLAlchemy(app)

class custom_design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return "<Design %r>" %self.id

class collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<URI %r>" %self.id

#
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/device")
def device():
    return render_template("device.html")

@app.route("/scientificObject/")
def scientificObject():
    return render_template("scientificObject.html")

#####
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

@app.route('/success')
def success():
    return render_template("success.html")
    #return   'Creating the following '+ session['subpath'] +' URI %s' % escape(session['URI'])

@app.route('/new_schema', methods=['GET', 'POST'])
def new_schema():
    if request.method == "POST":
        content_name = request.form['content-name']
        content = request.form['content']

        new_design = custom_design(content = content, name = content_name)
        try:
            db.session.add(new_design)
            db.session.commit()
            return redirect('/new_schema')

        except:
            return "There was an error, try again"
    else:
        designs = custom_design.query.all()
        key_class = request.form.get('key_class')
        key = key_generator(key_class=key_class)
        #return(str(key_class))
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
####

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
        Ash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/data/" + Ash

    return finalURI

def key_generator(key_class):
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

def export_csv(table):
    csv_table = pd.to_csv(table)









if __name__ == "__main__":
    app.run(debug=True)