import getopt
import json
import sys
import requests
import time
from datetime import datetime, timedelta


def usage():
    print(__doc__)

def generate_epoch(delta):
    """Generates the current epoch timestamp."""
    return int((time.time()- delta) * 1000)

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

def get_hr_violations_servers(token, controller_url):
    #get servers id for controller

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    serverResponse = requests.get(controller_url + "/controller/rest/applications/Server%20%26%20Infrastructure%20Monitoring?output=JSON", headers=headers)

    serverid = ''
    if (serverResponse.ok):
        #print(serverResponse.content)
        serverid = json.loads(serverResponse.content.decode('utf-8'))[0]['id']
        print(serverid)

        timebefore=1440 //time in seconds

        hrviolations = requests.get(controller_url + "/controller/rest/applications/"+ str(serverid) +"/problems/healthrule-violations?time-range-type=BEFORE_NOW&duration-in-mins=" + timebefore, headers=headers) 
        #hrviolations = requests.get(controller_url + "/controller/rest/applications/"+ str(serverid) +"/problems/healthrule-violations?time-range-type=BETWEEN_TIMES&start-time="+start+"end-time="+end, headers=headers) 

        if (hrviolations.ok):
            with open("hrviolations.xml", "a") as f:
                f.write(hrviolations.text)
                
        else:
            print("Error Occured in retrieving HR Violations for Server. Error Code" + str(hrviolations.status_code))
    else:
        print("Error Occured in retrieving Server Application ID. Error Coe." + str(serverResponse.status_code))



def main(argv):
    controller_url = ''
    client_id = ''
    client_secret = ""

    # retrieve api token
    token = retrieve_token(client_id, client_secret, controller_url)
    
    response = get_hr_violations_servers(token, controller_url)
    #print(response)
    # time_interval_to_run_in_hours = 1
    
    # numHours=24
    
    # for x in range(0, numHours):
    #     start=generate_epoch((numHours-x) * 3600)
    #     end=generate_epoch((numHours - x - 1) * 3600)
    #     # print(str(start) + "-" + str(end))
    #     # last_hour_date_time = datetime.now() - timedelta(hours = time_interval_to_run_in_hours * x)
    #     # current_hour_date_time = last_hour_date_time + timedelta(hours = time_interval_to_run_in_hours)
    #     # start = "{}.000-0700".format(last_hour_date_time.strftime('%Y-%m-%dT%H:%M:%S'))
    #     # end = "{}.000-0700".format(current_hour_date_time.strftime('%Y-%m-%dT%H:%M:%S'))
    #     get_hr_violations_server(token, controller_url, str(start), str(end))   




if __name__ == "__main__":
    main(sys.argv[1:])


