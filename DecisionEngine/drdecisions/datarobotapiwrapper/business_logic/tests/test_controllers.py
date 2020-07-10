import copy
from unittest.mock import patch

import pandas as pd
import pytest
from django.test import TestCase
from pytest import mark
from spyne import InvalidInputError

from datarobotapiwrapper.business_logic.controllers import \
    PriceCalculator, PREDICTED_PRICE
from datarobotapiwrapper.business_logic.datarobot_client import DataRobotClient
from datarobotapiwrapper.models import PredictionServer, LogicConnector
from .api_data_examples import *
from .sample_user_src_pandas import PROJECT_ID1, PROJECT_ID2, MODEL_ID1, MODEL_ID2


@mark.django_db
class TestPriceCalculator(TestCase):

    def setUp(self):
        with open('datarobotapiwrapper/business_logic/tests/sample_user_src_pandas.py', 'r') as src_file:
            business_logic = src_file.read()

        self.logic_connector = LogicConnector()
        self.logic_connector.business_logic = business_logic
        self.logic_connector.save()
        self.prediction_server = PredictionServer(logic_connector=self.logic_connector)
        self.prediction_server.save()
        self.price_calculator = PriceCalculator()

    def test_prediction_server(self):
        assert self.prediction_server == self.price_calculator.prediction_server()

    def test_get_logic_connector(self):
        assert self.logic_connector == self.price_calculator.prediction_server().logic_connector

    def test__get_logic_connector(self):
        self.assertEqual(
            self.logic_connector,
            self.price_calculator._get_logic_connector())

    # @patch('datarobotapiwrapper.business_logic.controllers.call_user_function', return_value=DAY_LIMIT)
    def test__data_prepare(self):
        api_data = API_DATA1
        premium = 111
        project_series = pd.Series([PROJECT_ID1, PROJECT_ID2])
        model_series = pd.Series([MODEL_ID1, MODEL_ID2])

        prepared_df = self.price_calculator._data_prepare(api_data, premium, self.logic_connector)
        assert all(prepared_df['project_id'] == project_series)
        assert all(prepared_df['model_id'] == model_series)

        with pytest.raises(InvalidInputError):
            api_data_with_reserved_column = copy.deepcopy(API_DATA1)
            api_data_with_reserved_column[PREDICTED_PRICE] = 'test_value'
            self.price_calculator._data_prepare(
                api_data_with_reserved_column, premium, self.logic_connector)

    @patch('datarobotapiwrapper.business_logic.controllers.put_record')
    @patch.object(DataRobotClient, '_request_predictions')
    def test_calculate(self, mock_request_predictions, mock_put_record):
        api_data = API_DATA1
        premium = 222

        mock_request_predictions.side_effect = [PREDICTIONS_RESPONSE_JSON1, PREDICTIONS_RESPONSE_JSON2]

        calculated_price = self.price_calculator.calculate(api_data, premium)

        assert mock_request_predictions.call_count == 2
        assert calculated_price == 0.75
