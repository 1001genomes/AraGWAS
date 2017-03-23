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
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from gwasdb import views

import gwasdb.rest as rest

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'associations', rest.AssociationViewSet)
router.register(r'studies', rest.StudyViewSet)
router.register(r'search', rest.SearchViewSet)
router.register(r'neighboring_snps', rest.SNPLocalViewSet)

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title="AraGWAS API", description="REST API for AraGWAS")),
    url(r'^api/', include(router.urls))
]

# for custom REST API endpoints (search, etc)
restpatterns = [
]

restpatterns = format_suffix_patterns(restpatterns, allowed=['json','zip','png','pdf'])
urlpatterns += restpatterns
