from django.shortcuts import render
from rest_framework import viewsets
from django.http import Http404
from rest_framework import status
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from rest_framework.reverse import reverse
from rest_framework import permissions

from .serializers import *

# Create your views here.


@api_view(['GET'])
def api_root(request, format=None):
    return Response ({
        'species':   reverse('species-list',   request=request, format=format),
        'varieties': reverse('varieties-list', request=request, format=format)
    })


class SpeciesViewSet(viewsets.ModelViewSet):
    """API endpoint to POST, PUT, GET the organism/reference/species"""
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SpeciesListSerializer
        return SpeciesSerializer

    def delete(self, serializer):
        Species.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class VarietyViewSet(viewsets.ModelViewSet):
    """API endpoint to POST, PUT, GET varieties"""
    queryset = Variety.objects.all()
    serializer_class = VarietySerializer
    parser_classes = (MultiPartParser, FormParser)
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    ordering = ('variety_name')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VarietyListSerializer
        return VarietySerializer

    def delete(self, serializer):
        Variety.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#class OutputFormatsViewSet(viewsets.ModelViewSet):
#    queryset = OutputFormats.objects.all()
#    serializer_class = OutputFormatsSerializer



class SubmitGeneIdentifiersViewSet(viewsets.ModelViewSet):
    """API endpoint for submission of data with gene identifiers as input"""
    queryset = SubmitGeneIdentifiers.objects.all()
    serializer_class = SubmitGeneIdentifiersSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubmitGeneIdentifiersListSerializer
        return SubmitGeneIdentifiersSerializer

    def delete(self, serializer):
        SubmitGeneIdentifiers.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubmitSequenceViewSet(viewsets.ModelViewSet):
    """API endpoint for submission of data with sequences (FASTA format) as input"""
    queryset = SubmitSequence.objects.all()
    serializer_class = SubmitSequenceSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubmitSequenceListSerializer
        return SubmitSequenceSerializer

    def delete(self, serializer):
        SubmitSequence.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResultsGeneIdentifiersViewSet(viewsets.ModelViewSet):
    """API endpoint for consensus sequence results"""

    queryset = ResultsGeneIdentifiers.objects.all()
    serializer_class = ResultsGeneIdentifiersSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ResultsGeneIdentifiersSerializer
        return ResultsGeneIdentifiersSerializer



    def delete(self, serializer):
        ResultsGeneIdentifiers.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MultiGeneIdentifiersFilesViewSet(viewsets.ModelViewSet):
    """API endpoint for multiple varieties selection output (muscle, multalin) html results"""

    queryset = MultiGeneIdentifiersFiles.objects.all()
    serializer_class = MultiGeneIdentifiersFilesSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MultiGeneIdentifiersFilesSerializer
        return MultiGeneIdentifiersFilesSerializer

    def delete(self, serializer):
        MultiGeneIdentifiersFiles.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MultipleVarietiesResultsViewSet(viewsets.ModelViewSet):
    """API endpoint for multiple varieties selection output (muscle, multalin) html results"""

    queryset = MultipleVarietiesResultsIDs.objects.all()
    serializer_class = MultipleVarietiesResultsSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MultipleVarietiesResultsSerializer
        return MultipleVarietiesResultsSerializer



    def delete(self, serializer):
        MultipleVarietiesResultsIDs.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




#class JobIDViewSet(viewsets.ModelViewSet):

#    queryset = JobID.objects.all()
#    serializer_class = JobID

#    def get_serializer_class(self):
#        if self.request.method == 'GET':
#            return JobIDSerializer
#        return JobIDSerializer

