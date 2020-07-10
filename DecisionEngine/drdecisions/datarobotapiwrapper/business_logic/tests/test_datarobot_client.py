from unittest import mock

import pandas as pd

from datarobotapiwrapper.business_logic.datarobot_client import DataRobotClient


def test_parse_response():
    predictions_json = {
        'data': [
            {
                'rowId': 2,
                'prediction': 2.05
            },
            {
                'rowId': 1,
                'prediction': 1.05
            }
        ]
    }
    index = pd.Index([1, 3])
    predictions = DataRobotClient._parse_response(predictions_json, index)
    expected = pd.DataFrame({'prediction': [1.05, 2.05]}, index=index)
    assert predictions.equals(expected)


@mock.patch.object(DataRobotClient, 'get_predictions')
def test_add_predictions(mock_get_predictions):
    prepared_data = pd.DataFrame(
        {
            'value': [1, 2, 3, 4],
            'project_id': ['p1', 'p2', 'p1', 'p2'],
            'model_id': ['m1', 'm2', 'm1', 'm3'],
        })

    prepared_data_deployment = pd.DataFrame(
        {
            'value': [1, 2, 3, 4],
            'deployment_id': ['d1', 'd2', 'd3', 'd1'],
        })

    def get_predictions(features, gorupby_ids):
        response = features.copy()
        response['prediction'] = response['value'] * 10
        return response

    mock_get_predictions.side_effect = get_predictions

    prediction_server = mock.MagicMock()
    datarobot = DataRobotClient(prediction_server)

    expected_data = pd.DataFrame(
        {
            'value': [1, 2, 3, 4],
            'project_id': ['p1', 'p2', 'p1', 'p2'],
            'model_id': ['m1', 'm2', 'm1', 'm3'],
            'target': [10, 20, 30, 40]
        })
    expected_data_deployment = pd.DataFrame(
        {
            'value': [1, 2, 3, 4],
            'deployment_id': ['d1', 'd2', 'd3', 'd1'],
            'target': [10, 20, 30, 40]
        })

    actual_data = datarobot.add_predictions(prepared_data, 'target')
    assert expected_data.equals(actual_data)

    actual_data_deployment = datarobot.add_predictions(prepared_data_deployment, 'target')
    assert expected_data_deployment.equals(actual_data_deployment)
