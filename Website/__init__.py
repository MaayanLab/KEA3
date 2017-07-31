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
import os, json, sys
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/home/maayanlab/Desktop/Projects/KEA3/Website/Uploaded_Files' ##
static_path = 'static'

##############################
##### 1.2 Setup App
##############################
# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER ##
app.secret_key = 'MySecretKey'

# Setup entry point
entry_point = '/BINDer'

# Read data
connection_file = 'static/db_connection.json'
#connection_file = '/binder/Website/static/db_connection.json'
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

db = SQLAlchemy(app)
db.create_all()

# Import custom Scripts
sys.path.append(static_path)
import Scripts

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
###  Home Page
#########################

@app.route(entry_point)

def Home():
	
	return render_template('home.html')

#########################
###  Help Page
#########################

@app.route(entry_point+'/help')

def Help():
	
	return render_template('help.html')

#########################
### Kinases Table
#########################

@app.route(entry_point+'/kinases')

def index():
	
	# Get the data stored in the MySQL table 'kinase_db'
	kinase_dataframe = pd.read_sql_query('SELECT * FROM kinase_db', engine)


	#Get the data stored in the MySQL table 'kin_pubmed_data'
	pubmed_dataframe = pd.read_sql_query('SELECT * FROM kin_pubmed_data', engine) 


	jupyter_dataframe = pd.read_sql_query('SELECT * FROM kin_notebooks', engine)
	print(jupyter_dataframe)

	file_dataframe = pd.read_sql_query('SELECT * FROM kin_processed_files', engine)


	colnames = ['Kinase-Substrate Database', 'Jupyter Notebook', 'Kinases', 'Substrates',
	'Total Unique Terms', 'Average Substrates per Kinase', 'Processed Files', 'Date Retrieved',
	'PMIDs']


	return render_template('index.html', kinase_dataframe=kinase_dataframe, pubmed=pubmed_dataframe, 
		jupyter = jupyter_dataframe, files = file_dataframe, colnames = colnames)


#########################
###  PPI Table
#########################

@app.route(entry_point+'/proteins')

def ppi():

	# Get the data stored in the MySQL table 'kinase_db'
	ppi_dataframe = pd.read_sql_query('SELECT * FROM ppi_db', engine)


	#Get the data stored in the MySQL table 'kin_pubmed_data'
	pubmed_dataframe = pd.read_sql_query('SELECT * FROM ppi_pubmed_data', engine) 


	jupyter_dataframe = pd.read_sql_query('SELECT * FROM ppi_notebooks', engine)


	file_dataframe = pd.read_sql_query('SELECT * FROM ppi_processed_files', engine)


	ppi_nr = pd.read_sql_query('SELECT * FROM ppi_nr', engine)

	colnames = ['PPI Database', 'Jupyter Notebook', 'Total Number of Proteins', 'Interactions', 
	'Hub Proteins (GMT)', 'Average Number Interactions per Protein', 'Processed Files',
	'Date Retrieved', 'PMIDs']


	return render_template('ppi.html', ppi_dataframe=ppi_dataframe, pubmed=pubmed_dataframe, 
		jupyter = jupyter_dataframe, files = file_dataframe, colnames = colnames, ppi_nr = ppi_nr)

#########################
###  TF Page
#########################

@app.route(entry_point+'/tf')

def TF():
	
	return render_template('tf.html')

#########################
###  Contribute
#########################

@app.route(entry_point+'/contribute')

def Contribute():

	resources = pd.read_excel("resources_file.xlsm")
	insert = "INSERT INTO resources (db_name, db_url) VALUES"+ ', '.join(['("{db_name}", "{db_url}")'.format(**rowData) for index, rowData in resources.iterrows()])
	engine.execute(insert)


	species_df = pd.read_sql_query('SELECT * FROM species', engine)
	resources = pd.read_sql_query('SELECT * FROM resources', engine)
	interaction_type_df = pd.read_sql_query('SELECT * FROM interaction_type', engine)
	file_types = pd.read_sql_query('SELECT * FROM file_types', engine)


	return render_template('contribute.html', int_type_df = interaction_type_df,
	species_df=species_df, resources=resources, file_types = file_types)


#########################
###  Contribute
#########################

@app.route(entry_point+'/gene')

def gene():

