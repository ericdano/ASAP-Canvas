# ASAP-Canvas
<h2>Introduction</h2>

ASAP Connected and Canvas LMS Scripts - Python Scripts for pulling and pushing data to both Systems and various Canvas Scripts

This project was started for <a href="https://www.acalanes.k12.ca.us/Domain/150">Acalanes Union High School District Adult Education</a>. In the summer of 2020, during COVID-19, the school district switched Learning Management Systems (LMS) to <a href="https://www.instructure.com/">Instructure Canvas</a>. The issue was that the state of California requires Adult Education to use <a href="https://app.asapconnected.com/">ASAP Connected</a> for it's enrollment and attendance for programs and Canvas and ASAP do not talk to each other.

After a roll out of about 1500 students using CSV files, I decided to dig in and figure out how to make it automated (cause, of course, I am lazy and don't want to keep pulling over things with CSV files).

Using Python, API calls, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and the great <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a> library for Python, this project was born. It calls ASAP Connected, grabs all the data it needs, figures out the last transaction you imported into Canvas, and then creates new students in Canvas (if needed) and enrolls them into a introduction class on Canvas, and the class they want to take.

<h2>Requirements</h2>

ASAP-Canvas uses Python 3.9.5, <a href="https://pandas.pydata.org/">Pandas for Python</a>, <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a>, and a few other Python libraries like requests (pip install requests
You will also need an API key generated from your Canvas instance, and an API key from ASAP Connected.

<h2>Installation and First Run</h2>
<p>You FIRST need to make sure you already have all the courses you are going to be pulling from ASAP Connected ALREADY setup in Canvas. This program does not create courses in Canvas. SIS ID for each class must match the course codes you use in ASAP. In the case of Acalanes Adult Education, we are using the ScheduledEvent.Eventcd field. The course code MUST match exactly in Canvas. So if the course is 022323, you need to have it be 022323 in Canvas. You cannot drop the leading zero. It is a string field, not a numeric field. If you are NOT conducting a course in Canvas, say a ESL or ELL test class that people are taking, then you need to add this course code to the "SkipCourses" array in the ASAPCanvas.json file.</p> 
You need <a href="https://www.python.org/downloads/">Python 3.8.5</a>
You need <a href="https://www.pypa.io/en/latest/">PIP installed</a>
You need the <a href="https://github.com/ucfopen/canvasapi">CanvasAPI library</a>. With Python installed, you can run "pip install canvasapi"
You need <a href="https://pandas.pydata.org/">Pandas for Python</A> installed.
You also need some sort of SMTP server to receive status messages from it (emails saying it added X number of students, etc, etc)
This python script should run on any computer. You probably want to set it up to run hourly? Daily? Your pick. This script is device agnostic and should work on Windows, Linux or macOS (developed and deployed on a Windows machine).
<br>
<p>You will also need to make a .ASAPCanvas directory in your home directory and copy ASAPCanvas.json to there. This is where the program looks for your API keys, etc, etc. You also need to create a lastrecordasap.csv file. This is a file that contains where you left off in the ASAP datastream. If you are running this for the FIRST TIME, I suggest running ASAP_Enrollments_to_CSV.py (run it and give it a filename you want to save to), and changing the classStartDate to whatever suits you. We are keying off and incremential serial number (I think?) field called EnrollmentStatusCd. You need to make a lastrecordasap.csv file that has atleast two lines in it, first one being the header of EnrollmentStatusCd, and the second a number where you want to start. It could be 0 if you want. I believe calling the ASAP API just gives you up to 60 days worth of information. Version .02 of the program will be a little smarter and also include the date in there so we don't have to grab so much from ASAP.</p>
Of note:
<UL>
<li><b>NewUserCourse</b> is a Canvas Introduction course we created for our students to give them a run down on what Canvas is and how to use it. Totally optional, and if you are not going to use it, then don't set it.
<li><b>SkipCourses</b> are courses we are not enrolling users into Canvas for. We offer some English language placement tests, and we do not put a student in Canvas when they are just enrolled in those classes. You can add a infinite list of skipped classes.
</ul>
<h2>Scripts</h2>
<UL>
  <li><b>ASAP_Classes_to_CSV.py</b> - This program needs a filename to run. So 'python ASAP_Classes_to_CSV.py output.csv' Generates a CSV of the current stuff out of ASAP Connected
  <li><b>ASAP_Enrollment_Into_Canvas.py</b> - This program reads a csv file of where to start, grabs data from ASAP Connected, and enrolls students into Canvas
  <li><b>Canvas_Course_Duplication.py</b> - This program copies a course from Canvas to a new course in Canvas. Reads a CSV file containing the SIS_ID of current course, SIS_ID of new course, and new course name. Will also put the course in the right subaccount based on the course you are copying from. And it will enroll the teacher of the copied course into the new course. It will ALSO put the course into a new Term. You need to set that IN THE PYTHON SCRIPT. Name needs to match whatever it is in Canvas. So if you are copying current course to a new term of 'Spring 2021', then set the Term to be 'Spring 2021'
  <li><b>Canvas Enroll Teacher In Course</b> - Bypasses you needing to wait for them to accept being the teacher in the class.
  <li><b>Canvas_Rename_Course_EndOfTerm</b> - Script to take whatever term (sis_id of term), and tack on an additional line to the title of classes. We used it for "archiving" older classes, so a class titled "Spanish 1b" that was in the Fall 2020 term, is now title "Fall 2020 - Spanish 1b".
</ul>
<h2>Support</h2>
<a href="https://drive.google.com/file/d/1-zm5MQK1nnfP65ZB_3_jmzaBJFkxkhV3/view?usp=sharing">Introduction video on how it works</a>.
Need a feature? Something not working? <a href=mailto:edannewitz@auhsdschools.org>Drop me a line.</a>
<h2>Version History</h2>
<ul>
<li>.096 - Verified that Python 3.9.5 runs everything ok. Adding more error checking to everything.
<li>.095 - Added a config variable to set if you want to send an intro letter or not for students enrolling for the first time this session. It will only send the email once as it keeps track of who it has emailed.
<li>.091 - Changed the ASAP API string to better catch drops and enrollments. Should be in this form
  https://api.asapconnected.com/api/Enrollments?includeAttendance=false&classStartDate=11-01-2020&classEndDate=04-01-2021&enrollmentStartDate=11-01-2020&enrollmentEndDate=04-01-2021
<li>.09 - Added a procedure to send out a "Welcome message" for people who are enrolling. It is sorta "Acalanes specific", but it is taking a html file (actually a letter that was done in Google Docs, and taking the html file and graphic and sending it out through the smtp server. It is also keeping track of whom it has sent out this "welcome" message to' If you do not want to use that, then comment out any references to emailintroletter() out in the python file.
<li>.07 - Added more error checking. Will now also include in the emails sent out if it skipped over classes in the skip classes list.
<li>.06 - Changed some of the error handling. Script will quit out and email when it encounters a class that is in ASAP but not in Canvas nor in the JSON config file as a skipped class. Restarting the script after fixing the error will not duplicate anything on the user end or Canvas end. (10/26/2020)
<li>.01 - Initial Release

