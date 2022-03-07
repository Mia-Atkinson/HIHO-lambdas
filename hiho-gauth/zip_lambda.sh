#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

if [ "$1" == "update" ]
then
	# Update Zip dependencies
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
	--zip-file fileb://gauth-deployment-package.zip \
