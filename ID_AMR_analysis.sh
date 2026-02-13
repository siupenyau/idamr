#!/bin/sh

echo "Welcome to ID_AMR (Version 1.0) analysis pipeline. It is for pathogen and antimicrobial resistance detection."
echo "This workflow is co-designed by Hiu Yin Lao, Timothy T.L. Ng, Gilman K.H. Siu"

# Usage message
usage() {
  echo "Usage: $0 <input folder of sequencing read files> <output folder> <samplelist> <database folder>"
  exit 1
}

# Check if the number of arguments is correct
if [ "$#" -ne 4 ]; then
  echo "Error: Incorrect number of arguments."
  usage
fi

# Check if input folder exists
if [ ! -d "$1" ]; then
  echo "Error: Input folder '$1' does not exist."
  usage
fi

# Check if output folder exists; if not, create it
if [ ! -d "$2" ]; then
  echo "Output folder '$2' does not exist. Creating it."
  mkdir -p "$2"
fi

# Check if samplelist file exists
if [ ! -f "$3" ]; then
  echo "Error: Sample list '$3' does not exist."
  usage
fi

# Check if database folder exists
if [ ! -d "$4" ]; then
  echo "Error: Database folder '$4' does not exist."
  usage
fi

# Proceed with the analysis
python3 file_management_sampleID_V2.py "$1" "$2" "$3"

# Starting the NanoFilt filtering
python3 nanofilt_V2.py "$2"

python3 emu_V2.py "$2" "$4"

export BLASTDB=$BLASTDB:"$4/blast_db/"

python3 ITS_qcov_60_V2.py "$2" "$4"

python3 AMR_qcov_80_V2.py "$2" "$4"

python3 seqkit_stat_V2.py "$2"

echo "Analysis is complete. Thank you for using ID_AMR."
echo "For any questions, please contact Hiu Yin Lao (hiu-yin.lao@connect.polyu.hk), Timothy T.L. Ng (tl-timothy.ng@connect.polyu.hk), or Gilman K.H. Siu (gilman.siu@polyu.edu.hk)."
echo "Have a nice day!"