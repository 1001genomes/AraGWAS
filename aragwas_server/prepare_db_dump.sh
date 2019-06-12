#!/bin/bash
# Script to generate a study list and compress hdf5 files.
directory=aragwas_data # CHANGE THIS FOR PRODUCTION?

python get_study_names_list.py -d $directory

# Zip them
zip $directory/aragwas_db.zip $directory/*.hdf5 $directory/study_info.csv
