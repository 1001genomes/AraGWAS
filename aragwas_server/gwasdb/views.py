from django.views.generic import DetailView

from django.shortcuts import render
from gwasdb.models import (Study,Association,SNP,Gene,Genotype,Phenotype)
from gwasdb.serializers import *

class SNPDetail(DetailView):
    """
    Detailed view for a single phenotype
    """
    model = SNP

