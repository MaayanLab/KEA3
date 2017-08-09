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
import datetime
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
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER ##
app.secret_key = 'MySecretKey'

# Setup entry point
entry_point = '/bionetbay'

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
###  About Page
#########################

@app.route(entry_point+'/about')

def about():
	
	return render_template('about.html')

#########################
### Kinases Table
#########################

@app.route(entry_point+'/kinases')

def index():
	
	# Define main column names (for now) --> be sure to include statistics columns later!!!!!
	#maybe include resource description?
	#column names not in same order of the table, so will need to make sure it all matches
	colnames = ["Submission Title", "Date of Contribution", "Resource Name", "Interaction Type", "Processing Script", "Processed File", "Kinases", "Substrates", "Unique Terms", "Average Substrates per Kinase", "PMID"]

	interaction_type = "kinase-substrate"

	submissions = pd.read_sql_query('SELECT submission_name, date_contributed, processing_script, hub_terms, target_terms, unique_terms, avg_term, db_name, db_url, pmid, interaction_name, type_name FROM statistics LEFT JOIN submissions ON submissions.id = statistics.submission_fk LEFT JOIN resources ON resources.id = submissions.resource_fk LEFT JOIN interaction_type ON interaction_type.id = submissions.submission_type_fk LEFT JOIN file_types ON file_types.id = submissions.file_type_fk WHERE interaction_name = "{interaction_type}"'.format(**locals()), engine)
	print(submissions)

	return render_template('submissions.html', colnames = colnames, submissions = submissions)


#########################
###  PPI Table
#########################

@app.route(entry_point+'/proteins')

def ppi():

# Define main column names (for now) --> be sure to include statistics columns later!!!!!
	#maybe include resource description?
	#column names not in same order of the table, so will need to make sure it all matches
	colnames = ["Submission Title", "Date of Contribution", "Resource Name", "Interaction Type", "Processing Script", "Processed File", "Total Proteins", "Interactions", "Hub Proteins", "Average Interactions per Protein", "PMID"]

	interaction_type = "protein-protein"

	submissions = pd.read_sql_query('SELECT submission_name, date_contributed, processing_script, interaction_num, hub_terms, unique_terms, avg_term, db_name, db_url, pmid, interaction_name, type_name FROM statistics LEFT JOIN submissions ON submissions.id = statistics.submission_fk LEFT JOIN resources ON resources.id = submissions.resource_fk LEFT JOIN interaction_type ON interaction_type.id = submissions.submission_type_fk LEFT JOIN file_types ON file_types.id = submissions.file_type_fk WHERE interaction_name = "{interaction_type}"'.format(**locals()), engine)
	print(submissions)

	return render_template('submissions.html', colnames = colnames, submissions = submissions)


#########################
###  TF Page
#########################

@app.route(entry_point+'/tf')

def TF():
	
	# Define main column names (for now) --> be sure to include statistics columns later!!!!!
	#maybe include resource description?
	#column names not in same order of the table, so will need to make sure it all matches
	colnames = ["Submission Title", "Date of Contribution", "Resource Name", "Interaction Type", "Processing Script", "Processed File", "Transcription Factors (TF)", "Targets", "Unique Terms", "Average Targets per TF", "PMID"]

	interaction_type = "transcription factor-target"

	submissions = pd.read_sql_query('SELECT submission_name, date_contributed, processing_script, hub_terms, target_terms, unique_terms, avg_term, db_name, db_url, pmid, interaction_name, type_name FROM statistics LEFT JOIN submissions ON submissions.id = statistics.submission_fk LEFT JOIN resources ON resources.id = submissions.resource_fk LEFT JOIN interaction_type ON interaction_type.id = submissions.submission_type_fk LEFT JOIN file_types ON file_types.id = submissions.file_type_fk WHERE interaction_name = "{interaction_type}"'.format(**locals()), engine)
	print(submissions)

	return render_template('submissions.html', colnames = colnames, submissions = submissions)

#########################
###  Contribute
#########################

@app.route(entry_point+'/contribute')

def Contribute():

	# Query Dataframes which contain options for the 'Contribute' form
	species_df = pd.read_sql_query('SELECT * FROM species', engine)
	resources = pd.read_sql_query('SELECT * FROM resources', engine)
	interaction_type_df = pd.read_sql_query('SELECT * FROM interaction_type', engine)
	file_types = pd.read_sql_query('SELECT * FROM file_types', engine)

	# Pass the dataframes containing user options to the html template
	return render_template('contribute.html', int_type_df = interaction_type_df,
	species_df=species_df, resources=resources, file_types = file_types)


#########################
###  Gene
#########################

