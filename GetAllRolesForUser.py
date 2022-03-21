import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
#
#load configs
# Script to get all roles for a user
# Useage >python getallrolesforuser.py user@gmail.com
#
#
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
useremail = sys.argv[1]
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#prep status (msg) and debug (dmsg) emails
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
user = canvas.get_user(useremail,'sis_login_id')
enrolls = user.get_enrollments(include=['sis_course_id'])
for e in enrolls:
    print(e)
    print('ID->' + str(e.id))
    print('SIS ID->' + str(e.sis_course_id))
    print('Role->' + e.role)
 #   print('Base Role ype->' + r.base_role_type)
    print('---------------------------')
