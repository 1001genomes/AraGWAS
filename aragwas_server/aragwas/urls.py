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
from django.conf.urls import url
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns

from gwasdb import views

import gwasdb.rest as rest

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title="AraGWAS API", description="REST API for AraGWAS"))]

restpatterns = [

    url(r'^api/associations/', rest.association_list)
    #search
    # url(r'^rest/search/$', rest.search),
    # url(r'^rest/search/(?P<query_term>.*)/$', rest.search),
]

restpatterns = format_suffix_patterns(restpatterns, allowed=['json','zip','png','pdf'])
urlpatterns += restpatterns
