import unittest
import unittest.mock as mock

import boto3
from es_aws_functions import exception_classes
from moto import mock_sns, mock_sqs

import es_success_handler  # noqa E402


class TestRuntimeErrorCapture(unittest.TestCase):

    @mock_sns
    @mock_sqs
    def test_method_pass(self):
        sqs = boto3.client("sqs", region_name="eu-west-2")
        sqs.create_queue(QueueName="test_queue")
        queue_url = sqs.get_queue_url(QueueName="test_queue")['QueueUrl']
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody="moo",
            MessageGroupId="123",
            MessageDeduplicationId="666"
        )

        indata = {
              "data": {"lambdaresult": {"success": True}},
              "run_id": "moo",
              "queue_url": queue_url}

        output = es_success_handler.lambda_handler(indata, "")
        assert "PASS" in output['resultFlag']
        error = ''
        try:
            sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
        except Exception as e:
            error = e.args
            # Extract e for use in finally block
            # so if it doesnt throw exception test will fail
        finally:

            assert "The specified queue does not exist" in str(error)

    @mock_sns
    @mock_sqs
    def test_method_fail(self):
        sqs = boto3.client("sqs", region_name="eu-west-2")
        sqs.create_queue(QueueName="test_queue")
        queue_url = sqs.get_queue_url(QueueName="test_queue")['QueueUrl']
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody="moo",
            MessageGroupId="123",
            MessageDeduplicationId="666"
        )
        indata = {
            "data": {"lambdaresult": {"success": False}},
            "run_id": "moo",
            "queue_url": queue_url}

        output = es_success_handler.lambda_handler(indata, "")
        assert "FAIL" in output['resultFlag']
        error = ''
        try:
            sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
        except Exception as e:
            error = e.args
            # Extract e for use in finally block
            # so if it doesnt throw exception test will fail
        finally:

            assert "The specified queue does not exist" in str(error)

    @mock_sqs
    def test_marshmallow_raises_exception(self):
        sqs = boto3.resource("sqs", region_name="eu-west-2")
        sqs.create_queue(QueueName="test_queue")
        queue_url = sqs.get_queue_by_name(QueueName="test_queue").url

        with unittest.TestCase.assertRaises(
                self, exception_classes.LambdaFailure) as exc_info:
            es_success_handler.lambda_handler(
                {"Cause": "Bad stuff",
                 "queue_url": queue_url
                 }, None
            )
        assert "Error validating environment" \
               in exc_info.exception.error_message

    @mock_sqs
    def test_catch_method_exception(self):
        # Method

        with mock.patch("es_success_handler.EnvironSchema.load") as mocked:
            mocked.side_effect = Exception("SQS Failure")
            with unittest.TestCase.assertRaises(
                    self, exception_classes.LambdaFailure) as exc_info:
                es_success_handler.lambda_handler(
                    {"Cause": "Bad stuff",
                     "run_id": "moo",
                     "queue_url": "abc"}, None
                )
            assert "General Error" \
                   in exc_info.exception.error_message
