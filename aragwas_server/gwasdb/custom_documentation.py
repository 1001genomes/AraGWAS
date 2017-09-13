from django.conf.urls import include, url
import coreapi, coreschema

from collections import OrderedDict

from rest_framework.renderers import (
    CoreJSONRenderer, DocumentationRenderer, SchemaJSRenderer
)
from rest_framework.schemas import SchemaView
from rest_framework.response import Response
from rest_framework import exceptions

def get_docs_view(title=None, description=None, schema_url=None, public=True):
    renderer_classes = [DocumentationRenderer, CoreJSONRenderer]

    return get_custom_schema_view(
        title=title,
        url=schema_url,
        description=description,
        renderer_classes=renderer_classes,
        public=public
    )


def get_schemajs_view(title=None, description=None, schema_url=None, public=True):
    renderer_classes = [SchemaJSRenderer]

    return get_custom_schema_view(
        title=title,
        url=schema_url,
        description=description,
        renderer_classes=renderer_classes,
        public=public
    )


def include_custom_docs_urls(title=None, description=None, schema_url=None, public=True):
    docs_view = get_docs_view(
        title=title,
        description=description,
        schema_url=schema_url,
        public=public
    )
    schema_js_view = get_schemajs_view(
        title=title,
        description=description,
        schema_url=schema_url,
        public=public
    )
    urls = [
        url(r'^$', docs_view, name='docs-index'),
        url(r'^schema.js$', schema_js_view, name='schema-js')
    ]
    return include(urls, namespace='api-docs')

class CustomSchemaView(SchemaView):
    title = None
    url = None
    description = None

    # Override the getter
    def get(self, request, *args, **kwargs):
        url = self.url
        if not url and request is not None:
            url = request.build_absolute_uri()
        schema = get_custom_schema(title=self.title, url=url, description=self.description, public=self.public)
        if schema is None:
            raise exceptions.PermissionDenied()
        return Response(schema)



def get_custom_schema_view(title=None, url=None, description=None, urlconf=None, renderer_classes=None, public=False):

    return CustomSchemaView.as_view(
        title=title,url=url,description=description,
        renderer_classes=renderer_classes,
        public=public,
    )

def get_custom_schema(title=None, url=None, description=None, urlconf=None, renderer_classes=None, public=False):
    links = get_custom_links()
    if not links:
        return None

    schema = coreapi.Document(
        title=title,
        url=url,
        description=description,
        content=links,
    )
    return schema

