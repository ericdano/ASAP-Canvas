
from canvasapi import Canvas
import pandas as pd
from pathlib import Path
import requests, json, logging, smtplib, datetime, sys

# Script to take ALL the students from one course
# and enroll them into another
# For a Transition ELL class we have

course_number = sys.argv[1]
new_course_number = sys.argv[2]
home = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
confighome = Path.home() / ".ASAPCanvas" / "ASAPCanvas.json"
with open(confighome) as f:
  configs = json.load(f)
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
column_names = ["student_sis_id","user_id"]
df = pd.DataFrame(columns = column_names)
#Connect to Canvvas
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
print(course_number)
course = canvas.get_course(course_number,use_sis_id=True)
users = course.get_users(
                enrollment_type=['student']
                )
#Get Users for a course_number
print(new_course_number)
for user in users:
  print(user)
  df = df.append({'student_sis_id':user.sis_user_id,
                'user_id':user.id}, ignore_index=True)
print('Printing Pandas Dataframe')
for index, row in df.iterrows():
    print(row["course_sis_id"],",",row["student_sis_id"],",",row["user_id"])

#    enrollment = course.enroll_user(user,"StudentEnrollment",
#                                        enrollment = {
#                                                    "sis_course_id": coursetoenroll,
#                                                    "notify": True,
#                                                    "enrollment_state": "active"
#                                                    }
#                                                )
#for index, row in df.iterrows():
#  print("Updating",row["id"],row["NewShortName"],row["New name"])
#  coursecode = row["NewShortName"]
#  newname = row["New name"]
#  cid = row["id"]
#  print("to ->",coursecode,newname)
#  course = canvas.get_course(cid)
#  course.update(course={'name': newname})
#  course.update(course={'course_code': coursecode})