#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Note, aspects of these scripts are based on example clients which can be found at
# https://github.com/OpenSILEX/phis-ws-clients/tree/master/python

import hashlib
import requests
import json
import os
import mimetypes
import copy
import pprint

# Token generation

def generate_token(host, username, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    
    headers = { 'Content-Type': 'application/json',
    'accept' : 'application/json',
    }

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': 'string'
    }
    
    json_data = json.dumps(data).encode('utf-8')

    url = host + 'brapi/v1/token'
    response = requests.post(url, headers = headers, data = json_data)
    #print(response.text + "\n")

    token = response.json()['access_token'];

    #print ("token : " + token + "\n")
    return token

  
def create_session(host, username, password):
    # This function just packages together the host URL and the session token so that we can easily pass these to subsequent calls at the same time
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    session_token = generate_token(host, username, password)
    session = {"token" : session_token, "host_url" : host}
    return session

last_response = None

def define_phis_request(http_request_type,
                        url_service_template, 
                        url_template_kwargs = [],
                        preprocess_data = lambda x:json.dumps(x), 
                        postprocess_response = lambda x:json.loads(x.text),
                        accept = 'application/json'):
    assert http_request_type in set(["GET", "POST", "PUT"]), "Only GET, POST and PUT requests are currently supported, but found %s." % http_request_type
    
    request_method = {"GET" : requests.get, "POST" : requests.post, "PUT" : requests.put}[http_request_type]
    
    def phis_request_method(session, query_params = {}, data = {}, debug_print = False, return_response_object = False, **kwargs):
        global last_response
        service_url = session["host_url"] + url_service_template
        
        arg_list = []
        for kwarg in url_template_kwargs:
            assert kwarg in kwargs, "Keyword argument %s is required" % kwarg
            arg = kwargs[kwarg]
            arg_list.append(arg)
        
        service_url = service_url % tuple(arg_list)
                        
        if debug_print:
            print()
            print("****************************")
            print("REQUEST START")
            print("----------------------------")
            print("Contacting service url: %s" % service_url)

        headers_metadata = { 
            'Content-Type': 'application/json',
            'accept' : accept,
            'Authorization':'Bearer ' + session["token"]
        }

        if debug_print:
            print("Header:")
            print("----------------------------")
            print(headers_metadata)
            print("----------------------------")
            print()
        
        data = preprocess_data(data)
            
        if debug_print:
            print("Data:")
            print("----------------------------")
            print(data)
            print("----------------------------")
            print()
            
        if debug_print:
            print("Performing %s request..." % http_request_type)
            
        response = request_method(service_url, params = query_params, headers=headers_metadata, data=data)
        last_response = response

        if debug_print:
            print("URL used was: %a" % response.url)
            print()
            print("Reponse:")
            print("----------------------------")
            print("Status code %a" % (response.status_code,))

            
        processed_response = postprocess_response(response)

        if debug_print:
            print(processed_response)
            print("----------------------------")
            print("REQUEST END")
            print("****************************")
 
        if return_response_object:
            return processed_response, response
        else:
            return processed_response
    
    return phis_request_method


def post_file_object(session, fileobject, filename, filetype, rdf_type, provenance_uri, concerned_items, metadata, date):
    global provenanceUri
    urlfilepost = session["host_url"] + 'data/file'
    headersfilepost = {
            'accept' : 'application/json',
            'Authorization':'Bearer ' + session["token"]
    }
    
    multipart_form_data = {
        'description': ('', json.dumps({
            'rdfType': rdf_type,
            'date': date,
            'provenanceUri': provenance_uri,
            'concernedItems': concerned_items,
            'metadata': metadata
        })),
        'file': (filename, fileobject, filetype)
    }
     
    #print()
    #print(multipart_form_data)
    #print()

    # send file and metadata to webservice
    req = requests.Request('POST', urlfilepost, headers=headersfilepost, files=multipart_form_data)
    prepared = req.prepare()

    response = requests.Session().send(prepared)

    print(response.text)

    return response


def post_file(session, filepath, rdf_type, provenance_uri, concerned_items, metadata, date, filetype = None):
    filename = os.path.basename(filepath)
    if filetype is None:
        filetype = mimetypes.guess_type(filepath)[0]
    fileobject = open(filepath, "rb")
    post_file_object(session, fileobject, filename, filetype, rdf_type, provenance_uri, concerned_items, metadata, date)

def define_matcher(getter):
    def matcher(query_params, properties_to_match):
        results = getter(query_params=query_params)["results"]["data"]
        matches = []
        for entry in results:
            for key in properties_to_match:
                query_value = query_params[key]
                return_value = entry[key]
                if (query_value != return_value):
                    continue # Drop this entry
            matches.append(entry)
        return matches

