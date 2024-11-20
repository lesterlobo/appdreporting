import getopt
import json
import sys
import requests
import time
from datetime import datetime, timedelta
import csv


def usage():
    print(__doc__)

def use_oauth_token(token, api_endpoint):
    """Makes a request to an API using an OAuth token."""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


def retrieve_token(client_id, client_secret, controller_url):
    payload = 'grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret
    tokenResponse = requests.post(controller_url + "/controller/api/oauth/access_token", data=payload)

    token = ''
    if tokenResponse.status_code == 200:
        token = json.loads(tokenResponse.content.decode('utf-8'))['access_token']
        return token
    else:
        raise Exception(f"API request failed with status code {tokenResponse.status_code}")
    

def get_application_id(token, controller_url, applicationName):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    serverResponse = requests.get(controller_url + "/controller/rest/applications/" + applicationName + "?output=JSON", headers=headers)
   
    if (serverResponse.ok):
        appid = json.loads(serverResponse.content.decode('utf-8'))[0]['id']
        return appid
    else:
        raise Exception(f"API request failed with status code {serverResponse.status_code}")
    

def get_actions_per_app(token, controller_url, applicationid, applicationName, fileName):
    #get servers id for controller
    print("Retrieving Actions for Server Application")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    #serverResponse = requests.get(controller_url + "/controller/rest/applications/Server%20%26%20Infrastructure%20Monitoring?output=JSON", headers=headers)
    actions = requests.get(controller_url + "/controller/alerting/rest/v1/applications/"+ str(applicationid) +"/actions", headers=headers) 
    response = json.loads(actions.content.decode('utf-8'))

    if (actions.ok):
        with open(fileName, 'a', newline='') as f:
            
            if (len(response) > 0):
                print(len(response) == 0)
                counter=0
                print(response)
                for action in actions:
                    actionid = response[counter]['id']
                    
                    #retrieve action details
                    actionDetail = requests.get(controller_url + "/controller/alerting/rest/v1/applications/"+ str(applicationid) + "/actions/" + str(actionid), headers=headers) 
                    if (actionDetail.ok):
                        f.write(applicationName + ", " + actionDetail.text + "\n")
                    else:
                        print("Error Occured in retrieving Action Details for Action" + response[counter]['name'] +  ". Error Code" + str(actionDetail.status_code))
                    counter = counter + 1
                
                #     with open("actions.xml", "a") as f:
                #         f.write(actions.text)
            else:
                print("No Actions configured for application id" + str(applicationid))
            
    else:
        print("Error Occured in retrieving Actions for Server. Error Code" + str(actions.status_code))
    
def get_actions_for_all_apps(token, controller_url, fileName):
    print("Retrieving Actions for all APM Applications")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    #serverResponse = requests.get(controller_url + "/controller/rest/applications/Server%20%26%20Infrastructure%20Monitoring?output=JSON", headers=headers)
    applications = requests.get(controller_url + "/controller/rest/applications?output=JSON", headers=headers) 

    if (applications.ok):
        print(applications.text)
        apps = json.loads(applications.content.decode('utf-8'))
        counter = 0
        if (len(apps) > 0):
            for app in apps:
                applicationid = apps[counter]['id']
                applicationName = apps[counter]['name']
                get_actions_per_app(token, controller_url, applicationid, applicationName, fileName)
                counter=counter+1
    else:
         print("Error Occured in retrieving Applications. Error Code" + str(applications.status_code))




def main(argv):
    controller_url = ''
    client_id = ''
    client_secret = ""
    fileName=""

    # retrieve api token
    token = retrieve_token(client_id, client_secret, controller_url)

    # # retrieve Actions for Server
    serverid = get_application_id(token, controller_url, "Server%20%26%20Infrastructure%20Monitoring")
    response = get_actions_per_app(token, controller_url, serverid, "Server Monitoring", fileName)

    # # retrieve Actions for Database
    databaseid = get_application_id(token, controller_url, "Database Monitoring")
    response = get_actions_per_app(token, controller_url, databaseid, "Database Monitoring", fileName)
   

    # retrieve Actions for Applications
    get_actions_for_all_apps(token, controller_url, fileName)
    

    
if __name__ == "__main__":
    main(sys.argv[1:])
