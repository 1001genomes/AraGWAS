import numpy, math, h5py


def getTopAssociations(hdf5_file, val=100, top_or_threshold='top'):
    if top_or_threshold == 'top': # retrieves top 'val' associations on each chromosome
        top = True
    elif top_or_threshold == 'threshold':
        top = False
        if val < 1:
            val = -math.log(val,10)
        print(val)
    else:
        raise Warning('Please provide a valid option: top or threshold')

    try:
        association_file = h5py.File(hdf5_file, 'r')
    except:
        raise FileNotFoundError("Impossible to find the appropriate study file ({})".format(hdf5_file))

    # Get SNP position in file
    pval = []
    pos = []
    mafs = []
    n_asso = 0
    if top:
        for i in range(5):
            pval.append(association_file['pvalues']['chr'+str(i+1)]['scores'][:val])
            pos.append(association_file['pvalues']['chr'+str(i+1)]['positions'][:val])
            mafs.append(association_file['pvalues']['chr'+str(i+1)]['mafs'][:val])
            n_asso += len(association_file['pvalues']['chr'+str(i+1)]['scores'])
    else:
        for i in range(5):
            local_pval = []
            local_pos = []
            local_mafs = []
            for j in range(10000):
                if float(association_file['pvalues']['chr'+str(i+1)]['scores'][j]) >= val:
                    local_pval.append(association_file['pvalues']['chr'+str(i+1)]['scores'][j])
                    local_pos.append(association_file['pvalues']['chr' + str(i + 1)]['positions'][j])
                    local_mafs.append(association_file['pvalues']['chr' + str(i + 1)]['mafs'][j])
                else:
                    # check next one and break:
                    if float(association_file['pvalues']['chr' + str(i + 1)]['scores'][j+1]) < val:
                        break
            pval.append(local_pval)
            pos.append(local_pos)
            mafs.append(local_mafs)
            n_asso += len(association_file['pvalues']['chr'+str(i+1)]['scores'])

    bt05 = -math.log(0.05/float(n_asso), 10)
    bt01 = -math.log(0.01/float(n_asso), 10)
    thresholds = {'bonferoni_threshold05': bt05,'bonferoni_threshold01': bt01, 'total_associations': n_asso}

    return pval, pos, mafs, n_asso, thresholds

def regroupAssociations(pval, pos, mafs):
    #regroups associations from a hdf5 file to generate an ordered top list, not chromosome-specific
    tot_pval = []
    tot_pos = []
    tot_mafs = []
    tot_chr = []
    for i in range(5):
        tot_pval.extend(pval[i])
        tot_pos.extend(pos[i])
        tot_mafs.extend(mafs[i])
        tot_chr.extend(i+1 for l in range(len(pval[i])))

    tot_pval = numpy.asarray(tot_pval)
    tot_pos = numpy.asarray(tot_pos)
    tot_mafs = numpy.asarray(tot_mafs)
    tot_chr = numpy.asarray(tot_chr)

    i = tot_pval.argsort()[::-1]
    return [tot_pval[i], tot_chr[i], tot_pos[i],tot_mafs[i]]
