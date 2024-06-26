import pandas as pd
import requests, json, logging, smtplib, datetime, gam, arrow, os
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from pathlib import Path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from logging.handlers import SysLogHandler

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
# .1 - 2021 -> Added logic to deal with ASAP accounts when they change the email address but the customer ID is the same

#load configs
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
if configs['logserveraddress'] is None:
    logfilename = Path.home() / ".ASAPCanvas" / configs['logfilename']
    thelogger = logging.getLogger('MyLogger')
    thelogger.basicConfig(filename=str(logfilename), level=thelogger.info)
else:
    thelogger = logging.getLogger('MyLogger')
    thelogger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = (configs['logserveraddress'],514))
    thelogger.addHandler(handler)

skippedcoursescsvfilename = Path.home() / ".ASAPCanvas" / configs['SkippedCoursesCSV']
lastrunplacefilename = Path.home() / ".ASAPCanvas" / configs['ASAPlastposfile']
thelogger.info('ASAP_Enrollment_Into_Canvas->Loaded config file and logfile started')
# Get Courses to Skip in Canvas from Google Sheet
gam.initializeLogging()
thelogger.info('ASAP_Enrollment_Into_Canvas->Getting Google Sheet and converting to CSV')
rc2 = gam.CallGAMCommand(['gam','user', 'edannewitz@auhsdschools.org','get','drivefile','id','192q_ghNXZVwJN7oUNlByXRaYZPIOyeMgU-Q5ohrDPrw','format','csv','targetfolder','e:\PythonTemp','targetname','AESkipList.csv','overwrite','true'])
if rc2 != 0:
    thelogger.critical('ASAP_Enrollment_Into_Canvas->GAM Error getting Google sheet')

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
totalnewstudents = 0 # Variable to count new students added to Canvas
totalenrollments = 0 # Variable to count new enrollments
totalreturningstudents = 0

if configs['SendIntroLetters'] == "True":
    thelogger.info('ASAP_Enrollment_Into_Canvas->Reading Previous Sent Intro Letters file')
    SentIntroLetters = pd.read_csv(Path(configs['IntroLetterPath']+configs['SentIntroLettersCSV']))
if configs['SendCOVIDLetters'] == "True":
    thelogger.info('ASAP_Enrollment_Into_Canvas->Reading Previous Sent COVID Letters file')
    SentCOVIDLetters = pd.read_csv(Path(configs['COVIDLetterPath']+configs['SentCOVIDLettersCSV']))
#
#
def Set_globals():
    global msgbody, skippedbody, dmsgbody
    msgbody = ''
    skippedbody = ''
    dmsgbody = ''
def PanicStop(panicmsgstr):
    global msgbody, skippedbody, dmsgbody
    # This gets called when we get an error we excepted for
    thelogger.error('ASAP_Enrollment_Into_Canvas->Canvas error ' + panicmsgstr + ' Stopping imports. ')
    print('Canvas error ' + panicmsgstr + ' Stopping imports.')
    s = smtplib.SMTP(configs['SMTPServerAddress'])
    msgbody += 'Panic!! Stopping imports on error ' + panicmsgstr +' \n\nPanic!!!\n'
    dmsgbody += 'Panic!! Stopping imports on error ' + panicmsgstr +' \n\nPanic!!!\n'
    msg.set_content(msgbody)
    s.send_message(msg)
    raise
    exit()
