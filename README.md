# Readme  

## Get started  

A get started page is avaliable within the app to help you use it correctly.

## URI generator  

This is a python application using Flask framework.
In order to run this application you should clone this repository.  
Open it using VScode (or an other software) set a python terminal and run the following commands :  

``` python
export FLASK_APP=app.py
python3 flask run
```

The app uses the default name app.py

You will need to install the appropriate libraries. To do so *conda* environment or *venv* are suitable.  
*(can you read the environment linked to this project?)*

## Adapt it  

The generator is using *jinja2* templates, it improves a base template named generator.html using :  

```python
{% extends "generator.html" %}
{% block title %}
```

To make use of this generator for your own instance, you can replace generator.html with your own page (using your own design).  

For more details about the Flask framework you can see the official documentation [here](https://flask.palletsprojects.com/en/1.1.x/)  
For details about the VSCode implémentation see [here](https://code.visualstudio.com/docs/python/tutorial-flask)
