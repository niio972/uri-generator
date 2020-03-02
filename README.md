# Readme  

## URI generator  

This is a python application using Flask framework.
in order to run this application you should clone this repository.  
Open it using VScode (or an other software) set a python terminal and run the following commands :  

``` python
export FLASK_APP=generator.py
python3 -m flask run
```

You will need to install the appropriate libraries. to do so *conda* environment or *venv* are suitable.  

## Adapt it  

The generator is using *jinja2* templates, it improves a base template named generator.py using :  

```python
{% extends "generator.html" %}
{% block title %}
```

To make use of this generator for your own instance, you can replace generator.py with your own page (using your own design). 

For more details about the Flask framework you can see the official documentation [here](https://flask.palletsprojects.com/en/1.1.x/)  
For details about the VSCode implémentation see [here](https://code.visualstudio.com/docs/python/tutorial-flask)