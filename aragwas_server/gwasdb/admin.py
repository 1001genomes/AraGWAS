from django.contrib import admin
from gwasdb.models import Study, Genotype

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transformation', 'genotype', 'method','publication','easygwas_link']
