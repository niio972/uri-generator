from flask import render_template, Flask, session, url_for, request, redirect
from markupsafe import escape
from datetime import datetime
import hashlib
import requests
import json
import os
import mimetypes
import copy
import pprint
import random
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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


@app.route('/success')
def index():
    if 'hostname' in session:
        return 'Creating the following '+ session['subpath'] +' URI %s' % escape(session['URI']) + " for host " + escape(session['hostname'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['hostname'] = request.form['hostname']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=hostname>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('hostname', None)
    return redirect(url_for('index'))   

@app.route('/uri/<path:subpath>', methods=['GET', 'POST'])
def execute_request(subpath):
    # show the subpath after /path/
    session['subpath']=subpath[0:-1]
    session['hostname'] = request.form['hostname']
    session['installationName'] = request.form['installationName']
    session['plyear'] = request.form['plyear']        
    session['relExp'] = request.form['relExp']        
    URI = URIgenerator(host= session['hostname'], installation=session['installationName'] , resource_type=session['subpath'], year=session['plyear'], project=session['relExp'])
    session['URI']=URI
    
    return redirect(url_for('index'))
    #return 'Creating the folllowing URI %s' % escape(session['URI']) + "for host" + escape(session['hostname'])




def URIgenerator(host, installation, resource_type, year="", project="", data={}):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"
    
    if resource_type=="Experiment":
        finalURI = finalURI + data.experiment
    
    if resource_type=="document":
        finalURI = finalURI + year + "/" + "do" + year[2:3] + random.randrange(0, 1001)

    if resource_type=="sensor":
        finalURI = finalURI + year + "/" + "s" + year[2:3] + random.randrange(0, 1001)
    
    if resource_type=="vector":
        finalURI = finalURI + year + "/" + "v" + year[2:3] + random.randrange(0, 1001)

    if resource_type=="plant":
        finalURI = finalURI + year + "/" + project + "/" + "pl" + year[2:]+ "000" + str(random.randrange(0, 1001))
    
    if resource_type=="pot":
        finalURI = finalURI + year + "/" + project + "/" + "pt" + year[2:]+ "000" + str(random.randrange(0, 1001))

    if resource_type=="leaf":
        finalURI = finalURI + year + "/" + project + "/" + "lf" + year[2:]+ "000" + str(random.randrange(0, 1001))

    if resource_type=="ear":
        finalURI = finalURI + year + "/" + project + "/" + "ea" + year[2:]+ "000" + str(random.randrange(0, 1001))

    if resource_type=="person":
        finalURI = finalURI + "/" + data.name 


    return finalURI