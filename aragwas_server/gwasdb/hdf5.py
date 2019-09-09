"""
functions to load pvalues from hdf5 files
"""
import math, csv
import numpy as np
import h5py


def _filter_by_maf( top_assocations, maf_filter):
    if (maf_filter == 0):
        return top_assocations
    top_mafs = top_assocations[2]
    maf_filter_cond = top_mafs > maf_filter
    return (np.compress(maf_filter_cond, top_assocations[0]), np.compress(maf_filter_cond, top_assocations[1]),np.compress(maf_filter_cond, top_mafs), np.compress(maf_filter_cond, top_assocations[3]), np.compress(maf_filter_cond, top_assocations[4]), np.compress(maf_filter_cond, top_assocations[5]))

def _filter_by_mac( top_assocations, mac_filter):
    if (mac_filter == 0):
        return top_assocations
    top_macs = top_assocations[3]
    mac_filter_cond = top_macs > mac_filter
    return (np.compress(mac_filter_cond, top_assocations[0]), np.compress(mac_filter_cond, top_assocations[1]),np.compress(mac_filter_cond, top_assocations[2]), np.compress(mac_filter_cond, top_macs), np.compress(mac_filter_cond, top_assocations[4]), np.compress(mac_filter_cond, top_assocations[5]))

def get_number_associations_after_filtering(associations_maf, maf):
    maf_filter_cond = associations_maf[:] > maf
    return np.count_nonzero(associations_maf[maf_filter_cond])

def load_permutation_thresholds(perm_file):
    with open(perm_file) as p_file:
        permutation_thresholds = dict()
        if perm_file[-3:] == 'csv':
            filereader = csv.reader(p_file, delimiter=',')
            next(filereader, None) #skip header
            for row in filereader:
                val = float(row[1])
                if val > 1:
                    permutation_thresholds[int(row[0])] = val
                else:
                    permutation_thresholds[int(row[0])] = -math.log(val, 10)
        else:
            # skip first line
            p_file.readline()
            for line in p_file:
                cols = line[:-1].split(',')
                # Check if p-value or score already:
                val = float(cols[1])
                if val > 1:
                    permutation_thresholds[int(cols[0])] = val
                else:
                    permutation_thresholds[int(cols[0])] = -math.log(val,10)
    return permutation_thresholds

def get_top_associations(hdf5_file, val=100, maf=0.05, top_or_threshold='top'):
    """Retrieves the top associations from an hdf5 file"""
    if top_or_threshold not in ('top', 'threshold'):
        raise Exception('Please provide a valid option: top or threshold')
    is_threshold = top_or_threshold == 'threshold'
    if is_threshold and val < 1.0:
        val = -math.log(val, 10)
    try:
        h5f = h5py.File(hdf5_file, 'r')
    except:
        raise FileNotFoundError("Study file not found ({})".format(hdf5_file))

    scores = np.empty(shape=(0,), dtype='f4')
    positions = np.empty(shape=(0,), dtype='i4')
    mafs = np.empty(shape=(0,), dtype='f4')
    macs = np.empty(shape=(0,), dtype='i4')
    chrs = np.empty(shape=(0,), dtype='U1')
    betas = np.empty(shape=(0,), dtype='f4')
    se_betas = np.empty(shape=(0,), dtype='f4')
    num_associations = 0
    for chrom in range(1, 6):
        group = h5f['pvalues']['chr%s' % chrom]
        end_idx = val
        if maf != 0:
            group_length = get_number_associations_after_filtering(group['mafs'], maf)
        else:
            group_length = len(group['positions'])
        num_associations += group_length
        if is_threshold:
            end_idx = len(group['scores']) - np.searchsorted(group['scores'][:][::-1], val, side='left')
        top_positions, top_scores, top_mafs, top_macs, top_betas, top_se_betas = _filter_by_maf((group['positions'][:end_idx],group['scores'][:end_idx],group['mafs'][:end_idx],group['macs'][:end_idx], group['beta'][:end_idx], group['se_beta'][:end_idx]), maf)

        # for the case of top list we have to loop until we get all requested top assocations
        if top_or_threshold == 'top' and len(top_positions) < end_idx:
            while (True):
                start_idx = end_idx
                end_idx = min(start_idx + val, group_length)
                add_positions, add_scores, add_mafs, add_macs, add_betas, add_se_betas = _filter_by_maf((group['positions'][start_idx:end_idx], group['scores'][start_idx:end_idx], group['mafs'][start_idx:end_idx], group['macs'][start_idx:end_idx], group['beta'][start_idx:end_idx], group['se_beta'][start_idx:end_idx]), maf)
                top_positions = np.concatenate((top_positions, add_positions))
                top_scores = np.concatenate((top_scores, add_scores))
                top_mafs = np.concatenate((top_mafs, add_mafs))
                top_macs = np.concatenate((top_macs, add_macs))
                top_betas = np.concatenate((top_betas, add_betas))
                top_se_betas = np.concatenate((top_se_betas, add_se_betas))
                if len(top_positions) >= val:
                    top_positions = top_positions[:val]
                    top_scores = top_scores[:val]
                    top_mafs = top_mafs[:val]
                    top_macs = top_macs[:val]
                    top_betas = top_betas[:val]
                    top_se_betas = top_se_betas[:val]
                    break
                if end_idx == group_length:
                    break;

        positions = np.concatenate((positions, top_positions))
        scores = np.concatenate((scores, top_scores))
        mafs = np.concatenate((mafs, top_mafs))
        macs = np.concatenate((macs, top_macs))
        betas = np.concatenate((betas, top_betas))
        se_betas = np.concatenate((se_betas, top_se_betas))

        # chr special
        chrs = np.concatenate((chrs, [str(chrom)] * len(top_positions)))

    bt05 = -math.log(0.05 / float(num_associations), 10)
    bt01 = -math.log(0.01 / float(num_associations), 10)
    bh_threshold = h5f['pvalues'].attrs.get('bh_thres', None)
    thresholds = {'bonferroni_threshold05': bt05, 'bonferroni_threshold01': bt01, 'bh_threshold': bh_threshold, 'total_associations': num_associations}
    top_associations = np.rec.fromarrays((chrs, positions, scores, mafs, macs, betas, se_betas), names='chr, position, score, maf, mac, beta, se_beta')
    return top_associations, thresholds

