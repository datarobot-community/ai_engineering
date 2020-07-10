from http import HTTPStatus

import pandas as pd
import requests
from spyne import ArgumentError


class DataRobotClient:
    def __init__(self, prediction_server):
        self.prediction_url = prediction_server.server_url
        self.https_session = self.get_https_session(prediction_server)

    def get_https_session(self, prediction_server):
        https_session = requests.Session()
        https_session.headers.update(
            {'datarobot-key': prediction_server.datarobot_key,
             'Content-Type': 'application/json',
             'x-forwarded-proto': 'https'})
        https_session.auth = (
            prediction_server.datarobot_username, prediction_server.api_token)
        return https_session

    def get_predictions(self, features, gorupby_ids):
        prediction_url = self.get_prediction_url(gorupby_ids)
        predictions_response = self._request_predictions(features, prediction_url)
        predictions = self._parse_response(
            predictions_response, features.index)

        return predictions

    def get_prediction_url(self, gorupby_ids):
        if len(gorupby_ids) == 1:
            full_url = f'{self.prediction_url}/predApi/v1.0/deployments/{gorupby_ids[0]}/predictions'
        else:
            full_url = f'{self.prediction_url}/predApi/v1.0/' \
                       f'{gorupby_ids[0]}/{gorupby_ids[1]}/predict'
        return full_url

    def _request_predictions(self, features, full_url):
        predictions_response = self.https_session.post(
            full_url,
            data=features.to_json(orient='records'))
        if predictions_response.status_code != HTTPStatus.OK:
            raise ArgumentError(
                faultstring=predictions_response.content.decode('utf-8'))
        return predictions_response.json()

    @staticmethod
    def _parse_response(predictions_json, index):
        unordered = {item['rowId']: item['prediction']
                     for item in predictions_json['data']}

        # The order of predictions which are returned by the server does not
        # match the order of the rows which were sent for scoring.
        # The server uses 'rowId' field to indicate the original order.
        ordered = [unordered[key] for key in sorted(unordered.keys())]

        return pd.DataFrame({'prediction': ordered}, index=index)

    def add_predictions(self, prepared_df, prediction_column):
        grouped_predictions = []

        if 'deployment_id' in prepared_df.columns:
            groupby_columns = ['deployment_id']
        else:
            groupby_columns = ['project_id', 'model_id']

        grouped_features = prepared_df.groupby(groupby_columns)

        for gorupby_ids, features in grouped_features:
            # http://pandas.pydata.org/pandas-docs/stable/groupby.html#iterating-through-groups
            ids = [gorupby_ids]
            if isinstance(gorupby_ids, tuple):
                ids = [id for id in gorupby_ids]

            predictions = self.get_predictions(
                features,
                ids)
            grouped_predictions.append(predictions)
        prepared_df[prediction_column] = \
            pd.concat(grouped_predictions)['prediction']
        return prepared_df
