import os

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
from gwasdb.hdf5 import get_top_associations, regroup_associations

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
    annos = params.getlist('annotation')
    filter_annot = [annos_dict[k] for k in annos]
    filter_type = params.getlist('type')
    filter_study = params.getlist('study_id')
    filter_phenotype = params.getlist('phenotype_id')
    filter_genotype = params.getlist('genotype_id')
    filter_significant = params.getlist('significant')
    filters = {'chr':filter_chr, 'maf': filter_maf, 'annotation': filter_annot, 'type': filter_type, 'study_id':filter_study, 'phenotype_id': filter_phenotype, 'genotype_id': filter_genotype, 'significant': filter_significant}
    return filters

def _get_percentages_from_buckets(buckets):
    out_dict = {}
    annos_dict = {'NON_SYNONYMOUS_CODING': 'ns', 'SYNONYMOUS_CODING': 's', 'INTERGENIC': 'i', 'INTRON': 'in'}
    tot_sum = sum(i['doc_count'] for i in buckets)
    for i in buckets:
        out_dict[annos_dict[i['key']] if i['key'] in annos_dict else str(i['key'])] = float(
            i['doc_count']) / tot_sum
    return out_dict


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
    Lists avaialble genotypes

    retrieve:
    Retreives information about one specific genotype
    """
    queryset = Genotype.objects.all()
    serializer_class = GenotypeSerializer


class StudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API for studies

    list:
    Lists all available GWAS studies

    retrieve:
    Retrieves information about a specific GWAS study
    """
    queryset = Study.objects.all()
    serializer_class = StudySerializer

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
            else:
                ordering = Lower(ordering)
            queryset = queryset.order_by(ordering)
            if inverted:
                queryset = queryset.reverse()
        return queryset

    @detail_route(methods=['GET'], url_path='download')
    def download(self, request, pk):
        study_file = "%s/%s.hdf5" % (settings.HDF5_FILE_PATH, pk)
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(study_file,"rb"), chunk_size),content_type="application/x-hdf5")
        response['Content-Length'] = os.path.getsize(study_file)
        response['Content-Disposition'] = "attachment; filename=%s.hdf5" % pk
        return response


    @detail_route(methods=['GET'], url_path='associations')
    def top_assocations(self, request, pk):
        """ Retrieves the top assocations for the study """
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
        """ Retrieves the top assocations for a study """
        filters = _get_filter_from_params(request.query_params)
        filters['study_id'] = [pk]
        chr, maf, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'types': type_dict, 'annotations': annotations_dict})

    @detail_route(methods=['GET'], url_path='gwas')
    def assocations_from_hdf5(self, request, pk):
        """ Retrieves assocations from the HDF5 file"""
        filter_type = request.query_params.get('filter_type', 'threshold')
        if filter_type not in ('threshold', 'top'):
            raise ValueError('filter_type must be either "threshold" or "top"')
        threshold_or_top = float(request.query_params.get('filter', 1))
        if filter_type == 'top':
            threshold_or_top = int(threshold_or_top)

        association_file = os.path.join(settings.HDF5_FILE_PATH, '%s.hdf5' % pk)
        top_associations, thresholds = get_top_associations(association_file, val=threshold_or_top, top_or_threshold=filter_type)
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

    @detail_route(methods=['GET'], url_path='top')
    def top_genes_and_snp_type(self, request, pk):
        """ Gets genes and snp type that got the most significant associations """
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
                # Need to check if all consequent maf ranges are present
                list_maf = []
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
    Lists available phenotypes

    retrieve:
    Retrieves information about a specific phenotype
    """
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeListSerializer

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
        """ Gets studies of phenotype """
        studies = Study.objects.filter(phenotype__id = pk)
        serializer = StudySerializer(studies, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET'], url_path='associations')
    def top_assocations(self, request, pk):
        """ Retrieves the top assocations for a phenotype """
        filters = _get_filter_from_params(request.query_params)
        filters['phenotype_id'] = [pk]
        paginator = EsPagination()
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        associations, count = elastic.load_filtered_top_associations(filters,offset,limit)
        queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_asso)

    @detail_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request, pk):
        """ Retrieves the top assocations for a phenotype """
        filters = _get_filter_from_params(request.query_params)
        filters['phenotype_id'] = [pk]
        chr, maf, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'types': type_dict, 'annotations': annotations_dict})

class AssociationViewSet(EsViewSetMixin, viewsets.ViewSet):
    """ API for associations """

    def list(self, request):
        """ Lists all associations sorted by score """
        filters = _get_filter_from_params(request.query_params)
        last_el = request.query_params.get('lastel', '')
        associations, count, lastel = elastic.load_filtered_top_associations_search_after(filters,last_el)
        print(lastel)
        queryset = EsQuerySetLastEl(associations, count, lastel)
        # associations, count = elastic.load_filtered_top_associations(filters,offset,limit)
        # queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response({'results': paginated_asso, 'count': count, 'lastel': [lastel[0], lastel[1]]})

    @list_route(url_path='count')
    def count(self, request):
        """  Retrieves the number of available associations """
        client = Elasticsearch([ES_HOST], timeout=60)
        count = Search().using(client).doc_type('associations').query('match_all').count()
        return Response(count)

    @list_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request):
        """ Retrieves the percentage for association meeting filters """
        filters = _get_filter_from_params(request.query_params)
        chr, maf, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'types': type_dict, 'annotations': annotations_dict})

    @list_route(methods=['GET'], url_path='map_histogram')
    def data_for_histogram(self, request):
        """ Get heatmap histogram data. Parameters need to be included in the filters dict
            Usage: chrom = indicate the chromosome(s) of interest ('all' or any chromosome),
                region_width = indicate the size of the bins for which to count hits should be passed under the form,
                threshold = indicate the type of threshold to look at (FDR, Bonferroni, permutation or none, default='FDR')
                region = indicate a specific window in which to aggregate for, default = ('','') looks at entire chromosome
                maf = indicate a minimum maf (default=0)
                mac = indicate a minimum mac (default=0)
        """
        # Get bin size
        filters = dict()
        filters['region_width'] = int(request.query_params.getlist('region_width')[0])
        # get the rest of the data
        results = elastic.get_gwas_overview_bins_data(filters)
        return Response(results)

    @list_route(methods=['GET'], url_path='map_heat')
    def data_for_heatmap(self, request):
        """ Get heatmap data. Parameters need to be included in the filters dict
            Usage: chrom = indicate the chromosome(s) of interest ('all' or any chromosome),
                region_width = indicate the size of the bins for which to count hits,
                threshold = indicate the type of threshold to look at (FDR, Bonferroni, permutation or none, default='FDR')
                region = indicate a specific window in which to aggregate for, default = ('','') looks at entire chromosome
                maf = indicate a minimum maf (default=0)
                mac = indicate a minimum mac (default=0)
        """
        # Load studies from regular db
        studies = Study.objects.all()
        studies_data = []
        for study in studies:
            studies_data.append(
                {'id': study.id, 'name': study.phenotype.name})  # For now only add phenotype name for shorted strings
        # get the rest of the data
        filters = dict()  # TODO: add parameters fetching from url, for now default values should be fine
        results = elastic.get_gwas_overview_heatmap_data(filters)
        results['studies'] = studies_data
        return Response(results)

    @list_route(methods=['GET'], url_path='download')
    def download_csv(self, request):
        """ Prepare a csv file from the elasticsearch database and return it as a downloadable file through a celery task
            Usage: takes same filters as any other associations query
        """
        # Load studies from regular db
        import datetime
        filters = _get_filter_from_params(request.query_params)
        file_name = 'temp/'+str(datetime.datetime.time())+'.csv' # give it a unique name
        opts = dict(doc_type='associations', output_name=file_name)
        opts['output_file'] = opts['doc_type'] + "_all.csv"
        fn = download_es2csv(opts, filters)
        # wait for file to be done
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(file_name, "rb"), chunk_size),
                        content_type="text/csv")
        response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = "attachment; filename=download.csv"

        return response


class GeneViewSet(EsViewSetMixin, viewsets.ViewSet):
    """ API for genes """

    def list(self, request):
        chrom = request.query_params['chr']
        start = request.query_params['start']
        end = request.query_params['end']
        is_features = 'features' in request.query_params
        genes = elastic.load_genes_by_region(chrom,start,end,is_features)
        return Response(genes)

    def retrieve(self, request, pk):
        """ Retrieves information about a specific gene """
        gene = elastic.load_gene_by_id(pk)
        return Response(gene)

    @list_route(methods=['GET'], url_path='autocomplete')
    def autocomplete(self, request):
        """ Autocompletes based on query term """
        search_term = request.query_params.get('term', '')
        genes = elastic.autocomplete_genes(search_term)
        return Response(genes)

    @detail_route(methods=['GET'], url_path='snps')
    def snps(self, request, pk):
        """ Returns associations for that gene """
        gene = elastic.load_gene_by_id(pk)
        gene['snps'] = elastic.load_snps_by_region(gene['chr'], gene['positions']['gte'],gene['positions']['lte'])
        return Response(gene)

    @detail_route(methods=['GET'], url_path='associations')
    def associations(self, request, pk):
        """ Returns snps for that gene """
        gene = elastic.load_gene_by_id(pk)
        zoom = int(request.query_params.get('zoom', 0))
        # last_el = [request.query_params.get('lastel', '')]
        filters = _get_filter_from_params(request.query_params)
        filters['chr'] = [gene['chr']]
        filters['start'] = gene['positions']['gte'] - zoom
        filters['end'] = gene['positions']['lte'] + zoom
        limit = self.paginator.get_limit(request)
        offset = self.paginator.get_offset(request)
        associations, count = elastic.load_filtered_top_associations(filters, offset, limit)
        queryset = EsQuerySet(associations, count)
        paginated_asso = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_asso)

    @detail_route(methods=['GET'], url_path='aggregated_statistics')
    def aggregated_statistics(self, request, pk):
        """ Returns snps for that gene """
        gene = elastic.load_gene_by_id(pk)
        zoom = int(request.query_params.get('zoom', 0))
        # last_el = [request.query_params.get('lastel', '')]
        filters = _get_filter_from_params(request.query_params)
        filters['chr'] = [gene['chr']]
        filters['start'] = gene['positions']['gte'] - zoom
        filters['end'] = gene['positions']['lte'] + zoom
        chr, maf, type, annotations = elastic.get_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'types': type_dict, 'annotations': annotations_dict})


    @list_route(methods=['GET'], url_path='top')
    def top(self, requests):
        """ Retrieves the top genes based on the assocations """
        agg = elastic.get_top_genes()
        list_top_genes = []
        for i in agg:
            list_top_genes.append([i['key'], i['doc_count']])
        return Response(list_top_genes)

    @list_route(methods=['GET'], url_path='top_list')
    def top_list(self, request):
        """ Retrieves the top genes based on the associations and provide full gene information """
        filters = _get_filter_from_params(request.query_params)
        paginator = EsPagination()
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)
        genes, count = elastic.load_filtered_top_genes(filters, offset, limit)
        queryset = EsQuerySet(genes, count)
        paginated_genes = self.paginate_queryset(queryset)
        return self.get_paginated_response(paginated_genes)

    @list_route(methods=['GET'], url_path='top_list_aggregated_statistics')
    def top_genes_aggregated_statistics(self, request):
        """ Returns snps for that gene """
        filters = _get_filter_from_params(request.query_params)
        chr = elastic.get_top_genes_aggregated_filtered_statistics(filters)
        chr_dict = _get_percentages_from_buckets(chr)
        return Response({'chromosomes': chr_dict})

class SNPViewSet(viewsets.ViewSet):
    """ API for SNPs """

    def list(self, request):
        """ Retrieves a list of SNPs """
        pass

    def retrieve(self, request, pk):
        """ Retrieves information about a SNP """
        pass

    @detail_route(methods=['GET'], url_path='neighboring')
    def neighboring_snps(self, request, pk):
        """
        Returns list of the neighboring SNPs, no information about LD (this will be retrieved or computed later)
        """
        window_size=request.GET.get('window_size', 1000000)
        include = 'include' in request.GET
        # TODO implement
        return Response({})

    @detail_route(methods=['GET'], url_path='ld')
    def snps_in_ld(request, pk):
        """
        Returns list of the neighboring SNPs in high LD
        """
        N = request.GET.get('N',20)
        # TODO implement
        ordered_positions, ordered_ld = compute_ld(snp.chromosome, snp.position, genotype_name)

        # return highest N SNPs
        snps = SNP.objects.filter(chromosome__equals=snp.chromosome).filter(position__in=ordered_positions)

        # Serialize
        serializer = SNPListSerializer(snps)
        # Attach correlation information
        return Response({'top_ld_snps': serializer.data,
                         'ld_values': ordered_ld,
                         'top_snps_positions': ordered_positions})

    @list_route(methods=['GET'], url_path='aggregated')
    def aggregated_statistics(self, requests):
        """ Retrieves the top genes based on the assocations """
        chr, maf, type, annotations = elastic.get_aggregated_filtered_statistics({1:1})
        chr_dict = _get_percentages_from_buckets(chr)
        maf_dict = _get_percentages_from_buckets(maf)
        type_dict = _get_percentages_from_buckets(type)
        annotations_dict = _get_percentages_from_buckets(annotations)
        return Response({'chromosomes': chr_dict, 'maf': maf_dict, 'types': type_dict, 'annotations': annotations_dict})


class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """ API for search """

    queryset = Study.objects.all()
    query_term = None
    serializer_class = StudySerializer
    pagination_class = CustomSearchPagination


    @list_route(url_path='search_results')
    def search_result(self, request):
        """ Displays results without search term """
        return self.search_results(request, query_term=None)

    @detail_route()
    def search_results(self, request, query_term):
        """ Displays results based on search term """
        is_gene_suggest = False
        if request.method == "GET":
            client = Elasticsearch([ES_HOST], timeout=60)
            search_gene = Search().using(client).doc_type('genes').source(exclude=['isoforms','GO'])#'isoforms.cds','GO'])
            if query_term==None:
                studies = Study.objects.all()
                phenotypes = Phenotype.objects.all()
                # Elasticsearch query cannot be made before knowing the ordering and the page number, etc as this is taken into account by elasticsearch.py
            else:
                studies = Study.objects.filter(Q(name__icontains=query_term) |
                                                      Q(phenotype__name__icontains=query_term)).order_by('name')
                phenotypes = Phenotype.objects.filter(name__icontains=query_term).order_by('name')
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
            ordering_fields = {'studies': ['name','genotype','phenotype','method','transformation'], 'phenotypes': ['name', 'description'], 'genes': ['name', 'chr', 'start_position', 'end_position', 'SNPs_count', 'association_count', 'description']}
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
                if ordering in ordering_fields['genes'] and genes:
                    # if ordering == 'snp' or ordering == 'study':
                    #     ordering += '__name'
                    # genes = genes.order_by(Lower(ordering))
                    search_gene.sort(ordering)
                    if inverted:
                        genes = genes.reverse()
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
