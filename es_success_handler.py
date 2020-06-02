import json
import logging

import boto3
from es_aws_functions import exception_classes, general_functions
from marshmallow import Schema, fields


class EnvironSchema(Schema):
    run_id = fields.Str(required=True)
    queue_url = fields.Str(required=True)
    data = fields.Dict(required=True)


def lambda_handler(event, context):
    logger = logging.getLogger("Success Handler")
    logger.setLevel(10)
    error_message = ''
    current_module = 'Success Handler'
    run_id = 0
    try:
        run_id = event['run_id']
        schema = EnvironSchema()
        config, errors = schema.load(event)
        if errors:
            raise ValueError(f"Error validating environment parameters: {errors}")

        queue_url = config['queue_url']

        sqs = boto3.client('sqs', region_name='eu-west-2')

        # now delete the queue
        sqs.delete_queue(QueueUrl=queue_url)

        outcome = 'PASS'

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
