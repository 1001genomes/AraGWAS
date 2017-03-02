from rest_framework import serializers

from gwasdb.models import SNP, Study, Association, Genotype, Gene

"""
Study List Serializer Class (read-only)
"""
class StudyListSerializer(serializers.ModelSerializer):
    # association_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = ('name','genotype','publication')

    def get_association_count(selfself, obj):
        try:
            return obj.association_set.count()
        except:
            return ""

"""
Association List Serializer Class (read-only) Can be used to serialize entire study data...
"""
class AssociationListSerializer(serializers.ModelSerializer):
    study = serializers.SerializerMethodField()
    snp = serializers.SerializerMethodField()

    class Meta:
        model = Association
        fields = ('snp', 'study','pvalue')

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

"""
Association Value Serializer Class (read-only)
"""
class AssociationValueSerializer(serializers.ModelSerializer):
    study = serializers.SerializerMethodField()
    snp = serializers.SerializerMethodField()
    chrom = serializers.SerializerMethodField()
    pos = serializers.SerializerMethodField()
    # genes = serializers.SerializerMethodField() # Still unsure whether to add this here


    class Meta:
        model = Association
        fields = ('snp','chrom','pos','maf','pvalue','beta','odds_ratio','confidence_interval','study')

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
"""
SNP List Serializer Class (read-only) Could be integrated in the AssociationValue Serializer above...
"""
class SNPListSerializer(serializers.ModelSerializer):
    genotype = serializers.SerializerMethodField()
    genotype_version = serializers.SerializerMethodField()

    class Meta:
        fields = ('name', 'chromosome', 'position', 'annotation', 'genotype', 'genotype_version')

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

"""
Gene View Serializer Class (read-only) Needs to be written, used when "traveling" on the genomic diagram
"""