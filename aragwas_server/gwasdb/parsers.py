import csv
from gff3 import Gff3
import gff3
gff3.gff3.logger.setLevel(100)
import io, re

SNPEFF_REGEX = re.compile(r"(\w+)\((.+)\)")

def parse_genes(gff3_file, go_terms_file):
    """parses the genes from gff3 and enriches it with additional information"""
    go_map = _get_go_map(go_terms_file)
    gff = Gff3(gff3_file)
    genes = [line for line in gff.lines if line['line_type'] == 'feature' and line['type'] == 'gene']

    genes_map = {}
    for gene in genes:
        gene_id = gene['attributes']['ID']
        symbol = gene['attributes'].get('symbol',None)
        full_name = gene['attributes'].get('full_name',None)
        aliases = gene['attributes'].get('Alias',[])
        aliases =  [{'symbol':aliases[i],'full_name':(None if i>=len(aliases)-1 else aliases[i+1])} for i in range(0,len(aliases),2)]

        if symbol and full_name:
            aliases.insert(0,{'symbol': symbol,'full_name':full_name})

        gene_dict = {'positions':{'gte':gene['start'],'lte': gene['end']},
                    'chr':gene['seqid'].lower(),'type':gene['type'],
                    'strand':gene['strand'],'name':gene_id,
                    'aliases':aliases,'isoforms':[],'GO':go_map.get(gene_id,[])}
        gene_dict['isoforms'] = _parse_isoforms(gff, gene)
        genes_map[gene_id] = gene_dict
        gene_dict['suggest'] = [gene_id]
        gene_dict['suggest'].extend(set([alias['symbol'] for alias in gene_dict['aliases']]))
    return genes_map


def _parse_isoforms(gff, gene):
    isoforms = []
    for mRNA in gff.descendants(gene):
        # skip sub features because they are stored within the isoform below
        if mRNA['type'] in ['CDS', 'exon','three_prime_UTR', 'five_prime_UTR']:
            continue
        cds = []
        exons = []
        for feature in gff.descendants(mRNA):
            feature_dict = {'positions':{'gte':feature['start'],'lte':feature['end']}}
            if feature['type'] == 'CDS':
                feature_dict['frame'] = feature['phase']
                cds.append(feature_dict)
            elif feature['type'] == 'exon':
                exons.append(feature_dict)
            else:
                continue
        mRNA_id = mRNA['attributes']['ID']
        short_description = mRNA['attributes'].get('Note',[None])[0]
        curator_summary = mRNA['attributes'].get('curator_summary',None)
        description = mRNA['attributes'].get('computational_description',None)

        mRNA_dict = {'positions': {'gte':mRNA['start'],'lte':mRNA['end']},
                    'strand':mRNA['strand'],'name':mRNA_id,'type':mRNA['type'],
                    'cds':cds,'exons':exons}
        if short_description:
            mRNA_dict['short_description'] = short_description
        if curator_summary:
            mRNA_dict['curator_summary'] = curator_summary
        if description:
            mRNA_dict['description'] = description
        isoforms.append(mRNA_dict)
    return isoforms

def _parse_snpeff_infos(genotype, info):
    infos = info.split(";")[-1].split("=")[-1].split(",")
    annotations = []
    coding = False
    gene_name = None
    for info in infos:
        matches = SNPEFF_REGEX.match(info)
        if not matches or len(matches.groups()) != 2:
            return (coding, annotations, gene_name)
        annotation = {'effect':matches.group(1)}
        fields = matches.group(2).split("|")
        if genotype != None and fields[-1] != genotype:
            continue
        annotation['impact'] = fields[0]
        if fields[1] != '':
            annotation['function'] = fields[1]
        if fields[2] != '':
            annotation['codon_change'] = fields[2]
        if fields[3] != '':
            annotation['amino_acid_change'] = fields[3]
        if fields[5] != '':
            annotation['gene_name'] = fields[5]
            if gene_name is None:
                gene_name = annotation['gene_name']
            coding = True
        if fields[8] != '':
            annotation['transcript_id'] = fields[8]
        if fields[9] != '':
            try:
                annotation['rank'] = int(fields[9])
            except:
                pass
        annotations.append(annotation)
    return coding, annotations, gene_name

def parse_snpeff(snp, is_custom_snp_eff):
    """parses the snpeff fields"""
    anc = ''
    if is_custom_snp_eff:
        anc = snp[4]
        if anc == '0':
            anc = snp[2]
        elif anc == '1':
            anc = snp[3]
    chrom = snp[0].lower()
    pos = int(snp[1])

    if is_custom_snp_eff:
        ref = snp[2]
        alt = snp[3]
        genotype = snp[5]
        info = snp[6]
    else:
        ref = snp[3]
        alt = snp[4]
        genotype = None
        info = snp[7]
    document = {'chr': chrom, 'position': pos, 'ref': ref, 'alt': alt, 'anc': anc}

    coding, annotations, gene_name = _parse_snpeff_infos(genotype, info)
    document['coding'] = coding
    if coding and gene_name:
        document['gene_name'] = gene_name
    document['annotations'] = annotations
    return document

def parse_lastel(last_el):
    # Need to transform _ to # and check if string contains square brackets
    if last_el[0] == '[':
        last_el = last_el[1:-1]
    last = last_el.split(',')
    print(last)
    score = float(last[0])
    uid = '#'.join(last[1][1:-1].split('-'))
    return [score, uid]

def _get_go_map(filename):
    go_dict = {}
    with open(filename, 'r') as fh:
        reader = csv.reader(fh, delimiter='\t')
        for row in reader:
            gene_id = row[0]
            go = {'object_name':row[2], 'relation':row[3],'term':row[4],'slim_term':row[8], 'go_id':row[5]}
            if gene_id not in go_dict:
                go_dict[gene_id] = []
            go_dict[gene_id].append(go)
    return go_dict
