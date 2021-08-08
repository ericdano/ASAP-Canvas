
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime, sys

# This script replaces two scripts. One that was called Rename Course End of Term
#
# Purpose - This script goes through a term, and tacks on a user defined string to the sis_course_id, and the course_code. 
#           It also tacks on a String to the course name
#
# Parameters - Three: Term, prependccstr, prependnamestr

home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
try:
    with open(confighome) as f:
        configs = json.load(f)
except EnvironmentError:
    print('Config file not found. Check to make sure there is a .ASAPCanvas folder in your home directory with a ASAPCanvas.json file in that folder.')
    raise
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
logging.info('Loaded config file and logfile started -- RollOverClasses.py')
if len(sys.argv) < 5:
      print('You must run with FOUR arguments, enclosed with quotes. Refer to documentation in script')
      print("Example->python3 RollOver_Classes.py 'SUM2021' 'SUM21' 'Summer 2021' 'DOIT'")
      print('Last Arg DOIT will actually do the rollover. All other time it will just be a test run. ie no Canvas data updated.')
      sys.exit()
termidlookingfor = sys.argv[1]
prependccstr = sys.argv[2]
prependnamestr = sys.argv[3]
shouldwedoit = sys.argv[4]
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
column_names = ["courseid","coursename","sistermid","newcoursename","newsisid","newcoursecode"]
df = pd.DataFrame(columns = column_names)
courses=account.get_courses(include=['term','sis_term_id'])
for course in courses:
  if course.term['sis_term_id'] == termidlookingfor:
    new_sis_id = course.sis_course_id + prependccstr
    new_course_name = prependnamestr + course.name
    print("Updating term->",termidlookingfor," courseid:",course.sis_course_id," to ", new_sis_id, " sis_id: ", course.sis_course_id, " to ", new_sis_id, " and ",course.name," to ",new_course_name)
    logging.info('Updating term->' + termidlookingfor + ' sis_course_id:' + course.sis_course_id + ' to ' + new_sis_id + ' course_code:' + course.course_code + ' to ' + new_sis_id + ' and ' + course.name + ' to ' + new_course_name)
    if shouldwedoit == 'DOIT':
      course.update(course={'course_code':new_sis_id,
                            'sis_course_id':new_sis_id,
                            'name':new_course_name})
      print('Updated Canvas course')
      logging.info('Updated Canvas')
logging.info('Done -- RollOver_classes.py')
print('Done!')
  