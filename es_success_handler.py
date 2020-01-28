import json
import logging

import boto3
from botocore.exceptions import ClientError
from es_aws_functions import exception_classes
from marshmallow import Schema, fields


class EnvironSchema(Schema):
    run_id = fields.Str(required=True)
    queue_url = fields.Str(required=True)
    data = fields.Dict(required=True)


def lambda_handler(event, context):
    logger = logging.getLogger("Success Handler")
    logger.setLevel(10)
    log_message = ''
    error_message = ''
    current_module = 'Success Handler'
    run_id = 0
    try:
        schema = EnvironSchema()
        config, errors = schema.load(event)
        if errors:
            raise ValueError(f"Error validating environment params: {errors}")

        queue_url = config['queue_url']
        run_id = config['run_id']
        sqs = boto3.client('sqs', region_name='eu-west-2')

        # now delete the queue
        sqs.delete_queue(QueueUrl=queue_url)
        if config['data']['lambdaresult']['success'] is True:
            outcome = 'PASS'
        else:
            outcome = 'FAIL'

        jsonresponse = """ {"resultFlag": \"""" + str(outcome)\
                       + """\", "id": \"""" + run_id + """\"}"""

    except ClientError as e:
        error_message = ("AWS Error in ("
                         + str(e.response["Error"]["Code"]) + ") "
                         + current_module + " |- "
                         + str(e.args)
                         + " | Run_id: " + str(run_id))

        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)

    except KeyError as e:
        error_message = ("Key Error in "
                         + current_module + " |- "
                         + str(e.args)
                         + " | Run_id: " + str(run_id)
                         )

        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)

    except ValueError as e:
        error_message = ("Blank or empty environment variable in "
                         + current_module + " |- "
                         + str(e.args)
                         + " | Run_id: " + str(run_id))

        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)
    except Exception as e:
        error_message = ("General Error in "
                         + current_module + " ("
                         + str(type(e)) + ") |- "
                         + str(e.args)
                         + " | Run_id: " + str(run_id))

        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)
    finally:
        if (len(error_message)) > 0:
            logger.error(log_message)
            raise exception_classes.LambdaFailure(error_message)
    return json.loads(jsonresponse)
