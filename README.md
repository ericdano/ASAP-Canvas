# ASAP-Canvas
Introduction

ASAP Connected and Canvas LMS Scripts - Python Scripts for pulling and pushing data to both Systems and various Canvas Scripts

This project was started for the <a href="https://acalanes.k12.ca.u/">Acalanes Union High School District Adult Education</a>. In the summer of 2020, during COVID-19, the school district switched Learning Management Systems (LMS) to <a href="https://www.instructure.com/">Instructure Canvas</a>. The issue was that the state of California requires Adult Education to use <a href="https://app.asapconnected.com/">ASAP Connected</a> for it's enrollment and attendance for programs and Canvas and ASAP do not talk to each other.

After a roll out of about 1500 students using CSV files, I decided to dig in and figure out how to make it automated (cause, of course, I am lazy and don't want to keep pulling over things with CSV files).

Using Python, API calls, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and the great <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a> library for Python, this project was born. It calls ASAP Connected, grabs all the data it needs, figures out the last transaction you imported into Canvas, and then creates new students in Canvas (if needed) and enrolls them into a introduction class on Canvas, and the class they want to take.

Installation

ASAP-Canvas uses Python 3.8.5, <a href="https://pandas.pydata.org/">Pandas for Python</a>, and <a href="https://github.com/ucfopen/canvasapi">CanvasAPI</a>
