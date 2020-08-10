import json

from es_aws_functions import exception_classes, general_functions


def lambda_handler(event, context):
    logger = general_functions.get_logger()
    error_message = ''
    current_module = "Success Handler."
    run_id = 0
    try:
        logger.info("Success Handler Begun.")
        run_id = event['RuntimeVariables']["run_id"]

        outcome = "PASS"

        jsonresponse = """ {"resultFlag": \"""" + str(outcome)\
                       + """\", "id": \"""" + run_id + """\"}"""
        jsonresponse = json.loads(jsonresponse)
    except Exception as e:
        error_message = general_functions.handle_exception(e, current_module,
                                                           run_id, context)
    finally:
        if (len(error_message)) > 0:
            logger.error(error_message)
            raise exception_classes.LambdaFailure(error_message)

    logger.info("Successfully completed module: " + current_module)

    return jsonresponse
