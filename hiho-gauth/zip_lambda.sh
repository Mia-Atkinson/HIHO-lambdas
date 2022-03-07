#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

FILE=gauth-deployment-package.zip

if [ "$1" == "update" ] || [ ! -f "$FILE" ]
then
	# Update Zip dependencies
	echo "Updating Dependencies"
	pip install --target package google-api-python-client
	cd package
	zip -r ../gauth-deployment-package.zip .
	cd ..

else
	echo "Not updating dependencies"
fi

# Add handler to package
zip -g gauth-deployment-package.zip gauth_handler.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-gAuth \
	--zip-file fileb://gauth-deployment-package.zip
