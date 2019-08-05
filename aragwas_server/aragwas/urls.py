"""aragwas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter, DynamicListRoute, DynamicDetailRoute, Route
from rest_framework.urlpatterns import format_suffix_patterns

from gwasdb import views

import gwasdb.rest as rest

class SearchRouter(DefaultRouter):
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'list'},
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            initkwargs={'suffix': 'Detail'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{methodname}/(?P<query_term>[^/.]+)/$',
            name='{basename}-{methodname}',
            initkwargs={}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}/$',
            name='{basename}-{methodname}',
            initkwargs={}
        )
    ]

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'genotypes', rest.GenotypeViewSet)
router.register(r'studies', rest.StudyViewSet)
router.register(r'phenotypes', rest.PhenotypeViewSet)
router.register(r'associations', rest.AssociationViewSet, base_name="associations")
router.register(r'koassociations', rest.KOAssociationViewSet, base_name="koassociations")
router.register(r'genes', rest.GeneViewSet, base_name="genes")
router.register(r'snps', rest.SNPViewSet, base_name="snps")

srouter = SearchRouter()
srouter.register(r'search', rest.SearchViewSet)

from gwasdb.custom_documentation import include_custom_docs_urls


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    # url(r'^docs/', include_docs_urls(title="AraGWAS API", description="REST API for AraGWAS")),
    url(r'^docs/', include_custom_docs_urls(title="AraGWAS API", description="REST API for AraGWAS")),
    url(r'^api/', include(router.urls, namespace="router_apis")),
    url(r'^api/', include(srouter.urls)),
    url(r'^api/version/$',rest.ApiVersionView.as_view(),name='api-version')
]

# for custom REST API endpoints (search, etc)
restpatterns = [
    #search
    # url(r'^api/search/search_results/$', ),
]

restpatterns = format_suffix_patterns(restpatterns, allowed=['json','zip','png','pdf'])
urlpatterns += restpatterns