"""
Funcction to email COVID vaccine status
Looks for a CVS file of emails previously sent out to not send out the same letter again
"""
def emailCOVIDletter(lettertoemail):
    global SentCOVIDLetters, msgbody, dmsgbody
    thelogger.info('ASAP_Enrollment_Into_Canvas->Prepping to send COVID letter from AE')
    IntroLetterRoot = MIMEMultipart('related')
    IntroLetterRoot['Subject'] = 'Voluntary Vaccination Verification'
    IntroLetterRoot['From'] = configs['SMTPAddressFrom']
    IntroLetterRoot['To'] = lettertoemail
    IntroLetterRoot.preamble = 'This is a multi-part message in MIME format.'
    IntroLetterAlt = MIMEMultipart('alternative')
    IntroLetterRoot.attach(IntroLetterAlt)
    IntroLetterText = MIMEText('This is the alternative plain text message.')
    IntroLetterAlt.attach(IntroLetterText)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Reading Previous Sent COVID Letters file')
    messagepath = Path(configs['COVIDLetterPath']+configs['COVIDLetterFile'])
    introfp1 = open(messagepath,'r')
    IntroLetterText = MIMEText(introfp1.read(),'html')
    IntroLetterAlt.attach(IntroLetterText)
    introfp1.close()
    smtpintroletter = smtplib.SMTP()
    smtpintroletter.connect(configs['SMTPServerAddress'])
    smtpintroletter.sendmail(configs['SMTPAddressFrom'], lettertoemail, IntroLetterRoot.as_string())
    smtpintroletter.quit()
    """
    Pandas 1.5 depreciated pd.append
    SentCOVIDLetters = SentCOVIDLetters.append({'Email': lettertoemail},ignore_index=True)
    """
    tempDF = pd.DataFrame([{'Email': lettertoemail}])
    SentCOVIDLetters = pd.concat([SentCOVIDLetters,tempDF],axis=0, ignore_index=True)
    SentCOVIDLetters.to_csv(Path(configs['COVIDLetterPath']+configs['SentCOVIDLettersCSV']), index=False)
    thelogger.info('ASAP_Enrollment_Into_Canvas->COVID letter sent to ' + lettertoemail)
    if configs['Debug'] == "True":
        dmsgbody += 'Added ' + lettertoemail + 'to sent COVID CSV file.\n'
        dmsgbody += 'Sent COVID letter to ' + lettertoemail + '\n'
    msgbody += 'Sent COVID letter to ' + lettertoemail + '\n'

#Funcction to email intro letter out to new Students
#Looks for a CVS file of emails previously sent out to not send out the same letter again
def emailintroletter(lettertoemail):
    global SentIntroLetters, msgbody, dmsgbody
    thelogger.info('ASAP_Enrollment_Into_Canvas->Prepping to send intro letter from AE')
    IntroLetterRoot = MIMEMultipart('related')
    IntroLetterRoot['Subject'] = configs['IntroLetterSubject']
    IntroLetterRoot['From'] = configs['SMTPAddressFrom']
    IntroLetterRoot['To'] = lettertoemail
    IntroLetterRoot.preamble = 'This is a multi-part message in MIME format.'
    IntroLetterAlt = MIMEMultipart('alternative')
    IntroLetterRoot.attach(IntroLetterAlt)
    IntroLetterText = MIMEText('This is the alternative plain text message.')
    IntroLetterAlt.attach(IntroLetterText)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Reading Previous Sent Intro Letters file')
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
    smtpintroletter.sendmail(configs['SMTPAddressFrom'], lettertoemail, IntroLetterRoot.as_string())
    smtpintroletter.quit()
    """
    Pandas 1.5 depreciated pd.append
    SentCOVIDLetters = SentCOVIDLetters.append({'Email': lettertoemail},ignore_index=True)
    """
    tempDF = pd.DataFrame([{'Email': lettertoemail}])
    SentIntroLetters = pd.concat([SentIntroLetters,tempDF],axis=0, ignore_index=True)
    SentIntroLetters.to_csv(Path(configs['IntroLetterPath']+configs['SentIntroLettersCSV']), index=False)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Intro letter sent to ' + lettertoemail)
    if configs['Debug'] == "True":
        dmsgbody += 'Added ' + lettertoemail + 'to sent CSV file.\n'
        dmsgbody += 'Sent intro letter to ' + lettertoemail + '\n'
    msgbody += 'Sent intro letter to ' + lettertoemail + '\n'

