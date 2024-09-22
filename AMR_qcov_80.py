import os, subprocess, glob, shutil, sys
import pandas as pd

print('Starting the AMR analysis. Please wait.')

inputdir=sys.argv[1]
amrdb=sys.argv[2]+str('/amr_db/')
currentdir=os.getcwd()

if not os.path.exists(str(inputdir) + '/amr_results/'):
	os.makedirs(str(inputdir) + '/amr_results/')


#Checking the sequencing alignment FASTA files in folder
FASTAFile = glob.glob(str(inputdir) + '/nanofilt_AMR/*.fasta')
TotalFASTAFile = sum('.fasta' in f for f in FASTAFile)
print('The total number of sequencing FASTA files is: ' + str(TotalFASTAFile))
FASTAfiledictionary = dict(enumerate(FASTAFile, 1)) #Setting a dictionary for the FASTA files in folder


#Submitting the FASTA files to AMR analysis.
def amr_analysis():
	b = 1
	PathtoFASTAfile = str(inputdir) + '/nanofilt_AMR/'
	inputFASTAfilename = []
	commandline = ''
	while b > 0 and b <= max(FASTAfiledictionary, key=int):
		inputFASTAfilename = FASTAfiledictionary[b]
		FASTAto16SMicrobial_commandline = 'blastn -db ' + str(amrdb) +'/AMR_CDS -num_threads 8 -perc_identity 95 -qcov_hsp_perc 80 -outfmt "6 qseqid sseqid sscinames qcovs pident qstart qend sstart send evalue" -max_target_seqs 1 -query ' + str(inputFASTAfilename) + ' -out ' + str(inputdir) + '/amr_results/' + inputFASTAfilename.rsplit('/')[-1][:-6] + '_hit_table.csv'
		print('BLASTN command: ' + FASTAto16SMicrobial_commandline)		
		print('Input file name: ' + inputFASTAfilename)
		subprocess.run(FASTAto16SMicrobial_commandline, shell = True)
		b = b + 1

amr_analysis()

#Checking the sequencing alignment csv files in folder
CSVFile = glob.glob(str(inputdir) + '/amr_results/*.csv')
TotalCSVFile = sum('.csv' in f for f in CSVFile)
print('The total number of sequencing csv files is: ' + str(TotalCSVFile))
CSVfiledictionary = dict(enumerate(CSVFile, 1)) #Setting a dictionary for the CSV files in folder

def speciesidentification():
	c = 1
	PathtoCSVfile = str(inputdir) + '/amr_results/'
	inputCSVfilename = []
	while c > 0 and c <= max(CSVfiledictionary, key=int):
		inputCSVfilename = CSVfiledictionary[c]
		pdcsv = pd.read_csv(str(inputCSVfilename), delimiter = '	', names = ["query_id", "subject_id", "scientific_name", "query_coverage", "%identity", "query_start", "query_end", "subject_start", "subject_end", "e_value"], index_col=False)
		Query_dict = dict(enumerate(pdcsv["query_id"].unique(), 1))
		d = 1
		if len(Query_dict)==0:
			pass
		else:
			while d > 0 and d <= max(Query_dict, key=int):
				e = 0
				Specificquerytolist = pdcsv.index[pdcsv['query_id'] == str(Query_dict[d])].tolist()
				if e >= 0 and e <= int(len(Specificquerytolist) - 1):
					fw = open(str(inputCSVfilename)[:-4] + '_top' + str(e+1) + '_extraction.csv', 'a')
					Specificqueryquery = pdcsv.loc[Specificquerytolist[e], 'query_id']
					Specificquerysubject = pdcsv.loc[Specificquerytolist[e], 'subject_id']
					Specificqueryscientificname = pdcsv.loc[Specificquerytolist[e], 'scientific_name']
					Specificqueryquerycoverage = pdcsv.loc[Specificquerytolist[e], 'query_coverage']
					Specificqueryidentity = pdcsv.loc[Specificquerytolist[e], '%identity']
					Specificqueryquerystart = pdcsv.loc[Specificquerytolist[e], 'query_start']
					Specificqueryqueryend = pdcsv.loc[Specificquerytolist[e], 'query_end']
					Specificquerysubjectstart = pdcsv.loc[Specificquerytolist[e], 'subject_start']
					Specificquerysubjectend = pdcsv.loc[Specificquerytolist[e], 'subject_end']
					Specificqueryevalue = pdcsv.loc[Specificquerytolist[e], 'e_value']
					fw.write(str(Specificqueryquery) + ',' + str(Specificquerysubject) + ',' + str(Specificqueryscientificname) + ',' + str(Specificqueryquerycoverage) + ',' + str(Specificqueryidentity) + ',' + str(Specificqueryquerystart) + ',' + str(Specificqueryqueryend) + ',' + str(Specificquerysubjectstart) + ',' + str(Specificquerysubjectend) + ',' + str(Specificqueryevalue) + ',' + '\n')
					fw.close()
				d = d + 1
		c = c + 1

speciesidentification()

ExtCSVFile = glob.glob(str(inputdir) + '/amr_results/*_extraction.csv')
TotalExtCSVFile = sum('_extraction.csv' in f for f in ExtCSVFile)
print('The total number of sequencing ranked csv files is: ' + str(TotalExtCSVFile))
ExtCSVfiledictionary = dict(enumerate(ExtCSVFile, 1)) #Setting a dictionary for the CSV files in folder

def speciesanalysis():
	f = 1
	PathtoExtCSVfile = str(inputdir) + '/amr_results/'
	inputExtCSVfilename = []
	while f > 0 and f <= max(ExtCSVfiledictionary, key=int):
		inputExtCSVfilename = ExtCSVfiledictionary[f]
		pdcsv = pd.read_csv(str(inputExtCSVfilename), delimiter = ',', names = ["query_id", "subject_id", "scientific_name", "query_coverage", "%identity", "query_start", "query_end", "subject_start", "subject_end", "e_value"], index_col=False)
		Species_dict = dict(enumerate(pdcsv["subject_id"].unique(), 1))
		g = 1
		fw2 = open(str(inputExtCSVfilename)[:-4] + '_and_analysis.csv', 'w') 
		while g > 0 and g <= max(Species_dict, key=int):
			Species_name = str(Species_dict[g])
			Species_count = pdcsv.query('subject_id == ' + '"' + str(Species_dict[g]) + '"').subject_id.count()
			fw2.write(Species_name + '|' + str(Species_count) + '\n')
			g = g + 1
		fw2.close()
		f = f + 1

speciesanalysis()

print('AMR analysis is complete. Please check the results in folder.')
