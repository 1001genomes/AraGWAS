from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import *

from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

"""
List all associations
"""
@api_view(['GET'])
def association_list(request,format=None):
    """
    List all available associations
    :param request:
    :param format:
    :return:
    """
    associations = Association.objects.all()
    if request.method == "GET":
        serializer = AssociationListSerializer(associations,many=True)
        return Response(serializer.data)
"""
List all associations in details (with chromosome, position, beta, etc...)
"""
@api_view(['GET'])
def association_list_detail(request,format=None):
    """
    List all available associations
    :param request:
    :param format:
    :return:
    """
    associations = Association.objects.all()
    if request.method == "GET":
        serializer = AssociationValueSerializer(associations,many=True)
        return Response(serializer.data)

'''
Association details # Do we want to see individual associations or we will always only see them in a SNP or Study page?
'''
@api_view(['GET'])
def association_detail(request,pk,format=None):
    """
    Detailed information about the association
    ---
    parameters:
        - name: pk
          description: the id of the association
          required: true
          type: string
          paramType: path

    serializer: AssociationListSerializer
    omit_serializer: false

    """
    try:
        association = Association.objects.get(pk=pk)
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = AssociationValueSerializer(association, many=False)
        return Response(serializer.data)


'''
Search Endpoint
'''
@api_view(['GET'])
def search(request,query_term=None,format=None):
    """
    Search for an accession, a study, a SNP/gene or a phenotype
    ---
    parameters:
        - name: query_term
          description: the search term
          required: true
          type: string
          paramType: path

    serializer: AssociationListSerializer, StudyListSerializer, PhenotypeListSerializer
    omit_serializer: false
    """
    if request.method == "GET":
        if query_term==None:
            studies = Study.objects.all()
            phenotypes = Phenotype.objects.all()
            associations = Association.objects.all()
        else:
            studies = Study.objects.published().filter(Q(name__icontains=query_term) |
                                                  Q(phenotype__name__icontains=query_term))
            associations = Association.objects.published().filter(Q(snp__position__icontains=query_term) |
                                                  Q(snp__gene__name__icontains=query_term) |
                                                  Q(snp__icontains=query_term)) # Does this call the __unicode__ method of SNP?
            phenotypes = Phenotype.objects.filter(name__icontains=query_term)

        study_serializer = StudyListSerializer(studies,many=True)
        phenotype_serializer = PhenotypeListSerializer(phenotypes,many=True)
        association_serializer = AssociationListSerializer(associations,many=True)
        return Response({'phenotype_search_results':phenotype_serializer.data,
                         'study_search_results':study_serializer.data,
                         'accession_search_results':association_serializer.data})

"""
Retrieve neighboring SNPs
"""
# Need to review permission (this one is used for testing)
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def neighboring_snps(request, snp_pk, window_size=1000000, include = True, format=None):
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
    window_of_interest = [min(int(position)-window_size/2, 0), int(position) + window_size/2] # no need to get chromosome size (since we'll run > or < queries)
    # Here we need to decide whether we include the original SNP or not.
    neighboring_s = SNP.objects.filter(chromosome=chromosome).filter(position__range=(window_of_interest[0], window_of_interest[1]))
    if not include:
        # Exclude original SNP
        neighboring_s = neighboring_s.filter(~Q(pk=snp_pk))
    if request.method == "GET":
        serializer = SNPListSerializer(neighboring_s, many=True)
        return Response(serializer.data)

"""
Retrieve SNPs in high LD
"""
