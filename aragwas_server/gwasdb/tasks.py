from __future__ import absolute_import, unicode_literals
from celery import shared_task
import h5py, numpy

@shared_task
def compute_ld(chromosome, position, genotype_name, N=20):
    """
    Returns ordered list of the N neighboring SNPs positions in high LD
    ---
    parameters:
        - name: snp_pk
          description: pk of the SNP of interest
          required: true
          type: string
          paramType: path
        - name: N
          description: number of top LD snps to return (default = 20, max 500)
          required: true
          type: bool
          paramType: path

    serializer: SNPListSerializer
    omit_serializer: false
    """
    # Load hdf5 genotype file:
    try:
        genotype_file = h5py.File(genotype_name + ".hdf5", 'r')
    except:
        raise FileNotFoundError("Impossible to find the appropriate genotype ({})".format(genotype_name))
    # Get SNP position in file
    h5gen = genotype_file['Genotype']
    n_snps = len(h5gen['chr_index'])

    # Find chromosome sub-portion:
    started = False
    completed = False
    chr_string = "Chr{}".format(chromosome)
    for idx, c in enumerate(h5gen['chr_index']):
        if c == numpy.bytes_(chr_string):
            if not started:
                started = True
                start_idx = idx
            continue
        if started:
            end_idx = idx
            completed = True
            break
    if not completed:
        raise ValueError("No values matching chromosome {} in genotype {}".format(snp.chromosome, genotype_name))

    found = False
    for idx, c in enumerate(h5gen['position_index'][start_idx:end_idx]):
        if c == position:
            snp_idx = idx
            found = True
            break

    if not found:
        raise ValueError("No values matching the position {} in chromosome {} on genotype {}".format(position,chromosome,genotype_name))

    idx_window = [max(snp_idx - 250, start_idx), min(snp_idx + 251, end_idx)]

    # Retrieve genotype data for SNPs in window !!! FOR NOW ALL SAMPLES ARE CONSIDERED!!! IF WE WANT TO ADD ONLY SPECIFIC SAMPLES, WE NEED TO STORE THE SAMPLE LIST (IDS) ASSOCIATED WITH A STUDY SOMEWHERE...
    if h5gen['raw'][:, snp_idx][0].decode('UTF-8').isalpha():
        transform = True
    else:
        transform = False
    genotype_data_dict = dict()
    freq_dict = dict()
    snp_positions = []
    # Genotype is stored in its encoded form (0,1, no 2 because all samples are homozygous) in a dictionary
    for idx in range(idx_window[0], idx_window[1]):
        snp_positions.append(h5gen['position_index'][idx])
        if transform:
            gen_str = ""
            acgt = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
            for a in h5gen['raw'][:, idx]:
                acgt[a.decode('UTF-8').upper()] += 1
                gen_str += a.decode('UTF-8').upper()
            # Find major and minor alleles
            sorted_acgt = sorted(acgt.items(), key=lambda x: x[1])
            if sorted_acgt[1][1] != 0:
                raise Warning("Three or more alleles")
            maj_a = sorted_acgt[3][0]
            min_a = sorted_acgt[2][0]
            # Save the minor allele frequencies
            freq_dict[h5gen['position_index'][idx]] = sorted_acgt[2][1] / len(h5gen['raw'][:, idx])
            genotype_encoded = numpy.zeros(len(h5gen['raw'][:, idx]))
            for string_idx, a in enumerate(gen_str):
                if a == min_a:
                    genotype_encoded[string_idx] = 1
        else:
            genotype_encoded = []
            for a in h5gen['raw'][:, idx]:
                genotype_encoded.append(int(a.decode('UTF-8')))
        genotype_data_dict[h5gen['position_index'][idx]] = genotype_encoded

    # Compute correlation matrix
    n_typed_snps = idx_window[1] - idx_window[0]

    ld_vector = []
    # Need to add some filtering for low freq
    # Estimate sigma_tt
    main_snp_pos = h5gen['position_index'][snp_idx]
    pi = freq_dict[main_snp_pos]
    for position_index in snp_positions:
        pj = freq_dict[position_index]
        pij = 0.
        for l in range(len(genotype_data_dict[main_snp_pos])):
            if genotype_data_dict[position_index] == 1 and genotype_data_dict[main_snp_pos] == 1:
                pij += 1
        pij = pij / len(genotype_data_dict[main_snp_pos])
        r = (pij - pi * pj) / numpy.sqrt(pi * (1.0 - pi) * pj * (1.0 - pj))
        ld_vector.append(r)

    # Sort highest values
    sorted_lists = reversed(sorted(zip(ld_vector, snp_positions)))
    ordered_ld = []
    ordered_positions = []
    for i in sorted_lists:
        ordered_ld.append(i[0])
        ordered_positions.append(i[1])
    ordered_ld = ordered_ld[:N]
    ordered_positions = ordered_positions[:N]

    # Return ordered lists
    return ordered_positions, ordered_ld