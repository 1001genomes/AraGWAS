from rest_framework import permissions
from rest_framework import viewsets, generics, filters
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import *
from gwasdb.paginator import CustomSearchPagination, CustomAssociationsPagination

from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from gwasdb.tasks import compute_ld
from gwasdb import __version__, __date__, __githash__,__build__, __buildurl__
from aragwas.settings import GITHUB_URL

import h5py, numpy, math

def get_api_version():
    BUILD_STATUS_URL = None
    if __buildurl__ != 'N/A':
        BUILD_STATUS_URL = __buildurl__
    return {'version':__version__,'date':__date__,'githash':__githash__,'build':__build__,'build_url':BUILD_STATUS_URL,'github_url':GITHUB_URL}


class ApiVersionView(APIView):
    """Displays git and version information"""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        serializer = ApiVersionSerializer(get_api_version(), many=False)
        return Response(serializer.data)

class AssociationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer

class AssociationsOfStudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations
    """
    queryset = Association.objects.all()
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            page = int(request.query_params.get('page', None))
        except:
            page = 1
        # associations = get_list_or_404(Association, study=pk)
        try:
            association_file = h5py.File("/Users/tomatteo/Documents/Projects/AraGWAS/AraGWAS/aragwas_server/gwasdb/" + pk + ".hdf5", 'r')
        except:
            raise FileNotFoundError("Impossible to find the appropriate study file ({})".format(pk + '.hdf5'))
        # Get SNP position in file

        pval = []
        chr = []
        pos = []
        mafs = []
        n_asso = 0

        # Get top 2500 associations for each chromosome.
        TOP = 100
        for i in range(5):
            pval.extend(association_file['pvalues']['chr'+str(i+1)]['scores'][:TOP])
            pos.extend(association_file['pvalues']['chr'+str(i+1)]['positions'][:TOP])
            mafs.extend(association_file['pvalues']['chr'+str(i+1)]['mafs'][:TOP])
            chr.extend(i+1 for l in range(TOP))
            n_asso += len(association_file['pvalues']['chr'+str(i+1)]['scores'])
        bt05 = -math.log(0.05/float(n_asso), 10)
        bt01 = -math.log(0.01/float(n_asso), 10)
        thresholds = {'bonferoni_threshold05': bt05,'bonferoni_threshold01': bt01, 'total_associations': n_asso}

        pval = numpy.asarray(pval)
        pos = numpy.asarray(pos)
        mafs = numpy.asarray(mafs)
        chr = numpy.asarray(chr)

        i = pval.argsort()[::-1]
        results = []
        for l in i:
            # get associated genes:
            name = ''
            pk = ''
            type = ''
            try:
                obj = SNP.objects.get(Q(chromosome=chr[l]) & Q(position=pos[l]))
                gene = Gene.objects.get(pk=obj.gene)
                name = gene.name
                pk = gene.pk
            except:
                pass
            results.append({'pvalue': "{:.5f}".format(pval[l]),'SNP': 'Chr'+str(chr[l])+':'+str(pos[l]), 'maf': "{:.3f}".format(mafs[l]), 'gene':{'name': name, 'pk': pk}, 'type': type})
        # Homemade paginator
        PAGE_SIZE = 20.
        page_count = int(math.ceil(float(len(i)) / PAGE_SIZE))
        if page > page_count:
            page = page_count
        data = {'count': len(i), 'page_count': int(math.ceil(float(len(i)) / PAGE_SIZE)), 'current_page': page, 'thresholds': thresholds, 'results': results[int(PAGE_SIZE)*(page-1):int(PAGE_SIZE)*page]}

        return Response(data, status=status.HTTP_200_OK)

class AssociationsForManhattanPlotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Fetch associations in hdf5 file for manhattan plots
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        # Load hdf5 genotype file:
        try:
            association_file = h5py.File("/Users/tomatteo/Documents/Projects/AraGWAS/AraGWAS/aragwas_server/gwasdb/" + pk + ".hdf5", 'r') # Absolute path for tests.
        except:
            raise FileNotFoundError("Impossible to find the appropriate study file ({})".format(pk + '.hdf5'))
        # Get SNP position in file
        output = {}
        n_asso = 0

        # Get top 2500 associations for each chromosome.
        for i in range(5):
            values_chr = association_file['pvalues']['chr'+str(i+1)]['scores'][:2500]
            pos_chr = association_file['pvalues']['chr'+str(i+1)]['positions'][:2500]
            mafs_chr = association_file['pvalues']['chr'+str(i+1)]['mafs'][:2500]
            output['chr'+str(i+1)] = {'pvalues': values_chr, 'positions': pos_chr, 'mafs': mafs_chr}
            n_asso += len(association_file['pvalues']['chr'+str(i+1)]['scores'])
        output['bonferoni_threshold'] = -math.log(0.05/float(n_asso), 10)

        return Response(output, status=status.HTTP_200_OK)

class AssociationsOfPhenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations of a specific phenotype
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            page = int(request.query_params.get('page', None))
        except:
            page = 1
        # get studies ids
        studies = Study.objects.filter(phenotype=pk)
        st_id = []
        for s in studies:
            st_id.append(s.pk)

        pval = []
        chr = []
        pos = []
        study = []
        n_asso = 0
        TOP = 20
        for study_pk in st_id:
            try:
                association_file = h5py.File("/Users/tomatteo/Documents/Projects/AraGWAS/AraGWAS/aragwas_server/gwasdb/" + str(study_pk) + ".hdf5", 'r')
            except:
                raise FileNotFoundError("Impossible to find the appropriate study file ({})".format(str(study_pk) + '.hdf5'))
            # Get top 2500 associations for each chromosome and each study
            for i in range(5):
                pval.extend(association_file['pvalues']['chr'+str(i+1)]['scores'][:TOP])
                pos.extend(association_file['pvalues']['chr'+str(i+1)]['positions'][:TOP])
                chr.extend(i+1 for l in range(TOP))
                study.extend(study_pk for l in range(TOP))
                n_asso += len(association_file['pvalues']['chr'+str(i+1)]['scores'])

        pval = numpy.asarray(pval)
        pos = numpy.asarray(pos)
        chr = numpy.asarray(chr)
        study = numpy.asarray(study)

        i = pval.argsort()[::-1]
        results = []
        for l in i:
            # get associated genes:
            name = ''
            pk = ''
            try:
                obj = SNP.objects.get(Q(chromosome=chr[l]) & Q(position=pos[l]))
                gene = Gene.objects.get(pk=obj.gene)
                name = gene.name
                pk = gene.pk
            except:
                pass
            study_name = studies.get(pk=study[l]).name
            results.append({'pvalue': "{:.5f}".format(pval[l]),'SNP': 'Chr'+str(chr[l])+':'+str(pos[l]), 'gene':{'name': name, 'pk': pk}, 'study':{'name': study_name, 'pk': study[l]}})
        # Homemade paginator
        PAGE_SIZE = 20.
        page_count = int(math.ceil(float(len(i)) / PAGE_SIZE))
        if page > page_count:
            page = page_count
        data = {'count': len(i), 'page_count': int(math.ceil(float(len(i)) / PAGE_SIZE)), 'current_page': page, 'total_associations': n_asso,
                'results': results[int(PAGE_SIZE) * (page - 1):int(PAGE_SIZE) * page]}
        return Response(data, status=status.HTTP_200_OK)

class AssociationsOfGeneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations of a specific phenotype
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        # Get study ids
        try:
            associations = Association.objects.get(SNP__gene=pk).order_by('pvalue')
            serializer = AssociationSerializer(associations)
            return Response(serializer.data)
        except Association.DoesNotExist:
            raise Http404('Associations do not exist')


class StudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS study
    """
    queryset = Study.objects.all()
    serializer_class = StudySerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def get_queryset(self):
        queryset = self.queryset
        ordering = self.request.query_params.get('ordering', None)
        if ordering is not None and ordering != '':
            from django.db.models.functions import Lower
            inverted = False
            if ordering.startswith('-'):
                ordering = ordering[1:]
                inverted = True
            if ordering == 'genotype' or ordering == 'phenotype':
                ordering += '__name'
            queryset = queryset.order_by(Lower(ordering))
            if inverted:
                queryset = queryset.reverse()
        return queryset

class PhenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about phenotypes
    """
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeListSerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def get_queryset(self):
        queryset = self.queryset
        ordering = self.request.query_params.get('ordering', None)
        if ordering is not None and ordering != '':
            from django.db.models.functions import Lower
            from django.db.models import Count
            inverted = False
            if ordering.startswith('-'):
                ordering = ordering[1:]
                inverted = True
            if ordering == 'n_studies':
                queryset = queryset.annotate(n_studies=Count('study')).order_by(Lower(ordering))
            else:
                queryset = queryset.order_by(Lower(ordering))
            if inverted:
                queryset = queryset.reverse()
        return queryset

class SimilarPhenotypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about similar phenotypes
    """
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeListSerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            ori_pheno = Phenotype.objects.get(pk=pk)
        except:
            raise ValueError('Phenotype with pk {} not found'.format(pk))
        trait_ontology = ori_pheno.to
        queryset = Phenotype.objects.filter(to=trait_ontology)
        serializer = PhenotypeListSerializer(queryset)
        return Response(serializer.data)

class GeneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information genes
    """
    queryset = Gene.objects.all()
    serializer_class = GeneListSerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def get_queryset(self):
        queryset = self.queryset
        ordering = self.request.query_params.get('ordering', None)
        if ordering is not None and ordering != '':
            from django.db.models.functions import Lower
            inverted = False
            if ordering.startswith('-'):
                ordering = ordering[1:]
                inverted = True
            queryset = queryset.order_by(Lower(ordering))
            if inverted:
                queryset = queryset.reverse()
        return queryset

class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allow for search in a viewset
    """
    queryset = Study.objects.all()
    query_term = None
    serializer_class = StudySerializer
    pagination_class = CustomSearchPagination


    @list_route(url_path='search_results')
    def search_result(self, request):
        return self.search_results(request, query_term=None)

    @detail_route()
    def search_results(self, request, query_term):
        if request.method == "GET":
            if query_term==None:
                studies = Study.objects.all()
                phenotypes = Phenotype.objects.all()
                genes = Gene.objects.all()
            else:
                studies = Study.objects.filter(Q(name__icontains=query_term) |
                                                      Q(phenotype__name__icontains=query_term)).order_by('name')
                associations = Association.objects.filter(Q(snp__position__icontains=query_term) |
                                                      Q(snp__gene__name__icontains=query_term))# |
                                                      #Q(snp__name__icontains=query_term)) # Does this call the __unicode__ method of SNP? Had to take it out, furthermore SNPs in A.t. are referenced using their positions.
                phenotypes = Phenotype.objects.filter(name__icontains=query_term).order_by('name')
                # Add chromosome position search for genomic regions
                try:
                    int(query_term)
                    isnum = True
                except ValueError:
                    isnum = False
                import re
                pattern = re.compile("(Chr|CHR|chr)+\s?([0-9]{1,2})+(-|:)?(\d*)\s*(-|:|)?\s*(\d+|)")
                if isnum: # Only a number, look for neighboring genes on all chromosomes.
                    genes = Gene.objects.filter(Q(start_position__lte=query_term) & Q(end_position__gte=query_term)).order_by('name')
                elif pattern.match(query_term): # Specific genomic range
                    splitted = re.split("(Chr|CHR|chr)+\s?([0-9]{1,2})+(-|:)?(\d*)\s*(-|:|)?\s*(\d+|)", query_term)
                    chr = int(splitted[2])
                    s_p = None
                    e_p = None
                    if splitted[4]:
                        s_p = int(splitted[4])
                    if splitted[6]:
                        e_p = int(splitted[6])
                    # Need to retrieve all genes that overlap somehow with that region (all-in, right part in, left part in, etc)
                    genes = Gene.objects.filter(chromosome__exact=chr)
                    if s_p:
                        if e_p:
                            genes = genes.filter((Q(end_position__gte=s_p) & Q(end_position__lte=e_p)) |
                                                 (Q(start_position__gte=s_p) & Q(start_position__lte=e_p)) |
                                                 (Q(start_position__lte=s_p) & Q(end_position__gte=e_p))).order_by('name')
                        else:
                            genes = genes.filter(Q(start_position__lte=s_p) & Q(end_position__gte=s_p)).order_by('name')
                else: # other type of request
                    genes = Gene.objects.filter(Q(name__icontains=query_term)).order_by('name')
            # custom ordering
            ordering = request.query_params.get('ordering', None)
            ordering_fields = {'studies': ['name','genotype','phenotype','method','transformation'], 'phenotypes': ['name', 'description'], 'genes': ['name', 'chr', 'start_position', 'end_position', 'SNPs_count', 'association_count', 'description']}
            if ordering is not None:
                from django.db.models.functions import Lower
                inverted = False
                if ordering.startswith('-'):
                    inverted = True
                    ordering = ordering[1:]
                if ordering in ordering_fields['studies'] and studies:
                    if ordering == 'phenotype' or ordering == 'genotype': # Need to reference the names and not the internal IDs for ordering
                        ordering += '__name'
                    studies = studies.order_by(Lower(ordering))
                    if inverted:
                        studies = studies.reverse()
                if ordering in ordering_fields['phenotypes'] and phenotypes:
                    phenotypes = phenotypes.order_by(Lower(ordering))
                    if inverted:
                        phenotypes = phenotypes.reverse()
                if ordering in ordering_fields['genes'] and genes:
                    if ordering == 'snp' or ordering == 'study':
                        ordering += '__name'
                    genes = genes.order_by(Lower(ordering))
                    if inverted:
                        genes = genes.reverse()

            if studies:
                pagest = self.paginate_queryset(studies)
                study_serializer = StudySerializer(pagest, many=True)
            else:
                study_serializer = StudySerializer(studies, many=True)

            if genes:
                pagege = self.paginate_queryset(genes)
                gene_serializer = GeneListSerializer(pagege, many=True)
            else:
                gene_serializer = GeneListSerializer(genes, many=True)

            if phenotypes:
                pagephe = self.paginate_queryset(phenotypes)
                phenotype_serializer = PhenotypeListSerializer(pagephe, many=True)
            else:
                phenotype_serializer = PhenotypeListSerializer(phenotypes, many=True)

            counts = [len(genes), len(phenotypes), len(studies)]
            PAGE_SIZE = 25.
            import math
            page_counts = [int(math.ceil(float(len(genes))/PAGE_SIZE)),int(math.ceil(float(len(phenotypes))/PAGE_SIZE)), int(math.ceil(float(len(studies))/PAGE_SIZE))]
            data = {'study_search_results':study_serializer.data,
                             'phenotype_search_results':phenotype_serializer.data,
                             'gene_search_results':gene_serializer.data,
                             'counts': counts,
                             'page_counts': page_counts}

            if any([studies,genes,phenotypes]):
                return self.get_paginated_response(data)
            else:
                return Response({'results': {i:data[i] for i in data if i!='counts'}, 'count':counts, 'page_count':[0,0,0]})



