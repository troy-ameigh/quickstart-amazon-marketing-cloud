# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import boto3
import os
from aws_lambda_powertools import Logger
from wfm import wfm_utils

logger = Logger(service="WorkFlowManagement", level="INFO")
wfmutils = wfm_utils.Utils(logger)

sqs = boto3.client('sqs')
ssm = boto3.client('ssm')
ddb = boto3.client('dynamodb')


def handle_updated_item(item, event_name, configs, workflows_table, workflow_schedule_table):

    logger.info('event: {} item {} '.format(event_name, item))

    # if the item passed in endemicType or customerPrefix then we have to remove the record from inapplicable customers
    endemic_flag = False
    prefix_flag = False

    workflow_endemic_type = ''
    if 'endemicType' in item:
        workflow_endemic_type = item['endemicType']
        endemic_flag = True
    workflow_customer_prefix = ''
    if 'customerPrefix' in item:
        workflow_customer_prefix = item['customerPrefix']
        prefix_flag = True
    
    for customerId in configs:
        logger.info(f'checking customer: {customerId}')

        workflow_item_to_update = item.copy()
        workflow_item_to_update['customerId'] = customerId
        workflow_item_to_update.pop('schedule', None)
        if 'schedule' in item:
            schedule_item_to_update = item['schedule'].copy()
            schedule_item_to_update['customerId'] = customerId

        enable_workflow_library = False
        if "enableWorkflowLibrary" in configs[customerId]['AMC']['WFM']:
            enable_workflow_library = configs[customerId]['AMC']['WFM']["enableWorkflowLibrary"]
        if not enable_workflow_library:
            logger.info(f'workflow library not enabled')
            continue

        customer_endemic_type = ''
        if "endemicType" in configs[customerId]:
            customer_endemic_type = configs[customerId]["endemicType"]
        if endemic_flag == True and workflow_endemic_type != customer_endemic_type:
            logger.info(f'workflow endemicType: {workflow_endemic_type}, customer endemicType: {customer_endemic_type}')
            wfmutils.dynamodb_delete_item(
                table_name=workflows_table, 
                key={
                    "customerId": customerId,
                    "workflowId": workflow_item_to_update["workflowId"]
                }
            )
            if schedule_item_to_update:
                wfmutils.dynamodb_delete_item(table_name=workflow_schedule_table, 
                key={
                    "customerId": customerId,
                    "Name": schedule_item_to_update["Name"]
                }
            )
            continue

        customer_customer_prefix = ''
        if "customerPrefix" in configs[customerId]:
            customer_customer_prefix = configs[customerId]["customerPrefix"]
        if prefix_flag == True and workflow_customer_prefix != customer_customer_prefix:
            logger.info(f'workflow customerPrefix: {workflow_customer_prefix}, customer customerPrefix: {customer_customer_prefix}')
            wfmutils.dynamodb_delete_item(
                table_name=workflows_table, 
                key={
                    "customerId": customerId,
                    "workflowId": workflow_item_to_update["workflowId"]
                }
            )
            if schedule_item_to_update:
                wfmutils.dynamodb_delete_item(table_name=workflow_schedule_table, 
                key={
                    "customerId": customerId,
                    "Name": schedule_item_to_update["Name"]
                }
            )
            continue

        # if all checks pass, add the item to the appropriate tables
        wfmutils.dynamodb_put_item(workflows_table, workflow_item_to_update)
        if schedule_item_to_update:
            wfmutils.dynamodb_put_item(workflow_schedule_table, schedule_item_to_update)


def handle_deleted_item(item, event_name, configs, workflows_table, workflow_schedule_table):

    logger.info('event: {} item {} '.format(event_name, item))

    for customerId in configs:
        logger.info(f'checking customer: {customerId}')

        enable_workflow_library = False
        if "enableWorkflowLibrary" in configs[customerId]['AMC']['WFM']:
            enable_workflow_library = configs[customerId]['AMC']['WFM']["enableWorkflowLibrary"]
        if not enable_workflow_library:
            logger.info(f'workflow library not enabled')
            continue

        if enable_workflow_library:
            workflow_item_to_delete = item.copy()
            wfmutils.dynamodb_delete_item(
                table_name=workflows_table, 
                key={
                    "customerId": customerId,
                    "workflowId": workflow_item_to_delete["workflowId"]
                }
            )
            if 'schedule' in item:
                schedule_item_to_delete = item['schedule'].copy()
                wfmutils.dynamodb_delete_item(table_name=workflow_schedule_table, 
                key={
                    "customerId": customerId,
                    "Name": schedule_item_to_delete["Name"]
                }
            )


def lambda_handler(event, context):

    logger.info('event: {}'.format(event))

    workflows_table = os.environ['WORKFLOWS_TABLE_NAME']
    workflow_schedule_table = os.environ['WORKFLOW_SCHEDULE_TABLE']
    workflow_library_table = os.environ['WORKFLOW_LIBRARY_DYNAMODB_TABLE']

    # check to see if the trigger is being invoked for a new customer that needs to have the default workflows deployed
    if 'customerId' in event and 'deployForNewCustomer' in event and event['deployForNewCustomer']:
        # get the customer config record for the specific customer
        customer_config = wfmutils.dynamodb_get_customer_config_records(os.environ['CUSTOMERS_DYNAMODB_TABLE'],
                                                                        event['customerId'])
        # get the entire workflow library record set
        dynamodb_records = wfmutils.dynamodb_get_all_records(workflow_library_table)
        for workflow_library_record in dynamodb_records:
            logger.info(workflow_library_record)
            # treat each workflow records with auto deploy as if it were a newly inserted record for this customerId
            handle_updated_item(workflow_library_record, 'INSERT', customer_config, workflows_table,
                                    workflow_schedule_table,)
        return

    configs = wfmutils.dynamodb_get_customer_config_records(os.environ['CUSTOMERS_DYNAMODB_TABLE'])
    response = {}
    for record in event['Records']:

        if 'dynamodb' in record and 'NewImage' in record['dynamodb']:
            new_record = wfmutils.deseralize_dynamodb_item(record['dynamodb']['NewImage'])

        if 'dynamodb' in record and 'OldImage' in record['dynamodb']:
            old_record = wfmutils.deseralize_dynamodb_item(record['dynamodb']['OldImage'])

        if record['eventName'] in ['INSERT', 'MODIFY']:
            handle_updated_item(new_record, record['eventName'], configs, workflows_table, workflow_schedule_table,)

        if record['eventName'] in ['REMOVE']:
            handle_deleted_item(old_record, record['eventName'], configs, workflows_table, workflow_schedule_table,)

    return response
