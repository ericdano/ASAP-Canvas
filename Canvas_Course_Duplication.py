import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
# Useage C:\python Canvas_Course_Duplication.py nameofcsv.csv
#
# This program reads a CSV file with the fields of
# NewSIS_ID, CurrentSIS_ID, CourseName
# It will create a new course with the SIS_ID from the CSV or use a course that already has the SIS_ID
# and copy the CurrentSIS_ID course contents to the new course
# and enroll the CurrentSIS_ID course teacher in the new course as the teacher
# version .01
# Created to help more easily roll over classes to a new term for Acalanes Adult Ed
#
# New classes are created using a Term defined here set to what it is in your Canvas Instance
CurrentCanvasTerm = 'Winter 2021'
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
    print('Copying Course....')
    print('New course id is -> ' + asapcoursestocopy['NewSIS_ID'][i])
    logging.info('Starting copying process to new course id' + asapcoursestocopy['NewSIS_ID'][i])
    # Get new course
    new_course = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i], use_sis_id=True)
    # Get old course
    old_course = canvas.get_course(asapcoursestocopy['CurrentSIS_ID'][i], use_sis_id=True)
    # Start migration
    new_course.create_content_migration('course_copy_importer', settings={'source_course_id': old_course.id})
    # Get the Canvas teacher(s) and enroll them into the copied course
    users = old_course.get_users(enrollment_type=['teacher'])
    for user in users:
        #canvas_user = canvas.get_user("Email", id_type="sis_login_id")
        new_course.enroll_user(user.id, "TeacherEnrollment", enrollment={"enrollment_state": "active"})

logging.info('Connecting to Canvas')
if configs['Debug'] == "True":
    dmsgbody = dmsgbody + 'Connecting to Canvas....\n'
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
#get get_enrollment_terms
terms = account.get_enrollment_terms()
term_id = 0
for term in terms:
    if term.name == CurrentCanvasTerm:
        logging.info('Loading CSV file to process')
        term_id = term.id
    else:
       logging.info('Can not Find Term')
       print('Error....cannot find term')
logging.info('Loading CSV file to process')
if configs['Debug'] == "True":
    dmsgbody = dmsgbody + 'Loading csv file....\n'
#read the csv file
asapcoursestocopy = pd.read_csv(csvfilename, dtype=str)
print('Loaded CSV....')
for i in asapcoursestocopy.index:
    print(asapcoursestocopy['NewSIS_ID'][i])
    try:
        asapclass = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i],use_sis_id=True)
        logging.info('Course already in Canvas.....now copying......')
        if configs['Debug'] == "True":
            dmsgbody = dmsgbody + asapcoursestocopy['NewSIS_ID'][i] + ' is in Canvas\n'
        copy_to_new_course()
    except CanvasException as e:
        if str(e) == "Not Found":
        #course does not exist, create it
            logging.info('Course ' + asapcoursestocopy['NewSIS_ID'][i] + ' is not in Canvas')
            print('Course not in Canvas, creating')
            dmsgbody = dmsgbody + asapcoursestocopy['NewSIS_ID'][i] + ' is NOT in Canvas\n'
            old_course1 = canvas.get_course(asapcoursestocopy['CurrentSIS_ID'][i],use_sis_id=True)
            subaccount = canvas.get_account(old_course1.account_id)
            newCourse = subaccount.create_course(
                                course={'name': asapcoursestocopy['CourseName'][i],
                                'course_code': asapcoursestocopy['NewSIS_ID'][i],
                                'sis_course_id': asapcoursestocopy['NewSIS_ID'][i],
                                'term_id': term_id}
                                )
            print(newCourse)
            dmsgbody = dmsgbody + 'created course ' + asapcoursestocopy['NewSIS_ID'][i] + ' in Canvas\n'
            copy_to_new_course()
s = smtplib.SMTP(configs['SMTPServerAddress'])
if configs['Debug'] == "True":
    print("All done!")
    dmsg.set_content(dmsgbody)
    s.send_message(dmsg)
