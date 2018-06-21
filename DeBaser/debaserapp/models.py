import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import Textarea
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.files.storage import FileSystemStorage
from django.core.validators import URLValidator
from jsonfield import JSONField

# Create your models here.
@python_2_unicode_compatible
class AbstractBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return ''

    class Meta:
        abstract = True

#@python_2_unicode_compatible
#class AbstractBaseWithUser(AbstractBase):
#    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

#    def __str__(self):
#        return self.user.email

#    class Meta:
#        abstract = True

@python_2_unicode_compatible
class Species(AbstractBase):
    species_fs = '/'.join(['species/'])
    species_name = models.CharField(max_length=100, blank=True)
    species_file = models.FileField(upload_to=species_fs)
    location = models.CharField(species_fs, max_length=200, default='input')

    def __str__(self):
        return self.species_name

    class Meta:
        ordering = ['species_name']

@python_2_unicode_compatible
class Variety(AbstractBase):
    variety_fs = '/'.join(['varieties/'])
    variety_name = models.CharField(max_length=100, blank=True)
    species = models.ForeignKey(Species, related_name='varieties', on_delete=models.CASCADE)
    variety_consensus = models.FileField(upload_to=variety_fs)
    location = models.CharField(variety_fs, max_length=200, default='varieties')

    class Meta:
        ordering = ['variety_name']

    def __str__(self):
        return self.variety_name


#@python_2_unicode_compatible
#class OutputFormats(AbstractBase):
#    outputformat = models.CharField(max_length=100, blank=True)

#    class Meta:
#        ordering = ['outputformat']

#    def __str__(self):
#        return self.outputformat


@python_2_unicode_compatible
class SubmitGeneIdentifiers(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    inputTYPE = models.TextField()
    organism = models.TextField()
    varieties = models.ManyToManyField(Variety, related_name="submitted_geneid")
    geneid = models.TextField()
    outputfmt = models.TextField()
    jobid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, blank=True)
    submitted_time = models.TimeField(auto_now_add=True, blank=True)
    uuid = models.TextField()

    def __str__(self):
        return str(self.uuid)

@python_2_unicode_compatible
class SubmitSequence(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    organism = models.TextField()
    varieties = models.ManyToManyField(Variety, related_name="submitted_sequence")
    sequence = models.TextField()
    outputfmt = models.TextField()
    jobid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, blank=True)
    submitted_time = models.TimeField(auto_now_add=True, blank=True)
    uuid = models.TextField()
    
    def __str__(self):
        return str(self.uuid)

@python_2_unicode_compatible
class ResultsGeneIdentifiers(models.Model):
    results_fs = '/'.join(['results-geneids/'])
    created_date = models.DateTimeField(auto_now_add=True)
    consensus_html = models.FileField(upload_to=results_fs, default='')
    consensus_file = models.FileField(upload_to=results_fs, default='')
    uniqueid = models.CharField(primary_key=True, max_length=20)
    consensuslink = models.FileField(upload_to=results_fs, default='')
    reportfile = models.FileField(upload_to=results_fs, default='')
    def __str__(self):       
        return str(self.uniqueid)


@python_2_unicode_compatible
class MultipleVarietiesResultsIDs(models.Model):
    multresultsids_fs = '/'.join(['multi-results-ids/'])
    created_date = models.DateTimeField(auto_now_add=True)
    consensus_file = models.FileField(upload_to=multresultsids_fs, default='')
    muscle_file = models.FileField(upload_to=multresultsids_fs, default='')
    multalin_file = models.FileField(upload_to=multresultsids_fs, default='')
    html_file = models.FileField(upload_to=multresultsids_fs, default='')
    uniqueid = models.CharField(primary_key=True, max_length=20, default='')
    htmlfilelist = JSONField(default='')
    linksfile = models.FileField(upload_to=multresultsids_fs, default='')
    

    def __str__(self):
        return self.html_file

@python_2_unicode_compatible
class MultiGeneIdentifiersFiles(models.Model):
    results_fs = '/'.join(['multi-varieties/'])
    created_date = models.DateTimeField(auto_now_add=True)
    html_file = models.FileField(upload_to=results_fs, default='')
    #htmlfilelist = models.ListField()
    #multivarietieshtmlfiles = models.ForeignKey(MultipleVarietiesResultsIDs, related_name='multigeneidentifiersfiles', on_delete=models.CASCADE)
    #uniqueid = models.CharField(primary_key=True, max_length=20)
    def __str__(self):       
        return str(self.uniqueid)