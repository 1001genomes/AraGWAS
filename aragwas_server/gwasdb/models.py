from django.db import models

class Phenotype(models.Model):
    """
    Phenotype model, if possible links to AraPheno
    """
    name = models.CharField(max_length=255) # name of phenotype
    description = models.TextField(blank=True, null=True) # short description
    date = models.DateTimeField(blank= True, null=True) # date of creation/update
    # to = models.CharField(max_length=255) # Trait ontology that regroups similar phenotypes TODO: add trait ontology to all phenotypes
    arapheno_link = models.URLField(blank=True, null=True) # link to phenotype entry in AraPheno

    def __str__(self):
        return "Phenotype: %s" % (self.name)

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
    easygwas_link = models.URLField(blank=True, null=True) # link to easygwas study page (if applicable)

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


