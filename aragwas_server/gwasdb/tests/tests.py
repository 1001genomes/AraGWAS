import os
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.test import APIRequestFactory
from gwasdb.models import *
from gwasdb.serializers import *
from gwasdb import rest
from rest_framework import status
from gwasdb import hdf5
import numpy as np
from gwasdb import elastic


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



# Test models, to implement when we'll have methods
class ModelRelationshipTests(TestCase):
    def test_generation_basic_db(self):
        """
        Simple test to generate basic database with one genotype, one study
        :return:
        """
        generate_basic_db()

        self.assertIs(len(Study.objects.all()) == 2, True)

    def test_db_connections(self):
        """
        Test basic database connections in toy example
        :return:
        """
        generate_basic_db()
        self.assertEqual(Study.objects.get(pk=1).genotype, Genotype.objects.get(pk=1)) # Test study-genotype relationship

class SerializerTests(TestCase):

    def test_study_list_serializers(self):
        """
        Test the StudyListSerializer
        """
        generate_basic_db()
        study = Study.objects.get(pk=1)
        serialized = StudySerializer(study)
        self.assertEqual(serialized.data['name'], study.name)


class ApiVersionTests(TestCase):

    def test_get_api_version(self):
        """test that api verison is returned"""

        factory = APIRequestFactory()
        request = factory.get(reverse('api-version'))
        view = rest.ApiVersionView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'date': '2017-04-26T09:11:18Z', 'version': 'N/A', 'build_url': None, 'build': 'N/A', 'github_url': 'https://github.com/1001genomes/aragwas/commit', 'githash': 'N/A'})


class HDF5LoadingTests(TestCase):

    def __init__(self, *args, **kwargs):
        self.hdf5_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/gwas.hdf5')
        super(HDF5LoadingTests, self).__init__(*args, **kwargs)

    def _check_return_array(self, top_associations):
        assert isinstance(top_associations, np.core.records.recarray)
        assert top_associations.dtype.names == ('chr', 'position', 'score', 'maf', 'mac', 'beta', 'se_beta')
        assert top_associations.dtype[0] == np.dtype('<U1')
        assert top_associations.dtype[1] == np.dtype('int32')
        assert top_associations.dtype[2] == np.dtype('float64')
        assert top_associations.dtype[3] == np.dtype('float64')
        assert top_associations.dtype[4] == np.dtype('int32')
        assert top_associations.dtype[5] == np.dtype('float64')
        assert top_associations.dtype[6] == np.dtype('float64')

    def test_load_top_associations_by_top_hits(self):
        """Test if top associations by number of hits cann be retrieved"""
        top_hit_num = 15
        top_hits = [('1', 6369772, 5.559458119903501, 0.1386861313868613, 19, 0.360335870170728, 0.0761941875889666),
                    ('2', 18351161, 5.221548337450959, 0.08029197080291971, 11, 0.328720498341187, 0.0747141063333232),
                    ('3', 18057816, 4.795206143400829, 0.2116788321167883, 29, -0.336795159960789, 0.0737295910747224),
                    ('4', 429928, 6.555416448260276, 0.4233576642335766, 58, 0.368255762771892, 0.0711756042811744 ),
                    ('5', 18577788, 6.219812361173065, 0.15328467153284672, 21, -0.327934944673749 ,0.0833854459419328 )]

        top_associations, thresholds = hdf5.get_top_associations(self.hdf5_file, top_hit_num, maf=0, top_or_threshold='top')
        assert thresholds['bonferroni_threshold01'] == 7.3140147710960965
        assert thresholds['bonferroni_threshold05'] == 6.615044766760077
        assert thresholds['bh_threshold'] == 6.6150447667600778
        assert thresholds['total_associations'] == 206070
        assert len(top_associations) == top_hit_num*5
        assert np.count_nonzero(top_associations['maf'] < 0.05) > 0
        self._check_return_array(top_associations)
        for i in range(0 ,5):
            assert top_associations[i*top_hit_num].tolist() == top_hits[i]

    def test_load_top_associations_by_top_threshold_and_maf(self):
        """Test if top associations by thresholds """
        top_associations, thresholds = hdf5.get_top_associations(self.hdf5_file, 1e-5, maf=0.1, top_or_threshold='threshold')
        assert len(top_associations) == 13
        assert np.count_nonzero(top_associations['maf'] < 0.1) == 0

    def test_load_top_associations_by_top_threshold(self):
        """Test if top associations by thresholds """
        top_associations, thresholds = hdf5.get_top_associations(self.hdf5_file, 5, maf=0, top_or_threshold='threshold')
        assert isinstance(top_associations, np.core.records.recarray)
        assert len(top_associations) == 14
        for assoc in top_associations:
            assert assoc['score'] >= 5.0

        top_associations_by_e, thresholds = hdf5.get_top_associations(self.hdf5_file, 1e-5, maf=0, top_or_threshold='threshold')
        assert isinstance(top_associations, np.core.records.recarray)
        assert len(top_associations) == len(top_associations_by_e)
        for i, assoc in enumerate(top_associations_by_e):
            assert assoc.tolist() == top_associations[i].tolist()

    def test_load_top_associations_by_top_hits_and_maf(self):
        """Test if top associations by number of hits cann be retrieved"""
        top_hit_num = 15
        top_hits = [('1', 6369772, 5.559458119903501, 0.1386861313868613, 19, 0.360335870170728, 0.0761941875889666),
                    ('2', 18351161, 5.221548337450959, 0.08029197080291971, 11, 0.328720498341187, 0.0747141063333232),
                    ('3', 18057816, 4.795206143400829, 0.2116788321167883, 29, -0.336795159960789, 0.0737295910747224),
                    ('4', 429928, 6.555416448260276, 0.4233576642335766, 58, 0.368255762771892, 0.0711756042811744 ),
                    ('5', 18577788, 6.219812361173065, 0.15328467153284672, 21, -0.327934944673749 ,0.0833854459419328 )]
        top_associations, thresholds = hdf5.get_top_associations(self.hdf5_file, top_hit_num, top_or_threshold='top')
        assert thresholds['bonferroni_threshold01'] == 7.294197188903931
        assert thresholds['bonferroni_threshold05'] == 6.5952271845679125
        assert thresholds['bh_threshold'] == 6.6150447667600778
        assert thresholds['total_associations'] == 196878
        assert len(top_associations) == top_hit_num*5
        assert np.count_nonzero(top_associations['maf'] < 0.05) == 0

        self._check_return_array(top_associations)
        for i in range(0 ,5):
            assert top_associations[i*top_hit_num].tolist() == top_hits[i]

    def test_regroup_top_assocations(self):
        top_associations, thresholds = hdf5.get_top_associations(self.hdf5_file, 5, maf=0, top_or_threshold='threshold')
        top_associations = hdf5.regroup_associations(top_associations)
        top_associations[0].tolist() == ('4',   429928,  6.55541645,  0.42335766, 58, 0.36825576, 0.0711756)
        top_associations[-1].tolist() == ('5', 18606578,  5.07844918,  0.47445255, 65, -0.34592279, 0.0832137)


class AssociationsFilteringTests(TestCase):

    def __init__(self, *args, **kwargs):
        self.hdf5_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/gwas.hdf5')
        super(AssociationsFilteringTests, self).__init__(*args, **kwargs)

    def test_load_top_associations_by_top_hits(self):
        #TODO: implement tests
        pass
