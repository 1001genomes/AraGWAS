import os, coreapi, coreschema
import requests
import numpy as np

from rest_framework import permissions
from rest_framework import viewsets, generics, filters, renderers
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from gwasdb.models import Phenotype, Study, Genotype
from gwasdb.serializers import *
from gwasdb.paginator import CustomSearchPagination, CustomAssociationsPagination, EsPagination

from rest_framework import status
from django.db.models import Q
from wsgiref.util import FileWrapper
import mimetypes
from django.http import StreamingHttpResponse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.encoding import smart_str
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from gwasdb.hdf5 import get_top_associations, regroup_associations, get_ko_associations, get_snps_from_genotype

from gwasdb.tasks import compute_ld, download_es2csv
from gwasdb import __version__, __date__, __githash__,__build__, __buildurl__
from aragwas import settings
from gwasdb import elastic


from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Range
from elasticsearch_dsl.query import Q as QES
from elasticsearch import Elasticsearch
from aragwas.settings import ES_HOST

from gwasdb.parsers import parse_lastel


import numpy, math

def get_api_version():
    BUILD_STATUS_URL = None
    if __buildurl__ != 'N/A':
        BUILD_STATUS_URL = __buildurl__
    return {'version':__version__,'date':__date__,'githash':__githash__,'build':__build__,'build_url':BUILD_STATUS_URL,'github_url':settings.GITHUB_URL}

def _get_filter_from_params(params):
    annos_dict = {'ns': 'NON_SYNONYMOUS_CODING', 's': 'SYNONYMOUS_CODING', 'i': 'INTERGENIC', 'in': 'INTRON'}
    # retrieve and sort filters.
    filter_chr = params.getlist('chr')
    filter_maf = params.getlist('maf')
    filter_mac = params.getlist('mac')
    annos = params.getlist('annotation')
    filter_annot = [annos_dict[k] for k in annos]
    filter_type = params.getlist('type')
    filter_study = params.getlist('study_id')
    filter_phenotype = params.getlist('phenotype_id')
    filter_genotype = params.getlist('genotype_id')
    filter_significant = params.getlist('significant')
    filters = {'chr':filter_chr, 'maf': filter_maf, 'mac': filter_mac, 'annotation': filter_annot, 'type': filter_type, 'study_id':filter_study, 'phenotype_id': filter_phenotype, 'genotype_id': filter_genotype, 'significant': filter_significant}
    return filters

def _check_missing_filters(filters):
    if 'chrom' not in filters.keys():
        filters['significant']=['p']
    return filters

def _get_percentages_from_buckets(buckets):
    out_dict = {}
    annos_dict = {'NON_SYNONYMOUS_CODING': 'ns', 'SYNONYMOUS_CODING': 's', 'INTERGENIC': 'i', 'INTRON': 'in'}
    tot_sum = sum(i['doc_count'] for i in buckets)
    if tot_sum == 0:
        for i in buckets:
            out_dict[annos_dict[i['key']] if i['key'] in annos_dict else str(i['key'])] = 0
    else:
        for i in buckets:
            out_dict[annos_dict[i['key']] if i['key'] in annos_dict else str(i['key'])] = float(
                i['doc_count']) / tot_sum
    return out_dict

def _is_filter_whole_dataset(filters):
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        return False
    if 'maf' in filters and len(filters['maf']) > 0 and len(filters['maf']) < 4:
        return False
    if 'mac' in filters and len(filters['mac']) > 0 and len(filters['mac']) < 2:
        return False
    if 'annotation' in filters and len(filters['annotation']) > 0 and len(filters['annotation']) < 4:
        return False
    if 'type' in filters and len(filters['type'])==1:
        return False
    if 'study_id' in filters and len(filters['study_id']) > 0:
        return False
    if 'phenotype_id' in filters and len(filters['phenotype_id']) > 0:
        return False
    if 'start' in filters:
        return False
    if 'end' in filters:
        return False
    if 'significant' in filters:
        if filters['significant'] == ['p'] or filters['significant'] == ['b']:
            return False
    return True


def get_accession_phenotype_values(phenotype_id):
    r = requests.get('https://arapheno.1001genomes.org:443/rest/phenotype/{}/values.json'.format(phenotype_id))
    js = r.json()
    return js

class EsQuerySet(object):

    def __init__(self, data, count):
        self._count = count
        self._data = data

    def count(self):
        return self._count

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        return self._data

class EsQuerySetLastEl(object):

    def __init__(self, data, count, lastel):
        self._count = count
        self._data = data
        self._lastel = lastel

    def count(self):
        return self._count

    def lastel(self):
        return self._lastel

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        return self._data

