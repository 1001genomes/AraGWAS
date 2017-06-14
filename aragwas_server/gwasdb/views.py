from django.views.generic import DetailView

from django.shortcuts import render
from gwasdb.models import (Study,Genotype,Phenotype)
from gwasdb.serializers import *


def index(request):
    '''
    Home View of AraGWAS
    '''
    return render(request, 'index.html')
