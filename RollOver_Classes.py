
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime

# This script replaces two scripts. One that was called Rename Course End of Term
#
# Purpose - This script goes through a term, and tacks on a user defined string to the sis_course_id, and the course_code. 
#           It also tacks on a String to the course name
#
# Parameters - Three: Term, prependccstr, prependnamestr

home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
except EnvironmentError:
    print('Config file not found. Check to make sure there is a .ASAPCanvas folder in your home directory with a ASAPCanvas.json file in that folder.')
    raise
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
logging.info('Loaded config file and logfile started -- RollOverClasses.py')
if len(sys.argv) < 4:
      print('You must run with TWO arguments, enclosed with quotes. Refer to documentation in script')
      sys.exit()
termidlookingfor = sys.argv[1]
prependccstr = sys.argv[2]
prependnamestr = sys.argv[3]
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
#    print(course.name)
#    print(course.sis_course_id)
#    print(course.term)
    print("found it")
    new_sis_id = course.sis_course_id + prependccstr
    #print(new_sis_id)
    #print(course.sis_course_id)
    print("Updating term->",termidlookingfor," courseid:",course.sis_course_id," to ", course.sis_course_id, prependccstr, " and ",course.name," to ",course.name,prependnamestr)
    logging.info('Updating term->' + termidlookingfor + ' courseid:' + course.sis_course_id + ' to ' + course.sis_course_id + prependccstr + ' and ' + course.name + ' to ' + course.name + prependnamestr)
    course.update(course={'course_code':new_sis_id,
                          'sis_course_id':new_sis_id,
                          'name':prependnamestr})
logging.info('Done -- RollOver_classes.py')
Print('Done!')
  