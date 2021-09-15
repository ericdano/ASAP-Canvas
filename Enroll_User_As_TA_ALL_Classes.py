import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
#
# This will enroll a user into ALL classes in Canvas as a TA for a term
# args ->python Enroll_User_As_TA_ALL_Classes.py 'Fall 2021' me@me.com
#
termidlookingfor = sys.argv[1]
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
column_names = ["courseid","course_sis_id","coursename"]
df = pd.DataFrame(columns = column_names)
print(teacheremail)
courses=account.get_courses(include=['term','sis_term_id','sis_course_id'])
print('Gathering Courses in Term')
for i in courses:
    if i.term['sis_term_id'] == termidlookingfor:
        df = df.append({'courseid':i.id,
                'course_sis_id':i.sis_course_id,
                'coursename':i.name}, ignore_index=True)
        print('Added to Pandas ',i.id,' Course Name:',i.name)
for index, row in df.iterrows():
    bid = row["courseid"]
    bname = row["coursename"]
    bsiscourseid = row["course_sis_id"]
    #print('Enrolled ',teacheremail,' as TA in class ',bname,'(',bid,') ','(',bsiscourseid,')')
    asapclass = canvas.get_course(bsiscourseid,use_sis_id=True)
    user = canvas.get_user(teacheremail,'sis_login_id')
    try:
        enrollment = asapclass.enroll_user(user.id, "TaEnrollment",
                    enrollment = {
                        "sis_course_id": bsiscourseid,
                        "notify": True,
                        "enrollment_state": "active"
                        }
                    )
        print('Enrolled ',teacheremail,' as TA in class ',bname,'(',bid,') ','(',bsiscourseid,')')
    except CanvasException as e:
        if str(e) == "Not Found":
            print('Error finding course')
            print(str(e))
