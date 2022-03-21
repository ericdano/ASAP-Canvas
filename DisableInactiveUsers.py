from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime, sys
from datetime import datetime
#
#
# Script to disable Canvas accounts after inactivity period
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
    configs = json.load(f)
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
allusers = account.get_users()
for user in allusers:
    print(user)
    userdetail = canvas.get_user(user.id,
                            include=['last_login'])
    if userdetail.last_login is None:                             
        lastlogindate = 'no last login'
    else:
        lastlogindate = datetime.strptime(userdetail.last_login,'%Y-%m-%dT%H:%M:%S%z')
    print(userdetail.login_id,'->',userdetail.sis_user_id,'->',userdetail.last_login,'->',lastlogindate)