class SNPLocalViewSet(viewsets.ViewSet):
    """
    Retrieve information about a SNP
    """
    queryset = SNP.objects.none()

    @detail_route()
    def neighboring_snps(self, request, pk):
        """
        Returns list of the neighboring SNPs, no information about LD (this will be retrieved or computed later)
        """
        window_size=request.GET.get('window_size', 1000000)
        include = 'include' in request.GET
        chromosome = SNP.objects.get(pk=pk).chromosome
        position = SNP.objects.get(pk=pk).position
        window_of_interest = [min(int(position) - window_size / 2, 0), int(
            position) + window_size / 2]  # no need to get chromosome size (since we'll run > or < queries)
        # Here we need to decide whether we include the original SNP or not.
        neighboring_s = SNP.objects.filter(chromosome=chromosome).filter(
            position__range=(window_of_interest[0], window_of_interest[1]))
        if not include:
            # Exclude original SNP
            neighboring_s = neighboring_s.filter(~Q(pk=pk))

        serializer = SNPListSerializer(neighboring_s, many=True)
        return Response(serializer.data)

    @detail_route()
    def snps_in_ld(request, pk):
        """
        Returns list of the neighboring SNPs in high LD
        """
        N = request.GET.get('N',20)
        snp = SNP.objects.get(pk=pk)
        # Get genotype
        genotype_name = snp.genotype

        # Call the celery task
        ordered_positions, ordered_ld = compute_ld(snp.chromosome, snp.position, genotype_name)

        # return highest N SNPs
        snps = SNP.objects.filter(chromosome__equals=snp.chromosome).filter(position__in=ordered_positions)

        # Serialize
        serializer = SNPListSerializer(snps)
        # Attach correlation information
        return Response({'top_ld_snps': serializer.data,
                         'ld_values': ordered_ld,
                         'top_snps_positions': ordered_positions})


