import os, sys, subprocess, glob, openpyxl
import pandas as pd

inputdir=sys.argv[1]
outputdir=sys.argv[2]
intermediatedir=str(sys.argv[2])+'intermediate/'
currentdir=os.getcwd()
samplelistfile=sys.argv[3]
compressedfastq=".fastq.gz"
uncompressedfastq=".fastq"
fastqformat=compressedfastq

#Checking the existence of output directory and making intermediate folder.
if not os.path.exists(str(sys.argv[2])):
	os.makedirs(str(sys.argv[2]))

if not os.path.exists(str(intermediatedir)):
	os.makedirs(str(intermediatedir))

print('Input directory: ' + inputdir)
print('Output directory: ' + outputdir)
print('Current directory: ' + currentdir)
print('Sample list file: ' + samplelistfile)

#Checking the sample list and cocatenating the sequencing read files.
samplelisttable=pd.read_excel(str(samplelistfile))
samplelist=list(x for x in samplelisttable.iterrows())
print('Number of samples on the provided sample list = ' + str(len(samplelist)))
if len(samplelist)==0:
    print('The provided sample list is empty. Please input the barcodes and the samples into the excel template.')
    sys.exit(1)  # Exit the program with an error code and message
else:
    for x in samplelist:
        barcode = str(x[1][0])
        print('Barcode: ' + barcode)
        sampleID = str(x[1][1])
        print('SampleID: ' + sampleID)
        output_filename = str(sampleID) + str(fastqformat)
        concatenate_commandline = 'find ' + str(inputdir) + str(barcode) + " -name '*" + str(fastqformat) + "' -exec cat {} + > " + str(outputdir) + str(output_filename)
        print(concatenate_commandline)
        concatfiles = subprocess.Popen([concatenate_commandline], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = concatfiles.communicate()[0]
