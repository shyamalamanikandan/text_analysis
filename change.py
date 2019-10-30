from flask import Flask, redirect, url_for, session, request, render_template, flash, Markup
from flask_oauth import OAuth
from flask import Flask, redirect, url_for, session, request, jsonify, Response,render_template
from flask import Flask, render_template, request
import pymysql.cursors
from urllib.parse import urlparse
from textblob import TextBlob
from Reader import fileReaderMethod
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
#from wordcloud import WordCloud, STOPWORDS
import requests
from wordcloud import WordCloud
from nltk.corpus import stopwords
from string import punctuation
from flask_oauth import OAuth
from uuid import uuid4
from flask_oauthlib.client import OAuth
from FrequencySummariser import Summariser
import threading
import os
import webbrowser
from flask import redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import csv, re, collections
from collections import Counter
from flask_mail import Mail, Message
import pyotp
import time

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '2229493917289490'
FACEBOOK_APP_SECRET = 'd252637a283f20c30cef24ecd15f1bc0'
GOOGLE_CLIENT_ID = '534978381583-75t3d5f8o64n67b7qufh0k041t3eif6d.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'rm2H7Hm5xQ2JuYYrrK4_mXNB'
#REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs 


app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
#connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
UPLOAD_FOLDER = '/home/ubuntu/project/FilesUploading'
ALLOWED_EXTENSIONS = set(['txt', 'pdf','doc','docx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'will2vigilant@gmail.com'
app.config['MAIL_PASSWORD'] = 'Will2Vigilant'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)
google = oauth.remote_app(
    'google',
    consumer_key='534978381583-75t3d5f8o64n67b7qufh0k041t3eif6d.apps.googleusercontent.com',
    consumer_secret='rm2H7Hm5xQ2JuYYrrK4_mXNB',
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)
						  
linkedin = oauth.remote_app(
    'linkedin',
    consumer_key='81dvhjgsnztbst',
    consumer_secret='7I9Ov8bWUWgezeoF',
    request_token_params={
        'scope': 'r_basicprofile',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

						  
@app.route('/google', methods=['GET', 'POST'])
def index():
    """if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({"data": me.data})"""
    return redirect(url_for('glogin'))

@app.route('/glogin')
def glogin():
    return google.authorize(callback=url_for('authorized', _external=True))
	
 
@app.route('/oauth2callback')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    username=me.data['id']
    session['email']=username
    query = "SELECT count(*) as count FROM register1 where email ='"+username+"'"
    #print(query)
    connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        cursor.execute(query)
        data=cursor.fetchall()
        count =0
        for row in data:
            count=row['count']
            print(count)
        if count ==0:

	     
         cursor.execute("INSERT INTO register1 (email) VALUES(%s)",(username))
    connection.close()
    return render_template('new.html')
	
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/facebook', methods=['GET', 'POST'])
def index1():
    return redirect(url_for('login'))

@app.route('/session_clear',methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('index.html')
 

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    username=me.data['id']
    session['email']=username
    query = "SELECT count(*) as count FROM register1 where email ='"+username+"'"
    print(query)
    connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        cursor.execute(query)
        data=cursor.fetchall()
        count =0
        for row in data:
            count=row['count']
            print(count)
        if count ==0:

	     
         cursor.execute("INSERT INTO register1 (email) VALUES(%s)",(username))
    connection.close()
    return render_template('new.html')

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
	
@app.route('/linkedin',methods=['GET','POST'])
def lindex():
    return redirect(url_for('llogin'))


@app.route('/llogin')
def llogin():
    return linkedin.authorize(callback=url_for('linkedin_authorized', _external=True))


@app.route('/oauth2linkedin')
def linkedin_authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    me = linkedin.get('people/~')
    username=me.data['id']
    session['email']=username
    query = "SELECT count(*) as count FROM register1 where email ='"+username+"'"
    print(query)
    connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        cursor.execute(query)
        data=cursor.fetchall()
        count =0
        for row in data:
            count=row['count']
            print(count)
        if count ==0:
            cursor.execute("INSERT INTO register1 (email) VALUES(%s)",(username))
    connection.close()
        
    #return jsonify(me.data)
    
    return render_template('new.html')


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')
	
def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

	
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route('/')
def jobportal():
    return render_template('index.html')
	
@app.route('/exit', methods=['GET', 'POST'])
def exit():
    
    return render_template('new.html')
	
@app.route('/error', methods=['GET', 'POST'])
def error():
    session.clear()
    return render_template('index.html')


   
@app.route("/forgotpass")
def mailvalidate():
    return render_template('otppassword.html')

@app.route('/otppassword',methods = ['POST', 'GET'])
def otpget():
    if request.method == 'POST':
        connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
	    
            totp = pyotp.TOTP('base32secret3232')
            otp=totp.now() # => '492039'
            otp=str(otp)
            
            session['email']=request.form['nm']
            print(session['email'])
            msg = Message('Your OTP for resetting Sentiment Analysis Password', sender = 'will2vigilant@gmail.com',
            recipients = [session['email']])
            msg.body = "Please enter below OTP to reset your account Password:  "+otp
            mail.send(msg)
            error="Invalid Email_ID"
            sql1=cursor.execute("select * from register1 WHERE email=%s",(session['email']))
            data = cursor.fetchone()
            print("Type =",type(data))
            if data is not None:
                sql="UPDATE register1 SET otp=%s WHERE email=%s"
                cursor.execute(sql,(otp,session['email']))
                return  render_template('chpass.html')
            connection.close()
        return render_template('otppassword.html',error=error)
"""sql = "UPDATE register1 SET otp=%s WHERE email=%s"
            cursor.execute(sql, (otp,session['email']))
            connection.commit()
        return  render_template('chpass.html')"""
		
@app.route("/pwchange",methods = ['POST', 'GET'])
def pwchange():
    if request.method == 'POST':
        connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            otp=request.form['otp']
            password=request.form['newpass']
            email=session['email']
            error="Invalid OTP"
            sql1=cursor.execute("select * from register1 WHERE otp=%s and email=%s",(otp,email))
            data = cursor.fetchone()
            print("Type =",type(data))
            if data is not None:
                sql="UPDATE register1 SET password=%s WHERE otp=%s"
                cursor.execute(sql,(password,otp))
                connection.close()
                return  render_template('new.html')
            connection.close()
        return render_template('chpass.html',error=error)


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
                connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

                with connection.cursor() as cursor:
                    session['username']= str(request.form['username'])
                    session['email'] = str(request.form['email'])
                    print(session['email'])
                    text3 = str(request.form['password'])
                    text4 = str(request.form['phoneno'])
                    text5= str(request.form['country'])
                    text6= str(request.form['city'])
                    text7= str(request.form['designation'])
                    text8= str(request.form['Organization'])
                    retVal = cursor.execute("INSERT INTO register1 (name,email,password,phone,country,city,designation,organization) VALUES(%s, %s, %s, %s, %s, %s,%s,%s)",(session['username'], session['email'], text3, text4, text5, text6, text7, text8))					
                connection.close()
        except:
            error= "Email ID is already registered with us . Please use your existing password to continue or use the forget password link to reset your password."
            return render_template('Register.html',error=error)
            			   	       
        #return render_template('Register.html')
        
        return render_template('index.html')
    else: 
        return render_template('Register.html')
		
@app.route('/login_page',methods=['GET','POST'])		
def login_form():
    if request.method == 'POST':
        connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            email = str(request.form['name'])
            password = str(request.form['password'])
            error = 'Invalid username or password. Please try again!'
            sql = cursor.execute("select * from register1 where email =%s AND password=%s",(email,password))
            data = cursor.fetchone()
            connection.close()
            print(sql)
            if sql > 0:
                session['email']=email
                print(session['email'])
                return render_template('new.html')
            else:
                
                return render_template('index.html', error = error)
            
		
        


   
@app.route('/reset', methods=['POST','GET'])
def reset():
   return render_template('new.html')
   
@app.route('/frontlogin', methods=['GET', 'POST'])
def f_login():
    return render_template('index.html')

@app.route('/sentiments', methods=['POST','GET'])
def getsentiments():
    try:
        val = ""
        
        session.pop('userid', None)
        results = []
        url_counter = 0
        if request.method == 'POST':
    	    #if(len(review)&&len(reviewurl)==0)
    		    
            # check if the post request has the file part 
            if 'file' not in request.files:
                review = request.form['review']
                reviewurl = request.form['reviewurl']
                if len(review) != 0:
                    val = review
                elif len(reviewurl) != 0:
                    val = reviewurl
                    url_counter = 1
            else:
    		    
                file = request.files['file']
                          
    
                #return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    val = fileReaderMethod(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if url_counter == 1:
                import urllib.request 
                from bs4 import BeautifulSoup 
                page = urllib.request.urlopen(val).read().decode('utf8')
                soup = BeautifulSoup(page)
                text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
                val = text
                
                
                     
            
    		#Polarity
            freq, summary, polarity = Summariser(val)
            print("sum",summary)			
            def sentiment_textblob(feedback): 
                senti = TextBlob(feedback) 
                polarity = senti.sentiment.polarity 
                if -1 <= polarity < -0.5: 
                    label = 'Highly Negative' 
                elif -0.5 <= polarity < -0.1: 
                    label = 'Negative' 
                elif -0.1 <= polarity < 0: 
                    label = 'Slightly Negative'
                elif polarity ==0:
                    label = 'Neutral'				
                elif 0 < polarity < 0.2:
                    label = "Slightly Positive"            
                elif 0.2 <= polarity < 0.6: 
                    label = 'Positive' 
                elif 0.6 <= polarity <= 1: 
                    label = 'Highly Positive' 
                return (label)
                				
            polarity=sentiment_textblob(val)
            results.append(polarity)
            allsummary = ""
            wordfrquencies = ""
            #results.append(freq)
            udata = (val[:10000] + '..') if len(val) > 10000 else val
            udata = udata.encode('ascii', 'ignore')
           
            emailId = str(session['email'])
            connection = pymysql.connect(host='localhost',user='root',password='',db='sentiment_analysis', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                query = "select id from register1 where email ='"+emailId+"'"
                print(query)
                cursor.execute(query)
                data=cursor.fetchall()
                userId = -1
                for row in data:
                    print(row)
                    userId=row['id']
                session['userId']=userId
                print(session['userId'])
            #print(userId,str(session['email']) )
            #session['userid']=userId
            
            with connection.cursor() as cursor:	
                cursor.execute("INSERT INTO `datatable1` VALUES(%s,%s)", (session['userId'],udata))
                print("database done") 	
            connection.close()
            wrdcnt = 0
            print("word count",wrdcnt)
            for k in freq:
                if(k.isalpha()):
                    wordfrquencies += str(k)+', '
                    wrdcnt += 1
                if wrdcnt  == 10:
                    print("word count1",wrdcnt)
                    break
            for s in summary:
                allsummary += s
                print("all ",allsummary)
            word_freqs_js, max_freq = wordCloudCaller(val)
            print("words",word_freqs_js)
            print("Max Freq",max_freq)
            results.append(wordfrquencies)
            results.append(allsummary)
            
            
        return render_template('result-new.html',results = results, word_freqs=word_freqs_js, max_freq=max_freq)
        
    except:
        error="please give valid input"
        return render_template('new.html',error=error)
        
			

			
def wordCloudCaller(text):
    print("Word Cloud")
    custom_stopwords = ["let","hi"]
    stopword1 = set(stopwords.words('english') + list(punctuation) + custom_stopwords)
    stripped_text = []
    #stripped_text = [word for word in text.split() if word.isalpha() and word.lower() not in open("stopwords", "r").read() and len(word) >= 2]
    stripped_text = [word for word in text.split() if word.isalpha() and word.lower() not in list(stopword1) ]
    word_freqs = Counter(stripped_text)
    word_freqs = dict(word_freqs)
    print(word_freqs)
    word_freqs_js = []


    for key,value in word_freqs.items():
        temp = {"text": key, "size": value}
        word_freqs_js.append(temp)

    max_freq = max(word_freqs.values())
    print("beginning wordcloud")
    wc = WordCloud(stopwords = stopword1).generate(text)
    plt.imshow(wc)
    plt.figure(1,figsize=(5,5))
    plt.axis('off')
    plt.title('Wordcloud')
    a=plt.savefig("static\\wordcloud.png")
    res = Response('delete cookies')
    res.set_cookie('a', '', expires=0)
    plt.close()
    return word_freqs_js, max_freq

    
    
if __name__ == '__main__':
     app.run()
