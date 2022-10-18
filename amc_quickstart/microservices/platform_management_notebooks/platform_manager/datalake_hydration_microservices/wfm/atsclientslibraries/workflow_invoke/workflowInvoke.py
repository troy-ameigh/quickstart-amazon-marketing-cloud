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
import json


def get_workflow_default_settings(workflow_id: str, customer_id: str, table_name: str, parameters: set):
    print(f'Override values not set for: {parameters}. Reverting to default schedule for these parameters')
    dynamodb_client_rd= boto3.client('dynamodb')
    wf_table_name = table_name

    try:
        response = dynamodb_client_rd.get_item(
            TableName=wf_table_name,
            Key = {
                'customerId': {'S': customer_id},
                'workflowId': {'S': workflow_id}
            }
        )
        if 'Item' not in response:
            print('ERROR: customerId and/or workflowId not found')
            return False

        default_settings = {}
        for param in parameters:
            try:
                val = response['Item']['defaultSchedule']['M']['Input']['M']['payload']['M'][param]['S']
                default_settings[param] = val
            except Exception as e:
                print(f'ERROR: No default value set for {e}. Set default value in the AMCWorkflows table or override in the payload')
                return False
        return default_settings
    
    except Exception as e:
        print(e)
        return False

def invoke_workflow(workflow, TEAM_NAME, ENV):
    client = boto3.client('lambda')
    item = workflow

    payload = {
        'customerId': item['customerId'],
        'payload': item['Input']['payload']
    }

    check_payload_values = {
        'timeWindowStart',
        'timeWindowEnd',
        'timeWindowType',
        'workflow_executed_date',
    }
    payload_overrides = set(payload['payload'].keys())
    check_payload_values -= payload_overrides
    if len(check_payload_values) > 0:
        default_settings = get_workflow_default_settings(
            workflow_id=payload['payload']['workflowId'],
            customer_id=payload['customerId'],
            table_name=f'wfm-{TEAM_NAME}-AMCWorkflows-{ENV}',
            parameters=check_payload_values
            )
        if default_settings == False: #if default settings returned an error do not invoke Lambda
            return
        for parameter in default_settings:
            payload['payload'][parameter] = default_settings[parameter]

    response = client.invoke(
            FunctionName=f'wfm-{TEAM_NAME}-ExecutionQueueProducer-{ENV}',
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
    return response

def invoke_workflows(workflow_list, TEAM_NAME, ENV, customer_id):
    responses =[]
    try:
        for workflow in workflow_list:
            workflow_record = {}
            workflow_record["customerId"] = customer_id
            workflow_record["Input"] = workflow["defaultSchedule"]["Input"]
            workflow_record["Input"]["payload"]["workflowId"] = workflow["workflowId"] + "_v" + str(workflow["version"])
            responses.append(invoke_workflow(workflow=workflow_record, TEAM_NAME=TEAM_NAME, ENV=ENV)) 
        return responses
    except Exception as e:
        print(e)