def exact_matches(query_params, list_of_matches):
    exact_match_list = []
    for match in list_of_matches:
        mismatch = False
        for key in query_params.keys():
            assert key in match, "Key " + key + " not in match dict. Was the query dictionary well-formed?"
            
            if (query_params[key] != match[key]):
                mismatch = True
                break
        if (not mismatch):
            exact_match_list.append(match)
    return exact_match_list
            

def define_post_or_put(getter, poster, putter):
    def post_or_put_entity(session, query_params, entity_dict, verbose=False):
        assert type(query_params) == dict
        assert type(entity_dict) == dict
        entity_dict = copy.deepcopy(entity_dict)
        existing_entities = getter(session, query_params=query_params)["result"]["data"]
        existing_entities = exact_matches(query_params, existing_entities)
        if verbose:
            print("Matching existing entities:")
            pprint.pprint(existing_entities)
        
        assert len(existing_entities) <= 1, "There should be either 0 or exactly 1 match for the entity in the repository, but there were %d. Did someone post the entity twice?" % (len(existing_entities),)
            
        if (len(existing_entities) == 0):
            if verbose:
                print("No existing entity matches, we POST the entity to create it.")
            result = poster(session, data = [entity_dict])
        else:
            if (putter is None):
                if verbose:
                    print("An entity matches, but there is no PUT to update it!")
                result = "No putter specified, is this intentional?"
            else:
                if verbose:
                    print("An entity matches, we use PUT to update it.")
                entity_uri = existing_entities[0]["uri"]
                entity_dict["uri"] = entity_uri
                result = putter(session, data = [entity_dict])
        
        # Now we double check that the project has been inserted
        existing_entities = getter(session, query_params=query_params)["result"]["data"]
        existing_entities = exact_matches(query_params, existing_entities)
        
        assert len(existing_entities) == 1, "There should be exactly 1 match for the project in the repository after posting, did the post call fail? " + "Result = " + str(result) + "Entities = " + str(existing_entities)
        return existing_entities[0]
    return post_or_put_entity

#def define_post_or_put(getter, poster, putter):
#    def post_or_put(data, properties_to_match):
        
get_projects = define_phis_request("GET", "projects")
post_projects = define_phis_request("POST", "projects")
put_projects = define_phis_request("PUT", "projects", postprocess_response=lambda x:x) # No response, so should parse as JSON

get_groups = define_phis_request("GET", "groups")
post_groups = define_phis_request("POST", "groups")
put_groups = define_phis_request("PUT", "groups", postprocess_response=lambda x:x) # No response, so should parse as JSON)

get_experiments = define_phis_request("GET", "experiments")
post_experiments = define_phis_request("POST", "experiments")
put_experiments= define_phis_request("PUT", "experiments", postprocess_response=lambda x:x) # No response, so should parse as JSON

get_provenances = define_phis_request("GET", "provenances")
post_provenances = define_phis_request("POST", "provenances")
put_provenances = define_phis_request("PUT", "provenances")

get_sensors = define_phis_request("GET", "sensors")
post_sensors = define_phis_request("POST", "sensors")
put_sensors = define_phis_request("PUT", "sensors")

get_sensor_profiles_uri = define_phis_request("GET", "sensors/profiles/%s", url_template_kwargs=["uri"])
post_sensor_profiles = define_phis_request("POST", "sensors/profiles")

get_scientific_objects = define_phis_request("GET", "scientificObjects")
post_scientific_objects = define_phis_request("POST", "scientificObjects")
put_scientific_object = define_phis_request("PUT", "scientificObjects/%s/%s", ["uri", "experiment"], postprocess_response=lambda x:x) # No response, so should parse as JSON

get_traits = define_phis_request("GET", "traits")
post_traits = define_phis_request("POST", "traits")
put_traits = define_phis_request("PUT", "traits")#, postprocess_response=lambda x:x) # No response, so should parse as JSON

get_methods = define_phis_request("GET", "methods")
post_methods = define_phis_request("POST", "methods")
put_methods = define_phis_request("PUT", "methods")

get_units = define_phis_request("GET", "units")
post_units = define_phis_request("POST", "units")
put_units = define_phis_request("PUT", "units")

get_variables = define_phis_request("GET", "variables")
post_variables = define_phis_request("POST", "variables")
put_variables = define_phis_request("PUT", "variables")

get_data_file_search = define_phis_request("GET", "data/file/search")


#__________________________
host="http://138.102.159.37:8080/openSilexTestAPI/rest/"

session=create_session(host=host,  password="guest", username="guest@opensilex.org")
get_experiments(query_params={}, session=session)
get_sensors(session=create_session(host=host,  password="guest", username="guest@opensilex.org"), query_params={}, debug_print=True, return_response_object=True)
get_scientific_objects(session=session, debug_print=True,   return_response_object=True,  query_params={'experiment':"http://www.phenome-fppn.fr/mtp/MTP2014-1"})
