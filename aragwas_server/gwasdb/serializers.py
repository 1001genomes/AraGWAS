from rest_framework import serializers

from gwasdb.models import Study, Genotype, Phenotype


class ApiVersionSerializer(serializers.Serializer):
    """Serializers the API version information"""
    version = serializers.CharField(read_only=True)
    githash = serializers.CharField(read_only=True)
    build = serializers.CharField(read_only=True)
    build_url = serializers.URLField(read_only=True)
    github_url = serializers.URLField(read_only=True)
    date = serializers.DateField(read_only=True)

class GenotypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genotype
        fields = '__all__'

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
        fields = ('id', 'suggest', 'name', 'transformation', 'method', 'genotype', 'phenotype','n_hits_bonf','n_hits_perm','n_hits_thr')


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
        fields = ('name','genotype','phenotype','phenotype_pk','method','transformation', 'publication','association_count','pk','n_hits_bonf','n_hits_perm','n_hits_thr','number_samples', 'number_countries')

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
Phenotype List Serializer Class (read-only)
"""
class PhenotypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phenotype
        fields = ('name','description','arapheno_link','pk','study_set')
