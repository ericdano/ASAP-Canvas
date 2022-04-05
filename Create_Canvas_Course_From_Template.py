import pandas as pd
import requests, json, logging, smtplib, datetime, sys
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
# Useage C:\python Create_Canvas_Course_From_Template nameofcsv.csv 'Fall 2020'
#

# This takes a CSV file of new course codes and creates generic templates for enrollment purposes
# CSV file needs CourseName, NewSIS_ID, Email, Template, SubAccount

if len(sys.argv) < 3:
    print('Script needs two arguments: python name.csv term (term needs to be in single quotes)')
    exit(0)
csvfilename = sys.argv[1]
CurrentCanvasTerm = sys.argv[2]
#teacheremail = sys.argv[3]
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
#read the csv file
asapcoursestocopy = pd.read_csv(csvfilename, dtype=str)
print('Loaded CSV....')
#Function to Copy Course
def copy_to_new_course():
    print('Copying Course....')
    print('New course id is -> ' + asapcoursestocopy['NewSIS_ID'][i])
    logging.info('Starting copying process to new course id' + asapcoursestocopy['NewSIS_ID'][i])
    # Get new course
    new_course = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i], use_sis_id=True)
    # Get old course
    old_course = canvas.get_course(asapcoursestocopy['Template'][i], use_sis_id=True)
    # Start migration
    new_course.create_content_migration('course_copy_importer', settings={'source_course_id': old_course.id})
    # Get the Canvas teacher(s) and enroll them into the copied course
    canvas_user = canvas.get_user(asapcoursestocopy['Email'][i], id_type="sis_login_id")
    new_course.enroll_user(canvas_user.id, "TeacherEnrollment", enrollment={"enrollment_state": "active"})

logging.info('Connecting to Canvas')
if configs['Debug'] == "True":
    dmsgbody = dmsgbody + 'Connecting to Canvas....\n'
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
#get get_enrollment_terms
terms = account.get_enrollment_terms()
term_id = 0
print('Looking for ' + CurrentCanvasTerm)
for term in terms:
    if term.name == CurrentCanvasTerm:
        logging.info('Found Term ID')
        term_id = term.id
    else:
       logging.info('Looking for Term ID')
       print('Looking for Term ID')
if term_id == 0:
    print('Term ID is still 0, stopping program.')
    dmsgbody=dmsgbody+'Did not find Term in Canvas. Aborted program.'
else:
    logging.info('Copying Course')
    for i in asapcoursestocopy.index:
        try:
            asapclass = canvas.get_course(asapcoursestocopy['NewSIS_ID'][i],use_sis_id=True)
            print('Course ' + str(asapcoursestocopy['NewSIS_ID'][i]) + ' is already in Canvas!!')
#            logging.info('Course already in Canvas.....now copying......')
#            if configs['Debug'] == "True":
#               dmsgbody = dmsgbody + asapcoursestocopy['NewSIS_ID'][i] + ' is in Canvas\n'
#            copy_to_new_course()
        except CanvasException as e:
            if str(e) == "Not Found":
                #course does not exist, create it
                logging.info('Course ' + asapcoursestocopy['NewSIS_ID'][i] + ' is not in Canvas')
                print('Course not in Canvas, creating')
                dmsgbody = dmsgbody + asapcoursestocopy['NewSIS_ID'][i] + ' is NOT in Canvas\n'
                old_course1 = canvas.get_course(asapcoursestocopy['Template'][i],use_sis_id=True)
                subaccount = canvas.get_account(asapcoursestocopy['SubAccount'][i])
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
