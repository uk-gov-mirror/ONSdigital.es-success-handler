import pytest
from es_aws_functions import test_generic_library

import es_success_handler as lambda_wrangler_function

runtime_variables = {
              "RuntimeVariables": {"run_id": "01201"},
              }

##########################################################################################
#                                     Generic                                            #
##########################################################################################


@pytest.mark.parametrize(
    "which_lambda,which_runtime_variables,which_environment_variables,mockable_function,"
    "expected_message,assertion",
    [
        (lambda_wrangler_function, runtime_variables,
         None, "es_success_handler.json.loads",
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

##########################################################################################
#                                     Specific                                           #
##########################################################################################


def test_method_pass():
    output = lambda_wrangler_function.lambda_handler(runtime_variables, "")

    assert output == {"id": "01201", "resultFlag": "PASS"}