def get_hit_count(hdf5_file, maf=0.05, mac=6, perm_threshold=None):
    try:
        h5f = h5py.File(hdf5_file, 'r')
    except:
        raise FileNotFoundError("Study file not found ({})".format(hdf5_file))
    scores = np.empty(shape=(0,), dtype='f4')
    num_associations = 0
    for chrom in range(1, 6):
        group = h5f['pvalues']['chr%s' % chrom]
        if maf != 0:
            group_length = get_number_associations_after_filtering(group['mafs'], maf)
        else:
            group_length = len(group['positions'])
        num_associations += group_length
        end_idx = len(group['scores']) - np.searchsorted(group['scores'][:][::-1], 1e-4, side='left')
        top_positions, top_scores, top_mafs, top_macs, top_betas, top_se_betas = _filter_by_maf((group['positions'][:end_idx],group['scores'][:end_idx],group['mafs'][:end_idx],group['macs'][:end_idx], group['beta'][:end_idx], group['se_beta'][:end_idx]), maf)
        top_positions, top_scores, top_mafs, top_macs, top_betas, top_se_betas = _filter_by_mac((top_positions, top_scores, top_mafs, top_macs, top_betas, top_se_betas), mac)
        scores = np.concatenate((scores, top_scores))
    bt05 = -math.log(0.05 / float(num_associations), 10)
    bt01 = -math.log(0.01 / float(num_associations), 10)
    bh_threshold = h5f['pvalues'].attrs.get('bh_thres', None)
    thresholds = {'bonferroni_threshold05': bt05, 'bonferroni_threshold01': bt01, 'bh_threshold': bh_threshold, 'total_associations': num_associations}
    if perm_threshold:
        thresholds['permutation'] = perm_threshold
    bt05_hits = 0
    bt01_hits = 0
    bh_hits = 0
    perm_hits = 0
    for score in scores:
        if score > bt05:
            bt05_hits += 1
            if score > bt01:
                bt01_hits += 1
        if score > bh_threshold:
            bh_hits += 1
        if perm_threshold:
            if score > perm_threshold:
                perm_hits += 1
    hits = {'bonferroni_hits05': bt05_hits, 'bonferroni_hits01': bt01_hits, 'bh_hits': bh_hits, 'thr_e-4': len(scores)}
    if perm_threshold:
        hits['permutation_hits'] = perm_hits
    return hits, thresholds

def regroup_associations(top_associations):
    """regroups associations from a hdf5 file to generate an ordered top list, not chromosome-specific"""
    top_associations.sort(order = 'score')
    return top_associations[::-1]

def get_ko_associations(csv_file):
    """Retrieves all KO associations from a csv file"""
    with open(csv_file) as csv_file_open:
        filereader = csv.DictReader(csv_file_open,  delimiter=',')
        genes = []
        chrs = []
        positions = []
        n_kos = []
        mafs = []
        macs = []
        scores = []
        betas = []
        se_betas = []
        for row in filereader:
            genes.append(row['SNP'])
            chrs.append(row['Chr'])
            positions.append(row['Pos'])
            n_kos.append(row['AC_1'])
            mafs.append(row['MAF'])
            macs.append(row['MAC'])
            scores.append(-math.log(float(row['Pval']),10))
            betas.append(float(row['beta']))
            se_betas.append(float(row['se_beta']))
    num_associations = len(genes)
    bt05 = -math.log(0.05 / float(num_associations), 10)
    bt01 = -math.log(0.01 / float(num_associations), 10)
    bt_ara = -math.log(0.01 / float(28000), 10) # total number of genes in AraGWAS
    associations = np.rec.fromarrays((genes, chrs, positions, n_kos, scores, betas, se_betas, mafs, macs), names='gene, chr, position, n_ko, score, beta, se_beta, maf, mac')
    thresholds = {'bonferroni_threshold05': bt05, 'bonferroni_threshold01': bt01,
                'bonferroni_ara': bt_ara, 'total_associations': num_associations}
    return associations, thresholds
def get_snps_from_genotype(genotype_hdf5, chr, pos_start, pos_end, accession_filter=None):
    """ Returns the snps for a given genotype for a specific range/position """
    h5f = h5py.File(genotype_hdf5, 'r')
    accessions = h5f['accessions'][:]
    pos = h5f['positions']
    snps = h5f['snps']
    chr_idx = np.where(pos.attrs['chrs'] == chr)[0]
    if len(chr_idx) != 1:
        raise Exception("Chr %s not found in genotype data" % chr)
    chr_idx = chr_idx[0]
    chr_start, chr_end = pos.attrs['chr_regions'][chr_idx]
    chr_positions = pos[chr_start:chr_end]
    start_pos_idx = chr_positions.searchsorted(pos_start)
    if pos_start == pos_end:
        end_pos_idx = start_pos_idx + 1
    else:
        end_pos_idx = chr_positions.searchsorted(pos_end)
    filtered_snps = snps[chr_start + start_pos_idx:chr_start+end_pos_idx]
    if accession_filter is not None:
        accession_idx = np.in1d(accessions, accession_filter)

        return filtered_snps[:,accession_idx], accessions[accession_idx]
    return filtered_snps, accessions


