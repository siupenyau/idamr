import os, subprocess, glob, sys
import pandas as pd

print('Starting the Emu classification. Please wait.')

#Checking the fastq files in folder
inputdir=sys.argv[1]
pathtoemudb=sys.argv[2] + str('/EMU_database/')
currentdir=os.getcwd()
fastqFile = glob.glob(str(inputdir) + '/nanofilt_16S/*.fastq')
TotalfastqFile = sum('.fastq' in f for f in fastqFile)
print('The total number of sequencing fastq files in folder is: ' + str(TotalfastqFile))
fastqfiledictionary = dict(enumerate(fastqFile, 1)) #Setting a dictionary for the fastq files in folder

if not os.path.exists(str(inputdir) + '/emu/'):
	os.makedirs(str(inputdir) + '/emu/')


# Starting the Emu classification
def emu():
	a = 1
	Pathtofastqfile = str(inputdir) + '/nanofilt_16S/'
	inputfastqfilename = []
	commandline = ''
	while a > 0 and a <= max(fastqfiledictionary, key=int):
		inputfastqfilename = fastqfiledictionary[a]
		emu_commandline = 'emu abundance ' + str(inputfastqfilename) + ' --output-dir ' + str(inputdir) + '/emu/ --thread 12 --db ' + str(pathtoemudb) + ' --keep-counts'
		print('Emu command: ' + emu_commandline)		
		print('Input file name: ' + inputfastqfilename)
		subprocess.run(emu_commandline, shell = True)
		a = a + 1

emu()
