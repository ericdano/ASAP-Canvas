# ASAP-Canvas
<h2>Introduction</h2>

ASAP Connected and Canvas LMS Scripts - Python Scripts for pulling and pushing data to both Systems and various Canvas Scripts

This project was started for the <a href="https://acalanes.k12.ca.u/">Acalanes Union High School District Adult Education</a>. In the summer of 2020, during COVID-19, the school district switched Learning Management Systems (LMS) to <a href="https://www.instructure.com/">Instructure Canvas</a>. The issue was that the state of California requires Adult Education to use <a href="https://app.asapconnected.com/">ASAP Connected</a> for it's enrollment and attendance for programs and Canvas and ASAP do not talk to each other.

After a roll out of about 1500 students using CSV files, I decided to dig in and figure out how to make it automated (cause, of course, I am lazy and don't want to keep pulling over things with CSV files).

Using Python, API calls, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and the great <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a> library for Python, this project was born. It calls ASAP Connected, grabs all the data it needs, figures out the last transaction you imported into Canvas, and then creates new students in Canvas (if needed) and enrolls them into a introduction class on Canvas, and the class they want to take.

<h2>Requirements</h2>

ASAP-Canvas uses Python 3.8.5, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a>
You will also need an API key generated from your Canvas instance, and an API key from ASAP Connected.

<h2>Installation and First Run</h2>
You need <a href="https://www.python.org/downloads/">Python 3.8.5</a>
You need <a href="https://www.pypa.io/en/latest/">PIP installed</a>
You need the <a href="https://github.com/ucfopen/canvasapi">CanvasAPI library</a>. With Python installed, you can run "pip install canvasapi"
You need <a href="https://pandas.pydata.org/">Pandas for Python</A> installed.
You also need some sort of SMTP server to receive status messages from it (emails saying it added X number of students, etc, etc)
This python script should run on any computer. You probably want to set it up to run hourly? Daily? Your pick. This script was developed on Windows and Linux.

You will also need to make a .ASAPCanvas directory and put ASAPCanvas.json in there. This is where the program looks for your API keys, etc, etc. 
Of note:
<UL>
<li><b>NewUserCourse</b> is a Canvas Introduction course we created for our students to give them a run down on what Canvas is and how to use it. Totally optional, and if you are not going to use it, then don't set it.
<li><b>SkipCourses</b> are courses we are not enrolling users into Canvas for. We offer some English language placement tests, and we do not put a student in Canvas when they are just enrolled in those classes. You can add a infinite list of skipped classes.
</ul>

Also in the .ASAPCanvas directory, you need to create a lastrecordasap.csv file. This is a file that contains where you left off in the ASAP datastream. If you are running this for the FIRST TIME, I suggest running ASAP_Enrollments_to_CSV.py (run it and give it a filename you want to save to), and changing the classStartDate to whatever suits you. We are keying off and incremential serial number (I think?) field called EnrollmentStatusCd. You need to make a lastrecordasap.csv file that has atleast two lines in it, first one being the header of EnrollmentStatusCd, and the second a number where you want to start. It could be 0 if you want. I believe calling the ASAP API just gives you up to 60 days worth of information. Version .02 of the program will be a little smarter and also include the date in there so we don't have to grab so much from ASAP.
