
from flask import *
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, flash, send_file
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors 
import re

app=Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='job'
mysql=MySQL(app)
model=pickle.load(open('random.pickle','rb'))
vecs=pickle.load(open('vectorizers.pickle','rb'))
classifiers=pickle.load(open('classifiers.pickle','rb'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    #output message if something goes wrong...
    msg=''
    #check if "username", "password", "email" POST request exist(user submitted from)
    if request.method=='POST'and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        #create variable for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        number = request.form['number']


        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #check if account exists using mysql
        cursor.execute('SELECT * FROM  register WHERE username = %s',(username,))
        account = cursor.fetchone()
        #if account exists show error and validation checks
        if account:
            msg = 'Account already exists..!' 
        elif  not re.match (r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email address..!'
        elif not re.match(r'[A-Za-z]+_[A-Za-z0-9]+',username):
            msg = 'Username must contain characters, underscope and numbers...!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one upper case character, one special symbol and must be between 6 to 10 characters long...!'
        elif not username or not password or not email:
            msg = 'Please fill out the form..!'
        else:
            #account doesn't exist and the form data is valid, now insert new account into register table
            cursor.execute('INSERT INTO register VALUES (NULL,%s,%s,%s,%s)',(username,email,number,password))
            mysql.connection.commit()
            flash('You have successfully registered...! Please proceed for login...!')
            return redirect(url_for('login'))
    elif request.method =='POST':
        #form is empty....(no post fill)
        msg = 'Please fill out the form..!'
        return msg
    #show registration form with message (if any)
    return render_template('register.html',msg=msg)


@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/loginaction',methods=['POST'])
def loginaction():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from register WHERE username = %s AND password=%s',(username,password,))
        account=cursor.fetchone()
        if account:
            return render_template('upload.html')
        else:
            return 'Invalid Login'

@app.route('/preview',methods=["POST"])
def preview():
    if request.method=='POST': 
        dataset=request.files['datasetfile']
        df=pd.read_csv(dataset,encoding='unicode_escape')
        return render_template('preview.html',df_view=df) 
        
@app.route('/fake')
def fake():
    return render_template('fake.html')            

@app.route('/predict',methods=['POST'])
def predict():
    features=[float(x) for x in request.form.values()]
    final_features=[np.array(features)]
    y_pred=model.predict(final_features)
    if y_pred[0]==1:
        label="Fake Job Post"
    elif y_pred[0]==0:
        label="Legit Job Post"
    return render_template('fake.html',prediction_texts=label)        
@app.route('/text')
def text():
     return render_template('text.html')

@app.route('/job')
def job():	
	abc = request.args.get('news')	
	input_data = [abc.rstrip()]
	# transforming input
	tfidf_test = vecs.transform(input_data)
	# predicting the input
	y_preds = classifiers.predict(tfidf_test)
	if y_preds[0] == 1:
		labels="Fake Job Post"
	elif y_preds[0] == 0:
		labels="Legit Job Post"
	return render_template('text.html', prediction_text=labels)     
    
@app.route('/chart')
def chart():
    return render_template('chart.html')    
@app.route('/performance')
def performance():
    return render_template('performance.html')   
    
if __name__=='__main__':
    app.run(debug=True)