@app.route(entry_point+'/gene')

def gene():

############################# Searches for Gene using Input Button #################################

#Tentative Query Script
	
	#Retrieve searched input string from the url
	#If the gene is of type string, uppercase the string
	# (so it matches the format of strings in the database)
	gene_string = request.args.get('input_gene')
	if type(gene_string) == type('hello'):
		gene_string = gene_string.upper()
	
	#Retrieve genes and species tables from database
	#Will be used to search for genes with both same gene_symbol
	#nd same species
	genes = pd.read_sql_query('SELECT * FROM genes', engine)
	genes.set_index('id', inplace = True)

	species = pd.read_sql_query('SELECT * FROM species', engine)
	species.set_index('id', inplace = True)

	#define boolean variable, 'True' if the db has a gene matching
	#input gene string or 'False' otherwise
	boole = genes.gene_symbol.str.contains('%s' %gene_string)

	#Define table containing genes with match to input string (if any)
	contains = genes.loc[boole]

	#Pass variables to html template
	return render_template('gene.html', gene_string=gene_string, contains=contains, species = species)

################################ Chooses Gene of Interest in Table #################################

@app.route(entry_point+'/interactions')

def gene_symbol():

	genes = pd.read_sql_query('SELECT * FROM genes', engine)
	genes.set_index('id', inplace = True)

	#will return the element of the dict related to the gene symbol
	# 'gene_s' is in format 'Gene-Symbol_Species' for specificity
	gene_s = request.args.get('gene_symbol', 'None')

	#Counts how many '_' are in the string
	count = gene_s.count("_")

	#Splits species name from the gene_symbol and saves it as 'organism'
	organism = gene_s.split("_", count)[-1]
	gene_s = "_".join(gene_s.split("_", count)[:-1])

	#Create df with data from database
	gene_interactions = pd.read_sql_query('''SELECT source_gene_fk, target_gene_fk, db_name, submission_type_fk, interaction_name FROM interactions i 
		LEFT JOIN submissions s 
			ON s.id = i.submission_fk 
		LEFT JOIN resources r 
			ON r.id = s.resource_fk 
		LEFT JOIN interaction_type it 
			ON it.id = s.submission_type_fk'''.format(**locals()), con = engine)

	#Obtain data on gene specifically indicated by 'gene_s' input gene
	gene_info = pd.read_sql_query('''SELECT g.id, gene_symbol, description, species_name FROM genes g LEFT JOIN species s ON s.id = g.species_fk'''.format(**locals()), con = engine)
	g = gene_info.query('gene_symbol==@gene_s and species_name == @organism')
	g.set_index('id', inplace = True)


	##################################################################### Subsetting Interaction Data ###################################################

	############# Subsetting Kinase Source/Target Data #############

	# Subset interactions where selected gene is a source in kinase-substrate interaction
	kin_source_df = gene_interactions.query('submission_type_fk ==1 and source_gene_fk == @g.index[0]')
	print(kin_source_df)
	kin_source_df.drop('source_gene_fk', axis =1, inplace=True)
	kin_source_df.drop_duplicates(inplace = True)

	# Subset interactions where selected gene is a target in kinase-substrate interaction
	kin_target_df = gene_interactions.query("target_gene_fk==@g.index[0] and submission_type_fk ==1")
	kin_target_df.drop('target_gene_fk', axis =1, inplace=True)
	kin_target_df.drop_duplicates(inplace = True)

	############# Subsetting TF Source/Target Data #############

	# Subset interactions where selected gene is a source in tf-target interaction
	tf_source_df = gene_interactions.query('submission_type_fk == 3 and source_gene_fk == @g.index[0]')
	tf_source_df.drop('source_gene_fk', axis =1, inplace=True)
	tf_source_df.drop_duplicates(inplace = True)

	# Subset interactions where selected gene is a target in tf-target interaction
	tf_target_df = gene_interactions.query("target_gene_fk==@g.index[0] and submission_type_fk == 3")
	tf_target_df.drop('target_gene_fk', axis =1, inplace=True)
	tf_target_df.drop_duplicates(inplace = True)

	############# Subsetting PPI Interaction Data #############

	# Subset protein-protein interactions for the selected gene
	ppi_df = gene_interactions.query("submission_type_fk == 2 and target_gene_fk==@g.index[0] or submission_type_fk == 2 and source_gene_fk==@g.index[0]")

	#Remove 'source'/'target' dataframe format for ppi interactions
	# And consolidate to a single column 'genes'
	ppi_df['gene'] = "" 
	#ppi_df['gene'] = [genes.gene_symbol[rowData.source_gene_fk] if rowData.source_gene_fk != gene_info.index[0] else genes.gene_symbol[rowData.target_gene_fk] for index, rowData in ppi_df.iterrows()]

	# this works!! But takes a longer amount of time than is ideal
	for index, rowData in ppi_df.iterrows():
		if rowData.source_gene_fk != gene_info.index[0]:
			ppi_df.gene[index] = genes.gene_symbol[rowData.source_gene_fk]
		else:
			ppi_df.gene[index] = genes.gene_symbol[rowData.target_gene_fk]

	# Drop unnecessary columns and duplicates from the df
	ppi_df.drop(['source_gene_fk', 'target_gene_fk'], axis =1, inplace = True)
	ppi_df.drop_duplicates(inplace=True)

	# Return all variables to render corresponding html template
	return render_template('gene_symbol.html', gene_s=gene_s, genes = genes, g=g, gene_info=gene_info, kin_source_df=kin_source_df, kin_target_df = kin_target_df, ppi_df=ppi_df, tf_source_df=tf_source_df, tf_target_df = tf_target_df)

