from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

class Phenotype(models.Model):
    """
    Phenotype model, if possible links to AraPheno
    """
    name = models.CharField(max_length=255) # name of phenotype
    study_name = models.CharField(max_length=255, default = "")
    description = models.TextField(blank=True, null=True) # short description
    date = models.DateTimeField(blank= True, null=True) # date of creation/update
    # to = models.CharField(max_length=255) # Trait ontology that regroups similar phenotypes TODO: add trait ontology to all phenotypes
    arapheno_link = models.URLField(blank=True, null=True) # link to phenotype entry in AraPheno
    trait_ontology_id = models.CharField(max_length=50, default="")
    trait_ontology_name = models.CharField(max_length=255, default="")
    trait_ontology_description = models.CharField(max_length=255, default="", null=True)

    @property
    def doi(self):
        """Returns the DOI"""
        return '%s/phenotype:%s' % (settings.DATACITE_PREFIX, self.id)

    def __str__(self):
        return "Phenotype: %s (%s)" % (self.name, self.study_name)

class Study(models.Model):
    """
    GWA Study model, associated with ONE phenotype, if possible links to easyGWAS
    """
    name = models.CharField(max_length=255) # name of the study
    transformation = models.CharField(max_length=255) # transformation used prior to GWAS (log, sqrt, box-cox, etc)
    genotype = models.ForeignKey("Genotype") # foreign key to a Genotype
    phenotype = models.ForeignKey("Phenotype", null=True) # foregin key to the phenotype of interest
    method = models.CharField(max_length=255) # method used to individuate associations (LM, KW, LMM, etc)
    publication = models.URLField(blank=True, null=True) # link to a DOI for a published study
    publication_name = models.CharField(max_length=255, blank=True, null=True) # internal name of the publication
    publication_pmid = models.CharField(max_length=255, blank=True, null=True) # pubmed id of publication
    publication_pmcid = models.CharField(max_length=255, blank=True, null=True) # pubmed central id of publication
    number_samples = models.IntegerField(blank=True, null=True) # number of samples used in the GWAS
    number_countries = models.IntegerField(blank=True, null=True) # number of countries of origin for the various accessions
    n_hits_thr = models.IntegerField(blank=True, null=True)  # number of hits with 1e-4 threshold
    n_hits_bonf = models.IntegerField(blank=True, null=True) # number of hits with Bonferoni threshold
    n_hits_fdr = models.IntegerField(blank=True, null=True) # number of hits above FDR (benjamini-hochberg) threshold
    n_hits_perm = models.IntegerField(blank=True, null=True) # number of hits with permutation threshold
    bh_threshold = models.FloatField(blank=True, null=True) # FDR threshold
    bonferroni_threshold = models.FloatField(blank=True, null=True) # bonferroni threshold
    permutation_threshold = models.FloatField(blank=True, null=True) # permutation threshold
    n_hits_total = models.IntegerField(blank=True, null=True) # total number of associations
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=None, null=True, blank=True)

    def get_absolute_url(self):
        """returns the submission page or study detail page"""
        url = reverse('index')
        return url + "#/study/%s" % self.pk

    @property
    def doi(self):
        """Returns the DOI"""
        return '%s/gwas:%s' % (settings.DATACITE_PREFIX, self.id)

    @property
    def doi_link(self):
        """Returns the DOI link to datacite"""
        return '%s/%s' % (settings.DATACITE_DOI_URL, self.doi)

    def __str__(self):
        return "Study: %s" % (self.name)

# TODO add number of markers as field and DOI for publication
# how to deal with versioning (maybe via N:M table)
class Genotype(models.Model):
    """
    Genotype model, specific to the dataset used for a particular GWAS
    """
    name = models.CharField(max_length=255)  # name of the genotype
    description = models.TextField(blank=True, null=True)  # short description
    version = models.CharField(max_length=255) # version of the dataset

    def __str__(self):
        return u"{} {}".format(self.name, self.version)


