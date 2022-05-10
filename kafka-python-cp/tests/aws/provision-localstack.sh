#!/bin/bash
set +x
GREEN="\033[32m"
NO_COLOUR="\033[0m"
RED="\033[31m"

until curl http://localstack:4566 &>/dev/null; do
   echo "endpoint localstack is unavailable, wait"
   sleep 2
done

AWSCMD="aws --region eu-west-1 --endpoint-url=http://localstack:4566"
function logs(){
   local message=$1
   local parameter=$2

   printf "${RED}=%.0s${NO_COLOUR}" {1..100}
   printf "\n${GREEN}# %s (%s) \n${NO_COLOUR}" "$message", "$parameter"
   printf "${RED}=%.0s${NO_COLOUR}" {1..100}
   printf "\n"
}

echo "Start provisioning"

logs "Validation of template for " "[${SERVICENAME}-${ENVIRONMENT}]"
${AWSCMD} cloudformation validate-template --template-body file://infrastructure/cfn-kafka-service.yaml
logs "Validation done for " "[${SERVICENAME}-${ENVIRONMENT}]"
logs "Creating stack " "[${SERVICENAME}-${ENVIRONMENT}]"
${AWSCMD} cloudformation create-stack \
   --stack-name ${SERVICENAME}-${ENVIRONMENT} \
   --template-body file://infrastructure/cfn-kafka-service.yaml \
   --parameters \
		ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
		ParameterKey=ServiceName,ParameterValue=${SERVICENAME}
   ${AWSCMD} cloudformation wait stack-create-complete \
		--stack-name ${SERVICENAME}-${ENVIRONMENT}

STACK=$(${AWSCMD} cloudformation describe-stacks --stack-name ${SERVICENAME}-${ENVIRONMENT})
printf "\n"
printf "${RED}*%.0s${NO_COLOUR}" {1..100}
printf "\n"
printf "##${GREEN} %s ${NO_COLOUR} ##\n"  "${STACK}"
printf "${RED}*%.0s${NO_COLOUR}" {1..100}
printf "\n"
