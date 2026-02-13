import os
import subprocess
import glob
import sys
import logging

# Function to set up logging
def setup_logging(outputdir):
    """Set up logging configuration."""
    logging.basicConfig(
        filename=os.path.join(outputdir, 'process.log'),  # Log file name
        level=logging.INFO,                  # Log level
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
    )

def initialize_directories(inputdir):
    """Create output directory for EMU results."""
    emu_dir = os.path.join(inputdir, 'emu')
    if not os.path.exists(emu_dir):
        os.makedirs(emu_dir)
        logging.info('Created directory: %s', emu_dir)
    return emu_dir

def count_fastq_files(inputdir):
    """Count the number of .fastq files in the nanofilt_16S directory."""
    fastqFile = glob.glob(os.path.join(inputdir, 'nanofilt_16S', '*.fastq'))
    total_files = len(fastqFile)
    logging.info('The total number of sequencing fastq files in folder is: %d', total_files)
    return fastqFile

def run_emu(inputdir, pathtoemudb, fastqfiledictionary):
    """Run EMU classification on the fastq files."""
    logging.info('Starting the EMU classification. Please wait.')
    
    for index in range(1, len(fastqfiledictionary) + 1):
        inputfastqfilename = fastqfiledictionary[index]
        emu_commandline = (
            f'emu abundance {inputfastqfilename} --output-dir {os.path.join(inputdir, "emu")} '
            f'--thread 12 --db {pathtoemudb} --keep-counts'
        )
        
        logging.info('Emu command: %s', emu_commandline)
        logging.info('Input file name: %s', inputfastqfilename)
        
        try:
            subprocess.run(emu_commandline, shell=True, check=True)
            logging.info('Successfully processed file: %s', inputfastqfilename)
        except subprocess.CalledProcessError as e:
            logging.error('Error processing file %s: %s', inputfastqfilename, str(e))

def main():
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python emu_V2.py <input_directory> <emudb_path>")
        sys.exit(1)

    inputdir = sys.argv[1]
    outputdir = inputdir  # Set output directory to input directory
    pathtoemudb = os.path.join(sys.argv[2], 'EMU_database')
    
    # Setup logging
    setup_logging(outputdir)
    
    # Initialize output directory
    emu_dir = initialize_directories(inputdir)
    
    # Count fastq files
    fastqFile = count_fastq_files(inputdir)
    
    # Create a dictionary for fastq files
    fastqfiledictionary = {index: f for index, f in enumerate(fastqFile, start=1)}
    
    if not fastqfiledictionary:
        logging.error('No fastq files found in the directory.')
        sys.exit(1)
    
    # Run EMU classification
    run_emu(inputdir, pathtoemudb, fastqfiledictionary)

if __name__ == '__main__':
    main()