import boto3
import pandas as pd
import json

from library.platform_utils import PlatformUtilities


class WorkflowInterface():
    '''
    Interface for managing workflows

    Constructors
    ----------
    TEAM_NAME: str
    ENV: str
    '''
    def __init__(
            self, 
            TEAM_NAME: str, 
            ENV: str,
        ):
        #required parameters
        self.TEAM_NAME = TEAM_NAME
        self.ENV = ENV

    def get_workflow_records(self):
        '''
        Returns a list of all records in the AMCWorkflows table
        '''

        dynamodb_client_rd = boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-AMCWorkflows-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)

        wf_dtls_list = []
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            wf_dtls_list.append(itm_dict)
      
        df = pd.DataFrame(wf_dtls_list)
        return df

    def set_workflow_record(self, workflowId: str, customerId: str, workflowDetails: dict):
        '''Creates/updates a workflow record

        Parameters
        ----------
        workflowDetails: {
            metadata: {
                workflowName: str
                description: str
            }
            sqlQuery: str
            filteredMetricsDiscriminatorColumn: str
            defaultPayload: {
                    timeWindowEnd: str
                    timeWindowStart: str
                    timeWindowType: str
                    timeWindowTimeZone: str
                    workflowExecutedDate: str
            }
        }
        '''

        item = {
            'customerId': customerId,
            'workflowId': workflowId,
            'sqlQuery': workflowDetails['sqlQuery'],
            'defaultPayload': workflowDetails['defaultPayload']
        }
        if 'metadata' in workflowDetails and len(workflowDetails['metadata']) > 0:
            item['metadata'] = {}
            for key, value in workflowDetails['metadata'].items():
                item['metadata'][key] = value
        if 'filteredMetricsDiscriminatorColumn' in workflowDetails:
            item['filteredMetricsDiscriminatorColumn'] = workflowDetails['filteredMetricsDiscriminatorColumn']

        #add item to the AMCWorkflows table
        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflows-{self.ENV}')
        response = wf_library_table.put_item(Item=item)
        return response
    
    def delete_workflow_record(self, workflowId: str, customerId: str):
        '''
        Deletes a workflow record
        '''

        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflows-{self.ENV}')
        
        response = wf_library_table.delete_item(
            Key = {
                'workflowId': workflowId,
                'customerId': customerId
            }
        )
        return response

    def invoke_workflow(self, workflowId: str, customerId: str, payload: dict={}):
        '''
        Invokes a saved workflow manually once

        Parameters
        ----------
        payload: {
            timeWindowStart: str
            timeWindowEnd: str
            timeWindowType: str
            workflowExecutedDate: str
        }
        '''

        client = boto3.client('lambda')
        cargo = {
            'payload': payload
            }

        #check the override values passed in and get defaults for missing values
        check_payload_values = {
            'timeWindowStart',
            'timeWindowEnd',
            'timeWindowType',
            'workflowExecutedDate',
        }
        if len(payload) > 0:
            payload_overrides = set(payload.keys())
            check_payload_values -= payload_overrides
        if len(check_payload_values) > 0:
            lookup_values = PlatformUtilities._get_workflow_default_parameters(
                workflow_table_name=f'wfm-{self.TEAM_NAME}-AMCWorkflows-{self.ENV}',
                customerId=customerId,
                workflowId=workflowId,
                parameters=check_payload_values
                )
            if lookup_values == False: #if _get_workflow_default_parameters returned an error do not invoke Lambda
                return
            for parameter in lookup_values:
                cargo['payload'][parameter] = lookup_values[parameter]

        cargo['customerId'] = customerId
        cargo['payload']['workflowId'] = workflowId
        
        '''
        cargo = {
            customerId
            payload : {
                workflowId,
                timeWindowStart,
                timeWindowEnd,
                timeWindowType,
                workflowExecutedDate
            }
        }
        '''
        response = client.invoke(
                FunctionName=f'wfm-{self.TEAM_NAME}-ExecutionQueueProducer-{self.ENV}',
                InvocationType='Event',
                Payload=json.dumps(cargo)
            )
        return response

    def get_workflow_schedules(self):
        '''
        Returns a list of all records in the AMCWorkflowSchedules table
        '''

        dynamodb_client_rd= boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-AMCWorkflowSchedules-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)
        
        wf_dtls_list =[]
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            wf_dtls_list.append(itm_dict)   
            
        df = pd.DataFrame(wf_dtls_list)
        return df

    def delete_workflow_schedule(self, customerId: str, scheduleName: str):
        '''
        Deletes a workflow schedule
        '''

        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflowSchedules-{self.ENV}')
        
        response = wf_library_table.delete_item(
            Key = {
                'customerId': customerId,
                'Name': scheduleName
            }
        )
        return response

    def set_workflow_schedule(self, workflowId: str, customerId: str, scheduleDetails: dict, payload: dict={}):
        '''
        Creates/updates a workflow schedule

        Parameters
        ----------
        scheduleDetails: {
            scheduleName: str
            state: 'ENABLED' || 'DISABLED'
            scheduleExpression: eg. "custom(D * 11)"
            metadata: {
                scheduleDescription: str
            }
        }
        payload: {
            timeWindowStart: str
            timeWindowEnd: str
            timeWindowType: str
            workflowExecutedDate: str
        }
        '''

        item = {
            "customerId": customerId,
            "Input": {
                "payload": {
                    "workflowId": workflowId,
                }
            },
            "Name": scheduleDetails['scheduleName'],
            "State": scheduleDetails['state'],
            "ScheduleExpression": scheduleDetails['scheduleExpression']
        }

        #get default payload value for any params not passed in to the schedule
        check_payload_values = {
                'timeWindowStart',
                'timeWindowEnd',
                'timeWindowType',
                'workflowExecutedDate',
        }
        if len(payload) > 0:
                payload_overrides = set(scheduleDetails['payload'].keys())
                check_payload_values -= payload_overrides
        if len(check_payload_values) > 0:
            lookup_values = PlatformUtilities._get_workflow_default_parameters(
                workflow_table_name=f'wfm-{self.TEAM_NAME}-AMCWorkflows-{self.ENV}',
                customerId=customerId,
                workflowId=workflowId,
                parameters=check_payload_values
                )
            if lookup_values == False: #if _get_workflow_default_parameters returned an error do not invoke Lambda
                return
            for parameter in lookup_values:
                item['Input']['payload'][parameter] = lookup_values[parameter]

        #add any metadata passed in to the schedule
        if 'metadata' in scheduleDetails and len(scheduleDetails['metadata']) > 0:
            item['metadata'] = {}
            for param in scheduleDetails['metadata']:
                item['metadata'][param] = scheduleDetails['metadata'][param]

        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflowSchedules-{self.ENV}')
    
        dynamodb_resp_wr = wf_library_table.put_item(Item=item)
        return dynamodb_resp_wr

    def get_workflow_library_records(self):
        '''
        Returns a list of all records in the AMCWorkflowLibrary table
        '''

        dynamodb_client_rd= boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-AMCWorkflowLibrary-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)
        
        wf_dtls_list =[]
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            wf_dtls_list.append(itm_dict)   
            
        df = pd.DataFrame(wf_dtls_list)
        return df

    def set_workflow_library_record(
            self, 
            workflowId: str,
            workflowDetails: dict, 
            customerPrefix: str=None,
            endemicType: str=None,
            schedule: dict=None
        ):
        '''
        Creates/updates a workflow library record

        Parameters
        ----------
        workflowDetails: {
            metadata: {
                workflowName: str
                description: str
            }
            sqlQuery: str
            filteredMetricsDiscriminatorColumn: str
            defaultPayload: {
                    timeWindowEnd: str
                    timeWindowStart: str
                    timeWindowType: str
                    timeWindowTimeZone: str
                    workflowExecutedDate: str
            }
        }
        schedule: {
            scheduleName: str
            scheduleDetails: {
                metadata: {
                    scheduleDescription: str
                }
                state: 'ENABLED' || 'DISABLED'
                scheduleExpression: eg. 'custom(D * 11)'
            }
        }
        '''

        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflowLibrary-{self.ENV}')

        item = {
            'workflowId': workflowId,
            'sqlQuery': workflowDetails['sqlQuery'],
            'defaultPayload': workflowDetails['defaultPayload']
        }
        if 'metadata' in workflowDetails and len(workflowDetails['metadata']) > 0:
            item['metadata'] = {}
            for key, value in workflowDetails['metadata'].items():
                item['metadata'][key] = value
        if 'filteredMetricsDiscriminatorColumn' in workflowDetails:
            item['filteredMetricsDiscriminatorColumn'] = workflowDetails['filteredMetricsDiscriminatorColumn']

        #check for customerPrefix and endemicType values
        if customerPrefix:
            item['customerPrefix'] = customerPrefix
        if endemicType:
            item['endemicType'] = endemicType

        #do not add to table if missing values
        if schedule:
            if 'scheduleName' not in schedule:
                print('Error: a scheduleName must be passed in to schedule')
                return
            #if all the parameters checks pass, format the schedule properly
            item['schedule'] = {
                    'Input': {
                        'payload': {
                            'workflowId': workflowId,
                        }
                    },
                    'Name': schedule['scheduleName'],
                    'State': schedule['scheduleDetails']['state'],
                    'ScheduleExpression': schedule['scheduleDetails']['scheduleExpression']
                }
            for key, value in workflowDetails['defaultPayload'].items():
                item['schedule']['Input']['payload'][key] = value
            if 'metadata' in schedule['scheduleDetails'] and len(schedule['scheduleDetails']['metadata']) > 0:
                item['schedule']['metadata'] = {}
                for param in schedule['scheduleDetails']['metadata']:
                    item['schedule']['metadata'][param] = schedule['scheduleDetails']['metadata'][param]
            
        dynamodb_resp_wr = wf_library_table.put_item(Item=item)
        return dynamodb_resp_wr

    def delete_workflow_library_record(self, workflowId: str):
        '''
        Deletes a workflow library record
        '''

        dynamodb_client_wr= boto3.resource('dynamodb')
        wf_library_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-AMCWorkflowLibrary-{self.ENV}')
        response = wf_library_table.delete_item(
            Key = {
                'workflowId': workflowId,
            }
        )
        
        return response

    def get_execution_status(self, rows: int=5):
        '''
        Returns a list of records in the AMCExecutionStatus table
        '''
        
        dynamodb_client_rd= boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-AMCExecutionStatus-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)
        
        wf_dtls_list =[]
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            wf_dtls_list.append(itm_dict)   
            
        pd.options.mode.chained_assignment = None
        df = pd.DataFrame(wf_dtls_list)
        slice = df[["customerId", "workflowId", "createTime", "executionStatus"]]
        slice["createTime"] = pd.to_datetime(slice["createTime"])
        sorted = slice.sort_values("createTime", ascending=False)
        sorted.reset_index(drop=True, inplace=True)
        return sorted.head(rows)