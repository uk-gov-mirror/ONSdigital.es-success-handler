import json
import logging

from es_aws_functions import aws_functions, exception_classes, general_functions
from marshmallow import EXCLUDE, Schema, fields


class RuntimeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def handle_error(self, e, data, **kwargs):
        logging.error(f"Error validating runtime params: {e}")
        raise ValueError(f"Error validating runtime params: {e}")

    bpm_queue_url = fields.Str(required=True)
    environment = fields.Str(required=True)
    run_id = fields.Str(required=True)
    survey = fields.Str(required=True)


def lambda_handler(event, context):
    error_message = ''
    current_module = "Success Handler."

    bpm_queue_url = None
    run_id = 0

    try:
        runtime_variables = RuntimeSchema().load(event["RuntimeVariables"])

        bpm_queue_url = runtime_variables["bpm_queue_url"]
        environment = runtime_variables["environment"]
        run_id = runtime_variables["run_id"]
        survey = runtime_variables["survey"]

    except Exception as e:
        error_message = general_functions.handle_exception(e, current_module,
                                                           run_id, context=context,
                                                           bpm_queue_url=bpm_queue_url)
        raise exception_classes.LambdaFailure(error_message)

    try:
        logger = general_functions.get_logger(survey, current_module, environment,
                                              run_id)
    except Exception as e:
        error_message = general_functions.handle_exception(e, current_module,
                                                           run_id, context=context,
                                                           bpm_queue_url=bpm_queue_url)
        raise exception_classes.LambdaFailure(error_message)

    try:
        logger.info("Started - retrieved configuration variables.")
        outcome = "PASS"
        jsonresponse = """ {"resultFlag": \"""" + str(outcome) \
                       + """\", "id": \"""" + run_id + """\"}"""
        jsonresponse = json.loads(jsonresponse)

    except Exception as e:
        error_message = general_functions.handle_exception(e, current_module,
                                                           run_id, context=context,
                                                           bpm_queue_url=bpm_queue_url)
    finally:
        if (len(error_message)) > 0:
            logger.error(error_message)
            raise exception_classes.LambdaFailure(error_message)

    logger.info("Successfully completed module.")
    # Send end status to BPM.
    status = "RUN COMPLETE"
    current_module = "BMI Results Processing Complete."
    aws_functions.send_bpm_status(bpm_queue_url, current_module, status, run_id)

    return jsonresponse
