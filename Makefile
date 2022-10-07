SHELL=/bin/bash
PROFILE=default
REGION=$(shell aws configure get region --profile ${PROFILE})
ENV=dev


.PHONY: delete_repositories deploy_artifacts deploy_satellite deploy_all insert_tps_records create_workflows

 
delete_all: delete_ddk delete_bootstrap delete_repositories delete_all_items

help:
	@echo "Helper for the aws-ddk MakeFile";
	@echo "For clean up of the solution execute the following command";
	@echo "make delete_all PROFILE=\"<your_aws_profile>\" REGION=\"<the_deployment_region>\"";
	@echo "-------------------------------------------\n";


delete_repositories:
	./scripts/cleanup_scripts/delete_repositories.sh -s ${PROFILE} -r ${REGION} -d ddk-amc-quickstart

delete_ddk:
	cdk destroy AMC-${ENV}-QuickStart/amc-foundations \
	AMC-${ENV}-QuickStart/amc-data-lake-pipeline \
	AMC-${ENV}-QuickStart/amc-platform-manager \
	AMC-${ENV}-QuickStart/amc-tps \
	AMC-${ENV}-QuickStart/amc-wfm \
	AMC-${ENV}-QuickStart/amc-data-lake-datasets --force --profile ${PROFILE};

	cdk destroy ddk-amc-quickstart-pipeline --force --profile ${PROFILE}

delete_bootstrap:
	aws cloudformation delete-stack --stack-name DdkDevBootstrap --profile ${PROFILE}

delete_all_items:
	sleep 120

	pushd scripts/cleanup_scripts; python3 ./list_items_to_delete.py ${ENV} ${PROFILE}; popd;
	pushd scripts/cleanup_scripts; python3 ./delete_script.py ${PROFILE}; popd;



