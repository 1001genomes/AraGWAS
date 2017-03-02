from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import AssociationListSerializer, AssociationValueSerializer, SNPListSerializer, StudyListSerializer

from rest_framework import status
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
