
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime

# Script to fix Course Names in our instance of CanvasAPIKey

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
  print(course.name)
  print(course.sis_course_id)
  print(course.term)
  if course.term == "FALL2020":
    if course.sis_course_id == "057429":
      print("found it")
      #changeit = canvas.get_course(id)
      #changeit.update(changeit={'course_code':changeit})
  

#for i in courses:
#    df = df.append({'courseid':i.id,
##               'coursename':i.name,
#               'sistermid':i.term['sis_term_id'],
#               'newcoursename':'Spring 2021 - ' + i.name}, ignore_index=True)
#for index, row in df.iterrows():
#    if row["sistermid"]=="FALL2020":
        #print("Updating term->",row["sistermid"]," courseid:",row["courseid"],"->",row["coursename"]," to ",row["newcoursename"])
#        print("Changing SIS from ->",row["newsisid"], row["newcoursecode"])
#        cid = row["courseid"]
#        course = canvas.get_course(cid,'sis_course_id')
#        print(course.sis_course_id)
#        print(course.course_code)

          #course.update(course={'course_code': cid + "F20"})
          #course.update(course={'sis_course_id': cid + "F20"})

  