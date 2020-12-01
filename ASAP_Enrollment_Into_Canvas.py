import pandas as pd
import requests, json, logging, smtplib, datetime, smtplib
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
# ASAP Connected to Canvas importer version .07
# This program grabs data from ASAP connected's API, dones so light processing,
# and creates new users in Canvas, adds new users to a tutorial class in Canvas,
# and then enrolls them into their class
# It also remembers where it left off in ASAP
#
# .05 Added some error checking for enrolling into a class that isn't in Canvas but in ASAP
# This will generate an error, quit the program, and send an email out that it needs to be addressed
# .06 Added more error checking
# .07 Added even more error checking and messaging (will now include in email if it skipped any classes in skip list)
#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
logging.basicConfig(filename=str(logfilename), level=logging.INFO)
lastrunplacefilename = Path.home() / ".ASAPCanvas" / configs['ASAPlastposfile']
logging.info('Loaded config file and logfile started')
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
#prep status (msg) and debug (dmsg) emails
msg = EmailMessage()
dmsg = EmailMessage()
msg['Subject'] = str(configs['SMTPStatusMessage'] + " " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
dmsg['Subject'] = str("Debug - " + configs['SMTPStatusMessage'] + " " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
msg['From'] = configs['SMTPAddressFrom']
introletterfrom = configs['SMTPAddressFrom']
dmsg['From'] = configs['SMTPAddressFrom']
msg['To'] = configs['SendInfoEmailAddr']
dmsg['To'] = configs['DebugEmailAddr']
msgbody = ''
skippedbody = ''
dmsgbody = ''
logging.info('Reading Previous Sent Intro Letters file')
SentIntroLetters = pd.read_csv(Path(configs['IntroLetterPath']+configs['SentIntroLetters']))
#Funcction to email intro letter out to new Students
#Looks for a CVS file of emails previously sent out to not send out the same letter again
def emailintroletter():
    global SentIntroLetters
    print('Starting Send')
    logging.info('Prepping to send intro letter from AE')
    IntroLetterRoot = MIMEMultipart('related')
    IntroLetterRoot['Subject'] = 'Acalanes Adult Winter 2021 Enrollment'
    IntroLetterRoot['From'] = configs['SMTPAddressFrom']
    IntroLetterRoot['To'] = newenrolls['Person.Email'][i]
    IntroLetterRoot.preamble = 'This is a multi-part message in MIME format.'
    IntroLetterAlt = MIMEMultipart('alternative')
    IntroLetterRoot.attach(IntroLetterAlt)
    IntroLetterText = MIMEText('This is the alternative plain text message.')
    IntroLetterAlt.attach(IntroLetterText)
    logging.info('Reading Previous Sent Intro Letters file')
    messagepath = Path(configs['IntroLetterPath']+configs['IntroLetterFile'])
    introfp1 = open(messagepath,'r')
    IntroLetterText = MIMEText(introfp1.read(),'html')
    IntroLetterAlt.attach(IntroLetterText)
    introfp1.close()
    imagepath =Path(configs['IntroLetterPath']+"aeimage1.jpg")
    introfp = open(imagepath, 'rb')
    IntroLetterImage = MIMEImage(introfp.read())
    introfp.close()
    IntroLetterImage.add_header('Content-ID', '<image1>')
    IntroLetterRoot.attach(IntroLetterImage)
    smtpintroletter = smtplib.SMTP()
    smtpintroletter.connect(configs['SMTPServerAddress'])
    smtpintroletter.sendmail(configs['SMTPAddressFrom'], newenrolls['Person.Email'][i], IntroLetterRoot.as_string())
    smtpintroletter.quit()
    new_row = {'Email': newenrolls['Person.Email'][i]}
    SentIntroLetters = SentIntroLetters.append(new_row,ignore_index=True)
    SentIntroLetters.to_csv(Path(configs['IntroLetterPath']+configs['SentIntroLetters']))


#Function to enroll or unenroll a student
def enrollstudent():
    global msgbody, dmsgbody
    if configs['Debug'] == "True":
        print('Enrolling ' + newenrolls['Person.Email'][i] + ' into ID ' +  newenrolls['ScheduledEvent.EventCd'][i])
        dmsgbody = dmsgbody + 'Enrolling ' + newenrolls['Person.Email'][i] + ' into ID ' +  newenrolls['ScheduledEvent.EventCd'][i] + '\n'
    logging.info('Found user - doing enrollments')
    coursetoenroll = newenrolls['ScheduledEvent.EventCd'][i]
    try:
        course = canvas.get_course(coursetoenroll,'sis_course_id')
        if newenrolls['EnrollmentStatusCd'][i] == "DROPPED":
            if configs['Debug'] == "True":
                dmsgbody = dmsgbody + 'Dropping ' + newenrolls['Person.Email'][i] +'\n'
            enrollments = course.get_enrollments(type='StudentEnrollment')
            for stu in enrollments:
                # You have to loop through all the enrollments for the class and then find the student id in the enrollment then tell it to delete it.
                if stu.user_id == user.id:
                    stu.deactivate(task='delete')
                    logging.info('Deleted student from ' + newenrolls['ScheduledEvent.Course.CourseName'][i])
                    msgbody = msgbody + 'Dropped ' + newenrolls['Person.Email'][i] + ' from ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + '\n'
                    if configs['Debug'] == "True":
                        dmsgbody = dmsgbody + 'Dropped ' + newenrolls['Person.Email'][i] + ' from ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + '\n'
        else:
            # Other ASAP things could be PEND or ENROLLED.
            enrollment = course.enroll_user(user,"StudentEnrollment",
                                            enrollment = {
                                                "sis_course_id": coursetoenroll,
                                                "notify": True,
                                                "enrollment_state": "active"
                                                }
                                            )
            logging.info('Enrolled ' + newenrolls['Person.Email'][i] + ' in ' + newenrolls['ScheduledEvent.Course.CourseName'][i])
            msgbody = msgbody + 'Enrolled ' + newenrolls['Person.Email'][i] + ' in ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + '\n'
            if configs['Debug'] == "True":
                dmsgbody = dmsgbody + 'Enrolled ' + newenrolls['Person.Email'][i] + ' in ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + '\n'
    except CanvasException as ec:
                #It all starts with figuring out if the user is in Canvas and enroll in tutorial course
        logging.info('Canvas error ' + str(ec) + ' Course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' - ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' is not in Canvas. Stopping imports. ')
        print('Canvas error ' + str(ec) + ' Course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' - ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' is not in Canvas. Stopping imports.')
        s = smtplib.SMTP(configs['SMTPServerAddress'])
        msgbody = msgbody + 'Course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' - ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' is not in Canvas. Stopping imports.\n\n\nPanic!!!\n'
        dmsgbody = dmsgbody + 'Course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' - ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' is not in Canvas. Stopping imports.\n\n\nPanic!!!\n'
        msg.set_content(msgbody)
        s.send_message(msg)
        raise
#-----ASAP Info
userid = configs['ASAPuserid']
orgid = configs['ASAPorgid']
password = configs['ASAPpassword']
apikey = configs['ASAPAPIKey']
url = configs['ASAPurl']
headers = {'Authorization' : 'user='+userid+'&organizationId='+orgid+'&password='+password+'&apiKey='+apikey}
logging.info('Getting ASAP Key')
r = requests.get(url,headers = headers)
if r.status_code == 404:
    logging.info('Failed to get ASAP Key')
    if configs['Debug'] == "True":
        print('Failed to connect to ASAP')
        logging.info('Failed to get ASAP Key')
        dmsgbody = dmsgbody + 'Failed to get ASAP Key....\n'
elif r.status_code == 200:
    logging.info('Got ASAP Key')
    if configs['Debug'] == "True":
        dmsgbody = dmsgbody + 'Got ASAP Key....\n'
    accesstoken = r.json()
    logging.info('Key is ' + accesstoken)
    url2 = configs['ASAPapiurl']
    header = {'asap_accesstoken' : accesstoken}
    logging.info('Getting data from ASAP')
    if configs['Debug'] == "True":
        dmsgbody = dmsgbody + 'Getting JSON from ASAP....\n'
    r2 = requests.get(url2,headers = header)
    results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop('Students',1)
    #Drop columns we don't need
    results.drop(inplace=True, columns=['FinalGrade','Goal1','Goal2','InvoiceItems','ScheduledEvent.AgeMin','ScheduledEvent.IsTBD',
                                        'IsFail','IsPass','TopsRecord','TotalCredits','ScheduledEvent.AgeMinMonths','ScheduledEvent.IsOvernight',
                                        'ScheduledEvent.Duration','ScheduledEvent.IsAfterschool','ScheduledEvent.IsArchived',
                                        'ScheduledEvent.IsSelfPaced','ScheduledEvent.HasRecurringFees','ScheduledEvent.BreakEnd',
                                        'ScheduledEvent.BreakMin','ScheduledEvent.BreakStart','ScheduledEvent.Course.HasPrereq','ScheduledEvent.Course.DepartmentID',
                                        'ScheduledEvent.Course.HideOnlineIfNoPrereq','ScheduledEvent.Course.IsSecure','ScheduledEvent.MinimumEnrollment',
                                        'ScheduledEvent.PayRateRoleType','ScheduledEvent.MinimumEnrollment','ScheduledEvent.TeacherPayRate',
                                        'CurrentLevelType','CurrentLevelValue','MemberStatus','HomeroomTeacher','DismissalMethod','ReferredBy',
                                        'Person.ImageFile','Person.GradeLevel','Person.ListnameStudentpickup','Person.ShirtSize',
                                        'ScheduledEvent.CompanyID','ScheduledEvent.AgeMaxMonths','ScheduledEvent.Course.AsapIntegrationID',
                                        'ScheduledEvent.AllowWaitlist','ScheduledEvent.Course.CourseImage','ScheduledEvent.Course.DepositAmount',
                                        'ScheduledEvent.Course.CreditValue','ScheduledEvent.Course.ImageAltText','ScheduledEvent.Course.LongDescription',
                                        'ScheduledEvent.EventImage','ScheduledEvent.EventStatus','ScheduledEvent.Course.Materials',
                                        'ScheduledEvent.Materials','ScheduledEvent.TeacherPaySchedule','RenewalRecurrence','SmsOptInType',
                                        'OrgAccountNo','ScheduledEvent.AgeMax','ScheduledEvent.Capacity','ScheduledEvent.Course.GradeMax','ScheduledEvent.Course.Instrument',
                                        'ScheduledEvent.Course.GradeMin','ScheduledEvent.Course.IsAfterSchool','ScheduledEvent.Course.IsArchived',
                                        'ScheduledEvent.DepartmentID','ScheduledEvent.Course.PrimarySiteID','CompletionDate',
                                        'ScheduledEvent.Course.IsPrivateLesson','ScheduledEvent.Course.PLFeeAmount','ScheduledEvent.Course.OrganizationID',
                                        'ScheduledEvent.Course.ProviderCourseID','ScheduledEvent.Course.Prerequisites','ScheduledEvent.Course.ProviderID',
                                        'ScheduledEvent.EventTypeCd','ScheduledEvent.JobClassCd','ScheduledEvent.OrganizationID','CustomerNo','DLNum',
                                        'OrganizationID','Person.Relationship','Person.Gender','LastModifiedDate','ScheduledEvent.IsShowOnline',
                                        'ScheduledEvent.SiteID','ConfirmationCd','ScheduledEvent.Course.CreatedDate','ScheduledEvent.Course.IsOnline'])
    # For Canvas, we only care about a few columns that ASAP gives us (hence the mass dropping of columns above)
    # EventEnrollmentID is basically a sequence number. This is what we are going to use to find out where we are in the transcation stream
    # EnrollmentStatusCd tells us what to do. ENROLLED and PEND mean put them in a class, DROPPED means remove them
    # ScheduledEvent.EventCd is the SIS ID for the Course
    # Person.Email is both the login and the Email
    # Person.FirstName is their FirstName
    # Person.LastName is their LastName
    # Load last record processed
    logging.info('Connecting to Canvas')
    if configs['Debug'] == "True":
        dmsgbody = dmsgbody + 'Connecting to Canvas....\n'
    canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
    account = canvas.get_account(1)
    logging.info('Getting last record we looked at')
    if configs['Debug'] == "True":
        dmsgbody = dmsgbody + 'Loading last record processed....\n'
    #load starting record position
    lastrunplace = pd.read_csv(lastrunplacefilename)
    #print(lastrunplace['EventEnrollmentID'])
    logging.info('Last place was ' + str(lastrunplace))
    newenrolls = results[results['EventEnrollmentID'] > lastrunplace['EventEnrollmentID'][0]]
    logging.info("Looking for enrollments")
    if configs['Debug'] == "True":
        dmsgbody = dmsgbody + "Looking for enrollments....\n"
    for i in newenrolls.index:
        #Look for classes we don't do canvas for, and skip
        if not newenrolls['ScheduledEvent.EventCd'][i] in configs['SkipCourses']:
            try:
                user = canvas.get_user(newenrolls['Person.Email'][i],'sis_login_id')
                logging.info(newenrolls['Person.Email'][i] + " is in Canvas")
                if configs['Debug'] == "True":
                    dmsgbody = dmsgbody + newenrolls['Person.Email'][i] + ' is in Canvas\n'
                logging.info("Looking if we have sent intro letter to person...")
                senttheletter = SentIntroLetters[SentIntroLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                if senttheletter.empty:
                    logging.info("Going to send intro letter....")
                    emailintroletter()
                enrollstudent()
            except CanvasException as e:
            #It all starts with figuring out if the user is in Canvas and enroll in tutorial course
                if str(e) == "Not Found":
                    if configs['Debug'] == "True":
                        print('Creating ' + newenrolls['Person.Email'][i])
                        dmsgbody = dmsgbody + 'Creating ' + newenrolls['Person.Email'][i] + ' in Canvas\n'
                    logging.info('User not found, creating')
                    newusername = newenrolls['Person.FirstName'][i] + " " + newenrolls['Person.LastName'][i]
                    sis_user_id = newenrolls['CustomerID'][i]
                    sortname = newenrolls['Person.LastName'][i] + ", " + newenrolls['Person.FirstName'][i]
                    emailaddr = newenrolls['Person.Email'][i]
                    if configs['Debug'] == "True":
                        print(newusername + " " + str(sis_user_id) + " " + emailaddr)
                    user = account.create_user(
                        user={
                            'name': newusername,
                            'short_name': newusername,
                            'sortable_name': sortname
                        },
                        pseudonym={
                            'unique_id': emailaddr.lower(),
                            'force_self_registration': True,
                            'sis_user_id': sis_user_id
                        }
                    )
                    msgbody = msgbody + 'Added new account ' + emailaddr + ' for ' + newusername + '\n'
                    if configs['NewUserCourse'] != '':
                        logging.info('Enrolling new user into intro student Canvas course')
                        if configs['Debug'] == "True":
                            dmsgbody = dmsgbody + 'Enrolling ' + newenrolls['Person.Email'][i] + ' into intro student Canvas course\n'
                        coursetoenroll = configs['NewUserCourse']
                        course = canvas.get_course(coursetoenroll,'sis_course_id')
                        enrollment = course.enroll_user(user,"StudentEnrollment",
                                                        enrollment = {
                                                            "sis_course_id": coursetoenroll,
                                                            "notify": True,
                                                            "enrollment_state": "active"
                                                            }
                                                        )
                        msgbody = msgbody + 'Enrolled ' + emailaddr + ' for ' + newusername + ' in the Intro to Canvas course\n'
                        dmsgbody = dmsgbody + 'Enrolled ' + emailaddr + ' for ' + newusername + ' in the Intro to Canvas course\n'
                    logging.info("Looking if we have sent intro letter to person...")
                    senttheletter = SentIntroLetters[SentIntroLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                    if senttheletter.empty:
                        logging.info("Going to send intro letter....")
                        emailintroletter()
                    enrollstudent()
        else:
            logging.info('Found course in Skip List. Course Code-> ' + newenrolls['ScheduledEvent.EventCd'][i])
            if configs['Debug'] == "True":
                dmsgbody = dmsgbody + 'Skipping enrollment for ' + newenrolls['Person.Email'][i] + ', found course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' in the skip list.\n'
            skippedbody = skippedbody + 'Skipping enrollment for ' + newenrolls['Person.Email'][i] + ', found course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' in the skip list.\n'
    # Send event email to interested admins on new enrolls or drops
    s = smtplib.SMTP(configs['SMTPServerAddress'])
    if msgbody == '':
        if skippedbody == '':
            msgbody = 'No new enrollments or drops for this iteration of ASAP-Canvas script\n\nSad Mickey\n'
            lastrunplace.to_csv(lastrunplacefilename)
            dmsgbody = dmsgbody + 'Wrote previous last record back to file'
        else:
            logging.info('Writing last record to file')
            lastrec = newenrolls.tail(1)
            lastrec.to_csv(lastrunplacefilename)
            msgbody = 'No new enrollments or drops for this iteration of ASAP-Canvas script\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n\nSad Mickey\n'
    else:
        logging.info('Writing last record to file')
        lastrec = newenrolls.tail(1)
        lastrec.to_csv(lastrunplacefilename)
        if skippedbody == '':
            msgbody = msgbody + '\n\nHappy Mickey\n'
        else:
            msgbody = msgbody + '\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n\nHappy Mickey\n'
            dmsgbody = dmsgbody + '\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n'
        dmsgbody = dmsgbody + 'wrote NEW last record to file'
    msg.set_content(msgbody)
    s.send_message(msg)
if configs['Debug'] == "True":
    print("All done!")
    dmsg.set_content(dmsgbody)
    s.send_message(dmsg)
