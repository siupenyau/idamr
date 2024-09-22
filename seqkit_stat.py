import subprocess, sys
import os

# Folder path containing fastq files
folder_path = sys.argv[1] + '/nanofilt_16S/'

# Output text file path
output_file = str(folder_path) + "/readcount_16S.txt"

# List all fastq.gz files in the folder
fastq_files = [file for file in os.listdir(folder_path) if file.endswith(".fastq")]

# Open output file in write mode
with open(output_file, "w") as f:
    # Iterate through each fastq file
    for file in fastq_files:
        # Generate the command to run seqkit stat
        command = f"seqkit stat {os.path.join(folder_path, file)}"
        
        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True, text=True)
        
        # Write the output to the file
        f.write(output)
        f.write("\n")  # Add a new line after each file's output

print("Statistics for nanofilt_16S saved to:", output_file)

# Folder path containing fastq files
folder_path = sys.argv[1] + '/nanofilt_AMR/'

# Output text file path
output_file = str(folder_path) + "/readcount_AMR.txt"

# List all fastq.gz files in the folder
fastq_files = [file for file in os.listdir(folder_path) if file.endswith(".fastq")]

# Open output file in write mode
with open(output_file, "w") as f:
    # Iterate through each fastq file
    for file in fastq_files:
        # Generate the command to run seqkit stat
        command = f"seqkit stat {os.path.join(folder_path, file)}"
        
        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True, text=True)
        
        # Write the output to the file
        f.write(output)
        f.write("\n")  # Add a new line after each file's output

print("Statistics for nanofilt_AMR saved to:", output_file)

folder_path = sys.argv[1]

# Output text file path
output_file = str(folder_path) + "/readcount_total.txt"

# List all fastq.gz files in the folder
fastq_files = [file for file in os.listdir(folder_path) if file.endswith(".fastq.gz")]

# Open output file in write mode
with open(output_file, "w") as f:
    # Iterate through each fastq file
    for file in fastq_files:
        # Generate the command to run seqkit stat
        command = f"seqkit stat {os.path.join(folder_path, file)}"
        
        # Run the command and capture the output
        output = subprocess.check_output(command, shell=True, text=True)
        
        # Write the output to the file
        f.write(output)
        f.write("\n")  # Add a new line after each file's output

print("Statistics for total reads saved to:", output_file)
