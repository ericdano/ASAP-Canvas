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