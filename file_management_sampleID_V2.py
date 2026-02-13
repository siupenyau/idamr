import os
import sys
import subprocess
import pandas as pd
import logging

inputdir = sys.argv[1]
outputdir = sys.argv[2]
intermediatedir = os.path.join(outputdir, 'intermediate/')
currentdir = os.getcwd()
samplelistfile = sys.argv[3]
compressedfastq = ".fastq.gz"
uncompressedfastq = ".fastq"
fastqformat = compressedfastq

# Set up logging
logging.basicConfig(
    filename=os.path.join(outputdir, 'process.log'),  # Log file name
    filemode='a',
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# Checking the existence of output directory and making intermediate folder.
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

if not os.path.exists(intermediatedir):
    os.makedirs(intermediatedir)

logging.info('Input directory: %s', inputdir)
logging.info('Output directory: %s', outputdir)
logging.info('Current directory: %s', currentdir)
logging.info('Sample list file: %s', samplelistfile)

# Checking the sample list and concatenating the sequencing read files.
# Reading the sample list from CSV file instead of Excel
samplelisttable = pd.read_csv(samplelistfile)
samplelist = samplelisttable.values.tolist()

logging.info('Number of samples on the provided sample list = %d', len(samplelist))
if len(samplelist) == 0:
    logging.error('The provided sample list is empty. Please input the barcodes and the samples into the csv template.')
    sys.exit(1)  # Exit the program with an error code and message
else:
    for x in samplelist:
        barcode = str(x[0])  # First column is Barcode
        logging.info('Barcode: %s', barcode)
        sampleID = str(x[1])  # Second column is SampleID
        logging.info('SampleID: %s', sampleID)
        
        output_filename = f"{sampleID}{fastqformat}"
        concatenate_commandline = (
            f'find {inputdir}{barcode} -name "*{fastqformat}" -exec cat {{}} + > {os.path.join(outputdir, output_filename)}'
        )
        logging.info('Concatenate Command: %s', concatenate_commandline)
        
        try:
            concatfiles = subprocess.Popen(concatenate_commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = concatfiles.communicate()[0]
            logging.info('Concatenation completed for SampleID: %s', sampleID)
        except Exception as e:
            logging.error('Error during concatenation for SampleID: %s - %s', sampleID, str(e))