#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/upload', methods = ["POST"])

def upload():

	if request.method == 'POST':

		#Checks if username is correct
		user_name = request.form.get('input_user')
		if user_name != '':
			return render_template('invalid_username.html') 

		#Checks if password is correct
		password = request.form.get('input_password')
		if password != '':
			return render_template('invalid_password.html')


		# Retrieve data submitted through the 'Contribute' form
		submission = request.form.get('new_submission_name')

		now = datetime.datetime.now().date()

		notebook = request.form.get("notebook_link")
		
		int_type = request.form.get('input_interaction')

		organism = request.form.get('input_species')
		
		resource = request.form.get('input_resource')

		file_type = request.form.get('input_type')

		file = request.files['input_file']


		###### Processing 'file' and uploading data to server ###############


		#wrap FileStorage object in a TextIOWrapper
		#So file can later be used 
		f = io.TextIOWrapper(file)

		# Submit data on submissions before processing the data
		#Must be done prior to processing the data so that the
		#submissions foreign key can be integrated into the
		# interactions table inserted when the file is processed
		submissions = pd.DataFrame(columns = ['submission_name', 'submission_type_fk', 'resource_fk'])
		submissions = submissions.append([{
			'submission_name': submission,
			'submission_type_fk': int(int_type),
			'resource_fk': int(resource),
			'date_contributed': str(now),
			'processing_script': str(notebook),
			'file_type_fk': int(file_type)
			}])

		#Insert submissions into the table
		insert_s = "INSERT INTO submissions (submission_name, submission_type_fk, resource_fk, date_contributed, processing_script, file_type_fk) VALUES"+ ', '.join(['("{submission_name}", {submission_type_fk}, {resource_fk}, "{date_contributed}", "{processing_script}", {file_type_fk})'.format(**rowData) for index, rowData in submissions.iterrows()])
		sub = engine.execute(insert_s)

		#Retrieve id of last insert into a database table (i.e. submission foreign key)
		submission_fk = sub.lastrowid
		print(submission_fk)

		#Process a gmt file if file type = 1
		if file_type == '1':
			gmt = f
			gmt_data = [x.strip().split('\t') for x in gmt.readlines()]
			sig_version = Scripts.GMT_to_SIG(gmt_data, secure_filename(file.filename))
			interactions = Scripts.SIG_to_Genes(sig_version, submission_fk, organism, engine)
			if type(interactions) == type("Error"):
				return render_template('processing_error.html')
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)

		##### Calculate Website Statistics for 'Submissions' Page for GMT File ################

			stat_df = sig_version.drop([1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], axis=1)
			stat_df.columns = ['ProteinA', 'ProteinB']

			# First stat: Number of Total Interactions
			interaction_num = len(stat_df)

			# Second stat: Number of Sources/Hubs
			hub_terms = len(stat_df.ProteinA.unique())
			print(hub_terms)

			# Third stat: Number of Targets
			target_terms = len(stat_df.ProteinB.unique())
			print(target_terms)		

			#Fourth stat: Total Number of Unique Terms
			if stat_df['ProteinA'].str.contains('_').all():
				stat_df['ProteinA'] = [x.split('_')[:-1] for x in stat_df.ProteinA]
				stat_df['ProteinA'] = ['_'.join(x) for x in stat_df['ProteinA']]

			if stat_df['ProteinA'].str.contains('-').all():
				stat_df['ProteinA'] = [x.split('-')[:-1] for x in stat_df.ProteinA]
				stat_df['ProteinA'] = ['-'.join(x) for x in stat_df['ProteinA']]

			else:
				pass

			if stat_df['ProteinB'].str.contains(',').all():
				stat_df['ProteinB'] = [x.split(',')[:-1] for x in stat_df.ProteinB]
				stat_df['ProteinB'] = [','.join(x) for x in stat_df['ProteinB']]

			else:
				pass

			unique_terms = len(pd.concat([stat_df.ProteinA, stat_df.ProteinB], axis = 0).unique())
			print(unique_terms)

			#Fifth stat: Avg. Interactions per Term
			stat_df.set_index('ProteinA', inplace=True)
			stat_df = stat_df.groupby('ProteinA').agg(lambda x: tuple(x))
			stat_df['targets'] = [int(len(lst)) for source, lst in stat_df['ProteinB'].iteritems()]

			avg_term = stat_df.targets.mean(axis = 0)
			print(round(avg_term))

			insert_stat = "INSERT INTO statistics (interaction_num, hub_terms, target_terms, unique_terms, avg_term, submission_fk) VALUES" + '(%d' %interaction_num + ', %d' %hub_terms + ', %d,' %target_terms + '%d,' %unique_terms + '%d,' %avg_term + ' %d)' %submission_fk
			engine.execute(insert_stat)


		#Process a sig file if the file type = 2
		if file_type == '2':
			sig = pd.read_table(f, header = None)
			if len(sig.columns) != 13:
				sig = pd.read_table(f, header = None, 
				names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], sep = ' ')
			interactions = Scripts.SIG_to_Genes(sig, submission_fk, organism, engine)
			if type(interactions) == type("Error"):
				return render_template('processing_error.html')
			insert_gene = "INSERT INTO interactions (source_gene_fk, target_gene_fk, submission_fk) VALUES"+ ', '.join(['({source_gene_fk}, {target_gene_fk}, {submission_fk})'.format(**rowData) for index, rowData in interactions.iterrows()])
			engine.execute(insert_gene)


			##### Calculate Website Statistics for 'Submissions' Page for GMT File ################

			stat_df = sig.drop([1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12], axis=1)
			stat_df.columns = ['ProteinA', 'ProteinB']

			# First stat: Number of Total Interactions
			interaction_num = len(stat_df)

			# Second stat: Number of Sources/Hubs
			hub_terms = len(stat_df.ProteinA.unique())
			print(hub_terms)

			# Third stat: Number of Targets
			target_terms = len(stat_df.ProteinB.unique())
			print(target_terms)		

			#Fourth stat: Total Number of Unique Terms
			if stat_df['ProteinA'].str.contains('_').all():
				stat_df['ProteinA'] = [x.split('_')[:-1] for x in stat_df.ProteinA]
				stat_df['ProteinA'] = ['_'.join(x) for x in stat_df['ProteinA']]

			if stat_df['ProteinA'].str.contains('-').all():
				stat_df['ProteinA'] = [x.split('-')[:-1] for x in stat_df.ProteinA]
				stat_df['ProteinA'] = ['-'.join(x) for x in stat_df['ProteinA']]

			else:
				pass

			if stat_df['ProteinB'].str.contains(',').all():
				stat_df['ProteinB'] = [x.split(',')[:-1] for x in stat_df.ProteinB]
				stat_df['ProteinB'] = [','.join(x) for x in stat_df['ProteinB']]

			else:
				pass

			unique_terms = len(pd.concat([stat_df.ProteinA, stat_df.ProteinB], axis = 0).unique())
			print(unique_terms)

			#Fifth stat: Avg. Interactions per Term
			stat_df.set_index('ProteinA', inplace=True)
			stat_df = stat_df.groupby('ProteinA').agg(lambda x: tuple(x))
			stat_df['targets'] = [int(len(lst)) for source, lst in stat_df['ProteinB'].iteritems()]

			avg_term = stat_df.targets.mean(axis = 0)
			print(round(avg_term))

			insert_stat = "INSERT INTO statistics (interaction_num, hub_terms, target_terms, unique_terms, avg_term, submission_fk) VALUES" + '(%d' %interaction_num + ', %d' %hub_terms + ', %d,' %target_terms + '%d,' %unique_terms + '%d,' %avg_term + ' %d)' %submission_fk
			engine.execute(insert_stat)


	#Return to 'Contribute' page after making the submission
	return redirect(url_for('Contribute'))