#Tentative Query Script

	#will return the third element of the dict related to the gene symbol
	#(if dict is split into "0:symbol", "1:=", "2:gene+symbol")
	gene_s = request.args.get('gene_symbol', 'None')
	print(gene_s)

	genes = pd.read_sql_query('SELECT * FROM genes', engine)
	genes.set_index('id', inplace = True)

	species = pd.read_sql_query('SELECT * FROM species', engine)
	species.set_index('id', inplace = True)

	interactions = pd.read_sql_query('SELECT * FROM interactions', engine)
	interactions.set_index('id', inplace=True)

	submissions = pd.read_sql_query('SELECT * FROM submissions', engine)
	submissions.set_index('id', inplace = True)

	resources = pd.read_sql_query('SELECT * FROM resources', engine)
	resources.set_index(['id'], inplace = True)

	interaction_type = pd.read_sql_query('SELECT * FROM interaction_type', engine)
	interaction_type.set_index(['id'], inplace = True)

	#Retrieve all information related to a gene based upon query
	gene = genes.query('gene_symbol==@gene_s')

	gene_id = ""
	species_id = ""
	organism = ""

	# Display all data in the row corresponding to the gene_symbol in table 'genes'
	for key, rowData in gene.iterrows():
		gene_id = key
		species_id = rowData.species_fk
	print(gene_id)
	
	source_df = pd.DataFrame()
	target_df = pd.DataFrame()

	for key, rowData in interactions.iterrows():
		if rowData.source_gene_fk == gene_id:
			source_df = source_df.append(rowData)
			
		if rowData.target_gene_fk == gene_id:
			target_df = target_df.append(rowData)
			

	for key, rowData in species.iterrows():
		if key == species_id:
			organism = rowData.species_name

	target_df['resources'] = ""
	source_df['resources'] = ""
	source_df['interaction'] = ""
	target_df['interaction'] = ""

	for index, rowData in source_df.iterrows():
		interaction_fk = submissions.submission_type_fk[rowData.submission_fk]
		interaction_t = interaction_type.interaction_name[interaction_fk]

		interaction_t = pd.Series(interaction_t)[0]

		source_df.interaction[index] = interaction_t

		resource_fk = submissions.resource_fk[rowData.submission_fk]
		resource_name = pd.Series(resources.db_name[resource_fk])[0]

		source_df.resources[index] = resource_name

	for index, rowData in target_df.iterrows():
		interaction_fk = submissions.submission_type_fk[rowData.submission_fk]
		interaction_t = interaction_type.interaction_name[interaction_fk]

		interaction_t = pd.Series(interaction_t)[0]

		target_df.interaction[index] = interaction_t

		resource_fk = submissions.resource_fk[rowData.submission_fk]
		resource_name = pd.Series(resources.db_name[resource_fk])[0]

		target_df.resources[index] = resource_name

	return render_template('gene.html', gene_s=gene_s, gene_id = gene_id, genes = genes, 
		organism = organism, source_df=source_df, target_df = target_df, gene = gene, 
		interactions =interactions, interaction_type = interaction_type, resources = resources,
		submissions = submissions)

#######################################################
##########  Retrieve Info From Submitted form ###########################
#######################################################

@app.route(entry_point+'/upload', methods = ["POST"])

def upload():

	if request.method == 'POST':


		#this works!
		#Check if username is correct!
		user_name = request.form.get('input_user')
		if user_name != '':
			return "Invalid username, please try again" 

		#this works!
		#Check if password is correct!
		password = request.form.get('input_password')
		if password != '':
			return "Invalid password, please try again" 

		#this works!
		submission = request.form.get('new_submission_name')
		print(submission)
		
		#this works!
		int_type = request.form.get('input_interaction')
		print(int_type)

		#this works!
		organism = request.form.get('input_species')
		

		#this works!
		resource = request.form.get('input_resource')
		print(resource)

		#this works!
		file_type = request.form.get('input_type')
		print(type(file_type))


		#this works!
		file = request.files['input_file']
		print(file)

		# this works!
		filename = secure_filename(file.filename)
		print(filename)

		#this works! (for now)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))


		#this works!
		submissions = pd.DataFrame(columns = ['submission_name', 'submission_type_fk', 'resource_fk'])
		submissions = submissions.append([{
			'submission_name': submission,
			'submission_type_fk': int(int_type),
			'resource_fk': int(resource)
			}])
		print(submissions)

		#When uncommented, this works! UNCOMMENT FOR FINAL TRIAL
		insert_s = "INSERT INTO submissions (submission_name, submission_type_fk, resource_fk) VALUES"+ ', '.join(['("{submission_name}", {submission_type_fk}, {resource_fk})'.format(**rowData) for index, rowData in submissions.iterrows()])
		sub = engine.execute(insert_s)

		#this works! --> NEEDS TO BE PASSED ONTO FUNCTION
		submission_fk = sub.lastrowid
		print(submission_fk)

		#add other 'if' statements to send file to right python processor based on int_type

		#also at some point once this whole process is over we also want to save these files 
		#somewhere and convert them to their alternate format --> I know procedure to save locally 
		#but is this what we really want? --> Won't be automatic uploads elsewhere

		#this works!
		if file_type == '1':
			gmt = UPLOAD_FOLDER+"/%s" %filename
			sig_version = Scripts.GMT_to_SIG(gmt)
			interactions = Scripts.SIG_to_Genes(sig_version, submission_fk)
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)
			

		#this works!
		if file_type == '2':
			sig = pd.read_table(UPLOAD_FOLDER+"/%s" %filename, header = None)
			if 5 not in sig.columns:
				sig = pd.read_table(UPLOAD_FOLDER+"/%s" %filename, header = None, 
				names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], sep = ' ')
			print(sig.head())
			interactions = Scripts.SIG_to_Genes(sig, submission_fk, organism)
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)


	return redirect(url_for('Contribute'))




#######################################################
##########  Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
