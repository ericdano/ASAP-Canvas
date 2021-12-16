import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
# Useage C:\python Hide_Courses_Until_Start.py "Fall2021"
#
# This program gathers ALL the courses in an upcoming Term and enabled the
# setting to only allow students to see a published course after the term starts
#
if len(sys.argv) < 2:
    print('Script needs one argument: python "term"')
    exit(0)
termidlookingfor = sys.argv[1]
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
account = canvas.get_account(1)
logging.info('Flipping bit to restrict students from seeing class before Term date')
column_names = ["courseid","coursename","sistermid"]
df = pd.DataFrame(columns = column_names)
courses=account.get_courses(include=['term','sis_term_id'])
for course in courses:
    if course.term['sis_term_id'] == termidlookingfor:
        df = df.append({'courseid':course.id,
               'coursename':course.name,
               'sistermid':course.term['sis_term_id']}, ignore_index=True)
for index, row in df.iterrows():
    bid = row["courseid"]
    c = canvas.get_course(bid)
    c.update(course={'restrict_student_future_view':'True'})
    print("Updating term->",termidlookingfor," courseid:",c.sis_course_id)
    logging.info('Updating term->' + termidlookingfor + ' courseid:' + c.sis_course_id)
logging.info('Done -- RollOver_classes.py')
print('Done!')
