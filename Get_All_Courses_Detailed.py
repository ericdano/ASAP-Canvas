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
# Now we have the data, lets find the unique sub-accounts and get their names
subaccount_df = df1.account_id.unique()
column_names = ["account_id","subaccount_name"]
df2 = pd.DataFrame(columns = column_names)
for subaccount in subaccount_df:
  try:
    temp_account = canvas.get_account(subaccount)
    df2 = df2.append({'account_id':temp_account.id,'subaccount_name':temp_account.name},ignore_index=True)
  except CanvasException as e:
    print('Error ->',subaccount)
# Get the Term Names
column_names = ["enrollment_term_id","sis_term_id","enrollment_name"]
df3 = pd.DataFrame(columns = column_names)
try:
  terms = account.get_enrollment_terms()
  for term in terms:
    df3 = df3.append({'enrollment_term_id':term.id,'sis_term_id':term.sis_term_id,'enrollment_name':term.name},ignore_index=True)
except CanvasException as e:
  print('Error ->Cant get account.get_enrollment_terms')
print(df1)
print(df2)
print(df3)

#df_final = df1
result = pd.merge(df1,df2[['account_id','subaccount_name']],on='account_id')
print(result)
result2 = pd.merge(result,df3[['enrollment_term_id','enrollment_name']],on='enrollment_term_id')
print(result2)
#now the slow part, 
for index, row in result2.iterrows():
  lookupcourse = canvas.get_course(row["course_id"])
  try:
    users = lookupcourse.get_users(enrollment_type=['teacher'])
    teacher = ''
    for user in users:
      if not teacher:
        teacher = user.name
      else:
        teacher = teacher + ' ' + user.name
  except CanvasException as e:
    if str(e) == "Not Found":
      teacher = 'No Teacher in Class'
  print('Found teacher->',teacher,' adding to dataframe')
  result2.at[index,'teacher'] = teacher  
print(result2)
result2.to_csv('Testoutput.csv')