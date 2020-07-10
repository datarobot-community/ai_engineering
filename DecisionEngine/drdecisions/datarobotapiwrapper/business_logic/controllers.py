import pandas as pd
from spyne import InvalidInputError

#from datarobotapiwrapper.logs.firehose import put_record
from datarobotapiwrapper.models import LogicConnector, BusinessEntity
from datarobotapiwrapper.models import PredictionServer
from datarobotapiwrapper.user_src.run_user_code import call_user_function
from .datarobot_client import DataRobotClient


DF_ORIENT = 'records'

ADJUSTED_PRICE_DEFAULT = 1.0



ENTITY = 'entity'
DECISION = 'decision'
DATA_PREPARE_FN = 'data_prepare'
BUSINESS_LOGIC_FN = 'business_logic'

RESERVED_COLUMNS = (ENTITY, DECISION, DATA_PREPARE_FN, BUSINESS_LOGIC_FN)


class DecisionEngine:
    def __init__(self):
        datarobot_client_settings = DecisionEngine.prediction_server()
        self.datarobot = DataRobotClient(datarobot_client_settings)

    @staticmethod
    def prediction_server():
        return PredictionServer.get_solo()

    @staticmethod
    def _get_default_logic_connector():
        return DecisionEngine.prediction_server().logic_connector

    @staticmethod
    def _get_logic_connector(entity):
        if entity is not None:
            try:
                return BusinessEntity.objects.select_related('logic_connector').get(name__exact=entity).logic_connector
            except BusinessEntity.DoesNotExist:
                pass
        return DecisionEngine._get_default_logic_connector()

    def makeDecision(self, api_data, entity):
        #entity = api_data.get(entity)
        logic_connector = DecisionEngine._get_logic_connector(entity)
        prepared_df = DecisionEngine._data_prepare(api_data, entity, logic_connector)
        prediction_df = self.datarobot.add_predictions(prepared_df, DECISION)
        adjusted_decision, result_df = call_user_function(logic_connector.business_logic,
                                                       BUSINESS_LOGIC_FN,
                                                       prediction_df)

        DecisionEngine._log_request(result_df, logic_connector.id)
        return adjusted_decision

    @staticmethod
    def _log_request(result_df, logic_connector_id):
        # usage counter
        LogicConnector.inc_run_count(logic_connector_id)
        DecisionEngine.log_df(result_df, logic_connector_id)

    @staticmethod
    def _data_prepare(api_data, entity, user_logic):
        # convert to Pandas DataFrame
        features_df = pd.DataFrame([api_data])
        has_reserved_column = any(col in RESERVED_COLUMNS for col in features_df.columns.values)
        if has_reserved_column:
            raise InvalidInputError(
                faultstring=f'Reserved column name found in data. '
                            f'All reserved columns {RESERVED_COLUMNS}')

        features_df[ENTITY] = entity
        prepared_df = call_user_function(user_logic.business_logic,
                                         DATA_PREPARE_FN,
                                         features_df)
        return prepared_df

    @staticmethod
    def log_df(data_frame, logic_connector_id):
        # convert all columns to str, for avoiding type problems
        for column in data_frame:
            data_frame[column] = data_frame[column].astype(str)
        # add logic_connector_id column
        data_frame['logic_connector'] = logic_connector_id
        data = data_frame.to_json(orient='records', lines=True)
        data_lines = data.split('\n')
        #put_record(data_lines)
        return len(data_lines)
