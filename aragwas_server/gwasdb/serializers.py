from rest_framework import serializers

from gwasdb.models import SNP, Study, Association, Genotype, Gene, Phenotype


class ApiVersionSerializer(serializers.Serializer):
    """Serializers the API version information"""
    version = serializers.CharField(read_only=True)
    githash = serializers.CharField(read_only=True)
    build = serializers.CharField(read_only=True)
    build_url = serializers.URLField(read_only=True)
    github_url = serializers.URLField(read_only=True)
    date = serializers.DateField(read_only=True)

class EsPhenotypeSerializer(serializers.ModelSerializer):
    """Serializer for elasticserach"""
    suggest = serializers.SerializerMethodField()

    def get_suggest(self, instance):
        return [instance.name]

    class Meta:
        model = Phenotype
        fields = ('id', 'suggest', 'name', 'description', 'date')


class EsGenotypeSerializer(serializers.ModelSerializer):
    """Serializer for elasticserach"""

    class Meta:
        model = Genotype
        fields = ('id', 'name', 'description', 'version')


class EsStudySerializer(serializers.ModelSerializer):
    """Serializer for elasticserach"""
    suggest = serializers.SerializerMethodField()
    genotype = EsGenotypeSerializer(many=False)
    phenotype = EsPhenotypeSerializer(many=False)


    def get_suggest(self, instance):
        return [instance.name]

    class Meta:
        model = Study
        fields = ('id', 'suggest', 'name', 'transformation', 'method', 'genotype', 'phenotype')


"""
Study List Serializer Class (read-only)
"""
class StudySerializer(serializers.ModelSerializer):
    association_count = serializers.SerializerMethodField()
    genotype = serializers.SerializerMethodField()
    phenotype = serializers.SerializerMethodField()
    phenotype_pk = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ('name','genotype','phenotype','phenotype_pk','method','transformation', 'publication','association_count','pk')

    def get_association_count(self, obj):
        try:
            return obj.association_set.count()
        except:
            return ""

    def get_genotype(self, obj):
        try:
            return "{} v{}".format(obj.genotype.name, obj.genotype.version)
        except:
            return ""

    def get_phenotype(self, obj):
        try:
            return obj.phenotype.name
        except:
            return ""
    def get_phenotype_pk(self,obj):
        try:
            return obj.phenotype.pk
        except:
            return ""

"""
Association List Serializer Class (read-only) Can be used to serialize entire study data...
"""
class AssociationListSerializer(serializers.ModelSerializer):
    study = serializers.SerializerMethodField()
    snp = serializers.SerializerMethodField()
    gene = serializers.SerializerMethodField()
    phenotype = serializers.SerializerMethodField()

    class Meta:
        model = Association
        fields = ('snp','study','pvalue','gene','phenotype')

    def get_study(self, obj):
        try:
            return obj.study.name
        except:
            return ""

    def get_snp(self, obj):
        try:
            return obj.snp.get_name()
        except:
            return ""

    def get_gene(self, obj):
        try:
            return obj.snp.gene.name
        except:
            return ""

    def get_phenotype(self, obj):
        try:
            return obj.study.phenotype.name
        except:
            return ""

"""
Association Value Serializer Class (read-only)
"""
class AssociationSerializer(serializers.ModelSerializer):
    study = serializers.SerializerMethodField()
    snp = serializers.SerializerMethodField()
    chrom = serializers.SerializerMethodField()
    pos = serializers.SerializerMethodField()
    phenotype = serializers.SerializerMethodField()
    # genes = serializers.SerializerMethodField() # Still unsure whether to add this here


    class Meta:
        model = Association
        fields = ('snp','chrom','pos','maf','pvalue','beta','odds_ratio','confidence_interval','phenotype','study')

    def get_study(self, obj):
        try:
            return obj.study.name
        except:
            return ""

    def get_snp(self, obj):
        try:
            return obj.snp.name
        except:
            return ""

    def get_chrom(self, obj):
        try:
            return obj.snp.chromosome
        except:
            return ""

    def get_pos(self, obj):
        try:
            return obj.snp.position
        except:
            return ""

    def get_phenotype(self, obj):
        try:
            return obj.study.phenotype.name
        except:
            return


"""
SNP List Serializer Class (read-only) Could be integrated in the AssociationValue Serializer above...
"""
class SNPListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    genotype = serializers.SerializerMethodField()
    genotype_version = serializers.SerializerMethodField()
    association_count = serializers.SerializerMethodField()

    class Meta:
        model = SNP
        fields = ('name', 'chromosome', 'position', 'annotation', 'genotype', 'genotype_version', 'association_count')

    def get_name(self, obj):
        try:
            return obj.get_name()
        except:
            return ""
    def get_genotype(self, obj):
        try:
            return obj.genotype.name
        except:
            return ""

    def get_genotype_version(self, obj):
        try:
            return obj.genotype.version
        except:
            return ""

    def get_association_count(self,obj):
        try:
            return obj.association_set.count()
        except:
            return ""

"""
Phenotype List Serializer Class (read-only)
"""
class PhenotypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phenotype
        fields = ('name','description','arapheno_link','pk','study_set')


"""
Gene List Serializer Class (read-only)
"""
class GeneListSerializer(serializers.ModelSerializer):
    association_count = serializers.SerializerMethodField()
    SNP_count = serializers.SerializerMethodField()
    SNPs = serializers.SerializerMethodField()

    class Meta:
        model = Gene
        fields = ('name','chromosome','start_position','end_position','SNPs','SNP_count','association_count','description','pk')

    def get_association_count(self, obj):
        try:
            return obj.SNPs_set.association_set.count()
        except:
            return ""

    def get_SNP_count(self, obj):
        try:
            return obj.SNPs_set.count()
        except:
            return ""

    def get_SNPs(self, obj):
        try:
            return obj.SNPs_set
        except:
            return
