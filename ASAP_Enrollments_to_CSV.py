import pandas as pd
import requests, json, logging, sys
from pathlib import Path
from logging.handlers import SysLogHandler

#load configs
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
try:
    with open(confighome) as f:
        configs = json.load(f)
except EnvironmentError:
    print('Config file not found. Check to make sure there is a .ASAPCanvas folder in your home directory with a ASAPCanvas.json file in that folder.')
    raise
# Logging
if configs['logserveraddress'] is None:
    logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
    thelogger = logging.getLogger('MyLogger')
    thelogger.basicConfig(filename=str(logfilename), level=logging.INFO)
else:
    thelogger = logging.getLogger('MyLogger')
    thelogger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = (configs['logserveraddress'],514))
    thelogger.addHandler(handler)

thelogger.info('Loaded config file and logfile started')
csvfilename = sys.argv[1]
#-----ASAP Info
userid = configs['ASAPuserid']
orgid = configs['ASAPorgid']
password = configs['ASAPpassword']
apikey = configs['ASAPAPIKey']
url = configs['ASAPurl']
headers = {'Authorization' : 'user='+userid+'&organizationId='+orgid+'&password='+password+'&apiKey='+apikey}
thelogger.info('Getting ASAP Key')
r = requests.get(url,headers = headers)
if r.status_code == 404:
    thelogger.info('Failed to get ASAP Key')
elif r.status_code == 200:
    thelogger.info('Got ASAP Key')
    accesstoken = r.json()
    thelogger.info('Key is ' + accesstoken)
    url2 = configs['ASAPapiurl']
    header = {'asap_accesstoken' : accesstoken}
    thelogger.info('Getting data from ASAP')
    r2 = requests.get(url2,headers = header)
    #print(r2)
    results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop(columns=['Students'])
      # was drop('Students',1)
    #Drop columns we don't need
    '''
    results.drop(results.columns.difference(['CreatedDate',
                                            'EventEnrollmentID',
                                            'ScheduledEvent.Course.CourseName',
                                            'ScheduledEvent.Course.IsOnline',
                                            'EnrollmentStatusCd',
                                            'ScheduledEvent.EventCd',
                                            'StudentID',
                                            'CustomerID',
                                            'Person.Email',
                                            'Person.FirstName',
                                            'Person.LastName']),axis=1,inplace=True)
    '''
#    EventEnrollmentID
    #Drop columns we don't need, keep the ones we want
#    results.drop(results.columns.difference(['CreatedDate',
#                                            'EventEnrollmentID',
#                                            'InvoiceItems.InvoiceItemID',
#                                            'ScheduledEvent.Course.CourseName',
#                                            'EnrollmentStatusCd',
#                                            'ScheduledEvent.EventCd',
#                                            'StudentID',
#                                            'CustomerID',
#                                            'Person.Email',
#                                            'Person.FirstName',
#                                            'Person.LastName']),axis=1,inplace=True)
    print(results)
    results.to_csv(csvfilename)
