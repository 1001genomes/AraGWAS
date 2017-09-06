from django.contrib import admin
from gwasdb.models import Study, Genotype, Phenotype

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transformation', 'genotype', 'method','publication']

@admin.register(Genotype)
class GenotypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'version']

@admin.register(Phenotype)
class PhenotypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description','date' ]
