import os, subprocess, glob, sys
import pandas as pd

print('Starting the NanoFilt filtering. Please wait.')

#Checking the fastq.gz files in folder
inputdir=sys.argv[1]
currentdir=os.getcwd()
fastqFile = glob.glob(str(inputdir) + '*.fastq.gz')
TotalfastqFile = sum('.fastq.gz' in f for f in fastqFile)
print('The total number of sequencing fastq.gz files in folder is: ' + str(TotalfastqFile))
fastqfiledictionary = dict(enumerate(fastqFile, 1)) #Setting a dictionary for the fastq.gz files in folder

if not os.path.exists(str(inputdir) + '/nanofilt_16S/'):
	os.makedirs(str(inputdir) + '/nanofilt_16S/')

if not os.path.exists(str(inputdir) + '/nanofilt_AMR/'):
	os.makedirs(str(inputdir) + '/nanofilt_AMR/')



#Filtering nanopore reads.
def nanofilt():
	a = 1
	Pathtofastqfile = inputdir
	inputfastqfilename = []
	commandline = ''
	while a > 0 and a <= max(fastqfiledictionary, key=int):
		inputfastqfilename = fastqfiledictionary[a]
		nanofilt_commandline = 'gunzip -c ' + str(inputfastqfilename) + ' | NanoFilt -q 10 -l 1300 --maxlength 1700 > ' + str(Pathtofastqfile) + '/nanofilt_16S/' + inputfastqfilename.rsplit('/')[-1][:-9] + '_16S.fastq'
		print('Nanofilt command: ' + nanofilt_commandline)		
		print('Input file name: ' + inputfastqfilename)
		subprocess.run(nanofilt_commandline, shell = True)
		a = a + 1

nanofilt()


#Filtering nanopore reads.
def nanofilt_AMR():
	a = 1
	Pathtofastqfile = inputdir
	inputfastqfilename = []
	commandline = ''
	while a > 0 and a <= max(fastqfiledictionary, key=int):
		inputfastqfilename = fastqfiledictionary[a]
		nanofilt_AMR_commandline = 'gunzip -c ' + str(inputfastqfilename) + ' | NanoFilt -q 10 -l 100 --maxlength 1200 > ' + str(Pathtofastqfile) + '/nanofilt_AMR/' + inputfastqfilename.rsplit('/')[-1][:-9] + '_AMR.fastq'
		print('Nanofilt_AMR command: ' + nanofilt_AMR_commandline)		
		print('Input file name: ' + inputfastqfilename)
		subprocess.run(nanofilt_AMR_commandline, shell = True)
		a = a + 1

nanofilt_AMR()
