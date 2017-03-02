from django.db import models

class Phenotype(models.Model):
    """
    Phenotype model, if possible links to AraPheno
    """
    name = models.CharField(max_length=255) # name of phenotype
    description = models.TextField(blank=True, null=True) # short description
    date = models.DateTimeField(blank= True, null=True) # date of creation/update
    arapheno_link = models.URLField(blank=True, null=True) # link to phenotype entry in AraPheno

class Study(models.Model):
    """
    GWA Study model, if possible links to easyGWAS
    """
    name = models.CharField(max_length=255) # name of the study
    transformation = models.CharField(max_length=255) # transformation used prior to GWAS (log, sqrt, box-cox, etc)
    genotype = models.ForeignKey("Genotype") # foreign key to a Genotype
    method = models.CharField(max_length=255) # method used to individuate associations (LM, KW, LMM, etc)
    publication = models.URLField(blank=True, null=True) # link to a DOI for a published study
    easygwas_link = models.URLField(blank=True, null=True) # link to easygwas study page (if applicable)

class Genotype(models.Model):
    """
    Genotype model, specific to the dataset used for a particular GWAS
    """
    name = models.CharField(max_length=255)  # name of the genotype
    description = models.TextField(blank=True, null=True)  # short description
    version = models.CharField(max_length=255) # version of the dataset

class SNP(models.Model):
    """
    SNP model, might be incorporated directly into Association
    """
    name = models.CharField(max_length=255,default="rs?")
    chromosome = models.IntegerField() # chromosome on which the SNP is located
    position = models.IntegerField() # position of the SNP on the chromosome
    annotation = models.CharField(max_length=255) # genome annotation used to refer to the position (TAIR10, etc)
    genotype = models.ForeignKey("Genotype") # foreign key to a Genotype
    gene = models.ManyToManyField("Gene") # key(s) to associated genes

class Association(models.Model):
    """
    Association model, core of the catalog,  associations found by multiple studies will represent multiple entries
    """
    study = models.ForeignKey("Study") # foreign key to study highlighting association
    snp = models.ForeignKey("SNP") # foreign key to the SNP of interest
    maf = models.FloatField() # minor allele frequency
    pvalue = models.FloatField() # reported association p-value
    beta = models.FloatField(blank=True, null=True) # beta of the regression model
    odds_ratio = models.FloatField(blank=True, null=True) # odds ratio (OR)
    confidence_interval = models.CharField(max_length=255,blank=True, null=True) # 95% confidence interval for OR or Beta

class Gene(models.Model):
    """
    Gene model, could be integrated in association table
    """
    name = models.CharField(max_length=255)  # name of the gene
    chromosome = models.IntegerField()  # chromosome on which the gene is located
    start_position = models.IntegerField()  # start position of the gene on the chromosome
    end_position = models.IntegerField()  # end position of the gene on the chromosome
    description = models.TextField(blank=True, null=True)  # short description

