from unittest.mock import MagicMock

from price.logs import firehose


def test_put_record():
    mock_firehose = MagicMock()
    firehose.firehose_client = mock_firehose
    records = ['rec1', 'rec2', 'rec3']
    records_for_firehose = [{'Data': record + '\n'} for record in records]

    firehose.put_record(records)
    mock_firehose.put_record_batch.assert_called_once_with(
        DeliveryStreamName='DELIVERY_STREAM',
        Records=records_for_firehose)
    assert mock_firehose.put_record_batch.call_count == 1
