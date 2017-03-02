from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .models import *

# Create your tests here.
# Test models, to implement when we'll have methods
class ModelRelationshipTests(TestCase):
    def test_generation_basic_db(self):
        """
        Simple test to generate simple database with one genotype and one study
        :return:
        """
        genotype1 = Genotype(name="1001genomes", version="1.2")
        print("geno loaded succesfully")
        study1 = Study(name="McIntosh et al., 2010", transformation="log", method="LMM",genotype=genotype1)
        self.assertIs(study1.genotype == genotype1, True)

    def