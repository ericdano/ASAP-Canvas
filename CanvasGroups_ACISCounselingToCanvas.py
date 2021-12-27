import pandas as pd
import os, sys, pyodbc, shlex, subprocess, json
from pathlib import Path
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

confighome = Path.home() / ".Acalanes" / "Acalanes.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging
#-----Canvas Info
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']


#Set up Counselors to pull from Aeries
counselors = [ ('acis','feinberg','sfeinberg@auhsdschools.org',10831)]

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=SATURN;'
                      'Database=DST21000AUHSD;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
students = pd.read_sql_query('SELECT ALTSCH.ALTSC, STU.LN, STU.SEM, STU.GR, STU.CU, TCH.EM FROM STU INNER JOIN TCH ON STU.SC = TCH.SC AND STU.CU = TCH.TN INNER JOIN ALTSCH ON STU.SC = ALTSCH.SCID WHERE (STU.SC = 6) AND STU.DEL = 0 AND STU.TG = \'\' AND STU.CU > 0 ORDER BY ALTSCH.ALTSC, STU.CU, STU.LN',conn)
students.drop(students.columns.difference(['SEM']),axis=1,inplace=True)
students = students.rename(columns={'SEM':'login_id'})
canvas = Canvas(Canvas_API_URL,Canvas_API_KEY)
account = canvas.get_account(1)
group = canvas.get_group(10831,include=['users'])
df = pd.DataFrame(group.users,columns=['id','name','login_id'])
print('Students from Aeries')
print(students)
print('Students in Canvas Group')
print(df)
print('Diff')
deletefromgroup = pd.DataFrame(set(df.login_id).symmetric_difference(students.login_id))
deletefromgroup.columns = ['login_id']
#People NOT in the Aeries data
notinaeries = pd.DataFrame(set(students.login_id).symmetric_difference(df.login_id))
notinaeries.columns = ['login_id']
#Delete Students from Canvas Group
for byebye in deletefromgroup:
  user = canvas.get_user(byebye.login_id,'sis_login_id')

# Add user to Canvas Group

#for index, student in students.iterrows():
#    user = canvas.get_user(student["SEM"],'sis_login_id')
#    m = group.create_membership(user.id)
#    print('Created user in group')
#    print(user)
