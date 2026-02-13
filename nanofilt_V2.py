import os
import subprocess
import glob
import sys
import logging

def setup_logging(outputdir):
    """Set up logging configuration."""
    logging.basicConfig(
        filename=os.path.join(outputdir, 'process.log'),  # Log file name
        level=logging.INFO,        # Log level
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
    )

def initialize_directories(inputdir):
    """Create output directories for filtered results."""
    filtered_dirs = ['nanofilt_16S', 'nanofilt_AMR']
    for d in filtered_dirs:
        path = os.path.join(inputdir, d)
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info('Created directory: %s', path)

def count_fastq_files(inputdir):
    """Count the number of .fastq.gz files in the directory."""
    fastq_files = glob.glob(os.path.join(inputdir, '*.fastq.gz'))
    total_files = len(fastq_files)
    logging.info('The total number of sequencing fastq.gz files in folder is: %d', total_files)
    return fastq_files

def run_nanofilt(inputdir, fastqfiledictionary):
    """Filter nanopore reads for 16S."""
    logging.info('Starting the NanoFilt filtering for 16S. Please wait.')
    for index in range(1, len(fastqfiledictionary) + 1):
        inputfastqfilename = fastqfiledictionary[index]
        output_filename = os.path.join(inputdir, 'nanofilt_16S', f"{os.path.basename(inputfastqfilename)[:-9]}_16S.fastq")
        
        nanofilt_commandline = f'gunzip -c {inputfastqfilename} | NanoFilt -q 10 -l 1300 --maxlength 1700 > {output_filename}'
        logging.info('Nanofilt command: %s', nanofilt_commandline)
        
        subprocess.run(nanofilt_commandline, shell=True)
        logging.info('Filtered file created: %s', output_filename)

def run_nanofilt_amr(inputdir, fastqfiledictionary):
    """Filter nanopore reads for AMR."""
    logging.info('Starting the NanoFilt filtering for AMR. Please wait.')
    for index in range(1, len(fastqfiledictionary) + 1):
        inputfastqfilename = fastqfiledictionary[index]
        output_filename = os.path.join(inputdir, 'nanofilt_AMR', f"{os.path.basename(inputfastqfilename)[:-9]}_AMR.fastq")
        
        nanofilt_amr_commandline = f'gunzip -c {inputfastqfilename} | NanoFilt -q 10 -l 100 --maxlength 1200 > {output_filename}'
        logging.info('Nanofilt_AMR command: %s', nanofilt_amr_commandline)
        
        subprocess.run(nanofilt_amr_commandline, shell=True)
        logging.info('Filtered file created: %s', output_filename)

def main():
    print('Starting the NanoFilt filtering. Please wait.')
    
    # Directory from the command line
    inputdir = sys.argv[1]
    outputdir = inputdir
    
    # Initialize output directories
    initialize_directories(inputdir)
    
    # Count fastq files
    fastqFile = count_fastq_files(inputdir)
    
    # Create a dictionary for fastq files
    fastqfiledictionary = {index: f for index, f in enumerate(fastqFile, start=1)}
    
    if not fastqfiledictionary:
        logging.error('No fastq.gz files found in the directory.')
        sys.exit(1)
    
    # Run NanoFilt filtering
    run_nanofilt(inputdir, fastqfiledictionary)
    
    # Run AMR NanoFilt filtering
    run_nanofilt_amr(inputdir, fastqfiledictionary)

if __name__ == '__main__':
    main()