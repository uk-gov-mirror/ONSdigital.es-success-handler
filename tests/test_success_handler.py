import boto3
import pytest
from es_aws_functions import test_generic_library
from moto import mock_sqs

import es_success_handler as lambda_wrangler_function

runtime_variables = {
              "RuntimeVariables": {},
              "data": {"lambdaresult": {"success": True}},
              "run_id": "01201",
              "queue_url": "queue_url"}
incomplete_runtime_variables = {
              "run_id": "01201"}
##########################################################################################
#                                     Generic                                            #
##########################################################################################


@pytest.mark.parametrize(
    "which_lambda,which_runtime_variables,which_environment_variables,"
    "which_data,expected_message,assertion",
    [
        (lambda_wrangler_function, runtime_variables,
         None, None,
         "ClientError", test_generic_library.wrangler_assert)
    ])
def test_client_error(which_lambda, which_runtime_variables,
                      which_environment_variables, which_data,
                      expected_message, assertion):
    test_generic_library.client_error(which_lambda, which_runtime_variables,
                                      which_environment_variables, which_data,
                                      expected_message, assertion)


@pytest.mark.parametrize(
    "which_lambda,which_runtime_variables,which_environment_variables,mockable_function,"
    "expected_message,assertion",
    [
        (lambda_wrangler_function, runtime_variables,
         None, "es_success_handler.EnvironSchema",
         "'Exception'", test_generic_library.wrangler_assert)
    ])
def test_general_error(which_lambda, which_runtime_variables,
                       which_environment_variables, mockable_function,
                       expected_message, assertion):
    test_generic_library.general_error(which_lambda, which_runtime_variables,
                                       which_environment_variables, mockable_function,
                                       expected_message, assertion)


@pytest.mark.parametrize(
    "which_lambda,which_environment_variables,expected_message,assertion",
    [
        (lambda_wrangler_function, None,
         "KeyError", test_generic_library.wrangler_assert)
    ])
def test_key_error(which_lambda, which_environment_variables,
                   expected_message, assertion):
    test_generic_library.key_error(which_lambda, which_environment_variables,
                                   expected_message, assertion)


@mock_sqs
@pytest.mark.parametrize(
    "which_lambda,expected_message,assertion,which_runtime_variables",
    [(lambda_wrangler_function,
      "Error validating environment parameters",
      test_generic_library.wrangler_assert, incomplete_runtime_variables)])
def test_value_error(which_lambda, expected_message, assertion, which_runtime_variables):
    test_generic_library.value_error(
        which_lambda, expected_message, assertion,
        runtime_variables=which_runtime_variables)

##########################################################################################
#                                     Specific                                           #
##########################################################################################


@mock_sqs
def test_method_pass():
    sqs = boto3.client("sqs", region_name="eu-west-2")
    sqs.create_queue(QueueName="test_queue")
    queue_url = sqs.get_queue_url(QueueName="test_queue")['QueueUrl']
    runtime_variables['queue_url'] = queue_url
    output = lambda_wrangler_function.lambda_handler(runtime_variables, "")

    assert output == {'id': '01201', 'resultFlag': 'PASS'}
    # Verify queue is deleted
    error = ''
    try:
        sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
    except Exception as e:
        error = e.args
        # Extract e for use in finally block
        # so if it doesnt throw exception test will fail
    finally:
        assert "The specified queue does not exist" in str(error)
