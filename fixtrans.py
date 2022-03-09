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
    try:
        asapclass = canvas.get_course(bsiscourseid,use_sis_id=True)
        enrollments = asapclass.get_enrollments(type='TeacherEnrollment')
        for stu in enrollments:
            if stu.user_id == 1196:
                print('Found user->' + str(stu.user_id) +' in class ' + bname)
                stu.deactivate(task='delete')
            else:
                print('Found OTHER user->' + str(stu.user_id) +' in class ' + bname)
    except CanvasException as e2:
        if str(e2) == "Not Found":
            print('Error finding course')
            print(str(e2))
        else:
            print(e2)

