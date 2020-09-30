# ASAP-Canvas
<h2>Introduction</h2>

ASAP Connected and Canvas LMS Scripts - Python Scripts for pulling and pushing data to both Systems and various Canvas Scripts

This project was started for the <a href="https://acalanes.k12.ca.u/">Acalanes Union High School District Adult Education</a>. In the summer of 2020, during COVID-19, the school district switched Learning Management Systems (LMS) to <a href="https://www.instructure.com/">Instructure Canvas</a>. The issue was that the state of California requires Adult Education to use <a href="https://app.asapconnected.com/">ASAP Connected</a> for it's enrollment and attendance for programs and Canvas and ASAP do not talk to each other.

After a roll out of about 1500 students using CSV files, I decided to dig in and figure out how to make it automated (cause, of course, I am lazy and don't want to keep pulling over things with CSV files).

Using Python, API calls, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and the great <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a> library for Python, this project was born. It calls ASAP Connected, grabs all the data it needs, figures out the last transaction you imported into Canvas, and then creates new students in Canvas (if needed) and enrolls them into a introduction class on Canvas, and the class they want to take.

<h2>Requirements</h2>

ASAP-Canvas uses Python 3.8.5, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a>
You will also need an API key generated from your Canvas instance, and an API key from ASAP Connected.

<h2>Installation</h2>
You need <a href="https://www.python.org/downloads/">Python 3.8.5</a>
You need <a href="https://www.pypa.io/en/latest/">PIP installed</a>
You need the <a href="https://github.com/ucfopen/canvasapi">CanvasAPI library</a>. With Python installed, you can run "pip install canvasapi"
You need <a href="https://pandas.pydata.org/">Pandas for Python</A> installed.
You also need some sort of SMTP server to receive status messages from it (emails saying it added X number of students, etc, etc)
This python script should run on any computer. You probably want to set it up to run hourly? Daily? Your pick. This script was developed on Windows and Linux.
