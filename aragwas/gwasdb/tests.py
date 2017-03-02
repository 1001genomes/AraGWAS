from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .models import *

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
    SNP1 = SNP.objects.create(name="rs1", chromosome=1, position=45602, annotation="TAIR10", genotype=genotype1)
    SNP2 = SNP.objects.create(name="rs2", chromosome=2, position=100000, annotation="TAIR10", genotype=genotype1)
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
    pass
