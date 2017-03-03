from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import *

from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

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

'''
Association details # Do we want to see individual associations or we will always only see them in a SNP or Study page?
'''
@api_view(['GET'])
def association_detail(request,q,format=None):
    """
    Detailed information about the association
    ---
    parameters:
        - name: q
          description: the id or doi of the phenotype
          required: true
          type: string
          paramType: path

    serializer: AssociationListSerializer
    omit_serializer: false

    """
    doi = _is_doi(DOI_PATTERN_PHENOTYPE,q)

    try:
        id = doi if doi else int(q)
        phenotype = Phenotype.objects.published().get(pk=id)
    except:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PhenotypeListSerializer(phenotype,many=False)
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
Retrieve neighboring SNPs (in high LD...)
"""