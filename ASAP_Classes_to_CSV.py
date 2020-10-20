import pandas as pd
import requests, json, logging, sys
from pathlib import Path
#Python program to grab classes from ASAP and dump them to csv
#load configs
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
#logging.basicConfig(filename=configs['logfilename'], level=logging.INFO)
logging.info('Loaded config file and logfile started')
csvfilename = sys.argv[1]
#-----ASAP Info
userid = configs['ASAPuserid']
orgid = configs['ASAPorgid']
password = configs['ASAPpassword']
apikey = configs['ASAPAPIKey']
url = configs['ASAPurl']
headers = {'Authorization' : 'user='+userid+'&organizationId='+orgid+'&password='+password+'&apiKey='+apikey}
logging.info('Getting ASAP Key')
r = requests.get(url,headers = headers)
if r.status_code == 404:
    logging.info('Failed to get ASAP Key')
elif r.status_code == 200:
    logging.info('Got ASAP Key')
    accesstoken = r.json()
    logging.info('Key is ' + accesstoken)
    url2 = 'https://api.asapconnected.com/api/Courses/GetCourses'
    header = {'asap_accesstoken' : accesstoken}
    logging.info('Getting data from ASAP')
    r2 = requests.get(url2,headers = header)
    results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="CourseGroups", max_level=2)], axis=1).drop('CourseGroups',1)
    print(results)
    results.to_csv(csvfilename)
