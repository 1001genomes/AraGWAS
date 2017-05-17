from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.test import APIRequestFactory
from gwasdb.models import *
from gwasdb.serializers import *
from gwasdb import rest
from rest_framework import status


# Create your tests here.
# Basic db initialization:
def generate_basic_db():
    """
    generate database entries for tests
    """
    genotype1 = Genotype.objects.create(name="1001genomes", version="1.2")
    phenotype1 = Phenotype.objects.create(name="Length of something")
    study1 = Study.objects.create(name="McIntosh et al., 2010", transformation="log", method="LMM", genotype=genotype1, phenotype = phenotype1)
    study2 = Study.objects.create(name="Test2", transformation="log", method="LMM", genotype=genotype1, phenotype = phenotype1)
    SNP1 = SNP.objects.create(chromosome=1, position=45602, annotation="TAIR10", genotype=genotype1)
    SNP2 = SNP.objects.create(chromosome=2, position=100000, annotation="TAIR10", genotype=genotype1)
    SNP3 = SNP.objects.create(chromosome=2, position=100100, annotation="TAIR10", genotype=genotype1)
    association1 = Association.objects.create(study=study1, snp = SNP1, maf=0.24, pvalue=1.4e-8)
    association2 = Association.objects.create(study=study1, snp=SNP2, maf=0.24, pvalue=1.4e-8)
    association3 = Association.objects.create(study=study2, snp=SNP2, maf=0.24, pvalue=1.4e-8)



# Test models, to implement when we'll have methods
class ModelRelationshipTests(TestCase):
    def test_generation_basic_db(self):
        """
        Simple test to generate basic database with one genotype, one study
        :return:
        """
        generate_basic_db()

        self.assertIs(len(Study.objects.all()) == 1, True)

    def test_db_connections(self):
        """
        Test basic database connections in toy example
        :return:
        """
        generate_basic_db()
        self.assertEqual(Study.objects.get(pk=1).genotype, Genotype.objects.get(pk=1)) # Test study-genotype relationship
        self.assertNotEqual(Association.objects.get(pk=1).snp, Association.objects.get(pk=2).snp) # Test independence of associations

class SerializerTests(TestCase):

    def test_study_list_serializers(self):
        """
        Test the StudyListSerializer
        """
        generate_basic_db()
        study = Study.objects.get(pk=1)
        serialized = StudySerializer(study)
        # print(serialized.data)
        associations = Association.objects.all()
        snp2 = SNP.objects.get(pk=2)
        serialized_assoc = AssociationListSerializer(associations, many=True)
        # print(serialized_assoc.data[0]['snp'])
        self.assertEqual(serialized.data['name'], study.name)
        self.assertEqual(serialized_assoc.data[1]['snp'], snp2.get_name())


class ApiVersionTests(TestCase):

    def test_get_api_version(self):
        """test that api verison is returned"""

        factory = APIRequestFactory()
        request = factory.get(reverse('api-version'))
        view = rest.ApiVersionView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'date': '2017-04-26T09:11:18Z', 'version': 'N/A', 'build_url': None, 'build': 'N/A', 'github_url': 'https://github.com/1001genomes/aragwas/commit', 'githash': 'N/A'})

class SNPTests(TestCase):

    def test_neightboring_snps(self):
        """
        Test the rest.py neighboring_snps serializer
        """
        generate_basic_db()
        factory = APIRequestFactory()
        view = rest.SNPLocalViewSet.as_view(actions={'get': 'neighboring_snps'})
        request = factory.get(reverse('snp-neighboring-snps', args=(2,))+'?include=True')
        response1 = view(request, pk=2)
        request = factory.get(reverse('snp-neighboring-snps', args=(2,)))
        response2 = view(request, pk=2)
        request = factory.get(reverse('snp-neighboring-snps', args=(1,)))
        response3 = view(request, pk=1)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), 2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response3.data), 0)

class AssociationOfPhenotypeTests(TestCase):

    def test_association_of_phenotype(self):
        """
        Test the rest association of phenotype
        :return:
        """
        generate_basic_db()
        view = rest.AssociationsOfPhenotypeViewSet.as_view()