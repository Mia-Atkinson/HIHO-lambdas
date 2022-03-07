#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

if [ "$1" == "update" ]
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
zip transcription-deployment-package.zip gauth_handler.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-gAuth \
	--zip-file fileb://transcription-deployment-package.zip \