#Function to enroll or unenroll a student
def enrollstudent(coursecodetoenroll,coursetoenrollname,enrollmentstatuscd,studentemailaddress):
    #get passed course, coursename, enrollmentstatus,and studentemailaddress
    global msgbody, dmsgbody
    # the globals are for the end email messages
    if configs['Debug'] == "True":
        thelogger.info('ASAP_Enrollment_Into_Canvas->Looking at ' + studentemailaddress + ' enrollment status for ID ' +  coursecodetoenroll)
        dmsgbody += 'Looking at ' + studentemailaddress + ' enrollment status for ID ' +  coursecodetoenroll + '\n'
    thelogger.info('ASAP_Enrollment_Into_Canvas->Found user - look at enrollments')
    try:
        course = canvas.get_course(coursecodetoenroll,'sis_course_id')
        thelogger.info('ASAP_Enrollment_Into_Canvas->EnrollmentStatusCd field is ' + enrollmentstatuscd)
        if configs['Debug'] == 'True':
            dmsgbody += 'Field is ' + enrollmentstatuscd + '\n'
        if enrollmentstatuscd == "DROPPED":
            thelogger.info('ASAP_Enrollment_Into_Canvas->Dropping ' + studentemailaddress)
            if configs['Debug'] == 'True':
                dmsgbody += 'Dropping ' + studentemailaddress +'\n'
            enrollments = course.get_enrollments(type='StudentEnrollment')
            lookfordelete = False
            for stu in enrollments:
                # You have to loop through all the enrollments for the class and then find the student id in the enrollment then tell it to delete it.
                if stu.user_id == user.id:
                    lookfordelete = True
                    stu.deactivate(task="delete")
                    thelogger.info('ASAP_Enrollment_Into_Canvas->Deleted student from ' + coursetoenrollname)
                    msgbody += 'Dropped ' + studentemailaddress + ' from ' + coursetoenrollname +  ' (' + coursecodetoenroll + ') \n'
                    if configs['Debug'] == "True":
                        dmsgbody += 'Dropped ' + studentemailaddress + ' from ' + coursetoenrollname +  ' (' + coursecodetoenroll + ') \n'
            if lookfordelete == False:
                msgbody += 'Tried to Drop ' + studentemailaddress + ' from ' + coursetoenrollname +  ' (' + coursecodetoenroll + ') but they had not made it into Canvas yet. (DROPPED class before last run) \n'
                thelogger.error('ASAP_Enrollment_Into_Canvas->Got a drop field from ASAP for ' + studentemailaddress + ' but they are not in Canvas')
        else:
            # Other ASAP things could be PEND or ENROLLED.
            enrollment = course.enroll_user(user,"StudentEnrollment",
                                            enrollment = {
                                                "sis_course_id": coursecodetoenroll,
                                                "notify": True,
                                                "enrollment_state": "active"
                                                }
                                            )
            thelogger.info('ASAP_Enrollment_Into_Canvas->Enrolled ' + studentemailaddress + ' in ' + coursetoenrollname)
            msgbody += 'Enrolled ' + studentemailaddress + ' in ' + coursetoenrollname + ' (' + coursecodetoenroll + ') \n'
            if configs['Debug'] == "True":
                dmsgbody += 'Enrolled ' + studentemailaddress + ' in ' + coursetoenrollname + ' (' + coursecodetoenroll + ') \n'
    except CanvasException as ec:
                #It all starts with figuring out if the user is in Canvas and enroll in tutorial course
        thelogger.critical('ASAP_Enrollment_Into_Canvas->Canvas error ' + str(ec) + ' Course code ' + coursecodetoenroll + ' - ' + coursetoenrollname + ' is not in Canvas. Stopping imports. ')
        print('Canvas error ' + str(ec) + ' Course code ' + coursecodetoenroll + ' - ' + coursetoenrollname + ' is not in Canvas. Stopping imports.')
        s = smtplib.SMTP(configs['SMTPServerAddress'])
        msgbody += 'Course code ' + coursecodetoenroll + ' - ' + coursetoenrollname + ' is not in Canvas. Stopping imports.\n\n\nPanic!!!\n'
        dmsgbody += 'Course code ' + coursecodetoenroll + ' - ' + coursetoenrollname + ' is not in Canvas. Stopping imports.\n\n\nPanic!!!\n'
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
thelogger.info('ASAP_Enrollment_Into_Canvas->Getting ASAP Key')
Set_globals()
r = requests.get(url,headers = headers)
if r.status_code == 404:
    thelogger.info('ASAP_Enrollment_Into_Canvas->Failed to get ASAP Key')
    if configs['Debug'] == "True":
        print('Failed to connect to ASAP')
        thelogger.info('ASAP_Enrollment_Into_Canvas->Failed to get ASAP Key')
        dmsgbody += 'Failed to get ASAP Key....\n'
