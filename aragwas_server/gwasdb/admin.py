from django.contrib import admin
from gwasdb.models import Study, Gene, Genotype, SNP, Association

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transformation', 'genotype', 'method','publication','easygwas_link']

@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ['snp', 'study', 'maf', 'pvalue', 'beta', 'odds_ratio','confidence_interval']
