import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage

#
# This program enrols a CSV list of users into a Canvas Group
# Usage is >python CSV_To_Group.py groupid csvname.csv
#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
group = canvas.get_group(23,include=['users'])
#print('Group print->]',group)
#print('Members->',group.members_count)
print('Users->',group.users)
print('--------------------')
df = pd.DataFrame(group.users,columns=['id','name','login_id'])
print(df)
print('--------------------')
#m = group.create_membership(864)
try:
    n = group.remove_user(1216)
except CanvasException as e:
    if str(e) == "Not Found":
        print('User not in group')
try:
    n = group.remove_user(864)
except CanvasException as e:
    if str(e) == "Not Found":
        print('User not in group')
user = canvas.get_user('ericdannewitz@me.com','sis_login_id')
#m = group.create_membership('ericdannewitz@me.com')
#m = group.create_membership('kpilkington@auhsdschools.org')
print(user)
m = group.create_membership(user.id)
user = canvas.get_user('kpilkington@auhsdschools.org','sis_login_id')
m = group.create_membership(user.id)
