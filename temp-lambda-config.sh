#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

aws lambda add-permission \
          --function-name HIHO-gAuth \
          --principal secretsmanager.amazonaws.com \
          --action lambda:InvokeFunction \
          --statement-id SecretsManagerAccess
