import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
#
# Quick and easy way to enroll a teacher as teacher in a class.
# python Canvas_Enroll_Teacher_In_Course.py 22222 me@institute.com
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
print(coursesisid)
print(teacheremail)
try:
    asapclass = canvas.get_course(coursesisid,use_sis_id=True)
    user = canvas.get_user(teacheremail,'sis_login_id')
    enrollment = asapclass.enroll_user(user.id, "TeacherEnrollment",
                    enrollment = {
                        "sis_course_id": coursesisid,
                        "notify": True,
                        "enrollment_state": "active"
                        }
                    )
    print('Enrolled teacher in class')
except CanvasException as e:
    if str(e) == "Not Found":
        print('Error finding course')
        print(str(e))
