# Supplementary informations  

The generator app is deployed in a demo server [here](https://uri-generator.herokuapp.com/get_started).  
Some other instances can be hosted locally or on shared servers.  
An integrated version hosted as PHIS external app is feasable and under proof of concept.  

## Collect the database  

A hidden function exists in order to retrieve the database and the full list of URI generated (for a potential migration of the tool).  

```bash
/export_all_db
```  

Access it like any of the other pages (eg: /import_file to generate URI)  
There is a function behind this address that exports the SQL database binary file.  
You can harvest the file like any SQL file.

## Modify the URI pattern  

The URI is defined in the `URIgenerator_series` python function (app/main.py), you can add some new types of objects or modify the pattern. For example: URI for an image is generated with a cryptographic part, but you may want to include some camera/file/date/time semantic insted.

You also have to turn the HTML form in the adequate format to retrieve the modified pattern or the new type of resources (`templates/import.html`).  

## Enrich URI mirror  

The function to enrich an existing identifier into an URI is almost a duplicate of the generation of new URI, so don't forget to update both functions at the same time.

## Initialise database for new user  

If you add new types of resources, the database yould be initiated accordingly. At the moment just a limited number of resources is registred, and this initialisation is hand made.  

## Different deployment alternatives

The intended deployment are gunicorn and uwsgi at the moment. Both require dedicated files to set the server in place. Both also work inside a docker environment and the difference between setting up the different images is really small.  
You can find details about the deployment of Flaks app [here](https://flask.palletsprojects.com/en/1.1.x/deploying/)  
