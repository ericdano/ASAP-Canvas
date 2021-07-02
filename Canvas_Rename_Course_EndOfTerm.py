
from numpy.lib.function_base import _parse_input_dimensions
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime, sys

# Script to rename classes in Canvas that are from the previous term
# We generally are keeping all previous classes in our Canvas rather than deleting them
# However, it is confusing for the teachers to have like 5 ESL Morning classes from different terms in their dashboard
# So, this script will RENAME a class depending on the TERM you are looking for
# The best way to do this is to GRAB all the courses, append the new names to them
# and then go through it again and anything in the TERM ID will be changed to the new name
# run it like this
# python canvas_rename_course_endofterm.py 'FALL2020' 'Fall 2020 -'
# this will look for your SIS TERM ID of FALL2020 and then prepend the second argument to the class
#
# suggest commenting out the LAST TWO LINES at the end of this file before you make changes to make sure things are correct!!!!!!!!
#
# ie the course = canvas.get_course(cid)
# and course.update(course={'name': newname})

#load configs
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
logging.info('Loaded config file and logfile started')
if len(sys.argv) < 3:
      print('You must run with TWO arguments, enclosed with quotes. Refer to documentation in script')
      sys.exit()
termidlookingfor = sys.argv[1]
prependname = sys.argv[2]
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
logging.info('Starting to rename classes')
logging.info('going to look for ' + termidlookingfor + 'and prepend ' + prependname + 'to it')
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
               'newcoursename':prependname + i.name}, ignore_index=True)
for index, row in df.iterrows():
    if row["sistermid"]==termidlookingfor:
          print("Updating term->",row["sistermid"]," courseid:",row["courseid"],"->",row["coursename"]," to ",row["newcoursename"])
          logging.info('Updating term->' + row["sistermid"] + ' courseid:' + row["courseid"] + '->' + row["coursename"] + ' to ' + row["newcoursename"])
          newname = row["newcoursename"]
          cid = row["courseid"]
          #------------------
          # uncomment the next two lines at the BOTTOM to make ACTUAL changes to your Canvas
          #---------------------------
          #course = canvas.get_course(cid)
          #course.update(course={'name': newname})
