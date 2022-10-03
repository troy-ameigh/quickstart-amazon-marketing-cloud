# Platform Notebook Manager

The CDK package deploys an Amazon Sagemaker Notebook instance with pre-loaded 'Getting Started' notebooks and sample code.

If this is the first time you are using the service please refer to the [Getting_Started_With_AMC_Quickstart](./platform_manager/Getting_Started_With_AMC_Quickstart.ipynb) notebook. This notebook contains code that will help you onboard a client for the first time using the [Tenant Provisioning Service](./platform_manager/client_manager_microservices/README.md) as well as write your first AMC workflows using the [Workflow Manager Service](./platform_manager/datalake_hydration_microservices/README.md).

Refer to the [Resources Deployed](#resources-deployed) section below for information on all of the additional notebooks contained.


## AWS Service Requirements

The following AWS services are used in this utility:

1.  [Amazon Sagemaker Notebook instance](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html)
2.  [AWS Key Management Service (KMS)](https://aws.amazon.com/kms/)
3.  [Amazon S3](https://aws.amazon.com/s3/)

## Resources Deployed

This CDK Application deploys the following resources:

1. The CDK stack `platform_manager_sagemaker.py` present in the repository.
2. The Amazon Sagemaker Notebook instance `<amc>-quickstart-platform-manager-notebooks`. It will contain the following sample notebooks:
   * ### Getting Started
      * **platform_manager/Getting_Started_With_AMC_Quickstart.ipynb** - Provides a starting point for new users to the service. Contains a walkthrough for onboarding your first client as well as creating/running AMC workflows.
   * ### Client Manager Microservices
      * **platform_manager/client_manager_microservices/tps/tps_GettingStarted.ipynb** - Provides a guide about configuring/using the different features of the Tenant Provisioning Service with FAQs.
      * **platform_manager/client_manager_microservices/tps/client_manager_adminstrator_sample.ipynb** - Provides a sample notebook for a demo client and how a new AMC instance or a tenant can be onboarded to the platform. It also provides a functionality for scheduling default AMC workflows during the onboarding process.
   * ### Data Lake Hyrdration Microservices
      * **platform_manager/datalake_hydration_microservices/wfm/wfm_GettingStarted.ipynb** - Provides a Guide about configuring/using the different features of the Workflow Management Service with FAQs.
      * **platform_manager/datalake_hydration_microservices/wfm/customerConfig_wfm_sample.ipynb** - Provides a sample notebook to add/update/delete AMC instance related details for an existing onboarded AMC instance or tenant.
      * **platform_manager/datalake_hydration_microservices/wfm/workflowLibrary_wfm_sample.ipynb** - Provides a sample notebook to add/update/delete pre-loaded AMC workflows which will be applicable to all new AMC instance or tenants which are onboarded to the platform.
      * **platform_manager/datalake_hydration_microservices/wfm/workflowSchedules_wfm_sample.ipynb** - Provides a sample notebook to add/update/delete AMC workflow schedules for an existing AMC instance or tenant which are already onboarded to the platform.
      * **platform_manager/datalake_hydration_microservices/wfm/workflows_wfm_sample.ipynb** - Provides a sample notebook to add/update/delete AMC workflow details for an existing AMC instance or tenant which are already onboarded to the platform.
      * **platform_manager/datalake_hydration_microservices/wfm/workflow_invoke_wfm_sample.ipynb** - Provides a sample notebook to adhoc (out of schedule) invocation of AMC workflows for a particular AMC instance or tenant.