#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/contribute/resource')

def resource():
	
	#Render html file with form to add a new resource
	return render_template('new_resource.html')



#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/new_resource', methods = ["POST"])

def new_resource():

	# Obtain information from form and insert it into the resources table
	if request.method == 'POST':

		resource_name = request.form.get("new_resource_name")

		resource_desc = request.form.get("new_input_description")

		resource_url = request.form.get("new_resource_url")

		resource_pmid = request.form.get("new_input_pubmed")

		insert_r = "INSERT IGNORE INTO resources (db_name, db_desc, db_url, pmid) VALUES" + '("%s"' %resource_name + ', "%s"' %resource_desc + ', "%s",' %resource_url  + '"%s")' %resource_pmid
		engine.execute(insert_r)

	# Return to 'Contribute' page so user can use a new resource
	return redirect(url_for('Contribute'))

#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/contribute/interaction_type')

def int_type():
	
	#Render html file with form to add a new interaction type
	return render_template('new_interaction_type.html')



#######################################################
##########  Retrieve Info From Submitted form #########
#######################################################

@app.route(entry_point+'/new_interaction_type', methods = ["POST"])

def new_interaction():
	# Obtain information from form and insert it into the interaction_typee table
	if request.method == 'POST':

		int_type = request.form.get("new_interaction_type")

		insert_i = "INSERT INTO interaction_type (interaction_name) VALUES" + '("%s")' %int_type
		engine.execute(insert_i)

	# Return to 'Contribute' page so user can use the new interaction_type
	return redirect(url_for('Contribute'))

