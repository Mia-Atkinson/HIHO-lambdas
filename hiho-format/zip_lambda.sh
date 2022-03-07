#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

FILE=format-deployment-package.zip

if [ "$1" == "update" ] || [ ! -f "$FILE" ]
then
	# Update Zip dependencies
	pip install --target ./package oauth2client==1.5.2
	pip install --target ./package tempfile
	cd package
	zip -r ../format-deployment-package.zip .
	cd ..

else
	echo "Not updating dependencies"
fi

# Add handler to package
zip -g format-deployment-package.zip lambda_function.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-format \
	--zip-file fileb://format-deployment-package.zip \

# aws lambda update-function-configuration \
# 	--function-name HIHO-format \
# 	--description "Takes an AWS Transcribe output json from S3, formats as a human readable script and uploads to Google Drive"
