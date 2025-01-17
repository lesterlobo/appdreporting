import getopt
import requests
import json
import sys
import time
from datetime import date

controllerURL = ''
userName = ''
userPassword = ''
outputFile = 'healthRules.txt'


def usage():
    print(__doc__)


def main(argv):

    headers = {
        "Content-Type": "application/json" 
    }
    
    applications = requests.get(controllerURL + "/controller/rest/applications?output=JSON", headers=headers, auth=(userName,userPassword)) 

    if (applications.ok):
        #print(applications.text)
        apps = json.loads(applications.content.decode('utf-8'))
        counter = 0
        if (len(apps) > 0):
            for app in apps:
                applicationid = apps[counter]['id']
                applicationName = apps[counter]['name']
                healthRules = requests.get(controllerURL + '/controller/alerting/rest/v1/applications/' + str(applicationid) + '/health-rules/?output=JSON', headers=headers, auth=(userName,userPassword)) 

                if (healthRules.ok):
                    #print(healthRules.text)
                    hrs = json.loads(healthRules.content.decode('utf-8'))
                    for hr in hrs:
                        hrid = hr["id"]
                        hrDetails = requests.get(controllerURL + '/controller/alerting/rest/v1/applications/' + str(applicationid) + '/health-rules/' + str(hrid) + '?output=JSON', headers=headers, auth=(userName,userPassword)) 
                        with open(outputFile, "w") as f:
                            f.write(applicationName + ", " + hrDetails.text + "\n")
                        #print(hrDetails.text)
                counter = counter + 1
    else:
         print("Error Occured in retrieving Applications. Error Code" + str(applications.status_code))

    

    

if __name__ == "__main__":
    main(sys.argv[1:])
