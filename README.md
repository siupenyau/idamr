This package idamr is a bioinformatic pipeline constructed for 16S and ITS bacteria identification and antimicrobial resistance (AMR) detection, with the in-house optimized primer design and software parameter setting> The objective is to 

Installation

Conda
mamba create -n idamr -c bioconda -c conda-forge nanofilt=2.8 emu=3.2 seqkit=2.5.1 blast=2.13.0
pip install openpyxl osfclient
mamba create

Database installation
export metadb=<path-to-database>
osf -p 56uf7 fetch osfstorage/emu-prebuilt/emu.tar ${EMU_DATABASE_DIR}/emu.tar
tar -xvf ${EMU_DATABASE_DIR}/emu.tar