class EsViewSetMixin(object):

    pagination_class = EsPagination

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator


    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

class ApiVersionView(APIView):
    """ API for version information """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """ Returns the git hash commit and version information """
        serializer = ApiVersionSerializer(get_api_version(), many=False)
        return Response(serializer.data)

class GenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for genotypes

    list:
    List available genotypes.

    retrieve:
    Retrieve information about a specific genotype.
    """
    queryset = Genotype.objects.all()
    serializer_class = GenotypeSerializer

    def filter_queryset(self, queryset):
        return queryset

    @list_route(methods=['GET'], url_path='download')
    def download(self, request):
        """Download the SNP matrix used for GWAS analyses"""
        bulk_file = "%s/genotype.zip" % (settings.HDF5_FILE_PATH)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(bulk_file,"rb"), chunk_size),content_type="application/x-zip")
        response['Content-Length'] = os.path.getsize(bulk_file)
        response['Content-Disposition'] = "attachment; filename=genotype.zip"
        return response

class StudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for studies

    list:
    List all available GWA studies.

    retrieve:
    Retrieve information about a specific GWA study.
    """
    queryset = Study.objects.all()
    serializer_class = StudySerializer

    def filter_queryset(self, queryset):
        return queryset

    def hide_list_fields(self, view):
        return

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
            if ordering == 'nHitsBonferroni':
                ordering = 'n_hits_bonf'
            if ordering == 'nHitsPermutation':
                ordering = 'n_hits_perm'
            else:
                ordering = Lower(ordering)
            queryset = queryset.order_by(ordering)
            if inverted:
                queryset = queryset.reverse()
        return queryset



    @detail_route(methods=['GET'], url_path='download')
    def download(self, request, pk):
        """Download the HDF5 file for the specific study. """
        study_file = "%s/gwas_results/%s.hdf5" % (settings.HDF5_FILE_PATH, pk)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(study_file,"rb"), chunk_size),content_type="application/x-hdf5")
        response['Content-Length'] = os.path.getsize(study_file)
        response['Content-Disposition'] = "attachment; filename=%s.hdf5" % pk
        return response

    @list_route(methods=['GET'], url_path='bulk_download')
    def bulkdownload(self, request):
        """Download all the compressed HDF5 files. """
        bulk_file = "%s/aragwas_db.zip" % (settings.HDF5_FILE_PATH)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(bulk_file,"rb"), chunk_size),content_type="application/x-zip")
        response['Content-Length'] = os.path.getsize(bulk_file)
        response['Content-Disposition'] = "attachment; filename=aragwas_db.zip"
        return response

    @detail_route(methods=['GET'], url_path='associations')
    def top_associations(self, request, pk):
        """ Retrieve top associations for the selected study. Can add other filters. Check the FAQ for details on the filters. """
        filters = _get_filter_from_params(request.query_params)
        filters['study_id'] = [pk]
        paginator = EsPagination()
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        associations, count = elastic.load_filtered_top_associations(filters,offset,limit)
        queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_asso)

    @detail_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request, pk):
        """
        Retrieve the aggregation statistics of the top assocations for a study and a specific set of filters. Check the FAQ for details on the filters.
        """
        filters = _get_filter_from_params(request.query_params)
        filters['study_id'] = [pk]
        chr, maf, mac, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        mac_dict = _get_percentages_from_buckets(mac)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'mac': mac_dict, 'types': type_dict, 'annotations': annotations_dict})

    @detail_route(methods=['GET'], url_path='gwas')
    def assocations_from_hdf5(self, request, pk):
        """ Retrieve associations from the HDF5 file of the study. Must provide 'filter_type' (which can be = 'top', to only retrieve the top N associations, or 'threshold', to retrieve all associations above the threshold) and 'filter' (which is either the threshold or the number of desired associations) params in url. """
        filter_type = request.query_params.get('filter_type', 'threshold')
        if filter_type not in ('threshold', 'top'):
            raise ValueError('filter_type must be either "threshold" or "top"')
        threshold_or_top = float(request.query_params.get('filter', 1))
        if filter_type == 'top':
            threshold_or_top = int(threshold_or_top)

        association_file = os.path.join(settings.HDF5_FILE_PATH, 'gwas_results', '%s.hdf5' % pk)
        top_associations, thresholds = get_top_associations(association_file, maf=0, val=threshold_or_top, top_or_threshold=filter_type)
        output = {}
        prev_idx = 0
        for chrom in range(1, 6):
            chr_idx = top_associations['chr'].searchsorted(str(chrom+1))
            output['chr%s' % chrom] = {'scores': top_associations['score'][prev_idx:chr_idx], 'positions': top_associations['position'][prev_idx:chr_idx], 'mafs': top_associations['maf'][prev_idx:chr_idx]}
            prev_idx = chr_idx
        for key, value in thresholds.items():
            value = int(value) if key == 'total_associations' else float(value)
            thresholds[key] = value
        output['thresholds'] = thresholds
        return Response(output, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'], url_path='ko_mutations')
    def ko_assocations_from_csv(self, request, pk):
        """ Retrieve KO associations from the csv file of the study."""
        ko_association_file = os.path.join(settings.HDF5_FILE_PATH,'ko', 'LOS%s.csv' % pk)
        ko_associations, thresholds = get_ko_associations(ko_association_file)
        output = {}
        prev_idx = 0
        for chrom in range(1, 6):
            chr_idx = ko_associations['chr'].searchsorted(str(chrom+1))
            output['chr%s' % chrom] = {'genes': ko_associations['gene'][prev_idx:chr_idx],
                'scores': ko_associations['score'][prev_idx:chr_idx],
                'positions': ko_associations['position'][prev_idx:chr_idx],
                'mafs': ko_associations['maf'][prev_idx:chr_idx]}
            prev_idx = chr_idx
        for key, value in thresholds.items():
            value = int(value) if key == 'total_associations' else float(value)
            thresholds[key] = value
        output['thresholds'] = thresholds
        return Response(output, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'], url_path='top')
    def top_genes_and_snp_type(self, request, pk):
        """ Get genes and SNP type that got the most significant associations for a specific study. """
        agg_results= elastic.get_top_genes_and_snp_type_for_study(pk)
        response = {}
        for key in agg_results.keys():
            if key == "snp_type_count":
                list_top_snp_type = []
                for i in agg_results[key]:
                    if i['key'] == 1:
                        label = 'Genic'
                    else:
                        label = 'Non genic'
                    list_top_snp_type.append([label, i['doc_count']])
                response['on_snp_type'] = list_top_snp_type
            elif key == "maf_hist":
                print(agg_results[key])
                # Need to check if all consequent maf ranges are present
                list_maf = []
                if len(agg_results[key]) > 0:
                    max = agg_results[key][-1]['key']
                    c = 0
                    for i in range(int(max*10)+1):
                        if agg_results[key][c]['key']== float(i)/10:
                            list_maf.append([agg_results[key][c]['key'], agg_results[key][c]['doc_count']])
                            c += 1
                        else:
                            list_maf.append([float(i)/10, 0])
                response[key]=list_maf
            else:
                list = []
                for i in agg_results[key]:
                    list.append([i['key'], i['doc_count']])
                response[key]=list
        return Response(response)

class PhenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for phenotypes

    list:
    List available phenotypes.

    retrieve:
    Retrieve information about a specific phenotype.
    """
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeListSerializer

    def filter_queryset(self, queryset):
        return queryset

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

    @detail_route(methods=['GET'], url_path='studies')
    def studies(self, requests, pk):
        """ Get a list of studies for a specific phenotype """
        studies = Study.objects.filter(phenotype__id = pk)
        serializer = StudySerializer(studies, many=True)
        return Response(serializer.data)

    # @detail_route(methods=['GET'], url_path='associations')
    # def top_assocations(self, request, pk):
    #     """ Retrieve top associations for the selected phenotype. Can add other filters. Check the FAQ for details on the filters. """
    #     filters = _get_filter_from_params(request.query_params)
    #     filters['phenotype_id'] = [pk]
    #     paginator = EsPagination()
    #     limit = paginator.get_limit(request)
    #     offset = paginator.get_offset(request)
    #     associations, count = elastic.load_filtered_top_associations(filters,offset,limit)
    #     queryset = EsQuerySet(associations, count)
    #     paginated_asso = self.paginate_queryset(queryset)
    #     return self.get_paginated_response(paginated_asso)

    # @detail_route(methods=['GET'], url_path='aggregated_statistics')
    # def aggregated_statistics(self, request, pk):
    #     """ Retrieve the aggregation statistics of the top assocations for a phenotype and a specific set of filters. Check the FAQ for details on the filters. """
    #     filters = _get_filter_from_params(request.query_params)
    #     filters['phenotype_id'] = [pk]
    #     chr, maf, mac, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
    #     chr_dict = _get_percentages_from_buckets(chr)
    #     maf_dict = _get_percentages_from_buckets(maf)
    #     mac_dict = _get_percentages_from_buckets(mac)
    #     type_dict = _get_percentages_from_buckets(type)
    #     annotations_dict = _get_percentages_from_buckets(annotations)
    #     return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'mac': mac_dict, 'types': type_dict, 'annotations': annotations_dict})

class AssociationViewSet(EsViewSetMixin, viewsets.ViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (r.CSVRenderer, )

    """ API for associations """
    def hide_list_fields(self, view):
        return

    def retrieve(self, request, pk):
        """ Retrieve information about a specific association """
        association = elastic.load_associations_by_id(pk)
        return Response(association)


    def list(self, request):
        """ List all associations sorted by score. """
        filters = _get_filter_from_params(request.query_params)
        if len(filters['significant']) == 0:
            filters['significant'] = 'p'
        last_el = request.query_params.get('lastel', '')
        associations, count, lastel = elastic.load_filtered_top_associations_search_after(filters,last_el)
        queryset = EsQuerySetLastEl(associations, count, lastel)
        # associations, count = elastic.load_filtered_top_associations(filters,offset,limit)
        # queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response({'results': paginated_asso, 'count': count, 'lastel': [lastel[0], lastel[1]]})

    @detail_route(methods=['GET'], url_path='details')
    def associations(self, request, pk, format=None):
        """ Return details for a specific assocation """
        association = elastic.load_associations_by_id(pk)
        study_id, chr, position = pk.split('_')
        study = Study.objects.get(pk=study_id)
        data = get_accession_phenotype_values(study.phenotype.pk)
        accessions = np.asarray(list(map(lambda item: item['accession_id'], data)), dtype='|S6')
        #[:,0].astype(np.dtype('|S6'))
        genotype_file = "%s/GENOTYPES/%s.hdf5" % (settings.HDF5_FILE_PATH, study.genotype.pk)
        alleles, genotyped_accessions = get_snps_from_genotype(genotype_file,int(chr),int(position), int(position), accession_filter = accessions)
        filtered_accessions_idx = np.in1d(accessions, genotyped_accessions)
        filtered_data = []
        for info, allele, is_genotyped in zip(data, alleles.tolist()[0], filtered_accessions_idx.tolist()):
            if is_genotyped:
                info['allele'] = association['snp']['alt'] if allele else association['snp']['ref']
                filtered_data.append(info)
        return Response(filtered_data)


    @list_route(url_path='count')
    def count(self, request):
        """  Retrieve the number of significant associations in the database. """
        client = Elasticsearch([ES_HOST], timeout=60)
        count = Search().using(client).doc_type('associations').query('match_all').filter('term',overPermutation='T').filter('range',mac={'gte':6}).count()
        return Response(count)

    @list_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request):
        """ Retrieve the aggregation percentage for associations meeting filters criteria. Check the FAQ for details on the filters."""
        filters = _get_filter_from_params(request.query_params)
        chr, maf, mac, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        mac_dict = _get_percentages_from_buckets(mac)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'mac': mac_dict, 'types': type_dict, 'annotations': annotations_dict})


    @list_route(methods=['GET'], url_path='map_histogram')
    def data_for_histogram(self, request):
        """ Get hitmap histogram data. Parameters need to be included in the filters. Check the FAQ for details on the filters."""
            # Usage: chrom = indicate the chromosome(s) of interest ('all' or any chromosome),
            #     region_width = indicate the size of the bins for which to count hits should be passed under the form,
            #     threshold = indicate the type of threshold to look at (FDR, Bonferroni, permutation or none, default='FDR')
            #     region = indicate a specific window in which to aggregate for, default = ('','') looks at entire chromosome
            #     maf = indicate a minimum maf (default=0)
            #     mac = indicate a minimum mac (default=0)
        # Get bin size
        filters = dict()
        filters['region_width'] = max(1,int(request.query_params.get('region_width')))
        recompute = request.query_params.getlist('recompute')
        if recompute != []:
            filters['chrom'] = request.query_params.get('chromosome')
            region = request.query_params.getlist('region')
            filters['region'] = (int(region[0]), int(region[1]))
        # get the rest of the data
        results = elastic.get_gwas_overview_bins_data(filters)
        return Response(results)

    @list_route(methods=['GET'], url_path='map_heat')
    def data_for_heatmap(self, request):
        """ Get hitmap data. Parameters need to be included in the filters. Check the FAQ for details on the filters."""
            # Usage: chrom = indicate the chromosome(s) of interest ('all' or any chromosome),
            #     region_width = indicate the size of the bins for which to count hits,
            #     threshold = indicate the type of threshold to look at (FDR, Bonferroni, permutation or none, default='FDR')
            #     region = indicate a specific window in which to aggregate for, default = ('','') looks at entire chromosome
            #     maf = indicate a minimum maf (default=0)
            #     mac = indicate a minimum mac (default=0)
        # Load studies from regular db
        recompute = request.query_params.getlist('recompute')
        if recompute == []:
            # import requests
            file_name = "%s/heatmap_data.json" % (settings.HDF5_FILE_PATH)
        #     url = 'https://gist.githubusercontent.com/mtog/95d29b45e0f58e5c11dc61818f4c57fb/raw/b5bf20b80d168e6d3a3a261e204c34a97c72ba5b/pre_loaded_heatmap_data.json'
        #     return Response(requests.get(url).json())
            import json
            with open(file_name) as data_file: # There seems to be a displaying problem when loading from file: the histograms are loaded and displayed twice
                data = json.load(data_file)
            return Response(data)
        studies = Study.objects.all()
        studies_data = []
        for study in studies:
            studies_data.append(
                {'id': study.id, 'name': study.phenotype.name})  # For now only add phenotype name for shorted strings
        # get the rest of the data
        filters = dict()
        # Get region params for zoomed regions...
        filters['chrom'] = request.query_params.get('chromosome')
        region = request.query_params.getlist('region')
        filters['region']=(int(region[0]),int(region[1]))
        filters['region_width'] = request.query_params.get('regionwidth')
        results = elastic.get_gwas_overview_heatmap_data(filters, len(studies))
        results['studies'] = studies_data
        return Response(results)

    @list_route(methods=['GET'], url_path='download')
    def download_csv(self, request):
        """ Prepare a csv file from the elasticsearch database and return it as a downloadable file through a celery task. Check the FAQ for details on the filters.
        """
        # Load studies from regular db
        import datetime
        filters = _get_filter_from_params(request.query_params)
        gene_id = request.query_params.getlist('gene_id') # We need to do this because we cannot solely rely on the annotations of the SNPs for gene-name
        import os
        export_folder = '%s/export' % settings.HDF5_FILE_PATH
        if not os.path.isdir(export_folder):
            os.mkdir(export_folder)
        # Other download basenames:
        download_name = "aragwas_associations"
        if filters['study_id'] != []:
            stid = filters['study_id']
            if isinstance(filters['study_id'], list):
                stid = stid[0]
                # filters['study_id'] = filters['study_id'][0]
            study_name = Study.objects.get(pk=stid).name
            download_name = "{}_associations".format(study_name)
        elif filters['phenotype_id'] != []:
            phenotype_name = Phenotype.objects.get(pk=filters['phenotype_id']).name
            download_name = "{}_associations".format(phenotype_name)
        if gene_id != []:
            download_name = "{}_associations".format(gene_id[0]) # Override previous ones
            zoom = int(request.query_params.getlist('zoom')[0])
            print(zoom)
            gene = elastic.load_gene_by_id(gene_id[0])
            filters['chr'] = [gene['chr']]
            filters['start'] = gene['positions']['gte'] - zoom
            filters['end'] = gene['positions']['lte'] + zoom
        if _is_filter_whole_dataset(filters):
            # download_name = "all_associations"
            file_name = "%s/all_associations.zip" % (settings.HDF5_FILE_PATH)
            chunk_size = 8192
            response = StreamingHttpResponse(FileWrapper(open(file_name, "rb"), chunk_size),
                                             content_type="text/csv")
            response['Content-Length'] = os.path.getsize(file_name)
        else:
            file_name = '%s/' % export_folder +str(datetime.datetime.now())+'.csv' # give it a unique name
            opts = dict(doc_type='associations', output_file=file_name)
            fn = download_es2csv(opts, filters)
            # wait for file to be done
            # Add filters to name:
            if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
                download_name += "_chr"
                for c in filters['chr']:
                    download_name += "_{}".format(c)
            if 'maf' in filters and len(filters['maf']) > 0 and len(filters['maf']) < 4:
                download_name += "_maf_filtered"
            if 'annotation' in filters and len(filters['annotation']) > 0 and len(filters['annotation']) < 4:
                download_name += "_annotation_filtered"
            if 'type' in filters and len(filters['type']) == 1:
                download_name += "_{}".format(filters['type'][0])
            if 'significant' in filters:
                if filters['significant'] == ['p']:
                    download_name += "_significant_permutation"
                elif filters['significant'] == ['b']:
                    download_name += "_significant_bonferroni"

            chunk_size = 8192
            response = StreamingHttpResponse(FileWrapper(open(file_name, "rb"), chunk_size),
                            content_type="text/csv")
            response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = "attachment; filename={}.csv".format(download_name)
        return response

class KOAssociationViewSet(EsViewSetMixin, viewsets.ViewSet):
    """ API for KO associations """
    def hide_list_fields(self, view):
        return

    def retrieve(self, request, pk):
        """ Retrieve information about a specific association """
        ko_association = elastic.load_ko_associations_by_id(pk)
        return Response(ko_association)


    def list(self, request):
        """ List all KO associations sorted by score. """
        filters = _get_filter_from_params(request.query_params)
        if len(filters['significant']) == 0:
            filters['significant'] = 'b' # TODO: change this to p once the permutations values are entered
        last_el = request.query_params.get('lastel', '')
        size = int(request.query_params.get('limit', 50))
        associations, count, lastel = elastic.load_filtered_top_ko_associations_search_after(filters,last_el, size)
        queryset = EsQuerySetLastEl(associations, count, lastel)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response({'results': paginated_asso, 'count': count, 'lastel': [lastel[0], lastel[1]]})

    @list_route(methods=['GET'], url_path='original_mutations')
    def originaldownload(self, request):
        """Download all the compressed csv files. """
        bulk_file = "%s/ko_original_mutations.zip" % (settings.HDF5_FILE_PATH)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(bulk_file,"rb"), chunk_size),content_type="application/x-zip")
        response['Content-Length'] = os.path.getsize(bulk_file)
        response['Content-Disposition'] = "attachment; filename=ko_original_mutations.zip"
        return response

    @list_route(methods=['GET'], url_path='bulk_download')
    def bulkdownload(self, request):
        """Download all the compressed csv files. """
        bulk_file = "%s/ko_csv.zip" % (settings.HDF5_FILE_PATH)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(bulk_file,"rb"), chunk_size),content_type="application/x-zip")
        response['Content-Length'] = os.path.getsize(bulk_file)
        response['Content-Disposition'] = "attachment; filename=ko_mutations_associations.zip"
        return response


class GeneViewSet(EsViewSetMixin, viewsets.ViewSet):
    """ API for genes """

    def list(self, request):
        """List all genes in the database. Can add 'chr', 'start' and 'end' as params in the url request."""
        chrom = request.query_params.get('chr','1')
        start = request.query_params.get('start',0)
        end = request.query_params.get('end', 100000)
        is_features = 'features' in request.query_params
        genes = elastic.load_genes_by_region(chrom,start,end,is_features)
        return Response(genes)

    def retrieve(self, request, pk):
        """ Retrieve information about a specific gene """
        gene = elastic.load_gene_by_id(pk)
        gene['ko_associations'] = elastic.load_gene_ko_associations(pk, return_only_significant=True)
        return Response(gene)

    @list_route(methods=['GET'], url_path='autocomplete')
    def autocomplete(self, request):
        """ Autocomplete gene name based on query term. Need to add 'term' as url params. """
        search_term = request.query_params.get('term', '')
        genes = elastic.autocomplete_genes(search_term)
        return Response(genes)

    # @detail_route(methods=['GET'], url_path='snps')
    # def snps(self, request, pk):
    #     """ Return SNPs for the selected gene. """
    #     gene = elastic.load_gene_by_id(pk)
    #     gene['snps'] = elastic.load_snps_by_region(gene['chr'], gene['positions']['gte'],gene['positions']['lte'])
    #     return Response(gene)

    @detail_route(methods=['GET'], url_path='associations')
    def associations(self, request, pk):
        """ Return associations for the selected gene. Can add zoom and other filters. Check the FAQ for details on the filters. """
        gene = elastic.load_gene_by_id(pk)
        zoom = int(request.query_params.get('zoom', 0))
        selected = bool(request.query_params.get('gene', '') == "1")
        # last_el = [request.query_params.get('lastel', '')]
        filters = _get_filter_from_params(request.query_params)
        filters['chr'] = [gene['chr']]
        filters['start'] = gene['positions']['gte'] - zoom
        filters['end'] = gene['positions']['lte'] + zoom
        if selected:
            filters['start'] = gene['positions']['gte']
            filters['end'] = gene['positions']['lte']
            filters['gene_id'] = gene['name']
        limit = self.paginator.get_limit(request)
        offset = self.paginator.get_offset(request)
        associations, count = elastic.load_filtered_top_associations(filters, offset, limit)
        queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_asso)

    @detail_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request, pk):
        """ Retrieve the aggregation percentage for associations meeting filters criteria for this gene. Check the FAQ for details on the filters. """
        gene = elastic.load_gene_by_id(pk)
        zoom = int(request.query_params.get('zoom', 0))
        selected = bool(request.query_params.get('gene', '') == "1")
        # last_el = [request.query_params.get('lastel', '')]
        filters = _get_filter_from_params(request.query_params)
        filters['chr'] = [gene['chr']]
        filters['start'] = gene['positions']['gte'] - zoom
        filters['end'] = gene['positions']['lte'] + zoom
        if selected:
            filters['start'] = gene['positions']['gte']
            filters['end'] = gene['positions']['lte']
            filters['gene_id'] = gene['name']
        chr, maf, mac, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        mac_dict = _get_percentages_from_buckets(mac)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'mac': mac_dict,'types': type_dict, 'annotations': annotations_dict})


    @list_route(methods=['GET'], url_path='top')
    def top(self, requests):
        """ Retrieve the top genes based on the number of significant assocations. """
        agg = elastic.get_top_genes()
        list_top_genes = []
        for i in agg:
            list_top_genes.append([i['key'], i['doc_count']])
        return Response(list_top_genes)

    @list_route(methods=['GET'], url_path='top_list')
    def top_list(self, request):
        """ Retrieve the top genes based on the number of significant associations and provide full gene information. """
        filters = _get_filter_from_params(request.query_params)
        if filters['significant'] == []:
            filters['significant'] = ['p']
        paginator = EsPagination()
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        genes, count = elastic.load_filtered_top_genes(filters, offset, limit)
        queryset = EsQuerySet(genes, count)
        paginated_genes = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_genes)

    @list_route(methods=['GET'], url_path='top_ko_list')
    def top_ko_list(self, request):
        """ Retrieve the top genes based on the number of significant KO mutations and provide full gene information. """
        filters = _get_filter_from_params(request.query_params)
        if filters['significant'] == []:
            filters['significant'] = ['p']
        paginator = EsPagination()
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        genes, count = elastic.load_filtered_top_ko_mutations_genes(filters, offset, limit)
        queryset = EsQuerySet(genes, count)
        paginated_genes = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_genes)

    @list_route(methods=['GET'], url_path='top_list_aggregated_statistics')
    def top_genes_aggregated_statistics(self, request):
        """ Retrieve the aggregation percentage for genes in the top list. Check the FAQ for details on the filters. """
        filters = _get_filter_from_params(request.query_params)
        chr = elastic.get_top_genes_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        return Response({'chromosomes': chr_dict})

class SNPViewSet(viewsets.ViewSet):
    """ API for SNPs """

    def list(self, request):
        """ Retrieve a list of all SNPs. (Inactive) """
        pass

    def retrieve(self, request, pk):
        """ Retrieve information about a particular SNP. (Inactive) """
        pass

    # @detail_route(methods=['GET'], url_path='neighboring')
    # def neighboring_snps(self, request, pk):
    #     """
    #     Return a list of the neighboring SNPs. (Inactive)
    #     """
    #     window_size=request.GET.get('window_size', 1000000)
    #     include = 'include' in request.GET
    #     # TODO implement
    #     return Response({})
    #
    # @detail_route(methods=['GET'], url_path='ld')
    # def snps_in_ld(request, pk):
    #     """
    #     Return a list of the neighboring SNPs in high LD. (Inactive)
    #     """
    #     N = request.GET.get('N',20)
    #     # TODO implement
    #     ordered_positions, ordered_ld = compute_ld(snp.chromosome, snp.position, genotype_name)
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

    @list_route(methods=['GET'], url_path='aggregated')
    def aggregated_statistics(self, requests):
        """ Retrieve general statistics (percentage) about all SNPs. """
        chr, maf, mac, type, annotations = elastic.get_aggregated_filtered_statistics({1:1})
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        mac_dict = _get_percentages_from_buckets(mac)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'mac': mac_dict, 'types': type_dict, 'annotations': annotations_dict})

