
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime, sys

# Script to fix Course Names in our instance of CanvasAPIKey
# takes a csv and changes the course codes
# csv needs to have currentcoursecode and coursecodenew as fields in it
csvfilename = sys.argv[1]
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
df = pd.read_csv(csvfilename, dtype=str)
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)

for index, row in df.iterrows():
  print("Updating",row["currentcoursecode"],row["coursecodenew"])
  currentcoursecode = row["currentcoursecode"]
  coursecodenew = row["coursecodenew"]
  print(currentcoursecode)
  print(coursecodenew)
  print("to ->",coursecodenew)
  course = canvas.get_course(currentcoursecode,'sis_course_id')
  course.update(course={'course_code': coursecodenew})
  course.update(course={'sis_course_id': coursecodenew})
