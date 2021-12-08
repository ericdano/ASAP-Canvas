import pandas as pd
import requests, json, logging, sys
from pathlib import Path
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
#Python program to grab classes from ASAP and dump them to csv
#load configs for Acalanes
confighome = Path.home() / ".Acalanes" / "Acalanes.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']
column_names = ["course_id","sis_course_id","Course_Name","account_id","enrollment_term_id","total_students","workflow_state","teacher"]
df1 = pd.DataFrame(columns = column_names)
canvas = Canvas(Canvas_API_URL, Canvas_API_KEY)
account = canvas.get_account(1)
courses = account.get_courses(include=['total_students',
                                        'workflow_state'])
#Put all the courses in a dataframe
for course in courses:
  df1 = df1.append({'course_id':course.id,
                    'sis_course_id':course.sis_course_id,
                    'Course_Name':course.name,
                    'account_id':course.account_id,
                    'enrollment_term_id':course.enrollment_term_id,
                    'total_students':course.total_students,
                    'workflow_state':course.workflow_state}, ignore_index=True)

print(df1)