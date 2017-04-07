from rest_framework import permissions
from rest_framework import viewsets, generics, filters
from rest_framework.views import APIView

from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import *
from gwasdb.paginator import CustomSearchPagination

from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from gwasdb.tasks import compute_ld

class AssociationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer


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
        if ordering is not None:
            from django.db.models.functions import Lower
            if ordering.startswith('-'):
                queryset = queryset.order_by(Lower(ordering[1:])).reverse()
            else:
                queryset = queryset.order_by(Lower(ordering))
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
                associations = Association.objects.all()
            else:
                studies = Study.objects.filter(Q(name__icontains=query_term) |
                                                      Q(phenotype__name__icontains=query_term)).order_by('name')
                associations = Association.objects.filter(Q(snp__position__icontains=query_term) |
                                                      Q(snp__gene__name__icontains=query_term) |
                                                      Q(snp__name__icontains=query_term)) # Does this call the __unicode__ method of SNP? Had to take it out, furthermore SNPs in A.t. are referenced using their positions.
                phenotypes = Phenotype.objects.filter(name__icontains=query_term).order_by('name')
            # custom ordering
            ordering = request.query_params.get('ordering', None)
            ordering_fields = {'studies': ['name','genotype','phenotype','method','transformation'], 'phenotypes': ['name', 'description'], 'associations': ['snp', 'maf', 'pvalue', 'beta', 'odds_ratio', 'confidence_interval', 'phenotype', 'study']}
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
                if ordering in ordering_fields['associations'] and associations:
                    if ordering == 'snp' or ordering == 'study':
                        ordering += '__name'
                    associations = associations.order_by(Lower(ordering))
                    if inverted:
                        associations = associations.reverse()

            if studies:
                pagest = self.paginate_queryset(studies)
                study_serializer = StudySerializer(pagest, many=True)
            else:
                study_serializer = StudySerializer(studies, many=True)

            if associations:
                pageass = self.paginate_queryset(associations)
                association_serializer = AssociationListSerializer(pageass, many=True)
            else:
                association_serializer = AssociationListSerializer(associations, many=True)

            if phenotypes:
                pagephe = self.paginate_queryset(phenotypes)
                phenotype_serializer = PhenotypeListSerializer(pagephe, many=True)
            else:
                phenotype_serializer = PhenotypeListSerializer(phenotypes, many=True)

            counts = [len(associations), len(phenotypes), len(studies)]
            data = {'phenotype_search_results':phenotype_serializer.data,
                             'study_search_results':study_serializer.data,
                             'association_search_results':association_serializer.data,
                             'counts': counts}

            if any([studies,associations,phenotypes]):
                return self.get_paginated_response(data)
            else:
                return Response({i:data[i] for i in data if i!='counts'})



class SNPLocalViewSet(viewsets.ViewSet):
    """
    Attempt view to localize SNPs in neighboring areas
    """
    queryset = SNP.objects.none()

    @detail_route()
    def neighboring_snps(self, request, snp_pk, window_size=1000000, include=True):
        """
        Returns list of the neighboring SNPs, no information about LD (this will be retrieved or computed later)
        ---
        parameters:
            - name: snp_pk
              description: pk of the SNP of interest
              required: true
              type: string
              paramType: path
            - name: window_size
              description: number of bp around the SNP of interest (default = 1'000'000 bp)
              required: true
              type: int
              paramType: path
            - name: include
              description: include original SNP (default = True)
              required: true
              type: bool
              paramType: path

        serializer: SNPListSerializer
        omit_serializer: false
        """
        chromosome = SNP.objects.get(pk=snp_pk).chromosome
        position = SNP.objects.get(pk=snp_pk).position
        window_of_interest = [min(int(position) - window_size / 2, 0), int(
            position) + window_size / 2]  # no need to get chromosome size (since we'll run > or < queries)
        # Here we need to decide whether we include the original SNP or not.
        neighboring_s = SNP.objects.filter(chromosome=chromosome).filter(
            position__range=(window_of_interest[0], window_of_interest[1]))
        if not include:
            # Exclude original SNP
            neighboring_s = neighboring_s.filter(~Q(pk=snp_pk))
        if request.method == "GET":
            serializer = SNPListSerializer(neighboring_s, many=True)
            return Response(serializer.data)

    @detail_route()
    def snps_in_ld(request, snp_pk, N=20):
        """
        Returns list of the neighboring SNPs in high LD
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
        snp = SNP.objects.get(pk=snp_pk)
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
