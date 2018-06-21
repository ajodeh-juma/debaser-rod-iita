"""DeBaser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include 
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from debaserapp import views

router = routers.DefaultRouter()
router.register(r'species', views.SpeciesViewSet)
router.register(r'varieties', views.VarietyViewSet)
#router.register(r'out-formats', views.OutputFormatsViewSet)
router.register(r'geneids', views.SubmitGeneIdentifiersViewSet)

router.register(r'results-geneids', views.ResultsGeneIdentifiersViewSet)
router.register(r'multi-varieties', views.MultiGeneIdentifiersFilesViewSet)
router.register(r'multi-results-ids', views.MultipleVarietiesResultsViewSet)

router.register(r'sequences', views.SubmitSequenceViewSet)
#router.register(r'jobids', views.JobIDViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    