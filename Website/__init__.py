############################################################
############################################################
###############  ###############
############################################################
############################################################

#######################################################
########## 1. Setup Python ############################
#######################################################

##############################
##### 1.1 Python Libraries
##############################
import os, json
import pandas as pd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


##############################
##### 1.2 Setup App
##############################
# Initialize Flask App
app = Flask(__name__)

# Setup entry point
entry_point = '/kryptonite'

# Read data
connection_file = 'static/db_connection.json'
if os.path.exists(connection_file):
	with open(connection_file) as openfile:
		connectionDict = json.loads(openfile.read())
	os.environ['DB_USER'] = connectionDict['DB_USER']
	os.environ['DB_PASS'] = connectionDict['DB_PASS']
	os.environ['DB_HOST'] = connectionDict['DB_HOST']
	os.environ['DB_NAME'] = connectionDict['DB_NAME']

# Initialize database engine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASS'] + '@' + os.environ['DB_HOST'] + '/' + os.environ['DB_NAME']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 290
engine = SQLAlchemy(app).engine

#######################################################
########## 2. Routes ##################################
#######################################################

##############################
##### 1. Templates
##############################

# #########################
# ### 1. Hello test
# #########################

# @app.route(entry_point)

# def index():
	
# 	# variable1 = 'hello'
# 	variable2 = ['hello', 'my', 'name', 'is', 'clark kent']

# 	# Return hello
# 	# return 'hello'
# 	# return render_template('index.html')
# 	# return render_template('index.html', variable1=variable1)
# 	return render_template('index.html', variable2=variable2)

#########################
### 1. About Page
#########################

@app.route(entry_point)

def About():
	
	return render_template('help.html')

#########################
### 2. Table test
#########################

@app.route(entry_point+'/kinases')

def index():
	
	# Get the data stored in the MySQL table 'kinase_db'
	kinase_dataframe = pd.read_sql_query('SELECT * FROM kinase_db', engine)
	print(kinase_dataframe)

	#Get the data stored in the MySQL table 'kin_pubmed_data'
	pubmed_dataframe = pd.read_sql_query('SELECT * FROM kin_pubmed_data', engine) 
	print(pubmed_dataframe)

	jupyter_dataframe = pd.read_sql_query('SELECT * FROM kin_notebooks', engine)
	print(jupyter_dataframe)

	file_dataframe = pd.read_sql_query('SELECT * FROM kin_processed_files', engine)
	print(file_dataframe)

	colnames = ['Kinase-Substrate Database', 'Jupyter Notebook', 'Kinases', 'Substrates',
	'Total Unique Terms', 'Average Substrates per Kinase', 'Processed Files', 'Date Retrieved',
	'PMID']
	print(colnames)

	return render_template('index.html', kinase_dataframe=kinase_dataframe, pubmed=pubmed_dataframe, 
		jupyter = jupyter_dataframe, files = file_dataframe, colnames = colnames)


#########################
### 3. Table test
#########################

@app.route(entry_point+'/proteins')

def table_test2():

	return 'kinases'



#######################################################
########## 3. Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')