class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """ API for search """

    queryset = Study.objects.all()
    query_term = None
    serializer_class = StudySerializer
    pagination_class = CustomSearchPagination

    def filter_queryset(self, queryset):
        return queryset

    @list_route(url_path='search_results')
    def search_result(self, request):
        """ Display results without search term. """
        return self.search_results(request, query_term=None)

    @detail_route()
    def search_results(self, request, query_term):
        """ Display results based on search term. """
        is_gene_suggest = False
        if request.method == "GET":
            client = Elasticsearch([ES_HOST], timeout=60)
            search_gene = Search().using(client).doc_type('genes').source(exclude=['isoforms.cds','isoforms.exons','GO'])#'isoforms.cds','GO'])
            if query_term==None:
                studies = Study.objects.all()
                phenotypes = Phenotype.objects.all()
                # Elasticsearch query cannot be made before knowing the ordering and the page number, etc as this is taken into account by elasticsearch.py
            else:
                studies = Study.objects.filter(Q(name__icontains=query_term) | Q(phenotype__trait_ontology_name__icontains=query_term) |
                                                      Q(phenotype__name__icontains=query_term) | Q(phenotype__description__icontains=query_term) | Q(publication_pmid__icontains=query_term) | Q(publication_pmcid__icontains=query_term)).order_by('n_hits_perm').reverse()
                phenotypes = Phenotype.objects.filter(Q(name__icontains=query_term) |
                                                      Q(description__icontains=query_term)).order_by('name')
                # Add chromosome position search for genomic regions
                try:
                    int(query_term)
                    isnum = True
                except ValueError:
                    isnum = False
                import re
                pattern = re.compile("(Chr|CHR|chr)+\s?([0-9]{1,2})+(-|:)?(\d*)\s*(-|:|)?\s*(\d+|)")
                if isnum: # Only a number, look for neighboring genes on all chromosomes.
                    q = QES('range', positions={"gte":int(query_term), 'lte':int(query_term)})
                    search_gene = search_gene.query(q)
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
                    q = QES('match', chr='chr'+str(chr))
                    search_gene = search_gene.query(q)
                    if s_p:
                        if e_p:
                            # Look for genes overlapping with region of interest
                            q = QES('range', positions={'gte':s_p, 'lte':e_p})|QES('range', positions={'gte':s_p, 'lte':s_p})|QES('range', positions={'gte':e_p, 'lte':e_p})
                        else:
                            q = QES('range', positions={'gte':s_p, 'lte':s_p}) | QES('range', positions={'gte': s_p})
                        search_gene = search_gene.query(q)
                else: # other type of request
                    is_gene_suggest = True
                    search_gene = search_gene.suggest('gene_suggest', query_term, completion={'field': 'suggest', 'size': 200})
            # custom ordering
            ordering = request.query_params.get('ordering', None)
            ordering_fields = {'studies': ['name','genotype','phenotype','method','transformation'], 'phenotypes': ['name', 'description'], 'genes': ['name', 'chr', 'start', 'end', 'SNPs_count', 'association_count', 'description']}
            if ordering is not None:
                from django.db.models.functions import Lower
                inverted = False
                if ordering.startswith('-'):
                    inverted = True
                    ordering = ordering[1:]
                if ordering in ordering_fields['studies'] and studies:
                    if ordering == 'phenotype' or ordering == 'genotype': # Need to reference the names and not the internal IDs for ordering
                        ordering += '__name'
                    studies = studies.order_by(Lower(ordering)).reverse()
                    if inverted:
                        studies = studies.reverse()
                if ordering in ordering_fields['phenotypes'] and phenotypes:
                    phenotypes = phenotypes.order_by(Lower(ordering))
                    if inverted:
                        phenotypes = phenotypes.reverse()
                if ordering in ordering_fields['genes']:
                    # if ordering == 'snp' or ordering == 'study':
                    #     ordering += '__name'
                    # genes = genes.order_by(Lower(ordering))
                    if ordering == 'start' or ordering == 'end':
                        ordering += '_position'
                    if inverted:
                        ordering = "-"+ordering
                    search_gene.sort(ordering)

            n_genes = search_gene.count()
            if studies:
                pagest = self.paginate_queryset(studies)
                study_serializer = StudySerializer(pagest, many=True)
            else:
                study_serializer = StudySerializer(studies, many=True)

            if n_genes:
                size = min(200, search_gene.count())
                if is_gene_suggest:
                    size = 0
                results = search_gene[0:size].execute()
                if is_gene_suggest:
                    genes = results.to_dict()['suggest']['gene_suggest'][0]['options']
                else:
                    genes = results.to_dict()['hits']['hits']
                genes_out = []
                for gene in genes:
                    genes_out.append(gene["_source"])
                pagege = self.paginate_queryset(genes_out)
            else:
                genes = []
                pagege = []

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
                             'gene_search_results':pagege,
                             'counts': counts,
                             'page_counts': page_counts}

            if any([studies,genes,phenotypes]):
                return self.get_paginated_response(data)
            else:
                return Response({'results': {i:data[i] for i in data if i!='counts'}, 'count':counts, 'page_count':[0,0,0]})
