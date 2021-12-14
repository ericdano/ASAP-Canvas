import pandas as pd
import requests, json, logging, smtplib, datetime, smtplib
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# ASAP Connected to Canvas importer version .07
# This program grabs data from ASAP connected's API, dones so light processing,
# and creates new users in Canvas, adds new users to a tutorial class in Canvas,
# and then enrolls them into their class
# It also remembers where it left off in ASAP
#
# .05 Added some error checking for enrolling into a class that isn't in Canvas but in ASAP
# This will generate an error, quit the program, and send an email out that it needs to be addressed
# .06 Added more error checking
# .07 Added even more error checking and messaging (will now include in email if it skipped any classes in skip list)
#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
lastrunplacefilename = Path.home() / ".ASAPCanvas" / configs['ASAPlastposfile']
logging.info('Loaded config file and logfile started')
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
emailaddr = 'ericdannewitz@mac.com'
olduseremail = 'kpilkington@auhsdschools.org'
try: 
    user = canvas.get_user('agent007','sis_user_id')
    print(user.name)
    # User has changed their email, take existing email, add it as a login, and make the this new email the sis_login_id
    olduseremail = user.login_id #get the current email address
    old_profile = user.get_profile()
    old_primary_email = old_profile['primary_email']
    old_login_id = old_profile['login_id']
#    old_login_id = user.get_profile('login_id')
 #   print(olduseremail)
    print(old_primary_email)
    print(old_login_id)
    #Change DEFAULT email
    try:
        user.edit(user={
                'email': emailaddr.lower()
                }
        )                              
    except CanvasException as e3:
        print(e3)   
    logins = user.get_user_logins()
    account.edit_user_login(user.id,login={'unique_id':'ericdano@yahoo.com'})
    #try:
    #logins = user.get_user_logins()
    ##for login in logins:
     #   print(login)
    #    try:
    #       login.edit('unique_id',emailaddr.lower())
    #    except CanvasException as e5:
    #        print(e5)
    #except CanvasException as e3:
    #    print(e3)      
#    create_user_login(user,olduseremail)    
except CanvasException as e2:
    print(e2)  
