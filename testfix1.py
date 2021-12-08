import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
# Useage C:\python Create_New_Classes.py nameofcsv.csv "Fall 2021"
#
# This program reads a CSV file with the fields of
# EMAIL, CourseName, COURSECODE, TEMPLATE
# It will create create new courses from CSV Based on the Template you want, and enroll the teacher into the course
#if len(sys.argv) < 3:
#    print('Script needs two arguments: python name.csv "term"')
#    print('CSV file should be have headers of COURSECODE, CurrentSIS_ID, CourseName')
#    exit(0)
#csvfilename = sys.argv[1]
#CurrentCanvasTerm = sys.argv[2]
#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
logging.info('Loaded config file and logfile started')
logging.info('Course Copy to New Term Starting...')
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
course = canvas.get_course(660)
print(course.name)
course.update(course={'restrict_student_future_view':'True'})