def get_custom_links():
    """
            Return a dictionary containing all the links that should be
            included in the API schema.
            """
    links = OrderedDict()
    # Somehow query filters dont work correctly in the documentation window, probably better to leave them out
    filterfields = [coreapi.Field(name="chr",schema=coreschema.Integer(title="Chromosome",description="The chromosome of interest. Multiple choices can be chained when accessing programmatically."),location="query"),
                    coreapi.Field(name="maf",schema=coreschema.String(title="MAF",description="The MAF filter, options are 1 (for <1%), 1-5 (for 1-5%), 5-10 (for 5-10%) and 10 (for >10%). Multiple choices can be chained when accessing programmatically."),location="query"),
                    coreapi.Field(name="mac",schema=coreschema.String(title="MAC",description="The MAC filter, options are 0 (for MAC≤5) and 5 (for MAC>5), default is 5. Multiple choices can be chained when accessing programmatically."),location="query"),
                    coreapi.Field(name="annotation",schema=coreschema.String(title="Annotation",description="The SNP annotation filter, options are ns (for non-synonymous coding), s (for synonymous coding), in (for introns) and i (for intergenic). Multiple choices can be chained when accessing programmatically."),location="query"),
                    coreapi.Field(name="type",schema=coreschema.String(title="Type",description="The SNP type filter, options are genic and non-genic."),location="query"),
                    coreapi.Field(name="significant",schema=coreschema.String(title="Significant",description="The significance filter, options are 0 for no filtering, p for permutation-threshold filtering and b for Bonferroni-threshold filtering. Default is p."),location="query"),
                    ]
    associations = {
        "list": coreapi.Link(url="/api/associations/",
                action="get",
                description="List all associations meeting the filtering criteria sorted by score.",
                fields=filterfields),
        "aggregated_statistics": coreapi.Link(url="/api/associations/aggregated_statistics/",
                             action="get",
                             description="Retrieve the aggregation percentage for associations meeting filters criteria.",
                             fields=filterfields),
        "count": coreapi.Link(url="/api/associations/count/",
                             action="get",
                             description="Retrieve the number of significant associations in the database.",),
    }
    genes = {
        "list": coreapi.Link(url="/api/genes/",
                action="get",
                description="List all genes in the database. Can add 'chrom', 'start' and 'end' as params in the url request.",
                fields=[coreapi.Field(name="chr",location="query",schema=coreschema.Integer(title="Chromosome",description="The chromosome of interest of the search region")),
                        coreapi.Field(name="start", location="query", schema=coreschema.Integer(title="Start position",
                                                                                                description="The begininning of the search region")),
                        coreapi.Field(name="end", location="query", schema=coreschema.Integer(title="End position",
                                                                                                description="The end of the search region"))]),
        "read": coreapi.Link(url="/api/genes/{id}/",
                             action="get",
                             description="Retrieve information about a specific gene.",
                             fields=[coreapi.Field(name="id",required=True,location="path",schema=coreschema.String(title="Gene ID",description="The name of the gene"))]),
        "top_list": coreapi.Link(url="/api/genes/top_list/",
                             action="get",
                             description="Retrieve the top genes based on the number of significant associations and provide full gene information.",fields=[]),
        "associations": coreapi.Link(url="/api/genes/{id}/associations/",
                             action="get",
                             description="Return associations meeting the filtering criteria for the selected gene.",
                             fields=filterfields[1:] + [coreapi.Field(name="id",required=True,location="path",schema=coreschema.String(title="Gene ID",description="The name of the gene for which associations should be loaded."))]),
        "aggregated_statistics": coreapi.Link(url="/api/genes/{id}/aggregated_statistics/",
                             action="get",
                             description="Retrieve the aggregation percentage for associations meeting the filtering criteria for this gene.",
                             fields=filterfields[1:] + [coreapi.Field(name="id",required=True,location="path",schema=coreschema.String(title="Gene ID",description="The name of the gene for which statistics should be computed."))]),
    }
    genotypes = {
        "list": coreapi.Link(url="/api/genotypes/",
                             action="get",
                             description="List available genotypes.",
                             fields=[]),
        "read": coreapi.Link(url="/api/genotypes/{id}/",
                             action="get",
                             description="Retrieve information about a specific genotype.",
                             fields=[coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Genotype ID",description="A unique integer value identifying this genotype."))]),
    }
    phenotypes = {
        "list": coreapi.Link(url="/api/phenotypes/",
                             action="get",
                             description="List available phenotypes.",
                             fields=[coreapi.Field(name="page", location="query", schema=coreschema.Integer(title="Page number",description="A page number within the paginated result set."))]),
        "read": coreapi.Link(url="/api/genotypes/{id}/",
                             action="get",
                             description="Retrieve information about a specific genotype.",
                             fields=[coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Phenotype ID",description="A unique integer value identifying this phenotype."))]),
        "studies": coreapi.Link(url="/api/genotypes/{id}/studies",
                             action="get",
                             description="Get a list of studies for a specific phenotype.",
                             fields=[coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Phenotype ID",description="A unique integer value identifying this phenotype."))]),
    }
    search = {
        "search_results": coreapi.Link(url="/api/search/search_results/{query_term}/",
                             action="get",
                             description="Display results based on search term.",
                             fields=[coreapi.Field(name="query_term", required=True, location="path",schema=coreschema.String(title="Query term",description="Search term"))]),
    }
    studies = {
        "list": coreapi.Link(url="/api/studies/",
                             action="get",
                             description="List all available GWA studies.",
                             fields=[coreapi.Field(name="page", location="query",
                                                   schema=coreschema.Integer(title="Page",description="A page number within the paginated result set."))]),
        "read": coreapi.Link(url="/api/studies/{id}/",
                             action="get",
                             description="Retrieve information about a specific GWA study.",
                             fields=[coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Study ID",description="A unique integer value identifying this study."))]),
        "aggregated_statistics": coreapi.Link(url="/api/studies/{id}/aggregated_statistics/",
                                action="get",
                                description="Retrieve the aggregation statistics of the top assocations  meeting the filtering criteria for a study and a specific set of filters.",
                                fields=filterfields + [coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Study ID",description="A unique integer value identifying this study."))]),
        "top_associations": coreapi.Link(url="/api/studies/{id}/associations/",
                                action="get",
                                description="Retrieve top associations meeting the filtering criteria for the selected study.",
                                fields=filterfields + [coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Study ID",description="A unique integer value identifying this study."))]),
        "top_genes_and_snp_type": coreapi.Link(url="/api/studies/{id}/top/",
                                action="get",
                                description="Get genes and SNP type that got the most significant associations for a specific study. The returned fields will be empty if there are no significant associations for the selected study.",
                                fields=[coreapi.Field(name="id", required=True, location="path",schema=coreschema.Integer(title="Study ID",description="A unique integer value identifying this study."))]),
    }

    links['associations'] = associations
    links['genes'] = genes
    links['genotypes'] = genotypes
    links['phenotypes'] = phenotypes
    links['search'] = search
    links['studies'] = studies
    return links

