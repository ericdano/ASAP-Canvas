# ASAP-Canvas
ASAP Connected and Canvas LMS Scripts - Python Scripts for pulling and pushing data to both Systems and various Canvas Scripts

This project was started for the Acalanes Union High School District Adult Education. In the summer of 2020, during COVID-19, the school district switched Learning Management Systems (LMS) to Canvas. The issue was that the state of California requires Adult Education to use ASAP Connected for it's enrollment and attendance for programs and Canvas and ASAP do not talk to each other.

After a roll out of about 1500 students using CSV files, I decided to dig in and figure out how to make it automated (cause, of course, I am lazy and don't want to keep pulling over things with CSV files).

Using Python, API calls, Pandas for Python, and the great CanvasAPI library for Python, this project was born. It calls ASAP Connected, grabs all the data it needs, figures out the last transaction you imported into Canvas, and then creates new students in Canvas (if needed) and enrolls them into a introduction class on Canvas, and the class they want to take.
