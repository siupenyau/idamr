#!/bin/sh

echo "Welcome to ID_AMR (Version 1.0) analysis pipeline. It is for pathogen and antimicrobial resistance detection."
echo "This workflow is co-designed by Hiu Yin Lao, Timothy T.L. Ng, Gilman K.H. Siu"

python3 file_management_sampleID.py $1 $2 $3

#Starting the NanoFilt filtering
python3 nanofilt.py $2

python3 emu.py $2 $4

export BLASTDB=$BLASTDB:$4/blast_db/

python3 ITS_qcov_60.py $2 $4

python3 AMR_qcov_80.py $2 $4

python3 seqkit_stat.py $2

echo "Analysis is complete. Thank you for using ID_AMR"
echo "For any questions, please contact Hiu Yin Lao (hiu-yin.lao@connect.polyu.hk), Timothy T.L. Ng (tl-timothy.ng@connect.polyu.hk), or Gilman K.H. Siu (gilman.siu@polyu.edu.hk)"
echo "Have a nice day!"
