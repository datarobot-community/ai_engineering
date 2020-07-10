from django.shortcuts import render
from basicauth.decorators import basic_auth_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from spyne import Application, Service, rpc
from spyne import Decimal, ComplexModel, XmlAttribute, Array, XmlData, Unicode, String
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoView

from datarobotapiwrapper.business_logic.controllers import DecisionEngine

SOAP_DATAROBOT = 'soap.datarobot'


class feature(ComplexModel):
    __namespace__ = SOAP_DATAROBOT
    name = XmlAttribute(Unicode)
    value = XmlData(Unicode)


class reason(ComplexModel):
    __namespace__ = SOAP_DATAROBOT
    feature = Unicode()
    strength = Decimal()


class response(ComplexModel):
    __namespace__ = SOAP_DATAROBOT
    identifier = Unicode()
    decision = String()


class ApiWrapperService(Service):

    # noinspection PyMethodParameters
    @rpc(Unicode, Array(feature, min_occurs=1), Unicode, _returns=response)
    def makeDecision(ctx, id, features, entity):
        api_data = {f.name: f.value for f in features}
        adjusted_prediction = DecisionEngine().makeDecision(api_data, entity)

        resp = response(identifier=id, decision=adjusted_prediction.iloc[0])
        return resp


@method_decorator(basic_auth_required, name='dispatch')
class RecordingView(DjangoView):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        resp = super(RecordingView, self).dispatch(request, *args, **kwargs, **{'throttle': True})
        return resp


app = Application([ApiWrapperService],
                  SOAP_DATAROBOT,
                  in_protocol=Soap11(validator='lxml'),
                  out_protocol=Soap11())