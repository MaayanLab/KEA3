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
import io
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/home/maayanlab/Desktop/Projects/KEA3/Website' ##
static_path = 'static'

##############################
##### 1.2 Setup App
##############################
# Initialize Flask App
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER ##
app.secret_key = 'MySecretKey'

# Setup entry point
entry_point = '/binder'

# Read data
connection_file = 'static/db_connection.json'
#connection_file = '/Website/static/db_connection.json'
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

	species_df = pd.read_sql_query('SELECT * FROM species', engine)
	resources = pd.read_sql_query('SELECT * FROM resources', engine)
	interaction_type_df = pd.read_sql_query('SELECT * FROM interaction_type', engine)
	file_types = pd.read_sql_query('SELECT * FROM file_types', engine)


	return render_template('contribute.html', int_type_df = interaction_type_df,
	species_df=species_df, resources=resources, file_types = file_types)


#########################
###  Gene
#########################

@app.route(entry_point+'/gene')

def gene():

############################# Searches for Gene using Input Button #################################

#Tentative Query Script

	gene_string = request.args.get('input_gene')
	if type(gene_string) == type('hello'):
		gene_string = gene_string.upper()
	
	genes = pd.read_sql_query('SELECT * FROM genes', engine)
	genes.set_index('id', inplace = True)

	species = pd.read_sql_query('SELECT * FROM species', engine)
	species.set_index('id', inplace = True)

	boole = genes.gene_symbol.str.contains('%s' %gene_string)

	contains = genes.loc[boole]

################################ Chooses Gene of Interest in Table #################################

	#Tentative Query Script

	#will return the third element of the dict related to the gene symbol
	#(if dict is split into "0:symbol", "1:=", "2:gene+symbol")
	gene_s = request.args.get('gene_symbol', 'None')
	

		#this works!!!
	gene_interactions = pd.read_sql_query('''SELECT source_gene_fk, target_gene_fk, submission_name, submission_type_fk, db_name FROM interactions i 
		LEFT JOIN submissions s 
			ON s.id = i.submission_fk 
		LEFT JOIN resources r 
			ON r.id = s.resource_fk 
		LEFT JOIN interaction_type it 
			ON it.id = s.submission_type_fk'''.format(**locals()), con = engine)#{gene_id}
	print(gene_interactions)


	gene_info = pd.read_sql_query('''SELECT g.id, gene_symbol, species_name FROM genes g LEFT JOIN species s ON s.id = g.species_fk'''.format(**locals()), con = engine)
	#gene_info.set_index('id', inplace = True)
	print(gene_info)

	#Retrieve all information related to a gene based upon query
	gene = gene_info.query('gene_symbol==@gene_s')
	print(gene)

	gene_id = ""
	species_id = ""
	organism = ""

	# Display all data in the row corresponding to the gene_symbol in table 'genes'
	for key, rowData in gene.iterrows():
		gene_id = key
		species_id = rowData.species_fk
	
	source_df = pd.DataFrame()
	target_df = pd.DataFrame()
	ppi_df = pd.DataFrame()
	ppi_df['data'] = ""
	ppi_df['submission_fk'] = ""

	for key, rowData in interactions.iterrows():
		if rowData.source_gene_fk == gene_id:
			if submissions.submission_type_fk[rowData.submission_fk] != 2:
				source_df = source_df.append(rowData)
			else:
				ppi_df = ppi_df.append({'data': rowData.target_gene_fk, 'submission_fk': rowData.submission_fk}, ignore_index = True)
			
		if rowData.target_gene_fk == gene_id:
			if submissions.submission_type_fk[rowData.submission_fk] != 2:
				target_df = target_df.append(rowData)
			else:
				ppi_df = ppi_df.append({'data': rowData.target_gene_fk, 'submission_fk': rowData.submission_fk}, ignore_index = True)

	for key, rowData in species.iterrows():
		if key == species_id:
			organism = rowData.species_name

	ppi_df['resources'] = ""
	ppi_df['interaction'] = ""
	target_df['resources'] = ""
	target_df['interaction'] = ""
	source_df['resources'] = ""
	source_df['interaction'] = ""

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

	for index, rowData in ppi_df.iterrows():
		interaction_fk = submissions.submission_type_fk[rowData.submission_fk]
		interaction_t = interaction_type.interaction_name[interaction_fk]
		interaction_t = pd.Series(interaction_t)[0]
		ppi_df.interaction[index] = interaction_t

		resource_fk = submissions.resource_fk[rowData.submission_fk]
		resource_name = pd.Series(resources.db_name[resource_fk])[0]
		ppi_df.resources[index] = resource_name

		print(ppi_df.data[index])
		print(genes.gene_symbol[ppi_df.data[index]])

	ppi_df.drop_duplicates(inplace=True)
	print(ppi_df)

	return render_template('gene.html', gene_string=gene_string, contains=contains, gene_s=gene_s, gene_id = gene_id, genes = genes, 
		organism = organism, source_df=source_df, target_df = target_df, gene = gene, 
		interactions =interactions, interaction_type = interaction_type, resources = resources,
		submissions = submissions, species = species, ppi_df=ppi_df)

