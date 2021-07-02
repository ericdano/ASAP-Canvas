
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime

# Script to Tack on Term to Course SIS_IDs and Course Codes

home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#df = pd.read_csv('Canvas-Course-Change-1FULL.csv')
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
column_names = ["courseid","coursename","sistermid","newcoursename","newsisid","newcoursecode"]
df = pd.DataFrame(columns = column_names)
courses=account.get_courses(include=['term','sis_term_id'])
for course in courses:
  if course.term['sis_term_id'] == "SPR2021ELL":
#    print(course.name)
#    print(course.sis_course_id)
#    print(course.term)
    print("found it")
    new_sis_id = course.sis_course_id + "SP21"
    print(new_sis_id)
    print(course.sis_course_id)
    course.update(course={'course_code':new_sis_id,
                          'sis_course_id':new_sis_id})


  