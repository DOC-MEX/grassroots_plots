import requests
import json
from django.conf import settings
#import aiohttp

server_url = 'https://grassroots.tools/public_backend'
server_url = 'http://localhost:2000/grassroots/public_backend'

'''
Get all field trial request from the backend
returns JSON from backend and send to the model
'''
def get_all_fieldtrials():
    list_all_ft_request = {
        "services": [
            {
                "so:name": "Search Field Trials",
                "start_service": True,
                "parameter_set": {
                    "level": "simple",
                    "parameters": [
                        {
                            "param": "FT Keyword Search",
                            "current_value": ""
                        },
                        {
                            "param": "FT Study Facet",
                            "current_value": True
                        },
                        {
                            "param": "FT Results Page Number",
                            "current_value": 0
                        },
                        {
                            "param": "FT Results Page Size",
                            "current_value": 500
                        }
                    ]
                }
            }
        ]
    }
    res = requests.post(server_url, data=json.dumps(list_all_ft_request))
    return json.dumps(res.json())

'''
Search field trials with a given string
returns JSON from backend and send to the model
'''
def search_fieldtrial(str):
    list_all_ft_request = {
        "services": [
            {
                "so:name": "Search Field Trials",
                "start_service": True,
                "parameter_set": {
                    "level": "simple",
                    "parameters": [
                        {
                            "param": "FT Keyword Search",
                            "current_value": str
                        },
                        {
                            "param": "FT Study Facet",
                            "current_value": True
                        },
                        {
                            "param": "FT Results Page Number",
                            "current_value": 0
                        },
                        {
                            "param": "FT Results Page Size",
                            "current_value": 500
                        }
                    ]
                }
            }
        ]
    }
    res = requests.post(server_url, data=json.dumps(list_all_ft_request))
    return json.dumps(res.json())

'''
Get a field trial with a id
returns JSON from backend and send to the model
'''
def get_fieldtrial(id):
    list_all_ft_request = {
        "services": [{
            "start_service": True,
            "so:name": "Search Field Trials",
            "parameter_set": {
                "level": "advanced",
                "parameters": [
                    {
                        "param": "FT Id",
                        "current_value": id
                    },
                    {
                        "param": "FT Trial Facet",
                        "current_value": True
                    },
                    {
                        "param": "FT Results Page Number",
                        "current_value": 0
                    },
                    {
                        "param": "FT Results Page Size",
                        "current_value": 100
                    }
                ]
            }
        }]
    }
    res = requests.post(server_url, data=json.dumps(list_all_ft_request))
    return json.dumps(res.json())
#    return res.json()

'''
Get a study with a id
returns JSON from backend and send to the model
'''
def get_study(id):
    study_request = {
            "services": [{
                "so:name": "Search Field Trials",
                "start_service": True,
                "parameter_set": {
                    "level": "advanced",
                    "parameters": [{
                        "param": "ST Id",
                        "current_value": id
                    }, {
                        "param": "Get all Plots for Study",
                        "current_value": True
                    }, {
                        "param": "ST Search Studies",
                        "current_value": True
                    }]
                }
            }]
        }
    res = requests.post(server_url, data=json.dumps(study_request))
    return json.dumps(res.json())


'''
Get plots from a study with a study id
returns JSON from backend and send to the model
'''
def get_plot(id):
    plot_request = {
            "services": [{
                "so:name": "Search Field Trials",
                "start_service": True,
                "parameter_set": {
                    "level": "advanced",
                    "parameters": [{
                        "param": "ST Id",
                        "current_value": id
                    }, {
                        "param": "Get all Plots for Study",
                        "current_value": True
                    }, {
                        "param": "ST Search Studies",
                        "current_value": True
                    }]
                }
            }]
        }
    res = requests.post(server_url, data=json.dumps(plot_request))
    return json.dumps(res.json())

################not needed as request is perform by Javascript###
async def updateRequest(selected_phenotype, selected_date, observation):
    amend_request = {
        "services":
            [{
            "start_service":True,
            "so:alternateName":"field_trial-submit_plots",
            "parameter_set":{"level":"simple","parameters":
                [{"param":"PL Upload","current_value":
                [{
                "Plot ID":"1",
                "Row":"1",
                "Column":"1",
                "Rack":"1",
                "Accession":
                "Hylux",
                "Hd_dto_day 2023-03-11":"3"}]},
                {"param":"PL Study",
                 "current_value":"63c7e48ca115ca392f4b6fd3"},
        {"param":"PL Data delimiter","current_value":","},
        {"param":"PL Amend","current_value":True},
        {"param":"ST Num Replicates","current_value":None},
        {"param":"ST Plot Width","current_value":None},
        {"param":"ST Plot Length","current_value":None}
        ]}}]}
    
    
    res = await requests.post(server_url, data=json.dumps(amend_request))
    return json.dumps(res.json())

############################################
def interact_backend(data):
    #private_url = 'https://grassroots.tools/private_backend'  # for live server
    #res = requests.post(private_url, data=data)               # for live server
    res = requests.post(server_url, data=data)  # for local(laptop) use server_url
    #print("res: ") 
    return json.dumps(res.json())


############################################
def interact_queen_server(data):
    #queen_url = 'http://10.0.152.67/grassroots/queen_bee_backend'  # for live server
    #res = requests.post(queen_url, data=data)               # for live server
    res = requests.post(server_url, data=data)# for local(laptop) use server_url
    #print("res: ") 
    return json.dumps(res.json())
