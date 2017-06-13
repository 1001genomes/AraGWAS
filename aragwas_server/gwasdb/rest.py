import os

from rest_framework import permissions
from rest_framework import viewsets, generics, filters
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from gwasdb.models import Phenotype, SNP, Association, Study, Gene, Genotype
from gwasdb.serializers import *
from gwasdb.paginator import CustomSearchPagination, CustomAssociationsPagination

from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from gwasdb.hdf5 import getTopAssociations, regroupAssociations

from gwasdb.tasks import compute_ld
from gwasdb import __version__, __date__, __githash__,__build__, __buildurl__
from aragwas import settings
from gwasdb import elastic


from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Range
from elasticsearch_dsl.query import Q as QES
from elasticsearch import Elasticsearch
from aragwas.settings import ES_HOST

import numpy, math

def get_api_version():
    BUILD_STATUS_URL = None
    if __buildurl__ != 'N/A':
        BUILD_STATUS_URL = __buildurl__
    return {'version':__version__,'date':__date__,'githash':__githash__,'build':__build__,'build_url':BUILD_STATUS_URL,'github_url':settings.GITHUB_URL}


class ApiVersionView(APIView):
    """Displays git and version information"""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request):
        serializer = ApiVersionSerializer(get_api_version(), many=False)
        return Response(serializer.data)

###############
# ELASTIC SEARCH REST FUNCTIONS
##############
class TopAssociationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve information about the best associations for the top associations list
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    # Fetch top associations in es with appropriate filters.
    def list(self, request, *args, **kwargs):
        # retrieve and sort filters.
        filters = {}
        filters['chr']= self.request.query_params.get('chr', None).split(',')
        filters['maf'] = self.request.query_params.get('maf', None).split(',')
        filters['annotation'] = self.request.query_params.get('anno', None).split(',')
        filters['type'] = self.request.query_params.get('type', None).split(',')
        # Get study ids
        try:
            asso = elastic.load_filtered_top_associations(filters)
            # TODO: aggregate results for neighboring snps with shared study
            paginated_asso = self.paginate_queryset(asso)
            return self.get_paginated_response(paginated_asso)
        except Association.DoesNotExist:
            raise Http404('Associations do not exist')
    pass

class AssociationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer

    @list_route(url_path='association_count')
    def association_count(self, request):
        client = Elasticsearch([ES_HOST], timeout=60)
        count = Search().using(client).doc_type('associations').query('match_all').count()
        return Response(count)


class AssociationsOfStudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations
    """
    queryset = Association.objects.all()
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            page = int(request.query_params.get('page', None))
        except:
            page = 1
        association_file = os.path.join(settings.HDF5_FILE_PATH,'%s.hdf5' % pk)
        pval, pos, mafs, n_asso, thresholds = getTopAssociations(association_file, 1e-4, 'threshold')
        # pval, pos, mafs, n_asso, thresholds = getTopAssociations(association_file, 100, 'top')
        pval, chr, pos, mafs = regroupAssociations(pval,pos,mafs)
        # associations = get_list_or_404(Association, study=pk)

        results = []
        for l in range(len(pval)):
            # get associated genes:
            name = ''
            pk = ''
            type = ''
            try:
                obj = SNP.objects.get(Q(chromosome=chr[l]) & Q(position=pos[l]))
                gene = Gene.objects.get(pk=obj.gene)
                name = gene.name
                pk = gene.pk
            except:
                pass
            results.append({'pvalue': "{:.5f}".format(pval[l]),'SNP': 'Chr'+str(chr[l])+':'+str(pos[l]), 'maf': "{:.3f}".format(mafs[l]), 'gene':{'name': name, 'pk': pk}, 'type': type})

        # Homemade paginator
        PAGE_SIZE = 20.
        page_count = int(math.ceil(float(len(pval)) / PAGE_SIZE))
        if page > page_count:
            page = page_count
        data = {'count': len(pval), 'page_count': int(math.ceil(float(len(pval)) / PAGE_SIZE)), 'current_page': page, 'thresholds': thresholds, 'results': results[int(PAGE_SIZE)*(page-1):int(PAGE_SIZE)*page]}

        return Response(data, status=status.HTTP_200_OK)

class AssociationsForManhattanPlotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Fetch associations in hdf5 file for manhattan plots
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        association_file = os.path.join(settings.HDF5_FILE_PATH,'%s.hdf5' % pk)
        pval, pos, mafs, n_asso, thresholds = getTopAssociations(association_file, 2500, 'top')
        output = {}
        for i in range(5):
            output['chr'+str(i+1)] = {'pvalues': pval[i], 'positions': pos[i], 'mafs': mafs[i]}
        output['bonferoni_threshold'] = -math.log(0.05/float(n_asso), 10)

        return Response(output, status=status.HTTP_200_OK)

class AssociationsOfPhenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations of a specific phenotype
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            page = int(request.query_params.get('page', None))
        except:
            page = 1
        # get studies ids
        studies = Study.objects.filter(phenotype=pk)
        st_id = []
        for s in studies:
            st_id.append(s.pk)

        pval = []
        chr = []
        pos = []
        study = []
        n_asso = 0
        for study_pk in st_id:
            association_file = os.path.join(settings.HDF5_FILE_PATH,'%s.hdf5' % pk)
            pval_st, pos_st, mafs_st, n_asso_st, thresholds = getTopAssociations(association_file, 1e-4, 'threshold')
            pval_st, chr_st, pos_st, mafs_st = regroupAssociations(pval_st, pos_st, mafs_st)
            pval.extend(pval_st)
            chr.extend(chr_st)
            pos.extend(pos_st)
            study.extend(study_pk for l in range(len(pval_st)))
            n_asso += n_asso_st
        pval = numpy.asarray(pval)
        pos = numpy.asarray(pos)
        chr = numpy.asarray(chr)
        study = numpy.asarray(study)

        i = pval.argsort()[::-1]
        results = []
        for l in i:
            # get associated genes:
            name = ''
            pk = ''
            try:
                obj = SNP.objects.get(Q(chromosome__exact=chr[l]) & Q(position__exact=pos[l]))
                gene = Gene.objects.get(pk=obj.gene)
                name = gene.name
                pk = gene.pk
            except:
                pass
            study_name = studies.get(pk=study[l]).name
            results.append({'pvalue': "{:.5f}".format(pval[l]),'SNP': 'Chr'+str(chr[l])+':'+str(pos[l]), 'gene':{'name': name, 'pk': pk}, 'study':{'name': study_name, 'pk': study[l]}})
        # Homemade paginator
        PAGE_SIZE = 20.
        page_count = int(math.ceil(float(len(i)) / PAGE_SIZE))
        if page > page_count:
            page = page_count
        data = {'count': len(i), 'page_count': int(math.ceil(float(len(i)) / PAGE_SIZE)), 'current_page': page, 'total_associations': n_asso,
                'results': results[int(PAGE_SIZE) * (page - 1):int(PAGE_SIZE) * page]}
        return Response(data, status=status.HTTP_200_OK)

class AssociationsOfGeneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS associations of a specific phenotype
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        # Get study ids
        try:
            asso = elastic.load_gene_associations(id)
            paginated_asso = self.paginate_queryset(asso)
            return self.get_paginated_response(paginated_asso)
        except Association.DoesNotExist:
            raise Http404('Associations do not exist')
"""
Mockup class to test es nested queries
class SnpsOfGeneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SNP.objects.all()
    serializer_class = AssociationSerializer
    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        # Get study ids
        try:
            asso = elastic.load_gene_snps(id)
            paginated_asso = self.paginate_queryset(asso)
            return self.get_paginated_response(paginated_asso)
        except Association.DoesNotExist:
            raise Http404('Associations do not exist')
"""

class StudyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about GWAS study
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
            queryset = queryset.order_by(Lower(ordering))
            if inverted:
                queryset = queryset.reverse()
        return queryset

class PhenotypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about phenotypes
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

class SimilarPhenotypesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information about similar phenotypes
    """
    queryset = Phenotype.objects.all()
    serializer_class = PhenotypeListSerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            ori_pheno = Phenotype.objects.get(pk=pk)
        except:
            raise ValueError('Phenotype with pk {} not found'.format(pk))
        trait_ontology = ori_pheno.name # TODO: change this once trait ontology has been added
        queryset = Phenotype.objects.filter(name__exact=trait_ontology)
        queryset = queryset.filter(~Q(pk=pk))
        pagephe = self.paginate_queryset(queryset)
        serializer = PhenotypeListSerializer(pagephe, many=True)
        return Response(serializer.data)

class GeneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves information genes
    """
    queryset = Gene.objects.all()
    serializer_class = GeneListSerializer

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
            queryset = queryset.order_by(Lower(ordering))
            if inverted:
                queryset = queryset.reverse()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        # To get the neighboring hits/SNPs and count them, we would need to query ES for SNPs in that region...
        gene = elastic.load_gene_by_id(id)
        gene['snps'] = elastic.load_snps_by_region(gene['chr'], gene['positions']['gte'],gene['positions']['lte'])
        return Response(gene)
        # snps = elastic.load_gene_snps(id)
        # snps = list(filter(None, snps))
        # return Response({'gene': gene, 'snps':snps, 'snp_count': len(snps)})

class TopGeneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Compute most associated genes and return top 8 genes for landing page plot
    """
    queryset = Gene.objects.all()
    serializer_class = GeneListSerializer

    # Overriding get_queryset to allow for case-insensitive custom ordering
    def get_queryset(self):
        return(elastic.get_top_genes())

    def retrieve(self, request, *args, **kwargs):
        id = kwargs['pk']
        # To get the neighboring hits/SNPs and count them, we would need to query ES for SNPs in that region...
        gene = elastic.load_gene_by_id(id)
        snps = elastic.load_gene_snps(id)
        snps = list(filter(None, snps))
        return Response({'gene': gene, 'snps':snps, 'snp_count': len(snps)})

class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allow for search in a viewset
    """
    queryset = Study.objects.all()
    query_term = None
    serializer_class = StudySerializer
    pagination_class = CustomSearchPagination


    @list_route(url_path='search_results')
    def search_result(self, request):
        return self.search_results(request, query_term=None)

    @detail_route()
    def search_results(self, request, query_term):
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
                    genes = Gene.objects.filter(Q(start_position__lte=query_term) & Q(end_position__gte=query_term)).order_by('name')
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
                            q = QES('range', positions={'gte':s_p, 'lte':s_p})
                        search_gene = search_gene.query(q)
                else: # other type of request
                    q = QES('match', _all=query_term)
                    search_gene = search_gene.query(q)
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
            print(n_genes)
            if studies:
                pagest = self.paginate_queryset(studies)
                study_serializer = StudySerializer(pagest, many=True)
            else:
                study_serializer = StudySerializer(studies, many=True)

            if n_genes:
                results = search_gene[0:min(200, search_gene.count())].execute()
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



class SNPLocalViewSet(viewsets.ViewSet):
    """
    Retrieve information about a SNP
    """
    queryset = SNP.objects.none()

    @detail_route()
    def neighboring_snps(self, request, pk):
        """
        Returns list of the neighboring SNPs, no information about LD (this will be retrieved or computed later)
        """
        window_size=request.GET.get('window_size', 1000000)
        include = 'include' in request.GET
        chromosome = SNP.objects.get(pk=pk).chromosome
        position = SNP.objects.get(pk=pk).position
        window_of_interest = [min(int(position) - window_size / 2, 0), int(
            position) + window_size / 2]  # no need to get chromosome size (since we'll run > or < queries)
        # Here we need to decide whether we include the original SNP or not.
        neighboring_s = SNP.objects.filter(chromosome=chromosome).filter(
            position__range=(window_of_interest[0], window_of_interest[1]))
        if not include:
            # Exclude original SNP
            neighboring_s = neighboring_s.filter(~Q(pk=pk))

        serializer = SNPListSerializer(neighboring_s, many=True)
        return Response(serializer.data)

    @detail_route()
    def snps_in_ld(request, pk):
        """
        Returns list of the neighboring SNPs in high LD
        """
        N = request.GET.get('N',20)
        snp = SNP.objects.get(pk=pk)
        # Get genotype
        genotype_name = snp.genotype

        # Call the celery task
        ordered_positions, ordered_ld = compute_ld(snp.chromosome, snp.position, genotype_name)

        # return highest N SNPs
        snps = SNP.objects.filter(chromosome__equals=snp.chromosome).filter(position__in=ordered_positions)

        # Serialize
        serializer = SNPListSerializer(snps)
        # Attach correlation information
        return Response({'top_ld_snps': serializer.data,
                         'ld_values': ordered_ld,
                         'top_snps_positions': ordered_positions})

@api_view()
@permission_classes((IsAuthenticatedOrReadOnly,))
def autocomplete_genes(request, search_term):
    genes = elastic.autocomplete_genes(search_term)
    return Response(genes)