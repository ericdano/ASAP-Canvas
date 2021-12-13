import pandas as pd
import os, sys, pyodbc, shlex, subprocess, json
from pathlib import Path
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

confighome = Path.home() / ".Acalanes" / "Acalanes.json"
with open(confighome) as f:
  configs = json.load(f)
# Logging


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=SATURN;'
                      'Database=DST21000AUHSD;'
                      'Trusted_Connection=yes;')

#populate a table with counselor parts
counselors = [ ('ahs','todd','ctodd@auhsdschools.org',''),
                ('ahs','meadows','',''),
                ('ahs','schonauer','',''),
                ('ahs','martin','',''),
                ('chs','turner'),'','',
                ('chs','dhaliwal','',''),
                ('chs','ochoa','',''),
                ('chs','magno','',''),
                ('llhs','wright','',''),
                ('llhs','feinberg','sfeinberg@auhsdschools.org',10835),
                ('llhs','constantin','',''),
                ('llhs','bloodgood','',''),
                ('llhs','sabeh','',''),
                ('mhs','vasquez','',''),
                ('mhs','conners','',''),
                ('mhs','watson','',''),
                ('mhs','vasicek','','') ]

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=SATURN;'
                      'Database=DST21000AUHSD;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
students = pd.read_sql_query('SELECT ALTSCH.ALTSC, STU.LN, STU.SEM, STU.GR, STU.CU, TCH.EM FROM STU INNER JOIN TCH ON STU.SC = TCH.SC AND STU.CU = TCH.TN INNER JOIN ALTSCH ON STU.SC = ALTSCH.SCID WHERE (STU.SC < 5) AND STU.DEL = 0 AND STU.TG = \'\' AND STU.SP <> \'2\' AND STU.CU > 0 ORDER BY ALTSCH.ALTSC, STU.CU, STU.LN',conn)
#-----Canvas Info()
Canvas_API_URL = configs['CanvasAPIURL']
Canvas_API_KEY = configs['CanvasAPIKey']

canvas = Canvas(Canvas_API_URL,Canvas_API_KEY)
account = canvas.get_account(1)
group = canvas.get_group(10835,include=['users'])
print(students)
print(counselors[11])
print(counselors[11][3])
for index, student in students.iterrows():
    if student["EM"] == counselors[11][2]:
        user = canvas.get_user(student["SEM"],'sis_login_id')
        m = group.create_membership(user.id)
        print('Created user in group')
        print(user)