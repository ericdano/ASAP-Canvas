
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
column_names = ["courseid","coursename","sistermid","newcoursename"]
df = pd.DataFrame(columns = column_names)
courses=account.get_courses(include=['term','sis_term_id'])
for i in courses:
    #print(i.id)
    #print(i.name)
    #print(i.term['sis_term_id'])
    df = df.append({'courseid':i.id,
               'coursename':i.name,
               'sistermid':i.term['sis_term_id'],
               'newcoursename':'Winter 2021 - ' + i.name}, ignore_index=True)
for index, row in df.iterrows():
    if row["sistermid"]=="FALL2020":
        print("Updating term->",row["sistermid"]," courseid:",row["courseid"],"->",row["coursename"]," to ",row["newcoursename"])
        newname = row["newcoursename"]
        cid = row["courseid"]
        course = canvas.get_course(cid)
        course.update(course={'name': newname})
