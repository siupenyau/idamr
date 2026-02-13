import subprocess
import sys
import os
import logging

def setup_logging(outputdir):
    """Set up logging configuration."""
    logging.basicConfig(
        filename=os.path.join(outputdir, 'process.log'),  # Log file name
        level=logging.INFO,            # Log level
        format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
    )

def process_fastq_files(folder_path, output_filename):
    """Process FASTQ files and write their statistics."""
    logging.info(f"Processing FASTQ files in: {folder_path}")

    # List all fastq files in the folder
    fastq_files = [file for file in os.listdir(folder_path) if file.endswith(".fastq")]

    # Open output file in write mode
    with open(output_filename, "w") as f:
        # Iterate through each fastq file
        for file in fastq_files:
            # Generate the command to run seqkit stat
            command = f"seqkit stat {os.path.join(folder_path, file)}"
            logging.info(f"Running command: {command}")

            try:
                # Run the command and capture the output
                output = subprocess.check_output(command, shell=True, text=True)
                f.write(output)
                f.write("\n")  # Add a new line after each file's output
                logging.info(f"Output written for {file}")

            except subprocess.CalledProcessError as e:
                logging.error(f"Error processing {file}: {e}")

def main(input_path):
    """Main function to coordinate processing."""
    
    # Validate input path
    if not os.path.isdir(input_path):
        logging.error(f"Input path '{input_path}' does not exist.")
        sys.exit(1)

    # Set up logging
    outputdir = input_path  # Set outputdir as the same as input_path
    setup_logging(outputdir)

    # Process nanofilt_16S
    folder_path_16S = os.path.join(input_path, 'nanofilt_16S')
    output_file_16S = os.path.join(folder_path_16S, "readcount_16S.txt")
    process_fastq_files(folder_path_16S, output_file_16S)

    # Process nanofilt_AMR
    folder_path_AMR = os.path.join(input_path, 'nanofilt_AMR')
    output_file_AMR = os.path.join(folder_path_AMR, "readcount_AMR.txt")
    process_fastq_files(folder_path_AMR, output_file_AMR)

    # Process total FASTQ files
    output_file_total = os.path.join(input_path, "readcount_total.txt")
    process_fastq_files(input_path, output_file_total)

    logging.info("All statistics have been processed and saved.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python seqkit_stat.py <input_folder>")
        sys.exit(1)  # Exit with an error code
    main(sys.argv[1])