"""
functions to load pvalues from hdf5 files
"""
import math
import numpy as np
import h5py



def get_top_associations(hdf5_file, val=100, top_or_threshold='top'):
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
    num_associations = 0
    for chrom in range(1, 6):
        group = h5f['pvalues']['chr%s' % chrom]
        end_idx = val
        num_associations += len(group['positions'])
        if is_threshold:
            end_idx = len(group['scores']) - np.searchsorted(group['scores'][:][::-1], val, side='left')
        positions = np.concatenate((positions, group['positions'][:end_idx]))
        scores = np.concatenate((scores, group['scores'][:end_idx]))
        mafs = np.concatenate((mafs, group['mafs'][:end_idx]))
        macs = np.concatenate((macs, group['macs'][:end_idx]))
        chrs = np.concatenate((chrs, [str(chrom)] * end_idx))

    bt05 = -math.log(0.05 / float(num_associations), 10)
    bt01 = -math.log(0.01 / float(num_associations), 10)
    bh_threshold = h5f['pvalues'].attrs.get('bh_thres', None)
    thresholds = {'bonferoni_threshold05': bt05, 'bonferoni_threshold01': bt01, 'bh_threshold': bh_threshold, 'total_associations': num_associations}
    top_associations = np.rec.fromarrays((chrs, positions, scores, mafs, macs), names='chr, position, score, maf, mac')
    return top_associations, thresholds


def regroup_associations(top_associations):
    """regroups associations from a hdf5 file to generate an ordered top list, not chromosome-specific"""
    top_associations.sort(order = 'score')
    return top_associations[::-1]
