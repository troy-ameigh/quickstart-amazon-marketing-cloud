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
import pandas as pd

from library.platform_utils import PlatformUtilities

class CustomerInterface():
    '''
    Interface for managing customers

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

    def onboard_customer(self, customerId: str, customerDetails: dict):
        '''
        Onboards a customer to the TPS and WFM microservices. 
        Overwrites configuration settings if ran on an existing customer.

        Parameters
        ----------
        customerDetails: {
            customerPrefix: str
            customerName: str
            endemicType: str
            AMC: {
                amcOrangeAwsAccount: str
                amcS3BucketName: str
                amcDatasetName: str
                amcApiEndpoint: str
                region: str
            }
        }
        '''

        cust_details = {
            "customerId":customerId,
            "customerPrefix":customerDetails['customerPrefix'],
            "customerName":customerDetails['customerName'],
            "endemicType":customerDetails['endemicType'],
            "AMC":{
                "amcOrangeAwsAccount":customerDetails.get("amc",{}).get("amcOrangeAwsAccount",None),
                "amcS3BucketName":customerDetails.get("amc",{}).get("amcS3BucketName",None),
                "amcDatasetName":customerDetails.get("amc",{}).get("amcDatasetName",None),
                "amcApiEndpoint":customerDetails.get("amc",{}).get("amcApiEndpoint",None),
                "amcTeamName":self.TEAM_NAME,
                "amcRegion":customerDetails['region']
            }
        }
    
        dynamodb_client_wr= boto3.resource('dynamodb')
        tps_table = dynamodb_client_wr.Table(f'tps-{self.TEAM_NAME}-CustomerConfig-{self.ENV}')
        
        dynamodb_resp_wr = tps_table.put_item(Item=cust_details)
        return dynamodb_resp_wr

    def get_customers(self):
        '''
        Returns a list of all records in the WFM-CustomerConfig table
        '''

        dynamodb_client_rd= boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-CustomerConfig-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)
        
        cust_dtls_list =[]
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            cust_dtls_list.append(itm_dict)   
            
        df = pd.DataFrame(cust_dtls_list)
        return df

    def set_customer_config(self, customerId: str, customerConfig: dict):
        '''
        Updates a customer configuration in the WFM-CustomerConfig table
        
        Parameters
        ----------
        customerConfig: {
            enableWorkflowLibrary: bool
        }
        '''
        
        customer_table_name = f'wfm-{self.TEAM_NAME}-CustomerConfig-{self.ENV}'
        
        #get current config record to replace only new values passed in
        current_config = PlatformUtilities._get_customer_config(
            customer_table_name=customer_table_name,
            customerId=customerId
        )
        if current_config == False: #if _get_customer_config returned an error do not update record
            return
        
        #replace the old record params with new params passed in
        new_config = PlatformUtilities._deserializeDyanmoDBItem(current_config)
        for key, value in customerConfig.items():
            new_config['AMC']['WFM'][key] = value
        
        #add new record to config table
        dynamodb_client_wr= boto3.resource('dynamodb')
        customer_table = dynamodb_client_wr.Table(customer_table_name)
        
        dynamodb_resp_wr = customer_table.put_item(Item=new_config)
        return dynamodb_resp_wr


    def delete_customer(self, customerId: str):
        '''
        Deletes a customer from both CustomerConfig tables
        '''

        dynamodb_client_wr= boto3.resource('dynamodb')
        
        wfm_customer_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-CustomerConfig-{self.ENV}')
        responses = []
        wfm_response = wfm_customer_table.delete_item(
            Key = {
                'customerId': customerId
            }
        ) 
        responses.append(wfm_response)

        tps_customer_table = dynamodb_client_wr.Table(f'tps-{self.TEAM_NAME}-CustomerConfig-{self.ENV}')
        responses = []
        tps_response = tps_customer_table.delete_item(
            Key = {
                'customerId': customerId
            }
        ) 
        responses.append(tps_response)

        return responses

        