# '''
# Search Endpoint
# '''
# @api_view(['GET'])
# def search(request, query_term=None, format=None):
#     """
#     Search for an accession, a study, a SNP/gene or a phenotype
#     ---
#     parameters:
#         - name: query_term
#           description: the search term
#           required: true
#           type: string
#           paramType: path
#
#     serializer: AssociationListSerializer, StudyListSerializer, PhenotypeListSerializer
#     omit_serializer: false
#     """
#     if request.method == "GET":
#         if query_term==None:
#             studies = Study.objects.all()
#             phenotypes = Phenotype.objects.all()
#             associations = Association.objects.all()
#         else:
#             studies = Study.objects.filter(Q(name__icontains=query_term) |
#                                                   Q(phenotype__name__icontains=query_term))
#             associations = Association.objects.filter(Q(snp__position__icontains=query_term) |
#                                                   Q(snp__gene__name__icontains=query_term) |
#                                                   Q(snp__icontains=query_term)) # Does this call the __unicode__ method of SNP?
#             phenotypes = Phenotype.objects.filter(name__icontains=query_term)
#
#         study_serializer = StudySerializer(studies, many=True)
#         phenotype_serializer = PhenotypeListSerializer(phenotypes,many=True)
#         association_serializer = AssociationListSerializer(associations,many=True)
#         return Response({'phenotype_search_results':phenotype_serializer.data,
#                          'study_search_results':study_serializer.data,
#                          'accession_search_results':association_serializer.data})

