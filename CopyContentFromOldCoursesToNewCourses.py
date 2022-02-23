import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
# Useage C:\python CopyContentFromOldCoursesToNewCourses.py nameofcsv.csv "term"
#
# This program reads a CSV file with the fields of
# NewSIS_ID, CurrentSIS_ID\
# It will create a new course with the SIS_ID from the CSV or use a course that already has the SIS_ID
# and copy the CurrentSIS_ID course contents to the new course
# and enroll the CurrentSIS_ID course teacher in the new course as the teacher
# version .01
# Created to help more easily roll over classes to a new term for Acalanes Adult Ed
#
# New classes are created using a Term defined here set to what it is in your Canvas Instance
if len(sys.argv) < 2:
    print('Script needs two arguments: python name.csv "term"')
    print('CSV file should be have headers of NewSIS_ID, CurrentSIS_ID')
    exit(0)
csvfilename = sys.argv[1]
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
#prep status (msg) and debug (dmsg) emails
dmsg = EmailMessage()
dmsg['Subject'] = str("Debug - " + configs['SMTPStatusMessage'] + " " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
dmsg['From'] = configs['SMTPAddressFrom']
dmsg['To'] = configs['DebugEmailAddr']
dmsgbody = ''
#Function to Copy Course
def copy_to_new_course():
    print('Copying Course->' + asapcoursestocopy['CurrentSIS_ID'][i] + ' to ->'+ asapcoursestocopy['NewSIS_ID'][i])
    logging.info('Starting copying process to new course id' + asapcoursestocopy['NewSIS_ID'][i])
    new_course = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i], use_sis_id=True)
    old_course = canvas.get_course(asapcoursestocopy['CurrentSIS_ID'][i], use_sis_id=True)
    new_course.create_content_migration('course_copy_importer', settings={'source_course_id': old_course.id})
    # Get the Canvas teacher(s) and enroll them into the copied course
    users = old_course.get_users(enrollment_type=['teacher'])
    for user in users:
        #canvas_user = canvas.get_user("Email", id_type="sis_login_id")
        new_course.enroll_user(user.id, "TeacherEnrollment", enrollment={"enrollment_state": "active"})
    tausers = old_course.get_users(enrollment_type=['TaEnrollment'])
    for user in tausers:
        new_course.enroll_user(user.id, "TaEnrollment", enrollment={"enrollment_state": "active"})       
logging.info('Connecting to Canvas')
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
logging.info('Loading CSV file to process')
asapcoursestocopy = pd.read_csv(csvfilename, dtype=str)
print('Loaded CSV....')
for i in asapcoursestocopy.index:
    print(asapcoursestocopy['NewSIS_ID'][i])
    try:
        asapclass = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i],use_sis_id=True)
        logging.info('Course already in Canvas.....resetting it......')
        asapclass.reset_content
        copy_to_new_course()
    except CanvasException as e:
        if str(e) == "Not Found":
            print('Error, this only copies content from old classes to new ones')
            exit()

