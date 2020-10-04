
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
df = pd.read_csv('Canvas-Course-Change-1FULL.csv')
#Connect to Canvvas
canvas = Canvas(API_URL, API_KEY)
account = canvas.get_account(1)

for index, row in df.iterrows():
  print("Updating",row["id"],row["NewShortName"],row["New name"])
  coursecode = row["NewShortName"]
  newname = row["New name"]
  cid = row["id"]
  print("to ->",coursecode,newname)
  course = canvas.get_course(cid)
  course.update(course={'name': newname})
  course.update(course={'course_code': coursecode})
