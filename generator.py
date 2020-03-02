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

@app.route("/uri/data/")
def data():
   return render_template("data.html")

@app.route('/success')
def success():
    return render_template("success.html")
    #return   'Creating the following '+ session['subpath'] +' URI %s' % escape(session['URI'])

@app.route('/uri/<path:subpath>', methods=['GET', 'POST'])
def execute_request(subpath):
    # show the subpath after /path/
    session['subpath']=subpath[0:-1]
    session['hostname'] = request.form['hostname']
    session['installationName'] = request.form['installationName']       
    URI = URIgenerator(host= session['hostname'], installation=session['installationName'] , resource_type=session['subpath'])
    session['URI']=URI
    
    return redirect(url_for('success'))
    #return 'Creating the folllowing URI %s' % escape(session['URI']) + "for host" + escape(session['hostname'])




def URIgenerator(host, installation, resource_type, year="", project="", data={}):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"
    
    if resource_type=="document":
        title = request.form['doctitle']
        finalURI = finalURI + "document/" + title

    if resource_type=="sensor":
        year = request.form['year'] 
        finalURI = finalURI + year + "/se" + year[2:] + str(random.randrange(0, 1001)).rjust(6, "0")
    
    if resource_type=="vector":
        year = request.form['year'] 
        finalURI = finalURI + year + "/ve" + year[2:] + str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type=="plant":
        year = request.form['year']  
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/pl" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")
    
    if resource_type=="pot":
        year = request.form['year']  
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/pt" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type=="leaf":
        year = request.form['year']  
        relPlant = request.form['relPlant']
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/lf" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0")

    if resource_type=="ear":
        year = request.form['year']  
        relPlant = request.form['relPlant']
        project = request.form['relExp']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/ea" + year[2:]+ str(random.randrange(0, 1001)).rjust(6, "0") 

    if resource_type=="data":
            year = request.form['year'] 
            Ash = hashlib.sha224(str(random.randrange(0,1001)).encode("utf-8")).hexdigest()
            finalURI = finalURI + year + "/data/" + Ash

    return finalURI