#######################################################
#####  Retrieve Info About Submissions and Display ####
#######################################################

@app.route(entry_point+'/submission') #EDIT!!!!!

def submission():

	# Define main column names (for now) --> be sure to include statistics columns later!!!!!
	#maybe include resource description?
	#column names not in same order of the table, so will need to make sure it all matches
	colnames = ["Submission Title", "Date of Contribution", "Resource Name", "Interaction Type", "Processing Script", "Processed File", "Interactions", "Source Proteins", "Target Proteins", "Total Proteins", "Average Interactions per Protein", "PMID"]

	submissions = pd.read_sql_query('SELECT submission_name, date_contributed, processing_script, interaction_num, hub_terms, target_terms, unique_terms, avg_term, db_name, db_url, pmid, interaction_name, type_name FROM statistics LEFT JOIN submissions ON submissions.id = statistics.submission_fk LEFT JOIN resources ON resources.id = submissions.resource_fk LEFT JOIN interaction_type ON interaction_type.id = submissions.submission_type_fk LEFT JOIN file_types ON file_types.id = submissions.file_type_fk '.format(**locals()), engine)
	print(submissions)

	return render_template('submissions.html', colnames = colnames, submissions = submissions)


#######################################################
##########  Retrieve Info About Submissions and Display #########
#######################################################

@app.route(entry_point+'/file', methods = ["GET"])

def get_file():

	submission_name = request.args.get("submission")

	interaction_dataframe = pd.read_sql_query('SELECT source_gene_fk, target_gene_fk, interaction_name, type_name FROM interactions i LEFT JOIN submissions s ON s.id = i.submission_fk LEFT JOIN interaction_type it ON it.id = s.submission_type_fk LEFT JOIN file_types f ON f.id = s.file_type_fk WHERE submission_name = "{submission_name}"'.format(**locals()), engine)
	print(interaction_dataframe)

	genes = pd.read_sql_query('SELECT * FROM genes', engine)

	labeled_interaction_dataframe = interaction_dataframe.merge(genes, left_on = 'source_gene_fk', right_on = 'id').rename(columns = {'gene_symbol': 'source_gene_symbol'}).merge(genes, left_on = 'target_gene_fk', right_on = 'id').rename(columns = {'gene_symbol': 'target_gene_symbol'})[['source_gene_symbol', 'target_gene_symbol', 'interaction_name', 'type_name']].set_index('source_gene_symbol')

	gmt_string = ""

	if labeled_interaction_dataframe.type_name.all() == 'GMT':
		gmt_string = "<br>".join(["\t".join([source_gene_symbol, 'None']+list(labeled_interaction_dataframe.loc[source_gene_symbol,"target_gene_symbol"])) for source_gene_symbol in labeled_interaction_dataframe.index.unique()])
	elif labeled_interaction_dataframe.type_name.all() == 'SIG':

		labeled_interaction_dataframe.reset_index(inplace=True)

		labeled_interaction_dataframe. drop(['type_name', 'interaction_name'], axis=1, inplace=True)
	
		for index, rowData in labeled_interaction_dataframe.iterrows():
			gmt_string = "<br>".join(["\t".join([rowData.source_gene_symbol, 'na', "na", "na", "na", rowData.target_gene_symbol, "na", "na", "na", "na", "na", "na", "na"]), gmt_string])

	return gmt_string
	
	

#######################################################
##########  Run Flask App ###########################
#######################################################
# Run App
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
