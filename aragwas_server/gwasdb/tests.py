from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.test import APIRequestFactory
from gwasdb.models import *
from gwasdb.serializers import *
from gwasdb.rest import neighboring_snps

# Create your tests here.
# Basic db initialization:
def generate_basic_db():
    """
    Simple test to generate basic database with one genotype, one study
    :return:
    """
    genotype1 = Genotype.objects.create(name="1001genomes", version="1.2")
    phenotype1 = Phenotype.objects.create(name="Length of something")
    study1 = Study.objects.create(name="McIntosh et al., 2010", transformation="log", method="LMM", genotype=genotype1, phenotype = phenotype1)
    SNP1 = SNP.objects.create(chromosome=1, position=45602, annotation="TAIR10", genotype=genotype1)
    SNP2 = SNP.objects.create(chromosome=2, position=100000, annotation="TAIR10", genotype=genotype1)
    SNP3 = SNP.objects.create(chromosome=2, position=100100, annotation="TAIR10", genotype=genotype1)
    association1 = Association.objects.create(study=study1, snp = SNP1, maf=0.24, pvalue=1.4e-8)
    association2 = Association.objects.create(study=study1, snp=SNP2, maf=0.24, pvalue=1.4e-8)


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
        self.assertEqual(Study.objects.get(pk=1).genotype,Genotype.objects.get(pk=1)) # Test study-genotype relationship
        self.assertNotEqual(Association.objects.get(pk=1).snp, Association.objects.get(pk=2).snp) # Test independence of associations

class RESTAPITests(TestCase):
    def test_list_serializers(self):
        """
        Test the StudyListSerializer
        :return:
        """
        generate_basic_db()
        study = Study.objects.get(pk=1)
        serialized = StudySerializer(study)
        # print(serialized.data)
        associations = Association.objects.all()
        snp2 = SNP.objects.get(pk=2)
        serialized_assoc = AssociationListSerializer(associations, many=True)
        # print(serialized_assoc.data[0]['snp'])
        self.assertEqual(serialized.data['name'],study.name)
        self.assertEqual(serialized_assoc.data[1]['snp'],snp2.get_name())
    #
    # def setUp(self):
    #     # Every test needs access to request factory
    #     self.factory = APIRequestFactory()
    #     self.user = User.objects.create_user

    def test_neighboring_snps(self):
        """
        Test the rest.py neighboring_snps serializer
        :return:
        """
        generate_basic_db()
        factory = APIRequestFactory()
        request = factory.get('/results')
        neighboring_SNP1 = neighboring_snps(request, snp_pk=1, include=False)
        neighboring_SNP2 = neighboring_snps(request, snp_pk=2)
        self.assertTrue(neighboring_SNP2)
        self.assertTrue(len(neighboring_SNP1.data) == 0)
        pass