#######################################################
##########  Retrieve Info From Submitted form #########
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

		#this works!
		date = request.form.get('date')
		print(date)

		#this works!
		notebook = request.form.get("notebook_link")
		print(notebook)
		
		#this works!
		int_type = request.form.get('input_interaction')

		#this works!
		organism = request.form.get('input_species')
		

		#this works!
		resource = request.form.get('input_resource')

		#this works!
		file_type = request.form.get('input_type')


		#this works!
		file = request.files['input_file']
		print(file)


		###### Processing 'file' and uploading data to server ###############


		#this works! (for now)
		f = io.TextIOWrapper(file)
		print(f)

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

		submission_fk = sub.lastrowid
		print(submission_fk)

		#add other 'if' statements to send file to right python processor based on int_type

		#also at some point once this whole process is over we also want to save these files 
		#somewhere and convert them to their alternate format --> I know procedure to save locally 
		#but is this what we really want? --> Won't be automatic uploads elsewhere

		#this works!
		if file_type == '1':
			gmt = f
			gmt_data = [x.strip().split('\t') for x in gmt.readlines()]
			sig_version = Scripts.GMT_to_SIG(gmt_data, secure_filename(file.filename))
			print(sig_version.head())
			interactions = Scripts.SIG_to_Genes(sig_version, submission_fk, organism, engine)
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)
			

		#this works!
		if file_type == '2':
			sig = pd.read_table(f, header = None)
			if 5 not in sig.columns:
				sig = pd.read_table(f, header = None, 
				names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], sep = ' ')
			print(sig.head())
			interactions = Scripts.SIG_to_Genes(sig, submission_fk, organism, engine)
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)

	return redirect(url_for('Contribute'))


#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/new_resource', methods = ["POST"])

def new_resource():

	if request.method == 'POST':

		resource_name = request.form.get("new_resource_name")
		print(resource_name)

		resource_desc = request.form.get("new_input_description")
		print(resource_desc)

		resource_url = request.form.get("new_resource_url")
		print(resource_url)

		resource_pmid = request.form.get("new_input_pubmed")
		print(resource_pmid)

		insert_r = "INSERT IGNORE INTO resources (db_name, db_desc, db_url, pmid) VALUES" + '("%s"' %resource_name + ', "%s"' %resource_desc + ', "%s",' %resource_url  + '"%s")' %resource_pmid
		engine.execute(insert_r)

	return redirect(url_for('Contribute'))


#######################################################
##########  Retrieve Info About Submissions and Display #########
#######################################################

@app.route(entry_point+'/submission', methods = ["POST"])

def submission():
	print('nothing')

#######################################################
##########  Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
