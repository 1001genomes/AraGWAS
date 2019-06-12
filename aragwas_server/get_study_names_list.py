# Quick script to fetch HDF5 study information from AraGWAS
# This is run by the prepare_download.sh script
# Assumption: this must be run once the studies of interest are already in AraGWAS
import os
import argparse
import requests
import numpy as np
# import pandas as pd

def _get_study_info(study_id):
    r = requests.get('http://aragwas.1001genomes.org/api/studies/{}'.format(study_id))
    js = r.json()
    l = []
    for a in [u'phenotype', u'phenotypeToDescription', u'publication']:
        try:
            l.append(';'.join(js[a].split(',')))
        except:
            l.append('')
    return l
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type = str, help = 'Directory containing the hdf5 files.')
    args = parser.parse_args()

    # Get all hdf5 files.
    hdf5_files = [f for f in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory,f)) and os.path.splitext(f)[-1]=='.hdf5']
    info = dict()
    for hd in sorted(hdf5_files):
        # get id
        id_hd = os.path.splitext(hd)[0]
        try:
            id_hd = int(id_hd)
        except:
            print("ID {} is not numeric, skipping.".format(id_hd))
            continue
        info[id_hd] = _get_study_info(id_hd)
        print('{} done'.format(id_hd))
    # Save info to csv.
    info_csv = []
    for hd in sorted(list(info.keys())):
        info_csv.append([hd] + info[hd])
    np.savetxt(os.path.join(args.directory, 'study_info.csv'), 
            np.array(info_csv), fmt='%s', delimiter=',', header='ID,phenotype,description,publication')
    
    # pd.DataFrame(info, columns=['phenotype', 'description', 'publication']).to_csv(os.path.join(args.directory, 'study_info.csv'))


if __name__=='__main__':
    main()