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
        dynamodb_client_wr= boto3.resource('dynamodb')

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
    
        tps_table = dynamodb_client_wr.Table(f'tps-{self.TEAM_NAME}-CustomerConfig-{self.ENV}')
        dynamodb_resp_wr = tps_table.put_item(Item=cust_details)
        return dynamodb_resp_wr

    def get_customers(self):
        dynamodb_client_rd= boto3.client('dynamodb')
        dynamodb_resp_rd = PlatformUtilities._dump_table(table_name=f'wfm-{self.TEAM_NAME}-CustomerConfig-{self.ENV}', dynamodb_client_rd=dynamodb_client_rd)
        
        cust_dtls_list =[]
        for itm in dynamodb_resp_rd:
            itm_dict = PlatformUtilities._deserializeDyanmoDBItem(itm)
            cust_dtls_list.append(itm_dict)   
            
        df = pd.DataFrame(cust_dtls_list)
        return df

    def delete_customer(self, customerId: str):
        dynamodb_client_wr= boto3.resource('dynamodb')
        
        customer_table = dynamodb_client_wr.Table(f'wfm-{self.TEAM_NAME}-CustomerConfig-{self.ENV}')
        
        response = customer_table.delete_item(
            Key = {
                'customerId': customerId
            }
        ) 
        
        return response