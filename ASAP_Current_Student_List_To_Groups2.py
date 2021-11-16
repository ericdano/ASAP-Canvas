import pandas as pd
import requests, json, logging, smtplib, datetime, smtplib
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
lastrunplacefilename = Path.home() / ".ASAPCanvas" / configs['ASAPlastposfile']
logging.info('Loaded config file and logfile started')

#-----ASAP Info
userid = configs['ASAPuserid']
orgid = configs['ASAPorgid']
password = configs['ASAPpassword']
apikey = configs['ASAPAPIKey']
url = configs['ASAPurl']
dmsgbody = ''
headers = {'Authorization' : 'user='+userid+'&organizationId='+orgid+'&password='+password+'&apiKey='+apikey}
logging.info('Getting ASAP Key')
r = requests.get(url,headers = headers)
if r.status_code == 404:
    logging.info('Failed to get ASAP Key')
    if configs['Debug'] == "True":
        print('Failed to connect to ASAP')
        logging.info('Failed to get ASAP Key')
        dmsgbody += 'Failed to get ASAP Key....\n'
elif r.status_code == 200:
    logging.info('Got ASAP Key')
    if configs['Debug'] == "True":
        dmsgbody += 'Got ASAP Key....\n'
    accesstoken = r.json()
    logging.info('Key is ' + accesstoken)
    url2 = configs['ASAPEnrolledStudents']
    header = {'asap_accesstoken' : accesstoken}
    logging.info('Getting data from ASAP')
    if configs['Debug'] == "True":
        dmsgbody += 'Getting JSON from ASAP....\n'
    r2 = requests.get(url2,headers = header)
    results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop('Students',1)
    #Drop columns we don't need
    results.drop(results.columns.difference(['Person.Email']),1,inplace=True)
    print(results)
    print(results.apply(lambda col: col.unique()))