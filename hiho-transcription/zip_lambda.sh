#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile
FILE=transcription-deployment-package.zip

if [ "$1" == "update" ] || [ ! -f "$FILE" ]
then
	echo "No dependencies to install"
	# Update Zip dependencies
	# pip install --target package google-api-python-client
	#cd package
	#zip -r ../transcription-deployment-package.zip .
	#cd ..
else
	echo "Not updating dependencies"
fi

# Add handler to package
zip transcription-deployment-package.zip transcription_handler.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-transcription \
	--zip-file fileb://transcription-deployment-package.zip

# aws lambda update-function-configuration \
# 	--function-name HIHO-transcription \
# 	--description "S3-put trigger to run AWS Transcribe on an Audio file and save the resulting json to S3"
