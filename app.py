from flask import Flask, render_template, request
import os
from flask import make_response

app = Flask(__name__)
@app.route('/')
def index():
   return render_template('demo.html')

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
   if request.method == 'POST':
       user = request.form['nm']
       
       resp = make_response(render_template(''))
       resp.set_cookie('user', '', expires=0)
       #resp.set_cookie('userID', user)
   
   return resp
@app.route('/getcookie')
def getcookie():
   name = request.cookies.get('userID')
   return '<h1>welcome '+name+'</h1>'

if __name__ == '__main__':
    app.debug = True
    app.run()