elif r.status_code == 200:
    thelogger.info('ASAP_Enrollment_Into_Canvas->Got ASAP Key')
    if configs['Debug'] == "True":
        dmsgbody += 'Got ASAP Key....\n'
    accesstoken = r.json()
    thelogger.info('ASAP_Enrollment_Into_Canvas->Key is ' + accesstoken)
    
    '''
    Redid the API URL for dates to just get stuff from a week ago and a week from now. I forget to advance the URL dates sometimes in the .JSON file
    '''
    CurrentDateStr = arrow.now()
    AWeekAgo = CurrentDateStr.shift(weeks=-1).format('YYYY-MM-DD')
    AWeekFromNow = CurrentDateStr.shift(weeks=+16).format('YYYY-MM-DD')
    url2 = "https://api.asapconnected.com/api/Enrollments?includeAttendance=false&classStartDate=" + AWeekAgo + "&classEndDate=" + AWeekFromNow + "&enrollmentStartDate=" + AWeekAgo + "&enrollmentEndDate=" + AWeekFromNow + "&includeCourseInfo=true"
    #url2 = configs['ASAPapiurl']
    header = {'asap_accesstoken' : accesstoken}
    dmsgbody += 'Using ' + url2 + ' as ASAP String\n'
    thelogger.info('ASAP_Enrollment_Into_Canvas->Getting data from ASAP')
    if configs['Debug'] == "True":
        dmsgbody += 'Getting JSON from ASAP....\n'
    r2 = requests.get(url2,headers = header)
    results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop(columns=['Students'])
    #results = pd.concat([pd.json_normalize(r2.json()), pd.json_normalize(r2.json(),record_path="Students", max_level=2)], axis=1).drop(columns='Students')
    # was drop('Students',1)
    #Drop columns we don't need
    results.drop(results.columns.difference(['CreatedDate',
                                            'EventEnrollmentID',
                                            'ScheduledEvent.Course.CourseName',
                                            'ScheduledEvent.Course.IsOnline',
                                            'EnrollmentStatusCd',
                                            'ScheduledEvent.EventCd',
                                            'StudentID',
                                            'CustomerID',
                                            'Person.Email',
                                            'Person.FirstName',
                                            'Person.LastName']),axis=1,inplace=True)
    '''
    For Canvas, we only care about a few columns that ASAP gives us (hence the mass dropping of columns above)
    EventEnrollmentID is basically a sequence number. This is what we are going to use to find out where we are in the transcation stream
    EnrollmentStatusCd tells us what to do. ENROLLED and PEND mean put them in a class, DROPPED means remove them
    ScheduledEvent.EventCd is the SIS ID for the Course
    Person.Email is both the login and the Email
    Person.FirstName is their FirstName
    Person.LastName is their LastName
    Load last record processed
    SkipList is a Google Sheet that is downloaded and then used to see if a class is offered but there is no Canvas for
    '''
    #results.to_csv('e:\PythonTemp\Messed.csv')
    thelogger.info('ASAP_Enrollment_Into_Canvas->Connecting to Canvas')
    if configs['Debug'] == "True":
        dmsgbody += 'Connecting to Canvas....\n'
    canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
    account = canvas.get_account(1)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Getting last record we looked at')
    if configs['Debug'] == "True":
        dmsgbody += 'Loading last record processed....\n'
    #Load Skipped Classes
    SkippedCourses = pd.read_csv('E:\PythonTemp\AESkipList.csv')
    os.remove('e:\PythonTemp\AESkipList.csv')
    thelogger.info('ASAP_Enrollment_Into_Canvas->Loading Skipped List CSV')
    print(SkippedCourses)
    if configs['Debug'] == "True":
        dmsgbody += 'Loading CSV of Classes to skip enrolling into Canvas....\n'
    #load starting record position
    print('Results')
    print(results)
    lastrunplace = pd.read_csv(lastrunplacefilename)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Last place was ' + str(lastrunplace))
    newenrolls = results[results['EventEnrollmentID'] > lastrunplace['EventEnrollmentID'][0]]
    thelogger.info('ASAP_Enrollment_Into_Canvas->Looking for enrollments')
    if configs['Debug'] == "True":
        dmsgbody += "Looking for enrollments....\n"
    for i in newenrolls.index:
        #Look for classes we don't do canvas for, and skip
        print(newenrolls['ScheduledEvent.EventCd'][i])
        thelogger.info('ASAP_Enrollment_Into_Canvas->Seeing if ' + newenrolls['ScheduledEvent.EventCd'][i] + ' is in skipped CSV')
        # This is where it looks if classes are in the skipped list CSV OR are you have enabled it to look for IsOnline from ASAP
        if not (newenrolls['ScheduledEvent.EventCd'][i] in SkippedCourses['CourseCode'].unique()) :
            # Check to make sure we have an email
            if (newenrolls['Person.Email'][i] == ''):
                thelogger.critical('ASAP_Enrollment_Into_Canvas->Email address field is empty')
                PanicStop('Email address is empty!!!')
            # Now look up the user by email
            try:
                user = canvas.get_user(newenrolls['Person.Email'][i],'sis_login_id')
                thelogger.info('ASAP_Enrollment_Into_Canvas->' + newenrolls['Person.Email'][i] + ' is in Canvas')
                if configs['Debug'] == "True":
                    dmsgbody += newenrolls['Person.Email'][i] + ' is in Canvas\n'
                # Check to see if we are sending welcome emails to this semester's students. Purely optional
                if configs['SendIntroLetters'] == "True":
                    thelogger.info('ASAP_Enrollment_Into_Canvas->Looking if we have sent intro letter to person...')
                    senttheletter = SentIntroLetters[SentIntroLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                    if senttheletter.empty:
                        thelogger.info('ASAP_Enrollment_Into_Canvas->Going to send intro letter....')
                        #pass email to send optional enrollment welcome letter
                        emailintroletter(newenrolls['Person.Email'][i])
                # Check to see if we are sending out COVID vaccinated status emails
                if configs['SendCOVIDLetters'] == "True":
                    # Check to see if we are sending welcome emails to this semester's students. Purely optional
                    thelogger.info('ASAP_Enrollment_Into_Canvas->Looking if we have sent COVID letter to person...')
                    senttheCletter = SentCOVIDLetters[SentCOVIDLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                    if senttheCletter.empty:
                        thelogger.info('ASAP_Enrollment_Into_Canvas->Going to send COVID letter....')
                        #pass email to send optional enrollment welcome letter
                        emailCOVIDletter(newenrolls['Person.Email'][i])
                #enrollstudent(newenrolls['ScheduledEvent.EventCd'][i],
                #    newenrolls['ScheduledEvent.Course.CourseName'][i],
                #    newenrolls['EnrollmentStatusCd'][i],
                #    newenrolls['Person.Email'][i])
                totalreturningstudents += 1
            except CanvasException as e:
            #Didn't find email address
            #Now see if the sis_user_id is in there - New code as of 12-2021
                if str(e) == "Not Found":
                    if configs['Debug'] == "True":
                        print('Email not found, checking for SIS_ID ' + newenrolls['Person.Email'][i])
                        dmsgbody += 'Email not found, checking for SIS_ID ' + str(newenrolls['CustomerID'][i])+ ' that has different email than ' + newenrolls['Person.Email'][i] + ' in Canvas\n'
                    thelogger.info('ASAP_Enrollment_Into_Canvas->User not found with sis_login_id, looking if CustomerID and sis_user_id are the same.')
                    newusername = newenrolls['Person.FirstName'][i] + " " + newenrolls['Person.LastName'][i]
                    sis_user_id = newenrolls['CustomerID'][i]
                    sortname = newenrolls['Person.LastName'][i] + ", " + newenrolls['Person.FirstName'][i]
                    emailaddr = newenrolls['Person.Email'][i]
                    #try and see if sis_user_id is in Canvas
                    try: 
                        user = canvas.get_user(newenrolls['CustomerID'][i],'sis_user_id')
                        # We made it here, no errors thrown by Canvas. So we found a SIS ID in Canvas that matches CustomerID
                        # User has changed their email, take existing email, add it as a login, and make the this new email the sis_login_id
                        #
                        olduseremail = user.login_id #get the current email address
                        old_profile = user.get_profile()
                        old_primary_email = old_profile['primary_email']
                        old_login_id = old_profile['login_id']
                        # Now lets make sure that we don't have a login already for this person, and that they are now
                        # using the LOGIN as the default
                        # Edit user and make new email the unique_id
                        try:
                            user.edit(
                                pseudonym={
                                'unique_id': emailaddr.lower()                                    
                                }
                           )
                        except CanvasException as ff1:
                            thelogger.critical('ASAP_Enrollment_Into_Canvas->Error editing user email address')
                            PanicStop(str(ff1) + ' when editing user email address') 
                        userlogins = user.get_user_logins()
                        foundanotherlogin = False
                        for login in userlogins:
                            if login.unique_id == olduseremail:
                                foundanotherlogin=True
                                print('Found ASAPs current default email '+ emailaddr.lower() + 'as a login')
                                thelogger.info('ASAP_Enrollment_Into_Canvas->Found ASAPs current default email ' + emailaddr.lower() + 'as a login')
                        thelogger.info('ASAP_Enrollment_Into_Canvas->Seems that we have someone ' + str(newenrolls['CustomerID'][i]) + ' who changed their ASAP email, so lets change it in Canvas and add the old one as a Login for them\n')
                        if configs['Debug'] == "True":
                            dmsgbody += 'CustomerID ' + str(newenrolls['CustomerID'][i]) + ' is associated with a different email\n'
                            dmsgbody += 'Changing ' + olduseremail + ' to ' + emailaddr 

                        try:
                            account.create_user_login(user={'id':user.id},
                                                    login={'unique_id':olduseremail.lower()}
                                                    )
                        # Create an additional LOGIN for the user using the OLD email address
                            thelogger.info('ASAP_Enrollment_Into_Canvas->Created additional login for user id=' + str(user.id))

                        except CanvasException as e11:
                            thelogger.critical('ASAP_Enrollment_Into_Canvas->Error when creating additional login for user')
                            PanicStop(str(e11) + ' when created additional login for user')
                    except CanvasException as e2:
                        if str(e2) == "Not Found":
                            #Ok, CustomerID is not the sis_user_id, so create the user
                            if configs['Debug'] == "True":
                                print('SIS_ID Not found in Canvas, creating new user ' + newusername + " " + str(sis_user_id) + " " + emailaddr)
                                dmsgbody += 'SIS_ID not in Canvas, creating new Canvas user ' + newusername + " " + str(sis_user_id) + " " + emailaddr + '\n'
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
                            totalnewstudents += 1
                            msgbody = msgbody + 'Added new account ' + emailaddr + ' for ' + newusername + '\n'
                            thelogger.info('ASAP_Enrollment_Into_Canvas->Created new account for '+ emailaddr + ' for ' + newusername)
                            if configs['NewUserCourse'] != '':
                                thelogger.info('ASAP_Enrollment_Into_Canvas->Enrolling new user into intro student Canvas course')
                            if configs['Debug'] == "True":
                                dmsgbody += 'Enrolling ' + newenrolls['Person.Email'][i] + ' into intro student Canvas course\n'
                            coursetoenroll = configs['NewUserCourse']
                            course = canvas.get_course(coursetoenroll,'sis_course_id')
                            enrollment = course.enroll_user(user,"StudentEnrollment",
                                                            enrollment = {
                                                                "sis_course_id": coursetoenroll,
                                                                "notify": True,
                                                                "enrollment_state": "active"
                                                                }
                                                            )
                            msgbody += 'Enrolled ' + emailaddr + ' for ' + newusername + ' in the Intro to Canvas course\n'
                            dmsgbody += 'Enrolled ' + emailaddr + ' for ' + newusername + ' in the Intro to Canvas course\n'
                # User has been created or login moved around, proceed to enroll student into class
                # Look in config to see that you want to send an intro letter to people this session
                if configs['SendIntroLetters'] == "True":
                    thelogger.info('ASAP_Enrollment_Into_Canvas->Looking if we have sent intro letter to person...')
                    senttheletter = SentIntroLetters[SentIntroLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                    if senttheletter.empty:
                        thelogger.info('ASAP_Enrollment_Into_Canvas->Going to send intro letter....')
                        emailintroletter(newenrolls['Person.Email'][i])
                if configs['SendCOVIDLetters'] == "True":
                # Check to see if we are sending welcome emails to this semester's students. Purely optional
                    thelogger.info('ASAP_Enrollment_Into_Canvas->Looking if we have sent COVID letter to person...')
                    senttheCletter = SentCOVIDLetters[SentCOVIDLetters['Email'].str.contains(newenrolls['Person.Email'][i])]
                    if senttheCletter.empty:
                        thelogger.info('ASAP_Enrollment_Into_Canvas->Going to send COVID letter....')
                        #pass email to send optional enrollment welcome letter
                        emailCOVIDletter(newenrolls['Person.Email'][i])
            #Done sending letters
            #Finally ENROLL the student into the Canvas Class
            totalenrollments += 1
            enrollstudent(newenrolls['ScheduledEvent.EventCd'][i],
                        newenrolls['ScheduledEvent.Course.CourseName'][i],
                        newenrolls['EnrollmentStatusCd'][i],
                        newenrolls['Person.Email'][i])
        else:
            thelogger.info('ASAP_Enrollment_Into_Canvas->Found course in Skip List. Course Code-> ' + newenrolls['ScheduledEvent.EventCd'][i])
            if configs['Debug'] == "True":
                dmsgbody += 'Skipping enrollment for ' + newenrolls['Person.Email'][i] + ', found course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' in the skip list.\n'
            skippedbody += 'Skipping enrollment for ' + newenrolls['Person.Email'][i] + ', found course code ' + newenrolls['ScheduledEvent.EventCd'][i] + ' ' + newenrolls['ScheduledEvent.Course.CourseName'][i] + ' in the skip list.\n'
    # Send event email to interested admins on new enrolls or drops
    s = smtplib.SMTP(configs['SMTPServerAddress'])
    if msgbody == '':
        if skippedbody == '':
            msgbody = 'No new enrollments or drops for this iteration of ASAP-Canvas script\n\nSad Mickey\n'
            thelogger.info('ASAP_Enrollment_Into_Canvas->No new enrollments this script run.....sad mickey')
            lastrunplace.to_csv(lastrunplacefilename)
            dmsgbody = dmsgbody + 'Wrote previous last record back to file'
            thelogger.info('ASAP_Enrollment_Into_Canvas->Writing last record to file')
        else:
            thelogger.info('ASAP_Enrollment_Into_Canvas->Writing last record to file')
            lastrec = newenrolls.tail(1)
            lastrec.to_csv(lastrunplacefilename)
            msgbody = 'No new enrollments or drops for this iteration of ASAP-Canvas script\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n\nSad Mickey\n'
    else:
        thelogger.info('ASAP_Enrollment_Into_Canvas->Writing last record to file')
        lastrec = newenrolls.tail(1)
        lastrec.to_csv(lastrunplacefilename)
        msgbody += 'Added ' + str(totalenrollments) + ' new Guests to classes.\n'
        msgbody += 'Added ' + str(totalnewstudents) + ' new Guests to Canvas.\n'
        msgbody += 'Had ' + str(totalreturningstudents) + ' Guests return to take classes.'
        if skippedbody == '':
            msgbody += '\n\nHappy Mickey\n'
        else:
            msgbody += '\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n\nHappy Mickey\n'
            dmsgbody += '\n\nSkipped enrolling these as course codes were in skip list:\n\n' + skippedbody + '\n'
        dmsgbody += 'wrote NEW last record to file'
    msg.set_content(msgbody)
    s.send_message(msg)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Sent Status emails')
if configs['Debug'] == "True":
    print("All done!")
    dmsg.set_content(dmsgbody)
    s.send_message(dmsg)
    thelogger.info('ASAP_Enrollment_Into_Canvas->Sent Debug emails')