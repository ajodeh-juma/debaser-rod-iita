from rest_framework import serializers

from.models import *
from .debaser import *



class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        order_by = 'id'
        fields = ('id', 'species_name', 'created_date', 'modified_date', 'species_file')


class SpeciesInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ('id', 'species_name', 'species_file', 'location')
        read_only_fields = ('species_file',)

class VarietyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        order_by = ['id']
        fields = ('id', 'variety_name', 'created_date', 'modified_date', 'variety_consensus', 'species')
        read_only_fields = ('created_date', 'modified_date')

class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        order_by = 'id'
        fields = ('id', 'variety_name', 'created_date', 'modified_date', 'variety_consensus', 'species', 'location')

class VarietyInlineSerializer(serializers.ModelSerializer):
    species = SpeciesInlineSerializer(read_only=True)

    
    class Meta:
        model = Variety
        order_by = 'id'
        fields = ('id', 'species', 'variety_name', 'variety_consensus', 'location')

class SpeciesListSerializer(serializers.ModelSerializer):
    varieties = VarietyInlineSerializer(many=True, read_only=True)
    class Meta:
        model = Species
        order_by = 'species_name'
        fields = ('id', 'species_name', 'created_date', 'modified_date', 'species_file', 'varieties')



#class OutputFormatsSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = OutputFormats
#        order_by = 'id'
#        fields = ('id', 'outputformat')

#class JobIDSerializer(serializers.ModelSerializer):
#	class Meta:
#		model = JobID
#		order_by = 'created_date'
#		fields = ('id', 'jobID', 'files')



class SubmitGeneIdentifiersSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        submitted_data = super(SubmitGeneIdentifiersSerializer, self).create(validated_data)
        geneid_dict = createGeneidDict(submitted_data)
        varietycat = varietyCategory(geneid_dict)
        consensusSingle = extractSingle(varietycat, geneid_dict)
        consensusMultiple = extractMultiple(varietycat, geneid_dict)
        muscleSeqID = run_muscle(consensusMultiple, geneid_dict)
        multalinSeqID = run_multalin(consensusMultiple, geneid_dict)
        multalinseqIDdoc2html = doc2html(multalinSeqID)
        resultsconsensus = postresults(muscleSeqID, multalinseqIDdoc2html, geneid_dict, consensusMultiple)
        #cleandir = clean_()
        return submitted_data

    class Meta:
        model = SubmitGeneIdentifiers
        order_by = ["submitted_time"]
        fields = ("id", "url", "created_date", "submitted_time", "jobid", "organism", "varieties", "geneid", "outputfmt", "uuid")

class SubmitGeneIdentifiersInlineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubmitGeneIdentifiers
        order_by = ["submitted_time"]
        fields = ("jobid",)

class SubmitGeneIdentifiersListSerializer(serializers.ModelSerializer):
	varieties = VarietyInlineSerializer(read_only=True, many=True)

	class Meta:
		model = SubmitGeneIdentifiers
		order_by = ["submitted_time"]
		fields = ("id", "url", "created_date", "submitted_time", "jobid", "organism", "varieties", "geneid", "outputfmt", "uuid")


class ResultsGeneIdentifiersInlineSerializer(serializers.ModelSerializer):

	class Meta:
		model = ResultsGeneIdentifiers
		order_by = ['created_date']
		fields = ('url', 'consensus_html', 'consensus_file', 'consensuslink', 'uniqueid', 'reportfile')
		read_only_fields = ('created_date',)

class ResultsGeneIdentifiersSerializer(serializers.ModelSerializer):
     
    def create(self, validated_data):
        results_data = super(ResultsGeneIdentifiersSerializer, self).create(validated_data)
        return results_data
	
    class Meta:
        model = ResultsGeneIdentifiers
        order_by = ['created_date']
        fields = ('url', 'consensus_html', 'consensus_file', 'consensuslink', 'uniqueid', 'reportfile')
        read_only_fields = ('created_date', )

class ResultsGeneIdentifiersListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ResultsGeneIdentifiers
        order_by = ['created_date']
        fields = ('url', 'created_date', 'consensus_html', 'consensus_file', 'consensuslink', 'uniqueid', 'reportfile')
        read_only_fields = ('created_date',)



class MultiGeneIdentifiersFilesInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiGeneIdentifiersFiles
        order_by = ['created_date']
        fields = ('id', 'url', 'html_file')
        read_only_fields = ('created_date',)

class MultiGeneIdentifiersFilesSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        results_data = super(MultiGeneIdentifiersFilesSerializer, self).create(validated_data)
        return results_data
    class Meta:
        model = MultiGeneIdentifiersFiles
        fields = ('id', 'url', 'created_date', 'html_file')
        read_only_fields = ('created_date',)

class MultiGeneIdentifiersFilesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiGeneIdentifiersFiles
        order_by = ['created_date']
        fields = ('id', 'url', 'created_date', 'html_file')
        read_only_fields = ('created_date',)


class MultipleVarietiesResultsInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = MultipleVarietiesResultsIDs
        order_by = ['created_date']
        fields = ('uniqueid', 'url', 'consensus_file', 'muscle_file', 'multalin_file', 'html_file', 'htmlfilelist', 'linksfile')
        read_only_fields = ('created_date',)

class MultipleVarietiesResultsSerializer(serializers.ModelSerializer):
     
    def create(self, validated_data):
        results_data = super(MultipleVarietiesResultsSerializer, self).create(validated_data)
        return results_data
    
    class Meta:
        model = MultipleVarietiesResultsIDs
        order_by = ['created_date']
        fields = ('uniqueid', 'url', 'consensus_file', 'muscle_file', 'multalin_file', 'html_file', 'htmlfilelist', 'linksfile', 'created_date')
        read_only_fields = ('created_date',)

class MultipleVarietiesResultsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleVarietiesResultsIDs
        order_by = ['created_date']
        fields = ('uniqueid', 'url', 'created_date', 'consensus_file', 'muscle_file', 'multalin_file', 'html_file', 'htmlfilelist' 'linksfile')
        read_only_fields = ('created_date',)


class SubmitSequenceSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        submitted_data = super(SubmitSequenceSerializer, self).create(validated_data)
        sequence_dict = createSequenceDict(submitted_data)
        mkblast = makelocalblast(sequence_dict)
        blastnSeq = runblast(sequence_dict)
        blastParsed = parseblastout(blastnSeq)
        varietycat = varietyCategory(blastParsed)
        singleSeq = extractSingle(varietycat, blastParsed)
        consensusMultiple = extractMultiple(varietycat, blastParsed)
        muscleSeq = run_muscle(consensusMultiple, blastParsed)
        multalinSeq  = run_multalin(consensusMultiple, blastParsed)
        multalinseqdoc2html = doc2html(multalinSeq)
        resultsconsensus = postresults(muscleSeq, multalinseqdoc2html, blastParsed, consensusMultiple)
        return submitted_data

    class Meta:
        model = SubmitSequence
        order_by = ["submitted_time"]
        fields = ("id", "url", "created_date", "submitted_time", "jobid", "organism", "varieties", "sequence", "outputfmt", "uuid")


class SubmitSequenceInlineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubmitSequence
        order_by = ["submitted_time"]
        fields = ("jobid",)


class SubmitSequenceListSerializer(serializers.ModelSerializer):
    varieties = VarietyInlineSerializer(read_only=True, many=True)

    class Meta:
        model = SubmitSequence
        order_by = ["submitted_time"]
        fields = ("id", "url", "created_date", "submitted_time", "jobid", "organism", "varieties", "sequence", "outputfmt", "uuid")




