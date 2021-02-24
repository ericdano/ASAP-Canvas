import pandas as pd
import requests, json, logging, sys
from pathlib import Path

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
csvfilename = sys.argv[1]
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
elif r.status_code == 200:
    logging.info('Got ASAP Key')
    accesstoken = r.json()
    logging.info('Key is ' + accesstoken)
    url2 = configs['ASAPapiurl']
    header = {'asap_accesstoken' : accesstoken}
    logging.info('Getting data from ASAP')
    r2 = requests.get(url2,headers = header)
    #print(r2)
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

    print(results)
    results.to_csv(csvfilename)
