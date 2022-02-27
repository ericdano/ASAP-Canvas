# This is a web interface for the ASAP/Canvas Programs
#
#pip install flask
#pip install wfastcgi
#then run wfastcgi-enable
#
# Refer to this documentation
# https://medium.com/@nerdijoe/how-to-deploy-flask-on-iis-with-windows-authentication-733839d657b7
#
from flask import Flask
from flask import request
app = Flask(__name__)
@app.route("/hello")
def hello():
    username = request.environ.get('REMOTE_USER')
    return username
if __name__=='__main__':
    app.run(debug=True)