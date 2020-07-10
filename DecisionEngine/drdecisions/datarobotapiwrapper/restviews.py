from django.shortcuts import render
from basicauth.decorators import basic_auth_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from spyne import Application, Service, rpc
from spyne import Decimal, ComplexModel, XmlAttribute, Array, XmlData, Unicode, String
from spyne import Application, rpc, ServiceBase, Iterable, UnsignedInteger, String
from spyne.server.django import DjangoView
from spyne.protocol.json import JsonDocument
from spyne.protocol.http import HttpRpc
from spyne.server.wsgi import WsgiApplication

from datarobotapiwrapper.business_logic.controllers import DecisionEngine

""" Please note that if only REST is required, a framework like djangorestframework 
    would probably be better suited than spyne """
class feature(ComplexModel):
    name = String()
    value = String()



class response(ComplexModel):
    identifier = Unicode()
    decision = String()


class RestApiWrapperService(Service):

    
    @rpc(Unicode, String, Array(feature, min_occurs=1), _returns=response)
    def makeDecision(ctx, id, entity, features ):
        api_data = {f.name: f.value for f in features}
        adjusted_prediction = DecisionEngine().makeDecision(api_data, entity)

        resp = response(identifier=id, decision=adjusted_prediction.iloc[0])
        return resp


@method_decorator(basic_auth_required, name='dispatch')
class RestRecordingView(DjangoView):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        resp = super(RestRecordingView, self).dispatch(request, *args, **kwargs, **{'throttle': True})
        # print('resp', resp)
        # print('resp', resp.content)
        # print('dir resp', dir(resp))
        return resp


restapp = Application([RestApiWrapperService],'datarobotdecisions',
                  in_protocol=JsonDocument(validator='soft'),
                  out_protocol=JsonDocument())