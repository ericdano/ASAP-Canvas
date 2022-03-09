import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
#
# Quick and easy way to enroll a users as teacher aid in a class.
# python Enroll_User_As_TA.py 22222 me@institute.com
#
coursesisid = sys.argv[1]
teacheremail = sys.argv[2]
#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#prep status (msg) and debug (dmsg) emails
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
#Function to Copy Course
print(coursesisid)
print(teacheremail)
try:
    asapclass = canvas.get_course(coursesisid,use_sis_id=True)
    try:
        user = canvas.get_user(teacheremail,'sis_login_id')
        try:
            enrollment = asapclass.enroll_user(user.id, "TaEnrollment",
                            enrollment = {
                                "sis_course_id": coursesisid,
                                "notify": True,
                                "enrollment_state": "active",
                                "role_id": 16
                            }
                        )
            print('Enrolled Transition Specialist in class')
        except CanvasException as e1:
            print('Error enrolling user')
    except CanvasException as e2:
        if str(e2) == "Not Found":
            print('Error Finding user')
            print(e2)
except CanvasException as e:
    if str(e) == "Not Found":
        print('Error finding course')
        print(str(e))
