import json
import logging

import boto3
from es_aws_functions import exception_classes, general_functions
from marshmallow import EXCLUDE, Schema, fields


class RuntimeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    def handle_error(self, e, data, **kwargs):
        logging.error(f"Error validating runtime params: {e}")
        raise ValueError(f"Error validating runtime params: {e}")

    run_id = fields.Str(required=True)
    queue_url = fields.Str(required=True)
    data = fields.Dict(required=True)


def lambda_handler(event, context):
    logger = logging.getLogger("Success Handler.")
    logger.setLevel(10)
    error_message = ''
    current_module = "Success Handler."
    run_id = 0
    try:
        logger.info("Success handler Begun.")
        run_id = event["run_id"]

        runtime_variables = RuntimeSchema().load(event)
        logger.info("Validated parameters.")

        queue_url = runtime_variables["queue_url"]
        logger.info("Retrieved configuration variables.")

        # Set up client
        sqs = boto3.client("sqs", region_name="eu-west-2")

        # Now delete the queue.
        sqs.delete_queue(QueueUrl=queue_url)

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
