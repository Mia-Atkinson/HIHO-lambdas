#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile
FILE=vocab-deployment-package.zip

if [ "$1" == "update" ] || [ ! -f "$FILE" ]
then
	echo "No dependencies to install"
	# Update Zip dependencies
	pip install --target package google-api-python-client
	cd package
	zip -r ../vocab-deployment-package.zip .
	cd ..
else
	echo "Not updating dependencies"
fi

# Add handler to package
zip vocab-deployment-package.zip vocab_handler.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-vocab \
	--zip-file fileb://vocab-deployment-package.zip

# aws lambda update-function-configuration \
# 	--function-name HIHO-transcription \
# 	--description "S3-put trigger to run AWS Transcribe on an Audio file and save the resulting json to S3"
