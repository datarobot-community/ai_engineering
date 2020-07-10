from django.conf.urls import url


from datarobotapiwrapper.soapviews import app, RecordingView
from datarobotapiwrapper.restviews import restapp, RestRecordingView

urlpatterns = [
    url(r'^soapapi/', RecordingView.as_view(application=app, cache_wsdl=False), name='soapapi'),
    url(r'^restapi/', RestRecordingView.as_view(application=restapp), name='restapi'),
]