# """
# Retrieve neighboring SNPs
# """
# # Need to review permission (this one is used for testing)
# @api_view(['GET'])
# @permission_classes((IsAuthenticatedOrReadOnly,))
# def neighboring_snps(request, snp_pk, window_size=1000000, include = True, format=None):
#     """
#     Returns list of the neighboring SNPs, no information about LD (this will be retrieved or computed later)
#     ---
#     parameters:
#         - name: snp_pk
#           description: pk of the SNP of interest
#           required: true
#           type: string
#           paramType: path
#         - name: window_size
#           description: number of bp around the SNP of interest (default = 1'000'000 bp)
#           required: true
#           type: int
#           paramType: path
#         - name: include
#           description: include original SNP (default = True)
#           required: true
#           type: bool
#           paramType: path
#
#     serializer: SNPListSerializer
#     omit_serializer: false
#     """
#     chromosome = SNP.objects.get(pk=snp_pk).chromosome
#     position = SNP.objects.get(pk=snp_pk).position
#     window_of_interest = [min(int(position)-window_size/2, 0), int(position) + window_size/2] # no need to get chromosome size (since we'll run > or < queries)
#     # Here we need to decide whether we include the original SNP or not.
#     neighboring_s = SNP.objects.filter(chromosome=chromosome).filter(position__range=(window_of_interest[0], window_of_interest[1]))
#     if not include:
#         # Exclude original SNP
#         neighboring_s = neighboring_s.filter(~Q(pk=snp_pk))
#     if request.method == "GET":
#         serializer = SNPListSerializer(neighboring_s, many=True)
#         return Response(serializer.data)
#
# """
# Retrieve SNPs in high LD
# """
# @api_view(['GET'])
# def snps_in_ld(request, snp_pk):
#     """
#     Returns list of the neighboring SNPs in high LD
#     ---
#     parameters:
#         - name: snp_pk
#           description: pk of the SNP of interest
#           required: true
#           type: string
#           paramType: path
#         - name: include
#           description: include original SNP (default = True)
#           required: true
#           type: bool
#           paramType: path
#
#     serializer: SNPListSerializer
#     omit_serializer: false
#     """
#     snp = SNP.objects.get(pk=snp_pk)
#     # Get genotype
#     genotype_name = snp.genotype
#
#     # Load hdf5 genotype file:
#     try:
#         genotype_file=h5py.File(genotype_name+".hdf5", 'r')
#     except:
#         raise FileNotFoundError("Impossible to find the appropriate genotype ({})".format(genotype_name))
#     # Get SNP position in file
#     h5gen = genotype_file['Genotype']
#     n_snps = len(h5gen['chr_index'])
#
#     # Find chromosome sub-portion:
#     started = False
#     completed = False
#     chr_string = "Chr{}".format(snp.chromosome)
#     for idx,c in enumerate(h5gen['chr_index']):
#         if c == numpy.bytes_(chr_string):
#             if not started:
#                 started = True
#                 start_idx = idx
#             continue
#         if started:
#             end_idx = idx
#             completed = True
#             break
#     if not completed:
#         raise ValueError("No values matching chromosome {} in genotype {}".format(snp.chromosome, genotype_name))
#
#     found = False
#     for idx,c in enumerate(h5gen['position_index'][start_idx:end_idx]):
#         if c == snp.position:
#             snp_idx = idx
#             found = True
#             break
#
#     if not found:
#         raise ValueError("No values matching the position {} in chromosome {} on genotype {}".format(snp.position, snp.chromosome, genotype_name))
#
#     idx_window = [max(snp_idx-250, start_idx), min(snp_idx+251, end_idx)]
#
#     # Retrieve genotype data for SNPs in window !!! FOR NOW ALL SAMPLES ARE CONSIDERED!!! IF WE WANT TO ADD ONLY SPECIFIC SAMPLES, WE NEED TO STORE THE SAMPLE LIST (IDS) ASSOCIATED WITH A STUDY SOMEWHERE...
#     if h5gen['raw'][:,snp_idx][0].decode('UTF-8').isalpha():
#         transform = True
#     else:
#         transform = False
#     genotype_data_dict = dict()
#     freq_dict = dict()
#     snp_positions = []
#     # Genotype is stored in its encoded form (0,1, no 2 because all samples are homozygous) in a dictionary
#     for idx in range(idx_window[0],idx_window[1]):
#         snp_positions.append(h5gen['position_index'][idx])
#         if transform:
#             gen_str = ""
#             acgt = {'A':0, 'C': 0, 'G': 0, 'T':0}
#             for a in h5gen['raw'][:,idx]:
#                 acgt[a.decode('UTF-8').upper()] += 1
#                 gen_str += a.decode('UTF-8').upper()
#             # Find major and minor alleles
#             sorted_acgt = sorted(acgt.items(), key = lambda x:x[1])
#             if sorted_acgt[1][1] != 0:
#                 raise Warning("Three or more alleles")
#             maj_a = sorted_acgt[3][0]
#             min_a = sorted_acgt[2][0]
#             # Save the minor allele frequencies
#             freq_dict[h5gen['position_index'][idx]]=sorted_acgt[2][1]/len(h5gen['raw'][:,idx])
#             genotype_encoded = numpy.zeros(len(h5gen['raw'][:,idx]))
#             for string_idx,a in enumerate(gen_str):
#                 if a == min_a:
#                     genotype_encoded[string_idx] = 1
#         else:
#             genotype_encoded = []
#             for a in h5gen['raw'][:,idx]:
#                 genotype_encoded.append(int(a.decode('UTF-8')))
#         genotype_data_dict[h5gen['position_index'][idx]] = genotype_encoded
#
#     # Compute correlation matrix
#     n_typed_snps = idx_window[1]-idx_window[0]
#
#     ld_vector = []
#     # Need to add some filtering for low freq
#     # Estimate sigma_tt
#     main_snp_pos = h5gen['position_index'][snp_idx]
#     pi = freq_dict[main_snp_pos]
#     for position_index in snp_positions:
#         pj = freq_dict[position_index]
#         pij = 0.
#         for l in range(len(genotype_data_dict[main_snp_pos])):
#             if genotype_data_dict[position_index]==1 and genotype_data_dict[main_snp_pos]==1:
#                 pij += 1
#         pij = pij/len(genotype_data_dict[main_snp_pos])
#         r = (pij - pi * pj) / numpy.sqrt(pi * (1.0 - pi) * pj * (1.0 - pj))
#         ld_vector.append(r)
#
#     # Sort highest values
#     sorted_lists = reversed(sorted(zip(ld_vector,snp_positions)))
#     ordered_ld = []
#     ordered_positions = []
#     for i in sorted_lists:
#         ordered_ld.append(i[0])
#         ordered_positions.append(i[1])
#     ordered_ld = ordered_ld[:20]
#     ordered_positions = ordered_positions[:20]
#
#     # return highest N SNPs
#     snps = SNP.objects.filter(chromosome__equals=snp.chromosome).filter(position__in=ordered_positions)
#
#     # Serialize
#     serializer = SNPListSerializer(snps)
#     # Attach correlation information
#     return Response({'top_ld_snps': serializer.data,
#                      'ld_values': ordered_ld,
#                      'top_snps_positions': ordered_positions})
